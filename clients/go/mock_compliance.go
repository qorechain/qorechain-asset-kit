// SPDX-License-Identifier: Apache-2.0

package assetkit

import (
	"context"
	"encoding/json"
	"fmt"
	"math"
	"math/big"
	"sort"
	"strconv"
	"strings"

	"google.golang.org/protobuf/proto"

	attestv1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/attest/v1"
	compliancev1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/compliance/v1"
)

func registryKey(moduleID string, version uint32) string {
	return moduleID + "@" + strconv.FormatUint(uint64(version), 10)
}

func (c *MockChain) bindingsOf(assetID string) []*compliancev1.Binding {
	list := c.bindings[assetID]
	out := make([]*compliancev1.Binding, 0, len(list))
	for _, b := range list {
		out = append(out, proto.Clone(b).(*compliancev1.Binding))
	}
	sort.SliceStable(out, func(i, j int) bool { return out[i].Position < out[j].Position })
	return out
}

func (c *MockChain) registerModule(m *compliancev1.MsgRegisterModule) (*compliancev1.MsgRegisterModuleResponse, error) {
	if m.Authority != c.authority {
		return nil, fail(ModuleCompliance, "ERROR_CODE_UNAUTHORIZED", "%s is not the governance authority", m.Authority)
	}
	mod := &compliancev1.ComplianceModule{}
	if m.Module != nil {
		mod = proto.Clone(m.Module).(*compliancev1.ComplianceModule)
	}
	if mod.ModuleId == "" || mod.Version < 1 {
		return nil, fail(ModuleCompliance, "ERROR_CODE_INVALID_PARAMS", "module id and a version >= 1 are required")
	}
	var latest uint32
	for _, x := range c.registry {
		if x.ModuleId == mod.ModuleId && x.Version > latest {
			latest = x.Version
		}
	}
	if mod.Version <= latest {
		return nil, fail(ModuleCompliance, "ERROR_CODE_MODULE_VERSION_EXISTS", "version must be greater than %d", latest)
	}
	if mod.Status == compliancev1.ModuleStatus_MODULE_STATUS_UNSPECIFIED {
		mod.Status = compliancev1.ModuleStatus_MODULE_STATUS_ACTIVE
	}
	c.registry[registryKey(mod.ModuleId, mod.Version)] = mod
	c.emit("qorechain.compliance.v1.EventModuleRegistered", &compliancev1.EventModuleRegistered{
		ModuleId: mod.ModuleId, Version: mod.Version, Runtime: mod.Runtime,
	})
	return &compliancev1.MsgRegisterModuleResponse{}, nil
}

func (c *MockChain) moduleVersion(moduleID string, version uint32) (*compliancev1.ComplianceModule, error) {
	mod, ok := c.registry[registryKey(moduleID, version)]
	if !ok {
		return nil, fail(ModuleCompliance, "ERROR_CODE_MODULE_NOT_FOUND", "module %s v%d not found", moduleID, version)
	}
	return mod, nil
}

func (c *MockChain) setModuleStatus(m *compliancev1.MsgSetModuleStatus) (*compliancev1.MsgSetModuleStatusResponse, error) {
	if m.Authority != c.authority {
		return nil, fail(ModuleCompliance, "ERROR_CODE_UNAUTHORIZED", "%s is not the governance authority", m.Authority)
	}
	mod, err := c.moduleVersion(m.ModuleId, m.Version)
	if err != nil {
		return nil, err
	}
	mod.Status = m.Status
	c.emit("qorechain.compliance.v1.EventModuleStatusChanged", &compliancev1.EventModuleStatusChanged{
		ModuleId: m.ModuleId, Version: m.Version, Status: m.Status,
	})
	return &compliancev1.MsgSetModuleStatusResponse{}, nil
}

func (c *MockChain) requireAssetIssuer(assetID, signer string) error {
	r, ok := c.assets[assetID]
	if !ok || r.asset.Issuer != signer {
		return fail(ModuleCompliance, "ERROR_CODE_NOT_ISSUER", "%s is not the issuer of %s", signer, assetID)
	}
	return nil
}

func isNonNegInt(v any) bool {
	f, ok := v.(float64)
	return ok && f >= 0 && f == math.Trunc(f)
}

func intList(p map[string]any, key string) bool {
	list, ok := p[key].([]any)
	if !ok || len(list) == 0 {
		return false
	}
	for _, x := range list {
		if !isNonNegInt(x) {
			return false
		}
	}
	return true
}

func numberList(p map[string]any, key string) []float64 {
	list, _ := p[key].([]any)
	out := make([]float64, 0, len(list))
	for _, x := range list {
		if f, ok := x.(float64); ok {
			out = append(out, f)
		}
	}
	return out
}

func decodeParams(js string) (map[string]any, bool) {
	if js == "" {
		js = "{}"
	}
	var v any
	if err := json.Unmarshal([]byte(js), &v); err != nil {
		return nil, false
	}
	p, ok := v.(map[string]any)
	return p, ok
}

func (c *MockChain) parseParams(moduleID, js string) (map[string]any, error) {
	p, ok := decodeParams(js)
	if !ok {
		return nil, fail(ModuleCompliance, "ERROR_CODE_INVALID_PARAMS", "params_json must be a JSON object")
	}
	bad := func(why string) error {
		return fail(ModuleCompliance, "ERROR_CODE_INVALID_PARAMS", "%s: %s", moduleID, why)
	}
	switch moduleID {
	case "identity-verified":
		if !intList(p, "topics") {
			return nil, bad("topics must be a non-empty list of integers")
		}
	case "country-allowlist", "country-blocklist":
		if !intList(p, "countries") {
			return nil, bad("countries must be a non-empty list of integers")
		}
	case "max-holders":
		if !isNonNegInt(p["max"]) || p["max"].(float64) < 1 {
			return nil, bad("max must be a positive integer")
		}
	case "max-balance":
		s, ok := p["max"].(string)
		if !ok || !integerPattern.MatchString(s) {
			return nil, bad("max must be an integer string")
		}
	case "attestation-fresh":
		s, _ := p["kind"].(string)
		if attestv1.AttestationKind_value[s] <= 0 {
			return nil, bad("kind must be an AttestationKind name")
		}
	}
	return p, nil
}

func (c *MockChain) bindModule(m *compliancev1.MsgBindModule) (*compliancev1.MsgBindModuleResponse, error) {
	if err := c.requireAssetIssuer(m.AssetId, m.Issuer); err != nil {
		return nil, err
	}
	mod, err := c.moduleVersion(m.ModuleId, m.Version)
	if err != nil {
		return nil, err
	}
	switch mod.Status {
	case compliancev1.ModuleStatus_MODULE_STATUS_DEPRECATED:
		return nil, fail(ModuleCompliance, "ERROR_CODE_MODULE_DEPRECATED", "module version is deprecated")
	case compliancev1.ModuleStatus_MODULE_STATUS_DISABLED:
		return nil, fail(ModuleCompliance, "ERROR_CODE_MODULE_DISABLED", "module version is disabled")
	}
	if _, err := c.parseParams(m.ModuleId, m.ParamsJson); err != nil {
		return nil, err
	}
	list := c.bindings[m.AssetId]
	for _, b := range list {
		if b.ModuleId == m.ModuleId {
			return nil, fail(ModuleCompliance, "ERROR_CODE_BINDING_EXISTS", "%s is already bound", m.ModuleId)
		}
	}
	if uint32(len(list)) >= c.assetParams.MaxComplianceModules {
		return nil, fail(ModuleCompliance, "ERROR_CODE_TOO_MANY_BINDINGS", "too many bindings")
	}
	var position uint32
	for _, b := range list {
		if b.Position+1 > position {
			position = b.Position + 1
		}
	}
	params := m.ParamsJson
	if params == "" {
		params = "{}"
	}
	c.bindings[m.AssetId] = append(list, &compliancev1.Binding{
		AssetId: m.AssetId, ModuleId: m.ModuleId, Version: m.Version, ParamsJson: params, Position: position,
	})
	c.emit("qorechain.compliance.v1.EventModuleBound", &compliancev1.EventModuleBound{
		AssetId: m.AssetId, ModuleId: m.ModuleId, Version: m.Version,
	})
	return &compliancev1.MsgBindModuleResponse{}, nil
}

func (c *MockChain) unbindModule(m *compliancev1.MsgUnbindModule) (*compliancev1.MsgUnbindModuleResponse, error) {
	if err := c.requireAssetIssuer(m.AssetId, m.Issuer); err != nil {
		return nil, err
	}
	list := c.bindings[m.AssetId]
	var kept []*compliancev1.Binding
	found := false
	for _, b := range list {
		if b.ModuleId == m.ModuleId {
			found = true
		} else {
			kept = append(kept, b)
		}
	}
	if !found {
		return nil, fail(ModuleCompliance, "ERROR_CODE_BINDING_NOT_FOUND", "%s is not bound", m.ModuleId)
	}
	c.bindings[m.AssetId] = kept
	c.emit("qorechain.compliance.v1.EventModuleUnbound", &compliancev1.EventModuleUnbound{AssetId: m.AssetId, ModuleId: m.ModuleId})
	return &compliancev1.MsgUnbindModuleResponse{}, nil
}

func (c *MockChain) migrateBinding(m *compliancev1.MsgMigrateBinding) (*compliancev1.MsgMigrateBindingResponse, error) {
	if err := c.requireAssetIssuer(m.AssetId, m.Issuer); err != nil {
		return nil, err
	}
	var b *compliancev1.Binding
	for _, x := range c.bindings[m.AssetId] {
		if x.ModuleId == m.ModuleId {
			b = x
		}
	}
	if b == nil {
		return nil, fail(ModuleCompliance, "ERROR_CODE_BINDING_NOT_FOUND", "%s is not bound", m.ModuleId)
	}
	mod, err := c.moduleVersion(m.ModuleId, m.ToVersion)
	if err != nil {
		return nil, err
	}
	if mod.Status != compliancev1.ModuleStatus_MODULE_STATUS_ACTIVE {
		return nil, fail(ModuleCompliance, "ERROR_CODE_MODULE_DEPRECATED", "target version is not active")
	}
	params := m.ParamsJson
	if params == "" {
		params = b.ParamsJson
	}
	if _, err := c.parseParams(m.ModuleId, params); err != nil {
		return nil, err
	}
	from := b.Version
	b.Version = m.ToVersion
	b.ParamsJson = params
	c.emit("qorechain.compliance.v1.EventBindingMigrated", &compliancev1.EventBindingMigrated{
		AssetId: m.AssetId, ModuleId: m.ModuleId, FromVersion: from, ToVersion: m.ToVersion,
	})
	return &compliancev1.MsgMigrateBindingResponse{}, nil
}

func refuse(reason string) (string, bool) { return reason, true }

func allow() (string, bool) { return "", false }

func joinTopics(ts []uint32) string {
	parts := make([]string, len(ts))
	for i, t := range ts {
		parts[i] = strconv.FormatUint(uint64(t), 10)
	}
	return strings.Join(parts, ",")
}

func containsCountry(list []float64, country uint32) bool {
	for _, x := range list {
		if x == float64(country) {
			return true
		}
	}
	return false
}

func (c *MockChain) builtinLogic(moduleID string) ModuleLogic {
	switch moduleID {
	case "identity-verified":
		return func(ctx ModuleContext) (string, bool) {
			var topics []uint32
			for _, t := range numberList(ctx.Params, "topics") {
				topics = append(topics, uint32(t))
			}
			if missing := ctx.Chain.MissingTopics(ctx.To, topics); len(missing) > 0 {
				return refuse(fmt.Sprintf("%s is not verified for topics %s", ctx.To, joinTopics(missing)))
			}
			return allow()
		}
	case "country-allowlist":
		return func(ctx ModuleContext) (string, bool) {
			country, ok := ctx.Chain.CountryOf(ctx.To)
			if !ok {
				return refuse(ctx.To + " has no identity")
			}
			if containsCountry(numberList(ctx.Params, "countries"), country) {
				return allow()
			}
			return refuse(fmt.Sprintf("country %d is not allowed", country))
		}
	case "country-blocklist":
		return func(ctx ModuleContext) (string, bool) {
			country, ok := ctx.Chain.CountryOf(ctx.To)
			if ok && containsCountry(numberList(ctx.Params, "countries"), country) {
				return refuse(fmt.Sprintf("country %d is blocked", country))
			}
			return allow()
		}
	case "max-holders":
		return func(ctx ModuleContext) (string, bool) {
			r := ctx.Chain.assets[ctx.AssetID]
			count := 0
			for _, h := range r.holders {
				if h.balance.Sign() > 0 {
					count++
				}
			}
			if ctx.Chain.peekHolder(r, ctx.To).balance.Sign() == 0 && ctx.Amount.Sign() > 0 {
				count++
			}
			if ctx.From != "" && ctx.From != ctx.To && ctx.Chain.peekHolder(r, ctx.From).balance.Cmp(ctx.Amount) == 0 {
				count--
			}
			max, _ := ctx.Params["max"].(float64)
			if float64(count) > max {
				return refuse(fmt.Sprintf("more than %v holders", ctx.Params["max"]))
			}
			return allow()
		}
	case "max-balance":
		return func(ctx ModuleContext) (string, bool) {
			r := ctx.Chain.assets[ctx.AssetID]
			s, _ := ctx.Params["max"].(string)
			max, _ := new(big.Int).SetString(s, 10)
			after := new(big.Int).Add(ctx.Chain.peekHolder(r, ctx.To).balance, ctx.Amount)
			if after.Cmp(max) > 0 {
				return refuse(fmt.Sprintf("balance of %s would exceed %s", ctx.To, s))
			}
			return allow()
		}
	case "attestation-fresh":
		return func(ctx ModuleContext) (string, bool) {
			name, _ := ctx.Params["kind"].(string)
			f := ctx.Chain.Freshness(ctx.AssetID, attestv1.AttestationKind(attestv1.AttestationKind_value[name])).Freshness
			if f == attestv1.Freshness_FRESHNESS_FRESH {
				return allow()
			}
			return refuse(fmt.Sprintf("latest %s attestation is %s", name, f.String()))
		}
	}
	return nil
}

type complianceResult struct {
	moduleID string
	version  uint32
	reason   string
}

func (c *MockChain) runCompliance(assetID, from, to string, amount *big.Int) *complianceResult {
	for _, b := range c.bindingsOf(assetID) {
		mod, ok := c.registry[registryKey(b.ModuleId, b.Version)]
		if !ok || mod.Status == compliancev1.ModuleStatus_MODULE_STATUS_DISABLED {
			return &complianceResult{b.ModuleId, b.Version, "module version is disabled"}
		}
		logic := c.customLogic[b.ModuleId]
		if logic == nil {
			logic = c.builtinLogic(b.ModuleId)
		}
		if logic == nil {
			return &complianceResult{b.ModuleId, b.Version, "no logic for this module in MockChain"}
		}
		params, _ := decodeParams(b.ParamsJson)
		ctx := ModuleContext{Chain: c, AssetID: assetID, From: from, To: to, Amount: new(big.Int).Set(amount), Params: params}
		if reason, refused := logic(ctx); refused {
			return &complianceResult{b.ModuleId, b.Version, reason}
		}
	}
	return nil
}

// mockCompliance adapts MockChain to ComplianceAPI.
type mockCompliance struct{ c *MockChain }

func (x mockCompliance) RegisterModule(_ context.Context, m *compliancev1.MsgRegisterModule) (*compliancev1.MsgRegisterModuleResponse, error) {
	return x.c.registerModule(orEmpty(m))
}

func (x mockCompliance) SetModuleStatus(_ context.Context, m *compliancev1.MsgSetModuleStatus) (*compliancev1.MsgSetModuleStatusResponse, error) {
	return x.c.setModuleStatus(orEmpty(m))
}

func (x mockCompliance) BindModule(_ context.Context, m *compliancev1.MsgBindModule) (*compliancev1.MsgBindModuleResponse, error) {
	return x.c.bindModule(orEmpty(m))
}

func (x mockCompliance) UnbindModule(_ context.Context, m *compliancev1.MsgUnbindModule) (*compliancev1.MsgUnbindModuleResponse, error) {
	return x.c.unbindModule(orEmpty(m))
}

func (x mockCompliance) MigrateBinding(_ context.Context, m *compliancev1.MsgMigrateBinding) (*compliancev1.MsgMigrateBindingResponse, error) {
	return x.c.migrateBinding(orEmpty(m))
}

func (x mockCompliance) Params(context.Context, *compliancev1.QueryParamsRequest) (*compliancev1.QueryParamsResponse, error) {
	return &compliancev1.QueryParamsResponse{Params: proto.Clone(x.c.complianceParams).(*compliancev1.Params)}, nil
}

func (x mockCompliance) Modules(_ context.Context, q *compliancev1.QueryModulesRequest) (*compliancev1.QueryModulesResponse, error) {
	q = orEmpty(q)
	out := &compliancev1.QueryModulesResponse{}
	for _, mod := range x.c.registry {
		if q.ModuleId == "" || mod.ModuleId == q.ModuleId {
			out.Modules = append(out.Modules, proto.Clone(mod).(*compliancev1.ComplianceModule))
		}
	}
	sort.Slice(out.Modules, func(i, j int) bool {
		if out.Modules[i].ModuleId != out.Modules[j].ModuleId {
			return out.Modules[i].ModuleId < out.Modules[j].ModuleId
		}
		return out.Modules[i].Version < out.Modules[j].Version
	})
	return out, nil
}

func (x mockCompliance) Module(_ context.Context, q *compliancev1.QueryModuleRequest) (*compliancev1.QueryModuleResponse, error) {
	q = orEmpty(q)
	mod, err := x.c.moduleVersion(q.ModuleId, q.Version)
	if err != nil {
		return nil, err
	}
	return &compliancev1.QueryModuleResponse{Module: proto.Clone(mod).(*compliancev1.ComplianceModule)}, nil
}

func (x mockCompliance) Bindings(_ context.Context, q *compliancev1.QueryBindingsRequest) (*compliancev1.QueryBindingsResponse, error) {
	return &compliancev1.QueryBindingsResponse{Bindings: x.c.bindingsOf(orEmpty(q).AssetId)}, nil
}

func (x mockCompliance) Check(_ context.Context, q *compliancev1.QueryCheckRequest) (*compliancev1.QueryCheckResponse, error) {
	q = orEmpty(q)
	amount := new(big.Int)
	if integerPattern.MatchString(q.Amount) {
		amount.SetString(q.Amount, 10)
	}
	if res := x.c.runCompliance(q.AssetId, q.From, q.To, amount); res != nil {
		return &compliancev1.QueryCheckResponse{Allowed: false, ModuleId: res.moduleID, Version: res.version, Reason: res.reason}, nil
	}
	return &compliancev1.QueryCheckResponse{Allowed: true}, nil
}

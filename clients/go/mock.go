// SPDX-License-Identifier: Apache-2.0

package assetkit

import (
	"math/big"
	"regexp"
	"sort"

	"google.golang.org/protobuf/proto"

	assetv1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/asset/v1"
	attestv1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/attest/v1"
	compliancev1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/compliance/v1"
	identityv1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/identity/v1"
	settlementv1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/settlement/v1"
)

// MockChain is an in-memory implementation of the PROPOSED modules, for
// building and testing applications. It is not QoreChain and proves nothing
// about how the chain would behave; it implements the rules written in
// docs/proposal.md. Signer fields are trusted as given: there are no
// signatures in the mock. A MockChain is not safe for concurrent use.
type MockChain struct {
	authority   string
	height      int64
	time        int64
	log         []Event
	keys        map[string]hybridKey
	bank        map[string]map[string]*big.Int
	customLogic map[string]ModuleLogic

	// x/asset
	assetParams *assetv1.Params
	assets      map[string]*assetRec

	// x/identity
	identityParams *identityv1.Params
	identities     map[string]*identityv1.Identity
	identityOf     map[string]string
	claimIssuers   map[string]*identityv1.ClaimIssuer

	// x/compliance
	complianceParams *compliancev1.Params
	registry         map[string]*compliancev1.ComplianceModule
	bindings         map[string][]*compliancev1.Binding

	// x/settlement
	settlementParams  *settlementv1.Params
	instructions      map[uint64]*settlementv1.Instruction
	nextInstructionID uint64
	venues            map[string]*settlementv1.Venue

	// x/attest
	attestParams      *attestv1.Params
	attesters         map[string]map[string]*attestv1.Attester
	attestations      []*attestv1.Attestation
	nextAttestationID uint64
}

// Event is one recorded event, in emission order.
type Event struct {
	// Full proto name, for example qorechain.asset.v1.EventMinted.
	Type   string
	Height int64
	Data   proto.Message
}

// ModuleContext is passed to a compliance module's logic.
type ModuleContext struct {
	Chain   *MockChain
	AssetID string
	// Empty for a mint.
	From   string
	To     string
	Amount *big.Int
	// The binding's parameters, parsed from JSON.
	Params map[string]any
}

// ModuleLogic returns a refusal reason and true to refuse, or false to allow.
type ModuleLogic func(ModuleContext) (reason string, refused bool)

// MockChainOptions configures NewMockChain.
type MockChainOptions struct {
	// Address treated as the governance authority. Default "authority".
	Authority string
	// Identity agents of x/identity. Default: none (the authority can always act).
	IdentityAgents []string
	// Initial block time, Unix seconds. Default 1767225600 (2026-01-01T00:00:00Z).
	Time int64
	// Initial height. Default 1.
	Height int64
}

type hybridKey struct{ registered, possessionProven bool }

var (
	assetIDPattern = regexp.MustCompile(`^[a-z][a-z0-9-]{2,31}$`)
	integerPattern = regexp.MustCompile(`^[0-9]+$`)
)

type builtinModule struct{ id, schema, description string }

var builtinModules = []builtinModule{
	{"identity-verified", `{"type":"object","required":["topics"],"properties":{"topics":{"type":"array","items":{"type":"integer"}}}}`,
		"The receiver is verified in x/identity for every listed claim topic."},
	{"country-allowlist", `{"type":"object","required":["countries"],"properties":{"countries":{"type":"array","items":{"type":"integer"}}}}`,
		"The receiver's identity country is in the list; no identity is refused."},
	{"country-blocklist", `{"type":"object","required":["countries"],"properties":{"countries":{"type":"array","items":{"type":"integer"}}}}`,
		"The receiver's identity country is not in the list; no identity is allowed."},
	{"max-holders", `{"type":"object","required":["max"],"properties":{"max":{"type":"integer","minimum":1}}}`,
		"The number of addresses with a positive balance never exceeds max."},
	{"max-balance", `{"type":"object","required":["max"],"properties":{"max":{"type":"string","pattern":"^[0-9]+$"}}}`,
		"The receiver's balance after the transfer is at most max."},
	{"attestation-fresh", `{"type":"object","required":["kind"],"properties":{"kind":{"type":"string"}}}`,
		"The latest attestation of the given kind for the asset is fresh."},
}

// NewMockChain returns an empty MockChain with the built-in compliance modules
// registered at version 1.
func NewMockChain(opts ...MockChainOptions) *MockChain {
	var o MockChainOptions
	if len(opts) > 0 {
		o = opts[0]
	}
	if o.Authority == "" {
		o.Authority = "authority"
	}
	if o.Time == 0 {
		o.Time = 1_767_225_600
	}
	if o.Height == 0 {
		o.Height = 1
	}
	c := &MockChain{
		authority:         o.Authority,
		height:            o.Height,
		time:              o.Time,
		keys:              map[string]hybridKey{},
		bank:              map[string]map[string]*big.Int{},
		customLogic:       map[string]ModuleLogic{},
		assetParams:       &assetv1.Params{CreationFee: "0", MaxAgents: 10, MaxComplianceModules: 10},
		assets:            map[string]*assetRec{},
		identityParams:    &identityv1.Params{IdentityAgents: append([]string(nil), o.IdentityAgents...)},
		identities:        map[string]*identityv1.Identity{},
		identityOf:        map[string]string{},
		claimIssuers:      map[string]*identityv1.ClaimIssuer{},
		complianceParams:  &compliancev1.Params{MaxModuleGas: 1_000_000},
		registry:          map[string]*compliancev1.ComplianceModule{},
		bindings:          map[string][]*compliancev1.Binding{},
		settlementParams:  &settlementv1.Params{MaxLegs: 10, MaxDeadlineSeconds: 30 * 86400},
		instructions:      map[uint64]*settlementv1.Instruction{},
		nextInstructionID: 1,
		venues:            map[string]*settlementv1.Venue{},
		attestParams:      &attestv1.Params{MaxObservationLagSeconds: 7 * 86400, MaxValiditySeconds: 400 * 86400},
		attesters:         map[string]map[string]*attestv1.Attester{},
		nextAttestationID: 1,
	}
	for _, m := range builtinModules {
		c.registry[registryKey(m.id, 1)] = &compliancev1.ComplianceModule{
			ModuleId:     m.id,
			Version:      1,
			Runtime:      compliancev1.ModuleRuntime_MODULE_RUNTIME_NATIVE,
			Status:       compliancev1.ModuleStatus_MODULE_STATUS_ACTIVE,
			ParamsSchema: m.schema,
			Description:  m.description,
		}
	}
	return c
}

var _ AssetKit = (*MockChain)(nil)

// Asset returns the x/asset facade.
func (c *MockChain) Asset() AssetAPI { return mockAsset{c} }

// Identity returns the x/identity facade.
func (c *MockChain) Identity() IdentityAPI { return mockIdentity{c} }

// Compliance returns the x/compliance facade.
func (c *MockChain) Compliance() ComplianceAPI { return mockCompliance{c} }

// Settlement returns the x/settlement facade.
func (c *MockChain) Settlement() SettlementAPI { return mockSettlement{c} }

// Attest returns the x/attest facade.
func (c *MockChain) Attest() AttestAPI { return mockAttest{c} }

// Authority is the address treated as the governance authority.
func (c *MockChain) Authority() string { return c.authority }

// Height is the current block height.
func (c *MockChain) Height() int64 { return c.height }

// Time is the current block time, Unix seconds.
func (c *MockChain) Time() int64 { return c.time }

// Advance moves the chain by blocks blocks and seconds seconds, then runs the
// end blocker: ON_BLOCK instructions due at the new height settle (or fail if
// not fully affirmed), then instructions past their deadline expire.
func (c *MockChain) Advance(blocks, seconds int64) {
	if blocks < 0 || seconds < 0 {
		panic("assetkit: cannot go back in time")
	}
	c.height += blocks
	c.time += seconds
	for _, id := range c.instructionIDs() {
		ins := c.instructions[id]
		due := ins.SettlementType == settlementv1.SettlementType_SETTLEMENT_TYPE_ON_BLOCK && ins.SettleHeight <= c.height
		switch {
		case due && ins.Status == settlementv1.InstructionStatus_INSTRUCTION_STATUS_AFFIRMED && c.time <= ins.Deadline:
			c.execute(ins)
		case due && ins.Status == settlementv1.InstructionStatus_INSTRUCTION_STATUS_PENDING:
			ins.Status = settlementv1.InstructionStatus_INSTRUCTION_STATUS_FAILED
			ins.FailureReason = "not fully affirmed at settle height"
			c.emit("qorechain.settlement.v1.EventInstructionFailed", &settlementv1.EventInstructionFailed{
				Id: ins.Id, LegIndex: 0, Reason: ins.FailureReason,
			})
		}
	}
	for _, id := range c.instructionIDs() {
		ins := c.instructions[id]
		if !isFinal(ins.Status) && c.time > ins.Deadline {
			ins.Status = settlementv1.InstructionStatus_INSTRUCTION_STATUS_EXPIRED
			c.emit("qorechain.settlement.v1.EventInstructionExpired", &settlementv1.EventInstructionExpired{Id: ins.Id})
		}
	}
}

// SetHybridKey sets what pqcKeyStatus would report for an address.
func (c *MockChain) SetHybridKey(address string, registered, possessionProven bool) {
	c.keys[address] = hybridKey{registered, possessionProven}
}

// HasHybridKey reports whether the address has a registered ML-DSA-87 key with
// proof of possession.
func (c *MockChain) HasHybridKey(address string) bool {
	k, ok := c.keys[address]
	return ok && k.registered && k.possessionProven
}

// FundBank credits a bank denom (for example "uqor") to an address: the cash
// side of DvP tests.
func (c *MockChain) FundBank(address, denom string, amount *big.Int) {
	m := c.bank[address]
	if m == nil {
		m = map[string]*big.Int{}
		c.bank[address] = m
	}
	cur := m[denom]
	if cur == nil {
		cur = new(big.Int)
	}
	m[denom] = new(big.Int).Add(cur, amount)
}

// BankBalance returns the bank balance of an address in a denom.
func (c *MockChain) BankBalance(address, denom string) *big.Int {
	if v := c.bank[address][denom]; v != nil {
		return new(big.Int).Set(v)
	}
	return new(big.Int)
}

// Events returns the recorded events, filtered by full type name when
// typeFilter is not empty. The returned slice is a copy.
func (c *MockChain) Events(typeFilter string) []Event {
	var out []Event
	for _, e := range c.log {
		if typeFilter == "" || e.Type == typeFilter {
			out = append(out, Event{Type: e.Type, Height: e.Height, Data: proto.Clone(e.Data)})
		}
	}
	return out
}

// DefineModuleLogic supplies the logic of a compliance module registered by
// governance (for example a WASM module).
func (c *MockChain) DefineModuleLogic(moduleID string, logic ModuleLogic) {
	c.customLogic[moduleID] = logic
}

func (c *MockChain) emit(typ string, data proto.Message) {
	c.log = append(c.log, Event{Type: typ, Height: c.height, Data: data})
}

func parseAmount(module, s string, allowZero bool) (*big.Int, error) {
	if !integerPattern.MatchString(s) {
		return nil, fail(module, "ERROR_CODE_INVALID_AMOUNT", "amount %q is not a non-negative integer", s)
	}
	n, _ := new(big.Int).SetString(s, 10)
	if !allowZero && n.Sign() == 0 {
		return nil, fail(module, "ERROR_CODE_INVALID_AMOUNT", "amount must be greater than zero")
	}
	return n, nil
}

func positiveInteger(s string) (*big.Int, bool) {
	if !integerPattern.MatchString(s) {
		return nil, false
	}
	n, _ := new(big.Int).SetString(s, 10)
	return n, n.Sign() > 0
}

func sortedKeys[V any](m map[string]V) []string {
	keys := make([]string, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	return keys
}

func contains[T comparable](list []T, v T) bool {
	for _, x := range list {
		if x == v {
			return true
		}
	}
	return false
}

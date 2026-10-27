// SPDX-License-Identifier: Apache-2.0

package assetkit

import (
	"context"
	"math/big"
	"sort"

	"google.golang.org/protobuf/proto"

	assetv1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/asset/v1"
)

type holder struct {
	balance      *big.Int
	authorized   bool
	frozen       bool
	frozenAmount *big.Int
}

func newHolder() *holder { return &holder{balance: new(big.Int), frozenAmount: new(big.Int)} }

func (h *holder) clone() *holder {
	return &holder{
		balance:      new(big.Int).Set(h.balance),
		authorized:   h.authorized,
		frozen:       h.frozen,
		frozenAmount: new(big.Int).Set(h.frozenAmount),
	}
}

type assetRec struct {
	asset *assetv1.Asset
	// address -> role -> granted height
	roles   map[string]map[assetv1.Role]int64
	holders map[string]*holder
}

type refusal struct {
	code     string
	moduleID string
	reason   string
}

func (r *refusal) message() string {
	if r.moduleID != "" {
		return r.moduleID + ": " + r.reason
	}
	return r.reason
}

func (r *refusal) err() error {
	return &MockChainError{Module: ModuleAsset, Code: r.code, Message: r.message()}
}

func flagsOf(r *assetRec) *assetv1.RwaFlagsV0 {
	if r.asset.Flags == nil {
		return &assetv1.RwaFlagsV0{}
	}
	return r.asset.Flags
}

func (c *MockChain) rec(assetID string) (*assetRec, error) {
	r, ok := c.assets[assetID]
	if !ok {
		return nil, fail(ModuleAsset, "ERROR_CODE_ASSET_NOT_FOUND", "asset %s not found", assetID)
	}
	return r, nil
}

func (c *MockChain) holderOf(r *assetRec, address string) *holder {
	h, ok := r.holders[address]
	if !ok {
		h = newHolder()
		r.holders[address] = h
	}
	return h
}

func (c *MockChain) peekHolder(r *assetRec, address string) *holder {
	if h, ok := r.holders[address]; ok {
		return h
	}
	return newHolder()
}

func hasRole(r *assetRec, address string, role assetv1.Role) bool {
	_, ok := r.roles[address][role]
	return ok
}

func (c *MockChain) requireSignerKey(r *assetRec, signer string) error {
	if flagsOf(r).RequireHybridSignature && !c.HasHybridKey(signer) {
		return fail(ModuleAsset, "ERROR_CODE_HYBRID_SIGNATURE_REQUIRED", "%s has no registered ML-DSA-87 key with proof of possession", signer)
	}
	return nil
}

func (c *MockChain) requireIssuer(r *assetRec, signer string) error {
	if r.asset.Issuer != signer {
		return fail(ModuleAsset, "ERROR_CODE_UNAUTHORIZED_ROLE", "%s is not the issuer of %s", signer, r.asset.AssetId)
	}
	return c.requireSignerKey(r, signer)
}

func (c *MockChain) requireAgent(r *assetRec, signer string) error {
	if r.asset.Issuer != signer && !hasRole(r, signer, assetv1.Role_ROLE_AGENT) {
		return fail(ModuleAsset, "ERROR_CODE_UNAUTHORIZED_ROLE", "%s is not an agent of %s", signer, r.asset.AssetId)
	}
	return c.requireSignerKey(r, signer)
}

// agentRec loads the asset and checks that the signer is an agent.
func (c *MockChain) agentRec(assetID, signer string) (*assetRec, error) {
	r, err := c.rec(assetID)
	if err != nil {
		return nil, err
	}
	return r, c.requireAgent(r, signer)
}

func (c *MockChain) issuerRec(assetID, signer string) (*assetRec, error) {
	r, err := c.rec(assetID)
	if err != nil {
		return nil, err
	}
	return r, c.requireIssuer(r, signer)
}

func (c *MockChain) createAsset(m *assetv1.MsgCreateAsset) (*assetv1.MsgCreateAssetResponse, error) {
	if !assetIDPattern.MatchString(m.AssetId) {
		return nil, fail(ModuleAsset, "ERROR_CODE_INVALID_ASSET_ID", "invalid asset id %q", m.AssetId)
	}
	if _, ok := c.assets[m.AssetId]; ok {
		return nil, fail(ModuleAsset, "ERROR_CODE_ASSET_EXISTS", "asset %s exists", m.AssetId)
	}
	flags := &assetv1.RwaFlagsV0{}
	if m.Flags != nil {
		flags = proto.Clone(m.Flags).(*assetv1.RwaFlagsV0)
	}
	maxSupply := ""
	if flags.SupplyCap {
		n, err := parseAmount(ModuleAsset, m.MaxSupply, false)
		if err != nil {
			return nil, err
		}
		maxSupply = n.String()
	}
	if flags.RequireHybridSignature && !c.HasHybridKey(m.Issuer) {
		return nil, fail(ModuleAsset, "ERROR_CODE_HYBRID_SIGNATURE_REQUIRED", "%s has no registered ML-DSA-87 key with proof of possession", m.Issuer)
	}
	a := &assetv1.Asset{
		AssetId:       m.AssetId,
		Issuer:        m.Issuer,
		Name:          m.Name,
		Symbol:        m.Symbol,
		Decimals:      m.Decimals,
		Flags:         flags,
		MaxSupply:     maxSupply,
		TotalSupply:   "0",
		Status:        assetv1.AssetStatus_ASSET_STATUS_ACTIVE,
		TermsHash:     append([]byte(nil), m.TermsHash...),
		TermsUri:      m.TermsUri,
		CreatedHeight: c.height,
	}
	c.assets[m.AssetId] = &assetRec{
		asset:   a,
		roles:   map[string]map[assetv1.Role]int64{m.Issuer: {assetv1.Role_ROLE_ISSUER: c.height}},
		holders: map[string]*holder{},
	}
	c.emit("qorechain.asset.v1.EventAssetCreated", &assetv1.EventAssetCreated{
		AssetId: m.AssetId, Issuer: m.Issuer, Flags: proto.Clone(flags).(*assetv1.RwaFlagsV0), MaxSupply: maxSupply,
	})
	return &assetv1.MsgCreateAssetResponse{Denom: "asset/" + m.AssetId}, nil
}

func (c *MockChain) updateFlags(m *assetv1.MsgUpdateFlags) (*assetv1.MsgUpdateFlagsResponse, error) {
	r, err := c.issuerRec(m.AssetId, m.Issuer)
	if err != nil {
		return nil, err
	}
	cur := flagsOf(r)
	next := &assetv1.RwaFlagsV0{}
	if m.Flags != nil {
		next = proto.Clone(m.Flags).(*assetv1.RwaFlagsV0)
	}
	immutable := []struct {
		name      string
		cur, next bool
	}{
		{"nonTransferable", cur.NonTransferable, next.NonTransferable},
		{"supplyCap", cur.SupplyCap, next.SupplyCap},
		{"requireHybridSignature", cur.RequireHybridSignature, next.RequireHybridSignature},
	}
	for _, f := range immutable {
		if f.cur != f.next {
			return nil, fail(ModuleAsset, "ERROR_CODE_FLAG_IMMUTABLE", "%s cannot change after creation", f.name)
		}
	}
	relaxable := []struct {
		name      string
		cur, next bool
	}{
		{"requireAuth", cur.RequireAuth, next.RequireAuth},
		{"freezable", cur.Freezable, next.Freezable},
		{"pausable", cur.Pausable, next.Pausable},
	}
	for _, f := range relaxable {
		if !f.cur && f.next {
			return nil, fail(ModuleAsset, "ERROR_CODE_FLAG_IMMUTABLE", "%s can only be switched off", f.name)
		}
	}
	r.asset.Flags = next
	c.emit("qorechain.asset.v1.EventFlagsUpdated", &assetv1.EventFlagsUpdated{AssetId: m.AssetId, Flags: proto.Clone(next).(*assetv1.RwaFlagsV0)})
	return &assetv1.MsgUpdateFlagsResponse{}, nil
}

func (c *MockChain) setRole(m *assetv1.MsgSetRole) (*assetv1.MsgSetRoleResponse, error) {
	r, err := c.issuerRec(m.AssetId, m.Issuer)
	if err != nil {
		return nil, err
	}
	if m.Role != assetv1.Role_ROLE_AGENT && m.Role != assetv1.Role_ROLE_AUDITOR {
		return nil, fail(ModuleAsset, "ERROR_CODE_UNAUTHORIZED_ROLE", "only ROLE_AGENT and ROLE_AUDITOR can be granted")
	}
	if m.Granted {
		if m.Role == assetv1.Role_ROLE_AGENT && !hasRole(r, m.Address, assetv1.Role_ROLE_AGENT) {
			agents := 0
			for _, set := range r.roles {
				if _, ok := set[assetv1.Role_ROLE_AGENT]; ok {
					agents++
				}
			}
			if uint32(agents) >= c.assetParams.MaxAgents {
				return nil, fail(ModuleAsset, "ERROR_CODE_TOO_MANY_AGENTS", "too many agents")
			}
		}
		set := r.roles[m.Address]
		if set == nil {
			set = map[assetv1.Role]int64{}
			r.roles[m.Address] = set
		}
		if _, ok := set[m.Role]; !ok {
			set[m.Role] = c.height
		}
	} else if set := r.roles[m.Address]; set != nil {
		delete(set, m.Role)
	}
	c.emit("qorechain.asset.v1.EventRoleChanged", &assetv1.EventRoleChanged{
		AssetId: m.AssetId, Address: m.Address, Role: m.Role, Granted: m.Granted,
	})
	return &assetv1.MsgSetRoleResponse{}, nil
}

func (c *MockChain) proposeIssuer(m *assetv1.MsgProposeIssuer) (*assetv1.MsgProposeIssuerResponse, error) {
	r, err := c.issuerRec(m.AssetId, m.Issuer)
	if err != nil {
		return nil, err
	}
	r.asset.PendingIssuer = m.NewIssuer
	c.emit("qorechain.asset.v1.EventIssuerTransferProposed", &assetv1.EventIssuerTransferProposed{
		AssetId: m.AssetId, Issuer: m.Issuer, NewIssuer: m.NewIssuer,
	})
	return &assetv1.MsgProposeIssuerResponse{}, nil
}

func (c *MockChain) acceptIssuer(m *assetv1.MsgAcceptIssuer) (*assetv1.MsgAcceptIssuerResponse, error) {
	r, err := c.rec(m.AssetId)
	if err != nil {
		return nil, err
	}
	if r.asset.PendingIssuer == "" || r.asset.PendingIssuer != m.NewIssuer {
		return nil, fail(ModuleAsset, "ERROR_CODE_UNAUTHORIZED_ROLE", "%s is not the pending issuer", m.NewIssuer)
	}
	if err := c.requireSignerKey(r, m.NewIssuer); err != nil {
		return nil, err
	}
	previous := r.asset.Issuer
	if set := r.roles[previous]; set != nil {
		delete(set, assetv1.Role_ROLE_ISSUER)
	}
	set := r.roles[m.NewIssuer]
	if set == nil {
		set = map[assetv1.Role]int64{}
		r.roles[m.NewIssuer] = set
	}
	set[assetv1.Role_ROLE_ISSUER] = c.height
	r.asset.Issuer = m.NewIssuer
	r.asset.PendingIssuer = ""
	c.emit("qorechain.asset.v1.EventIssuerTransferred", &assetv1.EventIssuerTransferred{
		AssetId: m.AssetId, PreviousIssuer: previous, NewIssuer: m.NewIssuer,
	})
	return &assetv1.MsgAcceptIssuerResponse{}, nil
}

func (c *MockChain) authorizeHolder(m *assetv1.MsgAuthorizeHolder) (*assetv1.MsgAuthorizeHolderResponse, error) {
	r, err := c.agentRec(m.AssetId, m.Agent)
	if err != nil {
		return nil, err
	}
	if !flagsOf(r).RequireAuth {
		return nil, fail(ModuleAsset, "ERROR_CODE_FLAG_NOT_ENABLED", "require_auth is not set")
	}
	c.holderOf(r, m.Holder).authorized = m.Authorized
	c.emit("qorechain.asset.v1.EventHolderAuthorized", &assetv1.EventHolderAuthorized{
		AssetId: m.AssetId, Holder: m.Holder, Authorized: m.Authorized, Agent: m.Agent,
	})
	return &assetv1.MsgAuthorizeHolderResponse{}, nil
}

// receiverRefusal holds the checks on a receiving address shared by mint,
// transfer and forced transfer.
func (c *MockChain) receiverRefusal(r *assetRec, to string) *refusal {
	f := flagsOf(r)
	h := c.peekHolder(r, to)
	if h.frozen {
		return &refusal{code: "ERROR_CODE_ADDRESS_FROZEN", reason: to + " is frozen"}
	}
	if f.RequireAuth && !h.authorized {
		return &refusal{code: "ERROR_CODE_HOLDER_NOT_AUTHORIZED", reason: to + " is not authorized"}
	}
	if f.RequireHybridSignature && !c.HasHybridKey(to) {
		return &refusal{code: "ERROR_CODE_HYBRID_SIGNATURE_REQUIRED", reason: to + " has no registered ML-DSA-87 key with proof of possession"}
	}
	return nil
}

func (c *MockChain) complianceRefusal(assetID, from, to string, amount *big.Int) *refusal {
	if res := c.runCompliance(assetID, from, to, amount); res != nil {
		return &refusal{code: "ERROR_CODE_COMPLIANCE_REJECTED", moduleID: res.moduleID, reason: res.reason}
	}
	return nil
}

// transferRefusal runs the ordered checks of docs/proposal.md section 4.1,
// without the amount parse.
func (c *MockChain) transferRefusal(r *assetRec, from, to string, amount *big.Int) *refusal {
	f := flagsOf(r)
	switch r.asset.Status {
	case assetv1.AssetStatus_ASSET_STATUS_RETIRED:
		return &refusal{code: "ERROR_CODE_ASSET_RETIRED", reason: "asset is retired"}
	case assetv1.AssetStatus_ASSET_STATUS_PAUSED:
		return &refusal{code: "ERROR_CODE_ASSET_PAUSED", reason: "asset is paused"}
	}
	if f.NonTransferable {
		return &refusal{code: "ERROR_CODE_NON_TRANSFERABLE", reason: "asset is non-transferable"}
	}
	hf := c.peekHolder(r, from)
	ht := c.peekHolder(r, to)
	if hf.frozen || ht.frozen {
		who := to
		if hf.frozen {
			who = from
		}
		return &refusal{code: "ERROR_CODE_ADDRESS_FROZEN", reason: who + " is frozen"}
	}
	if f.RequireAuth && (!hf.authorized || !ht.authorized) {
		who := to
		if !hf.authorized {
			who = from
		}
		return &refusal{code: "ERROR_CODE_HOLDER_NOT_AUTHORIZED", reason: who + " is not authorized"}
	}
	if f.RequireHybridSignature && (!c.HasHybridKey(from) || !c.HasHybridKey(to)) {
		who := to
		if !c.HasHybridKey(from) {
			who = from
		}
		return &refusal{code: "ERROR_CODE_HYBRID_SIGNATURE_REQUIRED", reason: who + " has no registered ML-DSA-87 key with proof of possession"}
	}
	if hf.balance.Cmp(amount) < 0 {
		return &refusal{code: "ERROR_CODE_INSUFFICIENT_BALANCE", reason: from + " balance is too low"}
	}
	if new(big.Int).Sub(hf.balance, hf.frozenAmount).Cmp(amount) < 0 {
		return &refusal{code: "ERROR_CODE_INSUFFICIENT_UNFROZEN_BALANCE", reason: from + " unfrozen balance is too low"}
	}
	return c.complianceRefusal(r.asset.AssetId, from, to, amount)
}

func (c *MockChain) move(r *assetRec, from, to string, amount *big.Int) {
	hf := c.holderOf(r, from)
	hf.balance.Sub(hf.balance, amount)
	if hf.frozenAmount.Cmp(hf.balance) > 0 {
		hf.frozenAmount.Set(hf.balance)
	}
	ht := c.holderOf(r, to)
	ht.balance.Add(ht.balance, amount)
}

func (c *MockChain) mint(m *assetv1.MsgMint) (*assetv1.MsgMintResponse, error) {
	r, err := c.agentRec(m.AssetId, m.Agent)
	if err != nil {
		return nil, err
	}
	amount, err := parseAmount(ModuleAsset, m.Amount, false)
	if err != nil {
		return nil, err
	}
	if r.asset.Status == assetv1.AssetStatus_ASSET_STATUS_RETIRED {
		return nil, fail(ModuleAsset, "ERROR_CODE_ASSET_RETIRED", "asset is retired")
	}
	if ref := c.receiverRefusal(r, m.To); ref != nil {
		return nil, ref.err()
	}
	total, _ := new(big.Int).SetString(r.asset.TotalSupply, 10)
	total.Add(total, amount)
	if flagsOf(r).SupplyCap {
		maxSupply, _ := new(big.Int).SetString(r.asset.MaxSupply, 10)
		if total.Cmp(maxSupply) > 0 {
			return nil, fail(ModuleAsset, "ERROR_CODE_SUPPLY_CAP_EXCEEDED", "supply would exceed %s", r.asset.MaxSupply)
		}
	}
	if ref := c.complianceRefusal(m.AssetId, "", m.To, amount); ref != nil {
		return nil, ref.err()
	}
	h := c.holderOf(r, m.To)
	h.balance.Add(h.balance, amount)
	r.asset.TotalSupply = total.String()
	c.emit("qorechain.asset.v1.EventMinted", &assetv1.EventMinted{
		AssetId: m.AssetId, To: m.To, Amount: amount.String(), Agent: m.Agent,
	})
	return &assetv1.MsgMintResponse{}, nil
}

func (c *MockChain) burn(m *assetv1.MsgBurn) (*assetv1.MsgBurnResponse, error) {
	r, err := c.agentRec(m.AssetId, m.Agent)
	if err != nil {
		return nil, err
	}
	amount, err := parseAmount(ModuleAsset, m.Amount, false)
	if err != nil {
		return nil, err
	}
	h := c.peekHolder(r, m.From)
	if h.frozen {
		return nil, fail(ModuleAsset, "ERROR_CODE_ADDRESS_FROZEN", "%s is frozen", m.From)
	}
	if h.balance.Cmp(amount) < 0 {
		return nil, fail(ModuleAsset, "ERROR_CODE_INSUFFICIENT_BALANCE", "%s balance is too low", m.From)
	}
	if new(big.Int).Sub(h.balance, h.frozenAmount).Cmp(amount) < 0 {
		return nil, fail(ModuleAsset, "ERROR_CODE_INSUFFICIENT_UNFROZEN_BALANCE", "%s unfrozen balance is too low", m.From)
	}
	hh := c.holderOf(r, m.From)
	hh.balance.Sub(hh.balance, amount)
	total, _ := new(big.Int).SetString(r.asset.TotalSupply, 10)
	r.asset.TotalSupply = total.Sub(total, amount).String()
	c.emit("qorechain.asset.v1.EventBurned", &assetv1.EventBurned{
		AssetId: m.AssetId, From: m.From, Amount: amount.String(), Agent: m.Agent,
	})
	return &assetv1.MsgBurnResponse{}, nil
}

func (c *MockChain) transfer(m *assetv1.MsgTransfer) (*assetv1.MsgTransferResponse, error) {
	amount, err := parseAmount(ModuleAsset, m.Amount, false)
	if err != nil {
		return nil, err
	}
	r, err := c.rec(m.AssetId)
	if err != nil {
		return nil, err
	}
	if ref := c.transferRefusal(r, m.From, m.To, amount); ref != nil {
		return nil, ref.err()
	}
	c.move(r, m.From, m.To, amount)
	c.emit("qorechain.asset.v1.EventTransferred", &assetv1.EventTransferred{
		AssetId: m.AssetId, From: m.From, To: m.To, Amount: amount.String(),
	})
	return &assetv1.MsgTransferResponse{}, nil
}

func requireFreezable(r *assetRec) error {
	if !flagsOf(r).Freezable {
		return fail(ModuleAsset, "ERROR_CODE_FLAG_NOT_ENABLED", "freezable is not set")
	}
	return nil
}

func (c *MockChain) freeze(m *assetv1.MsgFreeze) (*assetv1.MsgFreezeResponse, error) {
	r, err := c.agentRec(m.AssetId, m.Agent)
	if err != nil {
		return nil, err
	}
	if err := requireFreezable(r); err != nil {
		return nil, err
	}
	c.holderOf(r, m.Holder).frozen = m.Frozen
	c.emit("qorechain.asset.v1.EventFrozen", &assetv1.EventFrozen{
		AssetId: m.AssetId, Holder: m.Holder, Frozen: m.Frozen, Agent: m.Agent,
	})
	return &assetv1.MsgFreezeResponse{}, nil
}

func (c *MockChain) freezePartial(m *assetv1.MsgFreezePartial) (*assetv1.MsgFreezePartialResponse, error) {
	r, err := c.agentRec(m.AssetId, m.Agent)
	if err != nil {
		return nil, err
	}
	if err := requireFreezable(r); err != nil {
		return nil, err
	}
	amount, err := parseAmount(ModuleAsset, m.FrozenAmount, true)
	if err != nil {
		return nil, err
	}
	if amount.Cmp(c.peekHolder(r, m.Holder).balance) > 0 {
		return nil, fail(ModuleAsset, "ERROR_CODE_INSUFFICIENT_BALANCE", "frozen amount exceeds the balance")
	}
	c.holderOf(r, m.Holder).frozenAmount = amount
	c.emit("qorechain.asset.v1.EventPartiallyFrozen", &assetv1.EventPartiallyFrozen{
		AssetId: m.AssetId, Holder: m.Holder, FrozenAmount: amount.String(), Agent: m.Agent,
	})
	return &assetv1.MsgFreezePartialResponse{}, nil
}

func (c *MockChain) pause(m *assetv1.MsgPause) (*assetv1.MsgPauseResponse, error) {
	r, err := c.agentRec(m.AssetId, m.Agent)
	if err != nil {
		return nil, err
	}
	if r.asset.Status == assetv1.AssetStatus_ASSET_STATUS_RETIRED {
		return nil, fail(ModuleAsset, "ERROR_CODE_ASSET_RETIRED", "asset is retired")
	}
	if m.Paused && !flagsOf(r).Pausable {
		return nil, fail(ModuleAsset, "ERROR_CODE_FLAG_NOT_ENABLED", "pausable is not set")
	}
	if m.Paused {
		r.asset.Status = assetv1.AssetStatus_ASSET_STATUS_PAUSED
	} else {
		r.asset.Status = assetv1.AssetStatus_ASSET_STATUS_ACTIVE
	}
	c.emit("qorechain.asset.v1.EventPaused", &assetv1.EventPaused{AssetId: m.AssetId, Paused: m.Paused, Agent: m.Agent})
	return &assetv1.MsgPauseResponse{}, nil
}

func (c *MockChain) clawback(m *assetv1.MsgClawback) (*assetv1.MsgClawbackResponse, error) {
	r, err := c.agentRec(m.AssetId, m.Agent)
	if err != nil {
		return nil, err
	}
	if err := requireFreezable(r); err != nil {
		return nil, err
	}
	amount, err := parseAmount(ModuleAsset, m.Amount, false)
	if err != nil {
		return nil, err
	}
	if c.peekHolder(r, m.From).balance.Cmp(amount) < 0 {
		return nil, fail(ModuleAsset, "ERROR_CODE_INSUFFICIENT_BALANCE", "%s balance is too low", m.From)
	}
	c.move(r, m.From, r.asset.Issuer, amount)
	c.emit("qorechain.asset.v1.EventClawback", &assetv1.EventClawback{
		AssetId: m.AssetId, From: m.From, Amount: amount.String(), Agent: m.Agent, Reason: m.Reason,
	})
	return &assetv1.MsgClawbackResponse{}, nil
}

func (c *MockChain) forceTransfer(m *assetv1.MsgForceTransfer) (*assetv1.MsgForceTransferResponse, error) {
	r, err := c.agentRec(m.AssetId, m.Agent)
	if err != nil {
		return nil, err
	}
	if err := requireFreezable(r); err != nil {
		return nil, err
	}
	amount, err := parseAmount(ModuleAsset, m.Amount, false)
	if err != nil {
		return nil, err
	}
	if r.asset.Status == assetv1.AssetStatus_ASSET_STATUS_RETIRED {
		return nil, fail(ModuleAsset, "ERROR_CODE_ASSET_RETIRED", "asset is retired")
	}
	if c.peekHolder(r, m.From).balance.Cmp(amount) < 0 {
		return nil, fail(ModuleAsset, "ERROR_CODE_INSUFFICIENT_BALANCE", "%s balance is too low", m.From)
	}
	ref := c.receiverRefusal(r, m.To)
	if ref == nil {
		ref = c.complianceRefusal(m.AssetId, m.From, m.To, amount)
	}
	if ref != nil {
		return nil, ref.err()
	}
	c.move(r, m.From, m.To, amount)
	c.emit("qorechain.asset.v1.EventForcedTransfer", &assetv1.EventForcedTransfer{
		AssetId: m.AssetId, From: m.From, To: m.To, Amount: amount.String(), Agent: m.Agent, Reason: m.Reason,
	})
	return &assetv1.MsgForceTransferResponse{}, nil
}

func (c *MockChain) setTerms(m *assetv1.MsgSetTerms) (*assetv1.MsgSetTermsResponse, error) {
	r, err := c.issuerRec(m.AssetId, m.Issuer)
	if err != nil {
		return nil, err
	}
	r.asset.TermsHash = append([]byte(nil), m.TermsHash...)
	r.asset.TermsUri = m.TermsUri
	c.emit("qorechain.asset.v1.EventTermsUpdated", &assetv1.EventTermsUpdated{
		AssetId: m.AssetId, TermsHash: append([]byte(nil), m.TermsHash...), TermsUri: m.TermsUri,
	})
	return &assetv1.MsgSetTermsResponse{}, nil
}

func (c *MockChain) retire(m *assetv1.MsgRetire) (*assetv1.MsgRetireResponse, error) {
	r, err := c.issuerRec(m.AssetId, m.Issuer)
	if err != nil {
		return nil, err
	}
	r.asset.Status = assetv1.AssetStatus_ASSET_STATUS_RETIRED
	c.emit("qorechain.asset.v1.EventRetired", &assetv1.EventRetired{AssetId: m.AssetId})
	return &assetv1.MsgRetireResponse{}, nil
}

func (c *MockChain) assetView(r *assetRec) *assetv1.Asset {
	a := proto.Clone(r.asset).(*assetv1.Asset)
	a.ComplianceModuleIds = nil
	for _, b := range c.bindingsOf(r.asset.AssetId) {
		a.ComplianceModuleIds = append(a.ComplianceModuleIds, b.ModuleId)
	}
	return a
}

func holderState(assetID, address string, h *holder) *assetv1.HolderState {
	return &assetv1.HolderState{
		AssetId:      assetID,
		Address:      address,
		Balance:      h.balance.String(),
		Authorized:   h.authorized,
		Frozen:       h.frozen,
		FrozenAmount: h.frozenAmount.String(),
	}
}

func (c *MockChain) queryCanTransfer(q *assetv1.QueryCanTransferRequest) *assetv1.QueryCanTransferResponse {
	no := func(code, reason, moduleID string) *assetv1.QueryCanTransferResponse {
		return &assetv1.QueryCanTransferResponse{
			Allowed: false, Code: assetv1.ErrorCode(assetv1.ErrorCode_value[code]), ComplianceModuleId: moduleID, Reason: reason,
		}
	}
	amount, ok := positiveInteger(q.Amount)
	if !ok {
		return no("ERROR_CODE_INVALID_AMOUNT", "amount must be a positive integer", "")
	}
	r, found := c.assets[q.AssetId]
	if !found {
		return no("ERROR_CODE_ASSET_NOT_FOUND", "asset "+q.AssetId+" not found", "")
	}
	if ref := c.transferRefusal(r, q.From, q.To, amount); ref != nil {
		return no(ref.code, ref.reason, ref.moduleID)
	}
	return &assetv1.QueryCanTransferResponse{Allowed: true}
}

// mockAsset adapts MockChain to AssetAPI.
type mockAsset struct{ c *MockChain }

func (a mockAsset) CreateAsset(_ context.Context, m *assetv1.MsgCreateAsset) (*assetv1.MsgCreateAssetResponse, error) {
	return a.c.createAsset(orEmpty(m))
}

func (a mockAsset) UpdateFlags(_ context.Context, m *assetv1.MsgUpdateFlags) (*assetv1.MsgUpdateFlagsResponse, error) {
	return a.c.updateFlags(orEmpty(m))
}

func (a mockAsset) SetRole(_ context.Context, m *assetv1.MsgSetRole) (*assetv1.MsgSetRoleResponse, error) {
	return a.c.setRole(orEmpty(m))
}

func (a mockAsset) ProposeIssuer(_ context.Context, m *assetv1.MsgProposeIssuer) (*assetv1.MsgProposeIssuerResponse, error) {
	return a.c.proposeIssuer(orEmpty(m))
}

func (a mockAsset) AcceptIssuer(_ context.Context, m *assetv1.MsgAcceptIssuer) (*assetv1.MsgAcceptIssuerResponse, error) {
	return a.c.acceptIssuer(orEmpty(m))
}

func (a mockAsset) AuthorizeHolder(_ context.Context, m *assetv1.MsgAuthorizeHolder) (*assetv1.MsgAuthorizeHolderResponse, error) {
	return a.c.authorizeHolder(orEmpty(m))
}

func (a mockAsset) Mint(_ context.Context, m *assetv1.MsgMint) (*assetv1.MsgMintResponse, error) {
	return a.c.mint(orEmpty(m))
}

func (a mockAsset) Burn(_ context.Context, m *assetv1.MsgBurn) (*assetv1.MsgBurnResponse, error) {
	return a.c.burn(orEmpty(m))
}

func (a mockAsset) Transfer(_ context.Context, m *assetv1.MsgTransfer) (*assetv1.MsgTransferResponse, error) {
	return a.c.transfer(orEmpty(m))
}

func (a mockAsset) Freeze(_ context.Context, m *assetv1.MsgFreeze) (*assetv1.MsgFreezeResponse, error) {
	return a.c.freeze(orEmpty(m))
}

func (a mockAsset) FreezePartial(_ context.Context, m *assetv1.MsgFreezePartial) (*assetv1.MsgFreezePartialResponse, error) {
	return a.c.freezePartial(orEmpty(m))
}

func (a mockAsset) Pause(_ context.Context, m *assetv1.MsgPause) (*assetv1.MsgPauseResponse, error) {
	return a.c.pause(orEmpty(m))
}

func (a mockAsset) Clawback(_ context.Context, m *assetv1.MsgClawback) (*assetv1.MsgClawbackResponse, error) {
	return a.c.clawback(orEmpty(m))
}

func (a mockAsset) ForceTransfer(_ context.Context, m *assetv1.MsgForceTransfer) (*assetv1.MsgForceTransferResponse, error) {
	return a.c.forceTransfer(orEmpty(m))
}

func (a mockAsset) SetTerms(_ context.Context, m *assetv1.MsgSetTerms) (*assetv1.MsgSetTermsResponse, error) {
	return a.c.setTerms(orEmpty(m))
}

func (a mockAsset) Retire(_ context.Context, m *assetv1.MsgRetire) (*assetv1.MsgRetireResponse, error) {
	return a.c.retire(orEmpty(m))
}

func (a mockAsset) Params(context.Context, *assetv1.QueryParamsRequest) (*assetv1.QueryParamsResponse, error) {
	return &assetv1.QueryParamsResponse{Params: proto.Clone(a.c.assetParams).(*assetv1.Params)}, nil
}

func (a mockAsset) Asset(_ context.Context, q *assetv1.QueryAssetRequest) (*assetv1.QueryAssetResponse, error) {
	r, err := a.c.rec(orEmpty(q).AssetId)
	if err != nil {
		return nil, err
	}
	return &assetv1.QueryAssetResponse{Asset: a.c.assetView(r)}, nil
}

func (a mockAsset) Assets(_ context.Context, q *assetv1.QueryAssetsRequest) (*assetv1.QueryAssetsResponse, error) {
	q = orEmpty(q)
	out := &assetv1.QueryAssetsResponse{}
	for _, id := range sortedKeys(a.c.assets) {
		r := a.c.assets[id]
		if q.Issuer == "" || r.asset.Issuer == q.Issuer {
			out.Assets = append(out.Assets, a.c.assetView(r))
		}
	}
	return out, nil
}

func (a mockAsset) Holder(_ context.Context, q *assetv1.QueryHolderRequest) (*assetv1.QueryHolderResponse, error) {
	q = orEmpty(q)
	r, err := a.c.rec(q.AssetId)
	if err != nil {
		return nil, err
	}
	return &assetv1.QueryHolderResponse{Holder: holderState(q.AssetId, q.Address, a.c.peekHolder(r, q.Address))}, nil
}

func (a mockAsset) Holders(_ context.Context, q *assetv1.QueryHoldersRequest) (*assetv1.QueryHoldersResponse, error) {
	q = orEmpty(q)
	r, err := a.c.rec(q.AssetId)
	if err != nil {
		return nil, err
	}
	out := &assetv1.QueryHoldersResponse{}
	for _, addr := range sortedKeys(r.holders) {
		out.Holders = append(out.Holders, holderState(q.AssetId, addr, r.holders[addr]))
	}
	return out, nil
}

func (a mockAsset) Roles(_ context.Context, q *assetv1.QueryRolesRequest) (*assetv1.QueryRolesResponse, error) {
	q = orEmpty(q)
	r, err := a.c.rec(q.AssetId)
	if err != nil {
		return nil, err
	}
	out := &assetv1.QueryRolesResponse{}
	for address, set := range r.roles {
		for role, height := range set {
			out.Roles = append(out.Roles, &assetv1.RoleGrant{AssetId: q.AssetId, Address: address, Role: role, GrantedHeight: height})
		}
	}
	sort.Slice(out.Roles, func(i, j int) bool {
		if out.Roles[i].Role != out.Roles[j].Role {
			return out.Roles[i].Role < out.Roles[j].Role
		}
		return out.Roles[i].Address < out.Roles[j].Address
	})
	return out, nil
}

func (a mockAsset) CanTransfer(_ context.Context, q *assetv1.QueryCanTransferRequest) (*assetv1.QueryCanTransferResponse, error) {
	return a.c.queryCanTransfer(orEmpty(q)), nil
}

// orEmpty replaces a nil message by a new empty one, as the proto defaults would.
func orEmpty[T any, P interface{ *T }](m P) P {
	if m == nil {
		return P(new(T))
	}
	return m
}

// SPDX-License-Identifier: Apache-2.0

package assetkit_test

import (
	"context"
	"errors"
	"math/big"
	"strings"
	"testing"

	assetkit "github.com/qorechain/qorechain-asset-kit/clients/go"
	assetv1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/asset/v1"
	attestv1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/attest/v1"
	compliancev1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/compliance/v1"
	identityv1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/identity/v1"
	settlementv1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/settlement/v1"
)

const (
	issuer = "qor1issuer"
	agent  = "qor1agent"
	alice  = "qor1alice"
	bob    = "qor1bob"
	carol  = "qor1carol"
	kyc    = "qor1kycprovider"
	bondID = "bond-2030"
)

var bg = context.Background()

func must[T any](t *testing.T) func(T, error) T {
	return func(v T, err error) T {
		t.Helper()
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		return v
	}
}

func ok(t *testing.T, err error) {
	t.Helper()
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
}

func rejects(t *testing.T, err error, code string) *assetkit.MockChainError {
	t.Helper()
	var e *assetkit.MockChainError
	if !errors.As(err, &e) {
		t.Fatalf("want MockChainError %s, got %v", code, err)
	}
	if e.Code != code {
		t.Fatalf("want %s, got %s (%s)", code, e.Code, e.Message)
	}
	return e
}

func errOf[T any](_ T, err error) error { return err }

func bond(t *testing.T, c *assetkit.MockChain, flags *assetv1.RwaFlagsV0, maxSupply string) {
	t.Helper()
	if flags == nil {
		flags = &assetv1.RwaFlagsV0{}
	}
	flags.Freezable, flags.Pausable = true, true
	ok(t, errOf(c.Asset().CreateAsset(bg, &assetv1.MsgCreateAsset{
		Issuer: issuer, AssetId: bondID, Name: "Example 2030 Bond", Symbol: "EB30", Flags: flags, MaxSupply: maxSupply,
	})))
	ok(t, errOf(c.Asset().SetRole(bg, &assetv1.MsgSetRole{Issuer: issuer, AssetId: bondID, Address: agent, Role: assetv1.Role_ROLE_AGENT, Granted: true})))
}

func balance(t *testing.T, c *assetkit.MockChain, address string) string {
	t.Helper()
	return must[*assetv1.QueryHolderResponse](t)(c.Asset().Holder(bg, &assetv1.QueryHolderRequest{AssetId: bondID, Address: address})).Holder.Balance
}

func mint(c *assetkit.MockChain, to, amount string) error {
	return errOf(c.Asset().Mint(bg, &assetv1.MsgMint{Agent: agent, AssetId: bondID, To: to, Amount: amount}))
}

func transfer(c *assetkit.MockChain, from, to, amount string) error {
	return errOf(c.Asset().Transfer(bg, &assetv1.MsgTransfer{From: from, AssetId: bondID, To: to, Amount: amount}))
}

func freeze(c *assetkit.MockChain, holder string, frozen bool) error {
	return errOf(c.Asset().Freeze(bg, &assetv1.MsgFreeze{Agent: agent, AssetId: bondID, Holder: holder, Frozen: frozen}))
}

// ----------------------------------------------------------------- issuance

func TestIssuance(t *testing.T) {
	c := assetkit.NewMockChain()
	bond(t, c, &assetv1.RwaFlagsV0{SupplyCap: true}, "1000")

	ok(t, mint(c, alice, "600"))
	ok(t, transfer(c, alice, bob, "100"))
	if balance(t, c, alice) != "500" || balance(t, c, bob) != "100" {
		t.Fatal("wrong balances")
	}
	a := must[*assetv1.QueryAssetResponse](t)(c.Asset().Asset(bg, &assetv1.QueryAssetRequest{AssetId: bondID})).Asset
	if a.TotalSupply != "600" || a.Status != assetv1.AssetStatus_ASSET_STATUS_ACTIVE {
		t.Fatalf("unexpected asset %v", a)
	}
	if n := len(c.Events("qorechain.asset.v1.EventMinted")); n != 1 {
		t.Fatalf("want 1 EventMinted, got %d", n)
	}

	ok(t, mint(c, alice, "400"))
	rejects(t, mint(c, alice, "1"), "ERROR_CODE_SUPPLY_CAP_EXCEEDED")
	rejects(t, errOf(c.Asset().Mint(bg, &assetv1.MsgMint{Agent: bob, AssetId: bondID, To: bob, Amount: "1"})), "ERROR_CODE_UNAUTHORIZED_ROLE")
	rejects(t, mint(c, alice, "-5"), "ERROR_CODE_INVALID_AMOUNT")
	rejects(t, errOf(c.Asset().CreateAsset(bg, &assetv1.MsgCreateAsset{Issuer: issuer, AssetId: bondID})), "ERROR_CODE_ASSET_EXISTS")
}

func TestFlagsOnlyRelax(t *testing.T) {
	c := assetkit.NewMockChain()
	bond(t, c, &assetv1.RwaFlagsV0{SupplyCap: true}, "1000")
	rejects(t, errOf(c.Asset().UpdateFlags(bg, &assetv1.MsgUpdateFlags{Issuer: issuer, AssetId: bondID,
		Flags: &assetv1.RwaFlagsV0{Freezable: true, Pausable: true}})), "ERROR_CODE_FLAG_IMMUTABLE")
	ok(t, errOf(c.Asset().UpdateFlags(bg, &assetv1.MsgUpdateFlags{Issuer: issuer, AssetId: bondID,
		Flags: &assetv1.RwaFlagsV0{Freezable: true, SupplyCap: true}})))
	rejects(t, errOf(c.Asset().Pause(bg, &assetv1.MsgPause{Agent: agent, AssetId: bondID, Paused: true})), "ERROR_CODE_FLAG_NOT_ENABLED")
}

func TestRequireAuth(t *testing.T) {
	c := assetkit.NewMockChain()
	ok(t, errOf(c.Asset().CreateAsset(bg, &assetv1.MsgCreateAsset{Issuer: issuer, AssetId: "fund-a", Flags: &assetv1.RwaFlagsV0{RequireAuth: true}})))
	rejects(t, errOf(c.Asset().Mint(bg, &assetv1.MsgMint{Agent: issuer, AssetId: "fund-a", To: alice, Amount: "5"})), "ERROR_CODE_HOLDER_NOT_AUTHORIZED")
	ok(t, errOf(c.Asset().AuthorizeHolder(bg, &assetv1.MsgAuthorizeHolder{Agent: issuer, AssetId: "fund-a", Holder: alice, Authorized: true})))
	ok(t, errOf(c.Asset().Mint(bg, &assetv1.MsgMint{Agent: issuer, AssetId: "fund-a", To: alice, Amount: "5"})))
	rejects(t, errOf(c.Asset().Transfer(bg, &assetv1.MsgTransfer{From: alice, AssetId: "fund-a", To: bob, Amount: "1"})), "ERROR_CODE_HOLDER_NOT_AUTHORIZED")
}

func TestRequireHybridSignature(t *testing.T) {
	c := assetkit.NewMockChain()
	create := &assetv1.MsgCreateAsset{Issuer: issuer, AssetId: "pq-note", Flags: &assetv1.RwaFlagsV0{RequireHybridSignature: true}}
	rejects(t, errOf(c.Asset().CreateAsset(bg, create)), "ERROR_CODE_HYBRID_SIGNATURE_REQUIRED")
	c.SetHybridKey(issuer, true, true)
	ok(t, errOf(c.Asset().CreateAsset(bg, create)))
	c.SetHybridKey(alice, true, false)
	m := &assetv1.MsgMint{Agent: issuer, AssetId: "pq-note", To: alice, Amount: "1"}
	rejects(t, errOf(c.Asset().Mint(bg, m)), "ERROR_CODE_HYBRID_SIGNATURE_REQUIRED")
	c.SetHybridKey(alice, true, true)
	ok(t, errOf(c.Asset().Mint(bg, m)))
}

func TestNonTransferable(t *testing.T) {
	c := assetkit.NewMockChain()
	ok(t, errOf(c.Asset().CreateAsset(bg, &assetv1.MsgCreateAsset{Issuer: issuer, AssetId: "membership",
		Flags: &assetv1.RwaFlagsV0{NonTransferable: true, Freezable: true}})))
	ok(t, errOf(c.Asset().Mint(bg, &assetv1.MsgMint{Agent: issuer, AssetId: "membership", To: alice, Amount: "1"})))
	rejects(t, errOf(c.Asset().Transfer(bg, &assetv1.MsgTransfer{From: alice, AssetId: "membership", To: bob, Amount: "1"})), "ERROR_CODE_NON_TRANSFERABLE")
	ok(t, errOf(c.Asset().Clawback(bg, &assetv1.MsgClawback{Agent: issuer, AssetId: "membership", From: alice, Amount: "1", Reason: "membership ended"})))
}

// --------------------------------------------- freeze, pause, clawback, force

func funded(t *testing.T) *assetkit.MockChain {
	c := assetkit.NewMockChain()
	bond(t, c, nil, "")
	ok(t, mint(c, alice, "100"))
	return c
}

func TestFreeze(t *testing.T) {
	c := funded(t)
	ok(t, freeze(c, alice, true))
	rejects(t, transfer(c, alice, bob, "1"), "ERROR_CODE_ADDRESS_FROZEN")
	rejects(t, mint(c, alice, "1"), "ERROR_CODE_ADDRESS_FROZEN")
	q := must[*assetv1.QueryCanTransferResponse](t)(c.Asset().CanTransfer(bg, &assetv1.QueryCanTransferRequest{AssetId: bondID, From: alice, To: bob, Amount: "1"}))
	if q.Allowed || q.Code != assetv1.ErrorCode_ERROR_CODE_ADDRESS_FROZEN {
		t.Fatalf("unexpected %v", q)
	}
	ok(t, freeze(c, alice, false))
	ok(t, transfer(c, alice, bob, "1"))
}

func TestPartialFreeze(t *testing.T) {
	c := funded(t)
	ok(t, errOf(c.Asset().FreezePartial(bg, &assetv1.MsgFreezePartial{Agent: agent, AssetId: bondID, Holder: alice, FrozenAmount: "70"})))
	rejects(t, transfer(c, alice, bob, "31"), "ERROR_CODE_INSUFFICIENT_UNFROZEN_BALANCE")
	ok(t, transfer(c, alice, bob, "30"))
}

func TestPause(t *testing.T) {
	c := funded(t)
	ok(t, errOf(c.Asset().Pause(bg, &assetv1.MsgPause{Agent: agent, AssetId: bondID, Paused: true})))
	rejects(t, transfer(c, alice, bob, "1"), "ERROR_CODE_ASSET_PAUSED")
	ok(t, mint(c, bob, "1"))
	ok(t, errOf(c.Asset().Pause(bg, &assetv1.MsgPause{Agent: agent, AssetId: bondID, Paused: false})))
	ok(t, transfer(c, alice, bob, "1"))
}

func TestClawback(t *testing.T) {
	c := funded(t)
	ok(t, errOf(c.Asset().FreezePartial(bg, &assetv1.MsgFreezePartial{Agent: agent, AssetId: bondID, Holder: alice, FrozenAmount: "100"})))
	ok(t, freeze(c, alice, true))
	ok(t, errOf(c.Asset().Clawback(bg, &assetv1.MsgClawback{Agent: agent, AssetId: bondID, From: alice, Amount: "40", Reason: "court order 12/2026"})))
	h := must[*assetv1.QueryHolderResponse](t)(c.Asset().Holder(bg, &assetv1.QueryHolderRequest{AssetId: bondID, Address: alice})).Holder
	if h.Balance != "60" || h.FrozenAmount != "60" || balance(t, c, issuer) != "40" {
		t.Fatalf("unexpected state %v", h)
	}
	ev := c.Events("qorechain.asset.v1.EventClawback")[0].Data.(*assetv1.EventClawback)
	if ev.Reason != "court order 12/2026" {
		t.Fatalf("reason %q", ev.Reason)
	}
}

func TestForceTransfer(t *testing.T) {
	c := funded(t)
	ok(t, freeze(c, alice, true))
	ok(t, errOf(c.Asset().ForceTransfer(bg, &assetv1.MsgForceTransfer{Agent: agent, AssetId: bondID, From: alice, To: carol, Amount: "100", Reason: "lost key"})))
	if balance(t, c, carol) != "100" {
		t.Fatal("carol should hold 100")
	}
	ok(t, freeze(c, bob, true))
	rejects(t, errOf(c.Asset().ForceTransfer(bg, &assetv1.MsgForceTransfer{Agent: agent, AssetId: bondID, From: carol, To: bob, Amount: "1", Reason: "x"})),
		"ERROR_CODE_ADDRESS_FROZEN")
}

func TestIssuerTwoStepAndRetire(t *testing.T) {
	c := funded(t)
	ok(t, errOf(c.Asset().ProposeIssuer(bg, &assetv1.MsgProposeIssuer{Issuer: issuer, AssetId: bondID, NewIssuer: carol})))
	rejects(t, errOf(c.Asset().AcceptIssuer(bg, &assetv1.MsgAcceptIssuer{NewIssuer: bob, AssetId: bondID})), "ERROR_CODE_UNAUTHORIZED_ROLE")
	ok(t, errOf(c.Asset().AcceptIssuer(bg, &assetv1.MsgAcceptIssuer{NewIssuer: carol, AssetId: bondID})))
	roles := must[*assetv1.QueryRolesResponse](t)(c.Asset().Roles(bg, &assetv1.QueryRolesRequest{AssetId: bondID})).Roles
	if roles[0].Role != assetv1.Role_ROLE_ISSUER || roles[0].Address != carol {
		t.Fatalf("unexpected roles %v", roles)
	}
	ok(t, errOf(c.Asset().Retire(bg, &assetv1.MsgRetire{Issuer: carol, AssetId: bondID})))
	rejects(t, transfer(c, alice, bob, "1"), "ERROR_CODE_ASSET_RETIRED")
	ok(t, errOf(c.Asset().Burn(bg, &assetv1.MsgBurn{Agent: agent, AssetId: bondID, From: alice, Amount: "100"})))
	if a := must[*assetv1.QueryAssetResponse](t)(c.Asset().Asset(bg, &assetv1.QueryAssetRequest{AssetId: bondID})).Asset; a.TotalSupply != "0" {
		t.Fatalf("total %s", a.TotalSupply)
	}
}

// --------------------------------------------------- identity and compliance

func kycChain(t *testing.T) *assetkit.MockChain {
	c := assetkit.NewMockChain(assetkit.MockChainOptions{IdentityAgents: []string{kyc}})
	bond(t, c, nil, "")
	ok(t, errOf(c.Identity().SetClaimIssuer(bg, &identityv1.MsgSetClaimIssuer{Authority: "authority",
		ClaimIssuer: &identityv1.ClaimIssuer{Address: kyc, Name: "KYC provider", Topics: []uint32{1}}})))
	for _, p := range []struct {
		id, addr string
		country  uint32
	}{{"id-alice", alice, 756}, {"id-bob", bob, 408}} {
		ok(t, errOf(c.Identity().RegisterIdentity(bg, &identityv1.MsgRegisterIdentity{Agent: kyc, IdentityId: p.id, Address: p.addr, Country: p.country})))
		ok(t, errOf(c.Identity().AddClaim(bg, &identityv1.MsgAddClaim{ClaimIssuer: kyc, IdentityId: p.id, Topic: 1, DataHash: make([]byte, 32)})))
	}
	bind(t, c, "identity-verified", `{"topics":[1]}`)
	bind(t, c, "country-blocklist", `{"countries":[408]}`)
	return c
}

func bind(t *testing.T, c *assetkit.MockChain, moduleID, params string) {
	t.Helper()
	ok(t, errOf(c.Compliance().BindModule(bg, &compliancev1.MsgBindModule{Issuer: issuer, AssetId: bondID, ModuleId: moduleID, Version: 1, ParamsJson: params})))
}

func TestComplianceRejectsUnverifiedMint(t *testing.T) {
	c := kycChain(t)
	e := rejects(t, mint(c, carol, "1"), "ERROR_CODE_COMPLIANCE_REJECTED")
	if !strings.Contains(e.Message, "identity-verified") {
		t.Fatalf("message %q", e.Message)
	}
}

func TestComplianceRejectsBlockedCountry(t *testing.T) {
	c := kycChain(t)
	ok(t, mint(c, alice, "10"))
	rejects(t, transfer(c, alice, bob, "1"), "ERROR_CODE_COMPLIANCE_REJECTED")
	q := must[*assetv1.QueryCanTransferResponse](t)(c.Asset().CanTransfer(bg, &assetv1.QueryCanTransferRequest{AssetId: bondID, From: alice, To: bob, Amount: "1"}))
	if q.Allowed || q.Code != assetv1.ErrorCode_ERROR_CODE_COMPLIANCE_REJECTED || q.ComplianceModuleId != "country-blocklist" {
		t.Fatalf("unexpected %v", q)
	}
	chk := must[*compliancev1.QueryCheckResponse](t)(c.Compliance().Check(bg, &compliancev1.QueryCheckRequest{AssetId: bondID, From: alice, To: bob, Amount: "1"}))
	if chk.Allowed || chk.ModuleId != "country-blocklist" || chk.Version != 1 {
		t.Fatalf("unexpected %v", chk)
	}
}

func TestDistrustedClaimIssuerUnverifies(t *testing.T) {
	c := kycChain(t)
	ok(t, mint(c, alice, "1"))
	ok(t, errOf(c.Identity().SetClaimIssuer(bg, &identityv1.MsgSetClaimIssuer{Authority: "authority",
		ClaimIssuer: &identityv1.ClaimIssuer{Address: kyc, Topics: []uint32{1}}, Remove: true})))
	v := must[*identityv1.QueryIsVerifiedResponse](t)(c.Identity().IsVerified(bg, &identityv1.QueryIsVerifiedRequest{Address: alice, Topics: []uint32{1}}))
	if v.Verified {
		t.Fatal("alice should no longer be verified")
	}
	rejects(t, mint(c, alice, "1"), "ERROR_CODE_COMPLIANCE_REJECTED")
}

func TestDisabledModuleFailsClosed(t *testing.T) {
	c := kycChain(t)
	ok(t, mint(c, alice, "10"))
	ok(t, errOf(c.Compliance().RegisterModule(bg, &compliancev1.MsgRegisterModule{Authority: "authority",
		Module: &compliancev1.ComplianceModule{ModuleId: "country-blocklist", Version: 2, Runtime: compliancev1.ModuleRuntime_MODULE_RUNTIME_NATIVE}})))
	ok(t, errOf(c.Compliance().SetModuleStatus(bg, &compliancev1.MsgSetModuleStatus{Authority: "authority",
		ModuleId: "country-blocklist", Version: 1, Status: compliancev1.ModuleStatus_MODULE_STATUS_DISABLED})))
	rejects(t, mint(c, alice, "1"), "ERROR_CODE_COMPLIANCE_REJECTED")
	ok(t, errOf(c.Compliance().MigrateBinding(bg, &compliancev1.MsgMigrateBinding{Issuer: issuer, AssetId: bondID, ModuleId: "country-blocklist", ToVersion: 2})))
	ok(t, mint(c, alice, "1"))
	rejects(t, errOf(c.Compliance().BindModule(bg, &compliancev1.MsgBindModule{Issuer: issuer, AssetId: bondID, ModuleId: "max-holders", Version: 1, ParamsJson: `{"max":0}`})),
		"ERROR_CODE_INVALID_PARAMS")
}

func TestMaxHolders(t *testing.T) {
	c := kycChain(t)
	ok(t, errOf(c.Compliance().UnbindModule(bg, &compliancev1.MsgUnbindModule{Issuer: issuer, AssetId: bondID, ModuleId: "country-blocklist"})))
	bind(t, c, "max-holders", `{"max":1}`)
	ok(t, mint(c, alice, "10"))
	rejects(t, transfer(c, alice, bob, "1"), "ERROR_CODE_COMPLIANCE_REJECTED")
	ok(t, transfer(c, alice, bob, "10"))
}

func TestCustomModuleLogic(t *testing.T) {
	c := kycChain(t)
	ok(t, errOf(c.Compliance().RegisterModule(bg, &compliancev1.MsgRegisterModule{Authority: "authority",
		Module: &compliancev1.ComplianceModule{ModuleId: "lockup", Version: 1, Runtime: compliancev1.ModuleRuntime_MODULE_RUNTIME_WASM, CodeRef: "qor1lockupcontract"}})))
	c.DefineModuleLogic("lockup", func(ctx assetkit.ModuleContext) (string, bool) {
		if ctx.From != "" && ctx.Chain.Time() < 1_767_225_600+86400 {
			return "lock-up until day 1", true
		}
		return "", false
	})
	bind(t, c, "lockup", "{}")
	ok(t, mint(c, alice, "10"))
	ok(t, errOf(c.Identity().RegisterIdentity(bg, &identityv1.MsgRegisterIdentity{Agent: kyc, IdentityId: "id-carol", Address: carol, Country: 756})))
	ok(t, errOf(c.Identity().AddClaim(bg, &identityv1.MsgAddClaim{ClaimIssuer: kyc, IdentityId: "id-carol", Topic: 1, DataHash: make([]byte, 32)})))
	rejects(t, transfer(c, alice, carol, "1"), "ERROR_CODE_COMPLIANCE_REJECTED")
	c.Advance(10, 86400)
	ok(t, transfer(c, alice, carol, "1"))
}

// --------------------------------------------------------------- settlement

func dvpChain(t *testing.T) *assetkit.MockChain {
	c := assetkit.NewMockChain()
	bond(t, c, nil, "")
	ok(t, mint(c, alice, "10"))
	c.FundBank(bob, "uqor", big.NewInt(1000))
	return c
}

func legs(cash string) []*settlementv1.Leg {
	return []*settlementv1.Leg{
		{From: alice, To: bob, Denom: "asset/" + bondID, Amount: "10"},
		{From: bob, To: alice, Denom: "uqor", Amount: cash},
	}
}

func instruction(t *testing.T, c *assetkit.MockChain, id uint64) *settlementv1.Instruction {
	t.Helper()
	return must[*settlementv1.QueryInstructionResponse](t)(c.Settlement().Instruction(bg, &settlementv1.QueryInstructionRequest{Id: id})).Instruction
}

func TestSettlementBilateral(t *testing.T) {
	c := dvpChain(t)
	id := must[*settlementv1.MsgCreateInstructionResponse](t)(c.Settlement().CreateInstruction(bg, &settlementv1.MsgCreateInstruction{
		Creator: alice, Legs: legs("1000"), Deadline: c.Time() + 3600})).Id
	if instruction(t, c, id).Status != settlementv1.InstructionStatus_INSTRUCTION_STATUS_PENDING {
		t.Fatal("should be pending")
	}
	r := must[*settlementv1.MsgAffirmResponse](t)(c.Settlement().Affirm(bg, &settlementv1.MsgAffirm{Party: bob, Id: id}))
	if !r.Executed || balance(t, c, bob) != "10" || c.BankBalance(alice, "uqor").String() != "1000" {
		t.Fatal("settlement did not execute")
	}
}

func TestSettlementAllOrNothingCashLeg(t *testing.T) {
	c := dvpChain(t)
	id := must[*settlementv1.MsgCreateInstructionResponse](t)(c.Settlement().CreateInstruction(bg, &settlementv1.MsgCreateInstruction{
		Creator: alice, Legs: legs("1001"), Deadline: c.Time() + 3600})).Id
	r := must[*settlementv1.MsgAffirmResponse](t)(c.Settlement().Affirm(bg, &settlementv1.MsgAffirm{Party: bob, Id: id}))
	if r.Executed {
		t.Fatal("should not execute")
	}
	ins := instruction(t, c, id)
	if ins.Status != settlementv1.InstructionStatus_INSTRUCTION_STATUS_FAILED || !strings.Contains(ins.FailureReason, "leg 1") {
		t.Fatalf("unexpected %v", ins)
	}
	if balance(t, c, alice) != "10" || balance(t, c, bob) != "0" || c.BankBalance(bob, "uqor").String() != "1000" {
		t.Fatal("a leg moved")
	}
	if n := len(c.Events("qorechain.asset.v1.EventTransferred")); n != 0 {
		t.Fatalf("want no transfer events, got %d", n)
	}
	c.FundBank(bob, "uqor", big.NewInt(1))
	ex := must[*settlementv1.MsgExecuteInstructionResponse](t)(c.Settlement().ExecuteInstruction(bg, &settlementv1.MsgExecuteInstruction{Signer: bob, Id: id}))
	if ex.Status != settlementv1.InstructionStatus_INSTRUCTION_STATUS_EXECUTED {
		t.Fatalf("retry status %v", ex.Status)
	}
}

func TestSettlementAllOrNothingFrozenSeller(t *testing.T) {
	c := dvpChain(t)
	ok(t, freeze(c, alice, true))
	id := must[*settlementv1.MsgCreateInstructionResponse](t)(c.Settlement().CreateInstruction(bg, &settlementv1.MsgCreateInstruction{
		Creator: bob, Legs: legs("1000"), Deadline: c.Time() + 3600, SettlementType: settlementv1.SettlementType_SETTLEMENT_TYPE_MANUAL})).Id
	rejects(t, errOf(c.Settlement().ExecuteInstruction(bg, &settlementv1.MsgExecuteInstruction{Signer: bob, Id: id})), "ERROR_CODE_NOT_FULLY_AFFIRMED")
	ok(t, errOf(c.Settlement().Affirm(bg, &settlementv1.MsgAffirm{Party: alice, Id: id})))
	ex := must[*settlementv1.MsgExecuteInstructionResponse](t)(c.Settlement().ExecuteInstruction(bg, &settlementv1.MsgExecuteInstruction{Signer: alice, Id: id}))
	if ex.Status != settlementv1.InstructionStatus_INSTRUCTION_STATUS_FAILED || c.BankBalance(bob, "uqor").String() != "1000" {
		t.Fatal("frozen seller should fail the instruction")
	}
	if !strings.Contains(instruction(t, c, id).FailureReason, "ERROR_CODE_ADDRESS_FROZEN") {
		t.Fatal("failure reason should name the freeze")
	}
}

func TestSettlementExpiry(t *testing.T) {
	c := dvpChain(t)
	id := must[*settlementv1.MsgCreateInstructionResponse](t)(c.Settlement().CreateInstruction(bg, &settlementv1.MsgCreateInstruction{
		Creator: alice, Legs: legs("1000"), Deadline: c.Time() + 60})).Id
	rejects(t, errOf(c.Settlement().Affirm(bg, &settlementv1.MsgAffirm{Party: carol, Id: id})), "ERROR_CODE_NOT_A_PARTY")
	c.Advance(100, 61)
	if instruction(t, c, id).Status != settlementv1.InstructionStatus_INSTRUCTION_STATUS_EXPIRED {
		t.Fatal("should expire")
	}
	rejects(t, errOf(c.Settlement().Affirm(bg, &settlementv1.MsgAffirm{Party: bob, Id: id})), "ERROR_CODE_INVALID_STATUS")
}

func TestSettlementOnBlock(t *testing.T) {
	c := dvpChain(t)
	id := must[*settlementv1.MsgCreateInstructionResponse](t)(c.Settlement().CreateInstruction(bg, &settlementv1.MsgCreateInstruction{
		Creator: alice, Legs: legs("1000"), Deadline: c.Time() + 3600,
		SettlementType: settlementv1.SettlementType_SETTLEMENT_TYPE_ON_BLOCK, SettleHeight: c.Height() + 5})).Id
	ok(t, errOf(c.Settlement().Affirm(bg, &settlementv1.MsgAffirm{Party: bob, Id: id})))
	if instruction(t, c, id).Status != settlementv1.InstructionStatus_INSTRUCTION_STATUS_AFFIRMED {
		t.Fatal("should wait for the block")
	}
	c.Advance(5, 5)
	if instruction(t, c, id).Status != settlementv1.InstructionStatus_INSTRUCTION_STATUS_EXECUTED {
		t.Fatal("should execute at settle height")
	}
}

// ------------------------------------------------------------- attestations

const fundAdmin = "qor1fundadmin"

func attestChain(t *testing.T) *assetkit.MockChain {
	c := assetkit.NewMockChain()
	bond(t, c, nil, "")
	ok(t, errOf(c.Attest().SetAttester(bg, &attestv1.MsgSetAttester{Issuer: issuer, Attester: &attestv1.Attester{
		AssetId: bondID, Address: fundAdmin, Kinds: []attestv1.AttestationKind{attestv1.AttestationKind_ATTESTATION_KIND_NAV}, Name: "Fund admin"}})))
	return c
}

func latest(t *testing.T, c *assetkit.MockChain) *attestv1.QueryLatestResponse {
	t.Helper()
	return must[*attestv1.QueryLatestResponse](t)(c.Attest().Latest(bg, &attestv1.QueryLatestRequest{AssetId: bondID, Kind: attestv1.AttestationKind_ATTESTATION_KIND_NAV}))
}

func TestAttestationStaleness(t *testing.T) {
	c := attestChain(t)
	if latest(t, c).Freshness != attestv1.Freshness_FRESHNESS_MISSING {
		t.Fatal("should be missing")
	}
	ok(t, errOf(c.Attest().Submit(bg, &attestv1.MsgSubmit{Attester: fundAdmin, AssetId: bondID, Kind: attestv1.AttestationKind_ATTESTATION_KIND_NAV,
		Value: "101.25", Unit: "CHF", ObservedAt: c.Time() - 60, ValidForSeconds: 86400})))
	if l := latest(t, c); l.Freshness != attestv1.Freshness_FRESHNESS_FRESH || l.Attestation.Value != "101.25" {
		t.Fatalf("unexpected %v", l)
	}
	bind(t, c, "attestation-fresh", `{"kind":"ATTESTATION_KIND_NAV"}`)
	ok(t, mint(c, alice, "5"))
	c.Advance(1000, 86400)
	if latest(t, c).Freshness != attestv1.Freshness_FRESHNESS_STALE {
		t.Fatal("should be stale")
	}
	rejects(t, transfer(c, alice, bob, "1"), "ERROR_CODE_COMPLIANCE_REJECTED")
}

func TestAttestationRefusals(t *testing.T) {
	c := attestChain(t)
	nav := attestv1.AttestationKind_ATTESTATION_KIND_NAV
	submit := func(attester string, kind attestv1.AttestationKind, observed int64) error {
		return errOf(c.Attest().Submit(bg, &attestv1.MsgSubmit{Attester: attester, AssetId: bondID, Kind: kind, Value: "1", ObservedAt: observed, ValidForSeconds: 60}))
	}
	rejects(t, submit(bob, nav, c.Time()), "ERROR_CODE_NOT_AN_ATTESTER")
	rejects(t, submit(fundAdmin, nav, c.Time()+1), "ERROR_CODE_OBSERVATION_IN_FUTURE")
	ok(t, submit(fundAdmin, nav, c.Time()))
	rejects(t, submit(fundAdmin, nav, c.Time()-10), "ERROR_CODE_OLDER_THAN_LATEST")
	rejects(t, submit(fundAdmin, attestv1.AttestationKind_ATTESTATION_KIND_RESERVES, c.Time()), "ERROR_CODE_KIND_NOT_ALLOWED")
}

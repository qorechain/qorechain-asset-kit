// SPDX-License-Identifier: Apache-2.0

import { beforeEach, describe, expect, it } from "vitest";
import { MockChain, MockChainError, asset, attest, compliance, settlement } from "../src/index.js";

const ISSUER = "qor1issuer";
const AGENT = "qor1agent";
const ALICE = "qor1alice";
const BOB = "qor1bob";
const CAROL = "qor1carol";
const KYC = "qor1kycprovider";

async function rejectsWith(p: Promise<unknown>, code: string): Promise<MockChainError> {
  const e = await p.then(() => undefined, (x: unknown) => x);
  expect(e, `expected ${code}`).toBeInstanceOf(MockChainError);
  expect((e as MockChainError).code).toBe(code);
  return e as MockChainError;
}

async function bond(chain: MockChain, flags: Partial<asset.RwaFlagsV0> = {}, maxSupply = ""): Promise<void> {
  await chain.asset.createAsset({
    issuer: ISSUER,
    assetId: "bond-2030",
    name: "Example 2030 Bond",
    symbol: "EB30",
    decimals: 0,
    flags: { freezable: true, pausable: true, ...flags },
    maxSupply,
  });
  await chain.asset.setRole({ issuer: ISSUER, assetId: "bond-2030", address: AGENT, role: asset.Role.ROLE_AGENT, granted: true });
}

async function balance(chain: MockChain, address: string): Promise<string> {
  return (await chain.asset.holder({ assetId: "bond-2030", address })).holder!.balance;
}

describe("MockChain: issuance", () => {
  let chain: MockChain;
  beforeEach(async () => {
    chain = new MockChain();
    await bond(chain, { supplyCap: true }, "1000");
  });

  it("creates, mints and transfers", async () => {
    await chain.asset.mint({ agent: AGENT, assetId: "bond-2030", to: ALICE, amount: "600" });
    await chain.asset.transfer({ from: ALICE, assetId: "bond-2030", to: BOB, amount: "100" });
    expect(await balance(chain, ALICE)).toBe("500");
    expect(await balance(chain, BOB)).toBe("100");
    const a = (await chain.asset.asset({ assetId: "bond-2030" })).asset!;
    expect(a.totalSupply).toBe("600");
    expect(a.status).toBe(asset.AssetStatus.ASSET_STATUS_ACTIVE);
    expect(chain.events("qorechain.asset.v1.EventMinted")).toHaveLength(1);
  });

  it("enforces the supply cap", async () => {
    await chain.asset.mint({ agent: AGENT, assetId: "bond-2030", to: ALICE, amount: "1000" });
    await rejectsWith(chain.asset.mint({ agent: AGENT, assetId: "bond-2030", to: ALICE, amount: "1" }), "ERROR_CODE_SUPPLY_CAP_EXCEEDED");
  });

  it("refuses minting by a non-agent", async () => {
    await rejectsWith(chain.asset.mint({ agent: BOB, assetId: "bond-2030", to: BOB, amount: "1" }), "ERROR_CODE_UNAUTHORIZED_ROLE");
  });

  it("refuses an invalid amount and a duplicate asset", async () => {
    await rejectsWith(chain.asset.mint({ agent: AGENT, assetId: "bond-2030", to: ALICE, amount: "-5" }), "ERROR_CODE_INVALID_AMOUNT");
    await rejectsWith(chain.asset.createAsset({ issuer: ISSUER, assetId: "bond-2030" }), "ERROR_CODE_ASSET_EXISTS");
  });

  it("only relaxes flags", async () => {
    await rejectsWith(
      chain.asset.updateFlags({ issuer: ISSUER, assetId: "bond-2030", flags: { freezable: true, pausable: true, supplyCap: false } }),
      "ERROR_CODE_FLAG_IMMUTABLE",
    );
    await chain.asset.updateFlags({ issuer: ISSUER, assetId: "bond-2030", flags: { freezable: true, pausable: false, supplyCap: true } });
    await rejectsWith(chain.asset.pause({ agent: AGENT, assetId: "bond-2030", paused: true }), "ERROR_CODE_FLAG_NOT_ENABLED");
  });

  it("requires authorization when require_auth is set", async () => {
    const c = new MockChain();
    await c.asset.createAsset({ issuer: ISSUER, assetId: "fund-a", flags: { requireAuth: true } });
    await rejectsWith(c.asset.mint({ agent: ISSUER, assetId: "fund-a", to: ALICE, amount: "5" }), "ERROR_CODE_HOLDER_NOT_AUTHORIZED");
    await c.asset.authorizeHolder({ agent: ISSUER, assetId: "fund-a", holder: ALICE, authorized: true });
    await c.asset.mint({ agent: ISSUER, assetId: "fund-a", to: ALICE, amount: "5" });
    await rejectsWith(c.asset.transfer({ from: ALICE, assetId: "fund-a", to: BOB, amount: "1" }), "ERROR_CODE_HOLDER_NOT_AUTHORIZED");
  });

  it("requires a hybrid key with proof of possession when require_hybrid_signature is set", async () => {
    const c = new MockChain();
    await rejectsWith(
      c.asset.createAsset({ issuer: ISSUER, assetId: "pq-note", flags: { requireHybridSignature: true } }),
      "ERROR_CODE_HYBRID_SIGNATURE_REQUIRED",
    );
    c.setHybridKey(ISSUER, { registered: true, possessionProven: true });
    await c.asset.createAsset({ issuer: ISSUER, assetId: "pq-note", flags: { requireHybridSignature: true } });
    c.setHybridKey(ALICE, { registered: true, possessionProven: false });
    await rejectsWith(c.asset.mint({ agent: ISSUER, assetId: "pq-note", to: ALICE, amount: "1" }), "ERROR_CODE_HYBRID_SIGNATURE_REQUIRED");
    c.setHybridKey(ALICE, { registered: true, possessionProven: true });
    await c.asset.mint({ agent: ISSUER, assetId: "pq-note", to: ALICE, amount: "1" });
  });

  it("blocks holder transfers of a non-transferable asset but allows clawback", async () => {
    const c = new MockChain();
    await c.asset.createAsset({ issuer: ISSUER, assetId: "membership", flags: { nonTransferable: true, freezable: true } });
    await c.asset.mint({ agent: ISSUER, assetId: "membership", to: ALICE, amount: "1" });
    await rejectsWith(c.asset.transfer({ from: ALICE, assetId: "membership", to: BOB, amount: "1" }), "ERROR_CODE_NON_TRANSFERABLE");
    await c.asset.clawback({ agent: ISSUER, assetId: "membership", from: ALICE, amount: "1", reason: "membership ended" });
  });
});

describe("MockChain: freeze, pause, clawback, forced transfer", () => {
  let chain: MockChain;
  beforeEach(async () => {
    chain = new MockChain();
    await bond(chain);
    await chain.asset.mint({ agent: AGENT, assetId: "bond-2030", to: ALICE, amount: "100" });
  });

  it("freezes and unfreezes an address", async () => {
    await chain.asset.freeze({ agent: AGENT, assetId: "bond-2030", holder: ALICE, frozen: true });
    await rejectsWith(chain.asset.transfer({ from: ALICE, assetId: "bond-2030", to: BOB, amount: "1" }), "ERROR_CODE_ADDRESS_FROZEN");
    await rejectsWith(chain.asset.mint({ agent: AGENT, assetId: "bond-2030", to: ALICE, amount: "1" }), "ERROR_CODE_ADDRESS_FROZEN");
    const q = await chain.asset.canTransfer({ assetId: "bond-2030", from: ALICE, to: BOB, amount: "1" });
    expect(q.allowed).toBe(false);
    expect(q.code).toBe(asset.ErrorCode.ERROR_CODE_ADDRESS_FROZEN);
    await chain.asset.freeze({ agent: AGENT, assetId: "bond-2030", holder: ALICE, frozen: false });
    await chain.asset.transfer({ from: ALICE, assetId: "bond-2030", to: BOB, amount: "1" });
  });

  it("freezes part of a balance", async () => {
    await chain.asset.freezePartial({ agent: AGENT, assetId: "bond-2030", holder: ALICE, frozenAmount: "70" });
    await rejectsWith(chain.asset.transfer({ from: ALICE, assetId: "bond-2030", to: BOB, amount: "31" }), "ERROR_CODE_INSUFFICIENT_UNFROZEN_BALANCE");
    await chain.asset.transfer({ from: ALICE, assetId: "bond-2030", to: BOB, amount: "30" });
  });

  it("pauses transfers but not issuance", async () => {
    await chain.asset.pause({ agent: AGENT, assetId: "bond-2030", paused: true });
    await rejectsWith(chain.asset.transfer({ from: ALICE, assetId: "bond-2030", to: BOB, amount: "1" }), "ERROR_CODE_ASSET_PAUSED");
    await chain.asset.mint({ agent: AGENT, assetId: "bond-2030", to: BOB, amount: "1" });
    await chain.asset.pause({ agent: AGENT, assetId: "bond-2030", paused: false });
    await chain.asset.transfer({ from: ALICE, assetId: "bond-2030", to: BOB, amount: "1" });
  });

  it("claws back to the issuer ignoring the freeze", async () => {
    await chain.asset.freezePartial({ agent: AGENT, assetId: "bond-2030", holder: ALICE, frozenAmount: "100" });
    await chain.asset.freeze({ agent: AGENT, assetId: "bond-2030", holder: ALICE, frozen: true });
    await chain.asset.clawback({ agent: AGENT, assetId: "bond-2030", from: ALICE, amount: "40", reason: "court order 12/2026" });
    const h = (await chain.asset.holder({ assetId: "bond-2030", address: ALICE })).holder!;
    expect(h.balance).toBe("60");
    expect(h.frozenAmount).toBe("60");
    expect(await balance(chain, ISSUER)).toBe("40");
    const ev = chain.events("qorechain.asset.v1.EventClawback")[0]!.data as asset.EventClawback;
    expect(ev.reason).toBe("court order 12/2026");
  });

  it("force-transfers from a frozen address to a recovery wallet", async () => {
    await chain.asset.freeze({ agent: AGENT, assetId: "bond-2030", holder: ALICE, frozen: true });
    await chain.asset.forceTransfer({ agent: AGENT, assetId: "bond-2030", from: ALICE, to: CAROL, amount: "100", reason: "lost key" });
    expect(await balance(chain, CAROL)).toBe("100");
    await chain.asset.freeze({ agent: AGENT, assetId: "bond-2030", holder: BOB, frozen: true });
    await rejectsWith(
      chain.asset.forceTransfer({ agent: AGENT, assetId: "bond-2030", from: CAROL, to: BOB, amount: "1", reason: "x" }),
      "ERROR_CODE_ADDRESS_FROZEN",
    );
  });

  it("moves the issuer role in two steps", async () => {
    await chain.asset.proposeIssuer({ issuer: ISSUER, assetId: "bond-2030", newIssuer: CAROL });
    await rejectsWith(chain.asset.acceptIssuer({ newIssuer: BOB, assetId: "bond-2030" }), "ERROR_CODE_UNAUTHORIZED_ROLE");
    await chain.asset.acceptIssuer({ newIssuer: CAROL, assetId: "bond-2030" });
    expect((await chain.asset.asset({ assetId: "bond-2030" })).asset!.issuer).toBe(CAROL);
    const roles = (await chain.asset.roles({ assetId: "bond-2030" })).roles;
    expect(roles.find((r) => r.role === asset.Role.ROLE_ISSUER)!.address).toBe(CAROL);
  });

  it("retires: no transfer, burn still allowed", async () => {
    await chain.asset.retire({ issuer: ISSUER, assetId: "bond-2030" });
    await rejectsWith(chain.asset.transfer({ from: ALICE, assetId: "bond-2030", to: BOB, amount: "1" }), "ERROR_CODE_ASSET_RETIRED");
    await chain.asset.burn({ agent: AGENT, assetId: "bond-2030", from: ALICE, amount: "100" });
    expect((await chain.asset.asset({ assetId: "bond-2030" })).asset!.totalSupply).toBe("0");
  });
});

describe("MockChain: identity and compliance", () => {
  let chain: MockChain;
  beforeEach(async () => {
    chain = new MockChain({ identityAgents: [KYC] });
    await bond(chain);
    await chain.identity.setClaimIssuer({ authority: "authority", claimIssuer: { address: KYC, name: "KYC provider", topics: [1] } });
    for (const [id, addr, country] of [["id-alice", ALICE, 756], ["id-bob", BOB, 408]] as const) {
      await chain.identity.registerIdentity({ agent: KYC, identityId: id, address: addr, country });
      await chain.identity.addClaim({ claimIssuer: KYC, identityId: id, topic: 1, dataHash: new Uint8Array(32), validUntil: "0" });
    }
    await chain.compliance.bindModule({ issuer: ISSUER, assetId: "bond-2030", moduleId: "identity-verified", version: 1, paramsJson: '{"topics":[1]}' });
    await chain.compliance.bindModule({ issuer: ISSUER, assetId: "bond-2030", moduleId: "country-blocklist", version: 1, paramsJson: '{"countries":[408]}' });
  });

  it("rejects a mint to an unverified address", async () => {
    const e = await rejectsWith(chain.asset.mint({ agent: AGENT, assetId: "bond-2030", to: CAROL, amount: "1" }), "ERROR_CODE_COMPLIANCE_REJECTED");
    expect(e.message).toContain("identity-verified");
  });

  it("rejects a transfer to a blocked country and reports the module", async () => {
    await chain.asset.mint({ agent: AGENT, assetId: "bond-2030", to: ALICE, amount: "10" });
    await rejectsWith(chain.asset.transfer({ from: ALICE, assetId: "bond-2030", to: BOB, amount: "1" }), "ERROR_CODE_COMPLIANCE_REJECTED");
    const q = await chain.asset.canTransfer({ assetId: "bond-2030", from: ALICE, to: BOB, amount: "1" });
    expect(q).toMatchObject({ allowed: false, code: asset.ErrorCode.ERROR_CODE_COMPLIANCE_REJECTED, complianceModuleId: "country-blocklist" });
    const check = await chain.compliance.check({ assetId: "bond-2030", from: ALICE, to: BOB, amount: "1" });
    expect(check).toMatchObject({ allowed: false, moduleId: "country-blocklist", version: 1 });
  });

  it("revoking a claim or distrusting its issuer unverifies the holder", async () => {
    await chain.asset.mint({ agent: AGENT, assetId: "bond-2030", to: ALICE, amount: "1" });
    await chain.identity.setClaimIssuer({ authority: "authority", claimIssuer: { address: KYC, topics: [1] }, remove: true });
    expect((await chain.identity.isVerified({ address: ALICE, topics: [1] })).verified).toBe(false);
    await rejectsWith(chain.asset.mint({ agent: AGENT, assetId: "bond-2030", to: ALICE, amount: "1" }), "ERROR_CODE_COMPLIANCE_REJECTED");
  });

  it("disabling a module version fails closed until the binding migrates", async () => {
    await chain.asset.mint({ agent: AGENT, assetId: "bond-2030", to: ALICE, amount: "10" });
    await chain.compliance.registerModule({
      authority: "authority",
      module: { moduleId: "country-blocklist", version: 2, runtime: compliance.ModuleRuntime.MODULE_RUNTIME_NATIVE },
    });
    await chain.compliance.setModuleStatus({
      authority: "authority", moduleId: "country-blocklist", version: 1, status: compliance.ModuleStatus.MODULE_STATUS_DISABLED,
    });
    await rejectsWith(chain.asset.mint({ agent: AGENT, assetId: "bond-2030", to: ALICE, amount: "1" }), "ERROR_CODE_COMPLIANCE_REJECTED");
    await chain.compliance.migrateBinding({ issuer: ISSUER, assetId: "bond-2030", moduleId: "country-blocklist", toVersion: 2 });
    await chain.asset.mint({ agent: AGENT, assetId: "bond-2030", to: ALICE, amount: "1" });
    await rejectsWith(
      chain.compliance.bindModule({ issuer: ISSUER, assetId: "bond-2030", moduleId: "max-holders", version: 1, paramsJson: '{"max":0}' }),
      "ERROR_CODE_INVALID_PARAMS",
    );
  });

  it("caps the number of holders", async () => {
    await chain.compliance.unbindModule({ issuer: ISSUER, assetId: "bond-2030", moduleId: "country-blocklist" });
    await chain.compliance.bindModule({ issuer: ISSUER, assetId: "bond-2030", moduleId: "max-holders", version: 1, paramsJson: '{"max":1}' });
    await chain.asset.mint({ agent: AGENT, assetId: "bond-2030", to: ALICE, amount: "10" });
    await rejectsWith(chain.asset.transfer({ from: ALICE, assetId: "bond-2030", to: BOB, amount: "1" }), "ERROR_CODE_COMPLIANCE_REJECTED");
    await chain.asset.transfer({ from: ALICE, assetId: "bond-2030", to: BOB, amount: "10" });
  });

  it("runs custom module logic supplied by the application", async () => {
    await chain.compliance.registerModule({
      authority: "authority",
      module: { moduleId: "lockup", version: 1, runtime: compliance.ModuleRuntime.MODULE_RUNTIME_WASM, codeRef: "qor1lockupcontract" },
    });
    chain.defineModuleLogic("lockup", ({ chain: c, from }) => (from && c.time < 1_767_225_600 + 86400 ? "lock-up until day 1" : undefined));
    await chain.compliance.bindModule({ issuer: ISSUER, assetId: "bond-2030", moduleId: "lockup", version: 1, paramsJson: "{}" });
    await chain.asset.mint({ agent: AGENT, assetId: "bond-2030", to: ALICE, amount: "10" });
    await chain.identity.registerIdentity({ agent: KYC, identityId: "id-carol", address: CAROL, country: 756 });
    await chain.identity.addClaim({ claimIssuer: KYC, identityId: "id-carol", topic: 1, dataHash: new Uint8Array(32), validUntil: "0" });
    await rejectsWith(chain.asset.transfer({ from: ALICE, assetId: "bond-2030", to: CAROL, amount: "1" }), "ERROR_CODE_COMPLIANCE_REJECTED");
    chain.advance(10, 86400);
    await chain.asset.transfer({ from: ALICE, assetId: "bond-2030", to: CAROL, amount: "1" });
  });
});

describe("MockChain: settlement", () => {
  let chain: MockChain;
  const legs = (cash: string) => [
    { from: ALICE, to: BOB, denom: "asset/bond-2030", amount: "10" },
    { from: BOB, to: ALICE, denom: "uqor", amount: cash },
  ];

  beforeEach(async () => {
    chain = new MockChain();
    await bond(chain);
    await chain.asset.mint({ agent: AGENT, assetId: "bond-2030", to: ALICE, amount: "10" });
    chain.fundBank(BOB, "uqor", "1000");
  });

  it("settles both legs after bilateral affirmation", async () => {
    const { id } = await chain.settlement.createInstruction({ creator: ALICE, legs: legs("1000"), deadline: String(chain.time + 3600) });
    expect((await chain.settlement.instruction({ id })).instruction!.status).toBe(settlement.InstructionStatus.INSTRUCTION_STATUS_PENDING);
    const r = await chain.settlement.affirm({ party: BOB, id });
    expect(r.executed).toBe(true);
    expect(await balance(chain, BOB)).toBe("10");
    expect(chain.bankBalance(ALICE, "uqor")).toBe("1000");
  });

  it("is all or nothing: a failing cash leg moves no asset", async () => {
    const { id } = await chain.settlement.createInstruction({ creator: ALICE, legs: legs("1001"), deadline: String(chain.time + 3600) });
    const r = await chain.settlement.affirm({ party: BOB, id });
    expect(r.executed).toBe(false);
    const ins = (await chain.settlement.instruction({ id })).instruction!;
    expect(ins.status).toBe(settlement.InstructionStatus.INSTRUCTION_STATUS_FAILED);
    expect(ins.failureReason).toContain("leg 1");
    expect(await balance(chain, ALICE)).toBe("10");
    expect(await balance(chain, BOB)).toBe("0");
    expect(chain.bankBalance(BOB, "uqor")).toBe("1000");
    expect(chain.events("qorechain.asset.v1.EventTransferred")).toHaveLength(0);
    chain.fundBank(BOB, "uqor", "1");
    expect((await chain.settlement.executeInstruction({ signer: BOB, id })).status).toBe(settlement.InstructionStatus.INSTRUCTION_STATUS_EXECUTED);
  });

  it("is all or nothing: a frozen seller fails the asset leg", async () => {
    await chain.asset.freeze({ agent: AGENT, assetId: "bond-2030", holder: ALICE, frozen: true });
    const { id } = await chain.settlement.createInstruction({
      creator: BOB, legs: legs("1000"), deadline: String(chain.time + 3600), settlementType: settlement.SettlementType.SETTLEMENT_TYPE_MANUAL,
    });
    await rejectsWith(chain.settlement.executeInstruction({ signer: BOB, id }), "ERROR_CODE_NOT_FULLY_AFFIRMED");
    await chain.settlement.affirm({ party: ALICE, id });
    const r = await chain.settlement.executeInstruction({ signer: ALICE, id });
    expect(r.status).toBe(settlement.InstructionStatus.INSTRUCTION_STATUS_FAILED);
    expect(chain.bankBalance(BOB, "uqor")).toBe("1000");
    expect((await chain.settlement.instruction({ id })).instruction!.failureReason).toContain("ERROR_CODE_ADDRESS_FROZEN");
  });

  it("expires after the deadline and refuses non-parties", async () => {
    const { id } = await chain.settlement.createInstruction({ creator: ALICE, legs: legs("1000"), deadline: String(chain.time + 60) });
    await rejectsWith(chain.settlement.affirm({ party: CAROL, id }), "ERROR_CODE_NOT_A_PARTY");
    chain.advance(100, 61);
    expect((await chain.settlement.instruction({ id })).instruction!.status).toBe(settlement.InstructionStatus.INSTRUCTION_STATUS_EXPIRED);
    await rejectsWith(chain.settlement.affirm({ party: BOB, id }), "ERROR_CODE_INVALID_STATUS");
  });

  it("settles ON_BLOCK at the settle height", async () => {
    const { id } = await chain.settlement.createInstruction({
      creator: ALICE, legs: legs("1000"), deadline: String(chain.time + 3600),
      settlementType: settlement.SettlementType.SETTLEMENT_TYPE_ON_BLOCK, settleHeight: String(chain.height + 5),
    });
    await chain.settlement.affirm({ party: BOB, id });
    expect((await chain.settlement.instruction({ id })).instruction!.status).toBe(settlement.InstructionStatus.INSTRUCTION_STATUS_AFFIRMED);
    chain.advance(5, 5);
    expect((await chain.settlement.instruction({ id })).instruction!.status).toBe(settlement.InstructionStatus.INSTRUCTION_STATUS_EXECUTED);
  });
});

describe("MockChain: attestations", () => {
  let chain: MockChain;
  const ADMIN = "qor1fundadmin";
  beforeEach(async () => {
    chain = new MockChain();
    await bond(chain);
    await chain.attest.setAttester({
      issuer: ISSUER, attester: { assetId: "bond-2030", address: ADMIN, kinds: [attest.AttestationKind.ATTESTATION_KIND_NAV], name: "Fund admin" },
    });
  });

  it("is fresh, then stale, and can gate transfers", async () => {
    expect((await chain.attest.latest({ assetId: "bond-2030", kind: attest.AttestationKind.ATTESTATION_KIND_NAV })).freshness)
      .toBe(attest.Freshness.FRESHNESS_MISSING);
    await chain.attest.submit({
      attester: ADMIN, assetId: "bond-2030", kind: attest.AttestationKind.ATTESTATION_KIND_NAV, value: "101.25", unit: "CHF",
      observedAt: String(chain.time - 60), validForSeconds: String(86400),
    });
    const fresh = await chain.attest.latest({ assetId: "bond-2030", kind: attest.AttestationKind.ATTESTATION_KIND_NAV });
    expect(fresh.freshness).toBe(attest.Freshness.FRESHNESS_FRESH);
    expect(fresh.attestation!.value).toBe("101.25");

    await chain.compliance.bindModule({
      issuer: ISSUER, assetId: "bond-2030", moduleId: "attestation-fresh", version: 1, paramsJson: '{"kind":"ATTESTATION_KIND_NAV"}',
    });
    await chain.asset.mint({ agent: AGENT, assetId: "bond-2030", to: ALICE, amount: "5" });
    chain.advance(1000, 86400);
    expect((await chain.attest.latest({ assetId: "bond-2030", kind: attest.AttestationKind.ATTESTATION_KIND_NAV })).freshness)
      .toBe(attest.Freshness.FRESHNESS_STALE);
    await rejectsWith(chain.asset.transfer({ from: ALICE, assetId: "bond-2030", to: BOB, amount: "1" }), "ERROR_CODE_COMPLIANCE_REJECTED");
  });

  it("refuses unknown attesters, future observations and older statements", async () => {
    const nav = attest.AttestationKind.ATTESTATION_KIND_NAV;
    await rejectsWith(chain.attest.submit({ attester: BOB, assetId: "bond-2030", kind: nav, value: "1", observedAt: String(chain.time), validForSeconds: "60" }), "ERROR_CODE_NOT_AN_ATTESTER");
    await rejectsWith(chain.attest.submit({ attester: ADMIN, assetId: "bond-2030", kind: nav, value: "1", observedAt: String(chain.time + 1), validForSeconds: "60" }), "ERROR_CODE_OBSERVATION_IN_FUTURE");
    await chain.attest.submit({ attester: ADMIN, assetId: "bond-2030", kind: nav, value: "1", observedAt: String(chain.time), validForSeconds: "60" });
    await rejectsWith(chain.attest.submit({ attester: ADMIN, assetId: "bond-2030", kind: nav, value: "1", observedAt: String(chain.time - 10), validForSeconds: "60" }), "ERROR_CODE_OLDER_THAN_LATEST");
    await rejectsWith(chain.attest.submit({ attester: ADMIN, assetId: "bond-2030", kind: attest.AttestationKind.ATTESTATION_KIND_RESERVES, value: "1", observedAt: String(chain.time), validForSeconds: "60" }), "ERROR_CODE_KIND_NOT_ALLOWED");
  });
});

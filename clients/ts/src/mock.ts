// SPDX-License-Identifier: Apache-2.0
//
// MockChain: an in-memory implementation of the PROPOSED modules, for building
// and testing applications. It is not QoreChain and proves nothing about how
// the chain would behave; it implements the rules written in docs/proposal.md.
// Signer fields are trusted as given: there are no signatures in the mock.

import type { AssetApi, AssetKit, AttestApi, ComplianceApi, IdentityApi, In, SettlementApi } from "./api.js";
import { MockChainError, type ModuleName } from "./errors.js";
import * as A from "./gen/asset.js";
import * as I from "./gen/identity.js";
import * as C from "./gen/compliance.js";
import * as S from "./gen/settlement.js";
import * as T from "./gen/attest.js";

/** One recorded event, in emission order. */
export interface MockEvent {
  /** Full proto name, for example `qorechain.asset.v1.EventMinted`. */
  type: string;
  height: number;
  data: unknown;
}

/** Context passed to a compliance module's logic. */
export interface ModuleContext {
  chain: MockChain;
  assetId: string;
  /** Empty for a mint. */
  from: string;
  to: string;
  amount: bigint;
  /** The binding's parameters, parsed from JSON. */
  params: Record<string, unknown>;
}

/** Returns a refusal reason, or undefined to allow. */
export type ModuleLogic = (ctx: ModuleContext) => string | undefined;

export interface MockChainOptions {
  /** Address treated as the governance authority. Default "authority". */
  authority?: string;
  /** Identity agents of x/identity. Default: none (the authority can always act). */
  identityAgents?: string[];
  /** Initial block time, Unix seconds. Default 1767225600 (2026-01-01T00:00:00Z). */
  time?: number;
  /** Initial height. Default 1. */
  height?: number;
}

interface Holder {
  balance: bigint;
  authorized: boolean;
  frozen: boolean;
  frozenAmount: bigint;
}

interface AssetRec {
  asset: A.Asset;
  /** address -> role -> granted height */
  roles: Map<string, Map<A.Role, number>>;
  holders: Map<string, Holder>;
}

interface Refusal {
  code: string;
  moduleId?: string;
  reason: string;
}

const ASSET_ID = /^[a-z][a-z0-9-]{2,31}$/;
const INTEGER = /^[0-9]+$/;
const FINAL = new Set([
  S.InstructionStatus.INSTRUCTION_STATUS_EXECUTED,
  S.InstructionStatus.INSTRUCTION_STATUS_CANCELLED,
  S.InstructionStatus.INSTRUCTION_STATUS_EXPIRED,
]);

function fail(module: ModuleName, code: string, message: string): never {
  throw new MockChainError(message, code, module);
}

function parseAmount(module: ModuleName, value: string | undefined, allowZero = false): bigint {
  const s = value ?? "";
  if (!INTEGER.test(s)) fail(module, "ERROR_CODE_INVALID_AMOUNT", `amount "${s}" is not a non-negative integer`);
  const n = BigInt(s);
  if (!allowZero && n === 0n) fail(module, "ERROR_CODE_INVALID_AMOUNT", "amount must be greater than zero");
  return n;
}

function emptyHolder(): Holder {
  return { balance: 0n, authorized: false, frozen: false, frozenAmount: 0n };
}

function flagsOf(rec: AssetRec): A.RwaFlagsV0 {
  return rec.asset.flags ?? A.RwaFlagsV0.fromPartial({});
}

const BUILTIN_MODULES: Array<{ id: string; schema: string; description: string }> = [
  {
    id: "identity-verified",
    schema: '{"type":"object","required":["topics"],"properties":{"topics":{"type":"array","items":{"type":"integer"}}}}',
    description: "The receiver is verified in x/identity for every listed claim topic.",
  },
  {
    id: "country-allowlist",
    schema: '{"type":"object","required":["countries"],"properties":{"countries":{"type":"array","items":{"type":"integer"}}}}',
    description: "The receiver's identity country is in the list; no identity is refused.",
  },
  {
    id: "country-blocklist",
    schema: '{"type":"object","required":["countries"],"properties":{"countries":{"type":"array","items":{"type":"integer"}}}}',
    description: "The receiver's identity country is not in the list; no identity is allowed.",
  },
  {
    id: "max-holders",
    schema: '{"type":"object","required":["max"],"properties":{"max":{"type":"integer","minimum":1}}}',
    description: "The number of addresses with a positive balance never exceeds max.",
  },
  {
    id: "max-balance",
    schema: '{"type":"object","required":["max"],"properties":{"max":{"type":"string","pattern":"^[0-9]+$"}}}',
    description: "The receiver's balance after the transfer is at most max.",
  },
  {
    id: "attestation-fresh",
    schema: '{"type":"object","required":["kind"],"properties":{"kind":{"type":"string"}}}',
    description: "The latest attestation of the given kind for the asset is fresh.",
  },
];

/** In-memory implementation of the proposed modules. See docs/proposal.md. */
export class MockChain implements AssetKit {
  readonly authority: string;
  private _height: number;
  private _time: number;
  private log: MockEvent[] = [];
  private keys = new Map<string, { registered: boolean; possessionProven: boolean }>();
  private bank = new Map<string, Map<string, bigint>>();
  private customLogic = new Map<string, ModuleLogic>();

  // x/asset
  private assetParams = A.Params.fromPartial({ creationFee: "0", maxAgents: 10, maxComplianceModules: 10 });
  private assetsById = new Map<string, AssetRec>();

  // x/identity
  private identityParams: I.Params;
  private identities = new Map<string, I.Identity>();
  private identityOf = new Map<string, string>();
  private claimIssuersByAddress = new Map<string, I.ClaimIssuer>();

  // x/compliance
  private complianceParams = C.Params.fromPartial({ maxModuleGas: "1000000" });
  private registry = new Map<string, C.ComplianceModule>();
  private bindingsByAsset = new Map<string, C.Binding[]>();

  // x/settlement
  private settlementParams = S.Params.fromPartial({ maxLegs: 10, maxDeadlineSeconds: String(30 * 86400) });
  private instructions = new Map<string, S.Instruction>();
  private nextInstructionId = 1;
  private venues = new Map<string, S.Venue>();

  // x/attest
  private attestParams = T.Params.fromPartial({
    maxObservationLagSeconds: String(7 * 86400),
    maxValiditySeconds: String(400 * 86400),
  });
  private attestersByAsset = new Map<string, Map<string, T.Attester>>();
  private attestations: T.Attestation[] = [];
  private nextAttestationId = 1;

  readonly asset: AssetApi;
  readonly identity: IdentityApi;
  readonly compliance: ComplianceApi;
  readonly settlement: SettlementApi;
  readonly attest: AttestApi;

  constructor(options: MockChainOptions = {}) {
    this.authority = options.authority ?? "authority";
    this._time = options.time ?? 1_767_225_600;
    this._height = options.height ?? 1;
    this.identityParams = I.Params.fromPartial({ identityAgents: options.identityAgents ?? [] });
    for (const m of BUILTIN_MODULES) {
      this.registry.set(`${m.id}@1`, C.ComplianceModule.fromPartial({
        moduleId: m.id,
        version: 1,
        runtime: C.ModuleRuntime.MODULE_RUNTIME_NATIVE,
        status: C.ModuleStatus.MODULE_STATUS_ACTIVE,
        paramsSchema: m.schema,
        description: m.description,
      }));
    }
    const run = <R>(fn: () => R): Promise<R> => {
      try {
        return Promise.resolve(fn());
      } catch (e) {
        return Promise.reject(e);
      }
    };
    this.asset = {
      createAsset: (m) => run(() => this.createAsset(A.MsgCreateAsset.fromPartial(m))),
      updateFlags: (m) => run(() => this.updateFlags(A.MsgUpdateFlags.fromPartial(m))),
      setRole: (m) => run(() => this.setRole(A.MsgSetRole.fromPartial(m))),
      proposeIssuer: (m) => run(() => this.proposeIssuer(A.MsgProposeIssuer.fromPartial(m))),
      acceptIssuer: (m) => run(() => this.acceptIssuer(A.MsgAcceptIssuer.fromPartial(m))),
      authorizeHolder: (m) => run(() => this.authorizeHolder(A.MsgAuthorizeHolder.fromPartial(m))),
      mint: (m) => run(() => this.mint(A.MsgMint.fromPartial(m))),
      burn: (m) => run(() => this.burn(A.MsgBurn.fromPartial(m))),
      transfer: (m) => run(() => this.transfer(A.MsgTransfer.fromPartial(m))),
      freeze: (m) => run(() => this.freeze(A.MsgFreeze.fromPartial(m))),
      freezePartial: (m) => run(() => this.freezePartial(A.MsgFreezePartial.fromPartial(m))),
      pause: (m) => run(() => this.pause(A.MsgPause.fromPartial(m))),
      clawback: (m) => run(() => this.clawback(A.MsgClawback.fromPartial(m))),
      forceTransfer: (m) => run(() => this.forceTransfer(A.MsgForceTransfer.fromPartial(m))),
      setTerms: (m) => run(() => this.setTerms(A.MsgSetTerms.fromPartial(m))),
      retire: (m) => run(() => this.retire(A.MsgRetire.fromPartial(m))),
      params: () => run(() => A.QueryParamsResponse.fromPartial({ params: this.assetParams })),
      asset: (q) => run(() => this.queryAsset(A.QueryAssetRequest.fromPartial(q))),
      assets: (q) => run(() => this.queryAssets(A.QueryAssetsRequest.fromPartial(q ?? {}))),
      holder: (q) => run(() => this.queryHolder(A.QueryHolderRequest.fromPartial(q))),
      holders: (q) => run(() => this.queryHolders(A.QueryHoldersRequest.fromPartial(q))),
      roles: (q) => run(() => this.queryRoles(A.QueryRolesRequest.fromPartial(q))),
      canTransfer: (q) => run(() => this.queryCanTransfer(A.QueryCanTransferRequest.fromPartial(q))),
    };
    this.identity = {
      registerIdentity: (m) => run(() => this.registerIdentity(I.MsgRegisterIdentity.fromPartial(m))),
      updateCountry: (m) => run(() => this.updateCountry(I.MsgUpdateCountry.fromPartial(m))),
      bindAddress: (m) => run(() => this.bindAddress(I.MsgBindAddress.fromPartial(m))),
      unbindAddress: (m) => run(() => this.unbindAddress(I.MsgUnbindAddress.fromPartial(m))),
      addClaim: (m) => run(() => this.addClaim(I.MsgAddClaim.fromPartial(m))),
      revokeClaim: (m) => run(() => this.revokeClaim(I.MsgRevokeClaim.fromPartial(m))),
      removeIdentity: (m) => run(() => this.removeIdentity(I.MsgRemoveIdentity.fromPartial(m))),
      setClaimIssuer: (m) => run(() => this.setClaimIssuer(I.MsgSetClaimIssuer.fromPartial(m))),
      params: () => run(() => I.QueryParamsResponse.fromPartial({ params: this.identityParams })),
      identity: (q) => run(() => this.queryIdentity(I.QueryIdentityRequest.fromPartial(q))),
      identityByAddress: (q) => run(() => this.queryIdentityByAddress(I.QueryIdentityByAddressRequest.fromPartial(q))),
      claimIssuers: () => run(() => I.QueryClaimIssuersResponse.fromPartial({
        claimIssuers: [...this.claimIssuersByAddress.values()].sort((a, b) => cmp(a.address, b.address)),
      })),
      isVerified: (q) => run(() => this.queryIsVerified(I.QueryIsVerifiedRequest.fromPartial(q))),
    };
    this.compliance = {
      registerModule: (m) => run(() => this.registerModule(C.MsgRegisterModule.fromPartial(m))),
      setModuleStatus: (m) => run(() => this.setModuleStatus(C.MsgSetModuleStatus.fromPartial(m))),
      bindModule: (m) => run(() => this.bindModule(C.MsgBindModule.fromPartial(m))),
      unbindModule: (m) => run(() => this.unbindModule(C.MsgUnbindModule.fromPartial(m))),
      migrateBinding: (m) => run(() => this.migrateBinding(C.MsgMigrateBinding.fromPartial(m))),
      params: () => run(() => C.QueryParamsResponse.fromPartial({ params: this.complianceParams })),
      modules: (q) => run(() => this.queryModules(C.QueryModulesRequest.fromPartial(q ?? {}))),
      module: (q) => run(() => this.queryModule(C.QueryModuleRequest.fromPartial(q))),
      bindings: (q) => run(() => C.QueryBindingsResponse.fromPartial({
        bindings: this.bindingsOf(C.QueryBindingsRequest.fromPartial(q).assetId),
      })),
      check: (q) => run(() => this.queryCheck(C.QueryCheckRequest.fromPartial(q))),
    };
    this.settlement = {
      createVenue: (m) => run(() => this.createVenue(S.MsgCreateVenue.fromPartial(m))),
      createInstruction: (m) => run(() => this.createInstruction(S.MsgCreateInstruction.fromPartial(m))),
      affirm: (m) => run(() => this.affirm(S.MsgAffirm.fromPartial(m))),
      withdrawAffirmation: (m) => run(() => this.withdrawAffirmation(S.MsgWithdrawAffirmation.fromPartial(m))),
      executeInstruction: (m) => run(() => this.executeInstruction(S.MsgExecuteInstruction.fromPartial(m))),
      cancelInstruction: (m) => run(() => this.cancelInstruction(S.MsgCancelInstruction.fromPartial(m))),
      params: () => run(() => S.QueryParamsResponse.fromPartial({ params: this.settlementParams })),
      instruction: (q) => run(() => this.queryInstruction(S.QueryInstructionRequest.fromPartial(q))),
      instructionsByParty: (q) => run(() => this.queryInstructionsByParty(S.QueryInstructionsByPartyRequest.fromPartial(q))),
      venue: (q) => run(() => this.queryVenue(S.QueryVenueRequest.fromPartial(q))),
    };
    this.attest = {
      setAttester: (m) => run(() => this.setAttester(T.MsgSetAttester.fromPartial(m))),
      submit: (m) => run(() => this.submitAttestation(T.MsgSubmit.fromPartial(m))),
      revoke: (m) => run(() => this.revokeAttestation(T.MsgRevoke.fromPartial(m))),
      params: () => run(() => T.QueryParamsResponse.fromPartial({ params: this.attestParams })),
      latest: (q) => run(() => this.queryLatest(T.QueryLatestRequest.fromPartial(q))),
      history: (q) => run(() => this.queryHistory(T.QueryHistoryRequest.fromPartial(q))),
      attesters: (q) => run(() => T.QueryAttestersResponse.fromPartial({
        attesters: [...(this.attestersByAsset.get(T.QueryAttestersRequest.fromPartial(q).assetId)?.values() ?? [])]
          .sort((a, b) => cmp(a.address, b.address)),
      })),
    };
  }

  // ------------------------------------------------------------------ chain

  get height(): number {
    return this._height;
  }

  /** Block time, Unix seconds. */
  get time(): number {
    return this._time;
  }

  /**
   * Advances the chain by `blocks` blocks and `seconds` seconds, then runs the
   * end blocker: ON_BLOCK instructions due at the new height settle (or fail if
   * not fully affirmed), then instructions past their deadline expire.
   */
  advance(blocks: number, seconds: number): void {
    if (blocks < 0 || seconds < 0) throw new RangeError("cannot go back in time");
    this._height += blocks;
    this._time += seconds;
    for (const ins of [...this.instructions.values()].sort((a, b) => Number(a.id) - Number(b.id))) {
      const due = ins.settlementType === S.SettlementType.SETTLEMENT_TYPE_ON_BLOCK && Number(ins.settleHeight) <= this._height;
      if (due && ins.status === S.InstructionStatus.INSTRUCTION_STATUS_AFFIRMED && this._time <= Number(ins.deadline)) {
        this.execute(ins);
      } else if (due && ins.status === S.InstructionStatus.INSTRUCTION_STATUS_PENDING) {
        ins.status = S.InstructionStatus.INSTRUCTION_STATUS_FAILED;
        ins.failureReason = "not fully affirmed at settle height";
        this.emit("qorechain.settlement.v1.EventInstructionFailed", S.EventInstructionFailed.fromPartial({
          id: ins.id, legIndex: 0, reason: ins.failureReason,
        }));
      }
    }
    for (const ins of this.instructions.values()) {
      if (!FINAL.has(ins.status) && this._time > Number(ins.deadline)) {
        ins.status = S.InstructionStatus.INSTRUCTION_STATUS_EXPIRED;
        this.emit("qorechain.settlement.v1.EventInstructionExpired", S.EventInstructionExpired.fromPartial({ id: ins.id }));
      }
    }
  }

  /** Sets what pqcKeyStatus would report for an address. */
  setHybridKey(address: string, status: { registered: boolean; possessionProven: boolean }): void {
    this.keys.set(address, { ...status });
  }

  /** True when the address has a registered ML-DSA-87 key with proof of possession. */
  hasHybridKey(address: string): boolean {
    const k = this.keys.get(address);
    return !!k && k.registered && k.possessionProven;
  }

  /** Credits a bank denom (for example "uqor") to an address: the cash side of DvP tests. */
  fundBank(address: string, denom: string, amount: string | bigint): void {
    const n = typeof amount === "bigint" ? amount : BigInt(amount);
    const m = this.bank.get(address) ?? new Map<string, bigint>();
    m.set(denom, (m.get(denom) ?? 0n) + n);
    this.bank.set(address, m);
  }

  bankBalance(address: string, denom: string): string {
    return String(this.bank.get(address)?.get(denom) ?? 0n);
  }

  /** Recorded events, optionally filtered by full type name. Copies. */
  events(type?: string): MockEvent[] {
    return this.log.filter((e) => type === undefined || e.type === type).map((e) => ({ ...e }));
  }

  /** Supplies the logic of a compliance module registered by governance (for example a WASM module). */
  defineModuleLogic(moduleId: string, logic: ModuleLogic): void {
    this.customLogic.set(moduleId, logic);
  }

  private emit(type: string, data: unknown): void {
    this.log.push({ type, height: this._height, data });
  }

  // ---------------------------------------------------------------- x/asset

  private rec(assetId: string): AssetRec {
    const r = this.assetsById.get(assetId);
    if (!r) fail("x/asset", "ERROR_CODE_ASSET_NOT_FOUND", `asset ${assetId} not found`);
    return r;
  }

  private holderOf(r: AssetRec, address: string): Holder {
    let h = r.holders.get(address);
    if (!h) {
      h = emptyHolder();
      r.holders.set(address, h);
    }
    return h;
  }

  private peekHolder(r: AssetRec, address: string): Holder {
    return r.holders.get(address) ?? emptyHolder();
  }

  private hasRole(r: AssetRec, address: string, role: A.Role): boolean {
    return r.roles.get(address)?.has(role) ?? false;
  }

  private requireIssuer(r: AssetRec, signer: string): void {
    if (r.asset.issuer !== signer) fail("x/asset", "ERROR_CODE_UNAUTHORIZED_ROLE", `${signer} is not the issuer of ${r.asset.assetId}`);
    this.requireSignerKey(r, signer);
  }

  private requireAgent(r: AssetRec, signer: string): void {
    if (r.asset.issuer !== signer && !this.hasRole(r, signer, A.Role.ROLE_AGENT)) {
      fail("x/asset", "ERROR_CODE_UNAUTHORIZED_ROLE", `${signer} is not an agent of ${r.asset.assetId}`);
    }
    this.requireSignerKey(r, signer);
  }

  private requireSignerKey(r: AssetRec, signer: string): void {
    if (flagsOf(r).requireHybridSignature && !this.hasHybridKey(signer)) {
      fail("x/asset", "ERROR_CODE_HYBRID_SIGNATURE_REQUIRED", `${signer} has no registered ML-DSA-87 key with proof of possession`);
    }
  }

  private createAsset(m: A.MsgCreateAsset): A.MsgCreateAssetResponse {
    if (!ASSET_ID.test(m.assetId)) fail("x/asset", "ERROR_CODE_INVALID_ASSET_ID", `invalid asset id "${m.assetId}"`);
    if (this.assetsById.has(m.assetId)) fail("x/asset", "ERROR_CODE_ASSET_EXISTS", `asset ${m.assetId} exists`);
    const flags = A.RwaFlagsV0.fromPartial(m.flags ?? {});
    let maxSupply = "";
    if (flags.supplyCap) maxSupply = String(parseAmount("x/asset", m.maxSupply));
    if (flags.requireHybridSignature && !this.hasHybridKey(m.issuer)) {
      fail("x/asset", "ERROR_CODE_HYBRID_SIGNATURE_REQUIRED", `${m.issuer} has no registered ML-DSA-87 key with proof of possession`);
    }
    const asset = A.Asset.fromPartial({
      assetId: m.assetId,
      issuer: m.issuer,
      name: m.name,
      symbol: m.symbol,
      decimals: m.decimals,
      flags,
      maxSupply,
      totalSupply: "0",
      status: A.AssetStatus.ASSET_STATUS_ACTIVE,
      termsHash: m.termsHash,
      termsUri: m.termsUri,
      complianceModuleIds: [],
      createdHeight: String(this._height),
    });
    const roles = new Map<string, Map<A.Role, number>>([[m.issuer, new Map([[A.Role.ROLE_ISSUER, this._height]])]]);
    this.assetsById.set(m.assetId, { asset, roles, holders: new Map() });
    this.emit("qorechain.asset.v1.EventAssetCreated", A.EventAssetCreated.fromPartial({
      assetId: m.assetId, issuer: m.issuer, flags, maxSupply,
    }));
    return { denom: `asset/${m.assetId}` };
  }

  private updateFlags(m: A.MsgUpdateFlags): A.MsgUpdateFlagsResponse {
    const r = this.rec(m.assetId);
    this.requireIssuer(r, m.issuer);
    const cur = flagsOf(r);
    const next = A.RwaFlagsV0.fromPartial(m.flags ?? {});
    for (const k of ["nonTransferable", "supplyCap", "requireHybridSignature"] as const) {
      if (cur[k] !== next[k]) fail("x/asset", "ERROR_CODE_FLAG_IMMUTABLE", `${k} cannot change after creation`);
    }
    for (const k of ["requireAuth", "freezable", "pausable"] as const) {
      if (!cur[k] && next[k]) fail("x/asset", "ERROR_CODE_FLAG_IMMUTABLE", `${k} can only be switched off`);
    }
    r.asset.flags = next;
    this.emit("qorechain.asset.v1.EventFlagsUpdated", A.EventFlagsUpdated.fromPartial({ assetId: m.assetId, flags: next }));
    return {};
  }

  private setRole(m: A.MsgSetRole): A.MsgSetRoleResponse {
    const r = this.rec(m.assetId);
    this.requireIssuer(r, m.issuer);
    if (m.role !== A.Role.ROLE_AGENT && m.role !== A.Role.ROLE_AUDITOR) {
      fail("x/asset", "ERROR_CODE_UNAUTHORIZED_ROLE", "only ROLE_AGENT and ROLE_AUDITOR can be granted");
    }
    if (m.granted) {
      if (m.role === A.Role.ROLE_AGENT && !this.hasRole(r, m.address, A.Role.ROLE_AGENT)) {
        const agents = [...r.roles.values()].filter((x) => x.has(A.Role.ROLE_AGENT)).length;
        if (agents >= this.assetParams.maxAgents) fail("x/asset", "ERROR_CODE_TOO_MANY_AGENTS", "too many agents");
      }
      const set = r.roles.get(m.address) ?? new Map<A.Role, number>();
      if (!set.has(m.role)) set.set(m.role, this._height);
      r.roles.set(m.address, set);
    } else {
      r.roles.get(m.address)?.delete(m.role);
    }
    this.emit("qorechain.asset.v1.EventRoleChanged", A.EventRoleChanged.fromPartial({
      assetId: m.assetId, address: m.address, role: m.role, granted: m.granted,
    }));
    return {};
  }

  private proposeIssuer(m: A.MsgProposeIssuer): A.MsgProposeIssuerResponse {
    const r = this.rec(m.assetId);
    this.requireIssuer(r, m.issuer);
    r.asset.pendingIssuer = m.newIssuer;
    this.emit("qorechain.asset.v1.EventIssuerTransferProposed", A.EventIssuerTransferProposed.fromPartial({
      assetId: m.assetId, issuer: m.issuer, newIssuer: m.newIssuer,
    }));
    return {};
  }

  private acceptIssuer(m: A.MsgAcceptIssuer): A.MsgAcceptIssuerResponse {
    const r = this.rec(m.assetId);
    if (!r.asset.pendingIssuer || r.asset.pendingIssuer !== m.newIssuer) {
      fail("x/asset", "ERROR_CODE_UNAUTHORIZED_ROLE", `${m.newIssuer} is not the pending issuer`);
    }
    this.requireSignerKey(r, m.newIssuer);
    const previous = r.asset.issuer;
    r.roles.get(previous)?.delete(A.Role.ROLE_ISSUER);
    const set = r.roles.get(m.newIssuer) ?? new Map<A.Role, number>();
    set.set(A.Role.ROLE_ISSUER, this._height);
    r.roles.set(m.newIssuer, set);
    r.asset.issuer = m.newIssuer;
    r.asset.pendingIssuer = "";
    this.emit("qorechain.asset.v1.EventIssuerTransferred", A.EventIssuerTransferred.fromPartial({
      assetId: m.assetId, previousIssuer: previous, newIssuer: m.newIssuer,
    }));
    return {};
  }

  private authorizeHolder(m: A.MsgAuthorizeHolder): A.MsgAuthorizeHolderResponse {
    const r = this.rec(m.assetId);
    this.requireAgent(r, m.agent);
    if (!flagsOf(r).requireAuth) fail("x/asset", "ERROR_CODE_FLAG_NOT_ENABLED", "require_auth is not set");
    this.holderOf(r, m.holder).authorized = m.authorized;
    this.emit("qorechain.asset.v1.EventHolderAuthorized", A.EventHolderAuthorized.fromPartial({
      assetId: m.assetId, holder: m.holder, authorized: m.authorized, agent: m.agent,
    }));
    return {};
  }

  /** Checks on a receiving address shared by mint, transfer and forced transfer. */
  private receiverRefusal(r: AssetRec, to: string): Refusal | undefined {
    const f = flagsOf(r);
    const h = this.peekHolder(r, to);
    if (h.frozen) return { code: "ERROR_CODE_ADDRESS_FROZEN", reason: `${to} is frozen` };
    if (f.requireAuth && !h.authorized) return { code: "ERROR_CODE_HOLDER_NOT_AUTHORIZED", reason: `${to} is not authorized` };
    if (f.requireHybridSignature && !this.hasHybridKey(to)) {
      return { code: "ERROR_CODE_HYBRID_SIGNATURE_REQUIRED", reason: `${to} has no registered ML-DSA-87 key with proof of possession` };
    }
    return undefined;
  }

  private complianceRefusal(assetId: string, from: string, to: string, amount: bigint): Refusal | undefined {
    const c = this.runCompliance(assetId, from, to, amount);
    if (c) return { code: "ERROR_CODE_COMPLIANCE_REJECTED", moduleId: c.moduleId, reason: c.reason };
    return undefined;
  }

  /** The ordered checks of docs/proposal.md section 4.1, without the amount parse. */
  private transferRefusal(r: AssetRec, from: string, to: string, amount: bigint): Refusal | undefined {
    const f = flagsOf(r);
    if (r.asset.status === A.AssetStatus.ASSET_STATUS_RETIRED) return { code: "ERROR_CODE_ASSET_RETIRED", reason: "asset is retired" };
    if (r.asset.status === A.AssetStatus.ASSET_STATUS_PAUSED) return { code: "ERROR_CODE_ASSET_PAUSED", reason: "asset is paused" };
    if (f.nonTransferable) return { code: "ERROR_CODE_NON_TRANSFERABLE", reason: "asset is non-transferable" };
    const hf = this.peekHolder(r, from);
    const ht = this.peekHolder(r, to);
    if (hf.frozen || ht.frozen) return { code: "ERROR_CODE_ADDRESS_FROZEN", reason: `${hf.frozen ? from : to} is frozen` };
    if (f.requireAuth && (!hf.authorized || !ht.authorized)) {
      return { code: "ERROR_CODE_HOLDER_NOT_AUTHORIZED", reason: `${!hf.authorized ? from : to} is not authorized` };
    }
    if (f.requireHybridSignature && (!this.hasHybridKey(from) || !this.hasHybridKey(to))) {
      const who = !this.hasHybridKey(from) ? from : to;
      return { code: "ERROR_CODE_HYBRID_SIGNATURE_REQUIRED", reason: `${who} has no registered ML-DSA-87 key with proof of possession` };
    }
    if (hf.balance < amount) return { code: "ERROR_CODE_INSUFFICIENT_BALANCE", reason: `${from} balance is too low` };
    if (hf.balance - hf.frozenAmount < amount) {
      return { code: "ERROR_CODE_INSUFFICIENT_UNFROZEN_BALANCE", reason: `${from} unfrozen balance is too low` };
    }
    return this.complianceRefusal(r.asset.assetId, from, to, amount);
  }

  private move(r: AssetRec, from: string, to: string, amount: bigint): void {
    const hf = this.holderOf(r, from);
    hf.balance -= amount;
    if (hf.frozenAmount > hf.balance) hf.frozenAmount = hf.balance;
    this.holderOf(r, to).balance += amount;
  }

  private mint(m: A.MsgMint): A.MsgMintResponse {
    const r = this.rec(m.assetId);
    this.requireAgent(r, m.agent);
    const amount = parseAmount("x/asset", m.amount);
    if (r.asset.status === A.AssetStatus.ASSET_STATUS_RETIRED) fail("x/asset", "ERROR_CODE_ASSET_RETIRED", "asset is retired");
    const refusal = this.receiverRefusal(r, m.to);
    if (refusal) fail("x/asset", refusal.code, refusal.reason);
    const total = BigInt(r.asset.totalSupply) + amount;
    if (flagsOf(r).supplyCap && total > BigInt(r.asset.maxSupply)) {
      fail("x/asset", "ERROR_CODE_SUPPLY_CAP_EXCEEDED", `supply would exceed ${r.asset.maxSupply}`);
    }
    const c = this.complianceRefusal(m.assetId, "", m.to, amount);
    if (c) fail("x/asset", c.code, `${c.moduleId}: ${c.reason}`);
    this.holderOf(r, m.to).balance += amount;
    r.asset.totalSupply = String(total);
    this.emit("qorechain.asset.v1.EventMinted", A.EventMinted.fromPartial({
      assetId: m.assetId, to: m.to, amount: String(amount), agent: m.agent,
    }));
    return {};
  }

  private burn(m: A.MsgBurn): A.MsgBurnResponse {
    const r = this.rec(m.assetId);
    this.requireAgent(r, m.agent);
    const amount = parseAmount("x/asset", m.amount);
    const h = this.peekHolder(r, m.from);
    if (h.frozen) fail("x/asset", "ERROR_CODE_ADDRESS_FROZEN", `${m.from} is frozen`);
    if (h.balance < amount) fail("x/asset", "ERROR_CODE_INSUFFICIENT_BALANCE", `${m.from} balance is too low`);
    if (h.balance - h.frozenAmount < amount) {
      fail("x/asset", "ERROR_CODE_INSUFFICIENT_UNFROZEN_BALANCE", `${m.from} unfrozen balance is too low`);
    }
    this.holderOf(r, m.from).balance -= amount;
    r.asset.totalSupply = String(BigInt(r.asset.totalSupply) - amount);
    this.emit("qorechain.asset.v1.EventBurned", A.EventBurned.fromPartial({
      assetId: m.assetId, from: m.from, amount: String(amount), agent: m.agent,
    }));
    return {};
  }

  private transfer(m: A.MsgTransfer): A.MsgTransferResponse {
    const amount = parseAmount("x/asset", m.amount);
    const r = this.rec(m.assetId);
    const refusal = this.transferRefusal(r, m.from, m.to, amount);
    if (refusal) fail("x/asset", refusal.code, refusal.moduleId ? `${refusal.moduleId}: ${refusal.reason}` : refusal.reason);
    this.move(r, m.from, m.to, amount);
    this.emit("qorechain.asset.v1.EventTransferred", A.EventTransferred.fromPartial({
      assetId: m.assetId, from: m.from, to: m.to, amount: String(amount),
    }));
    return {};
  }

  private requireFreezable(r: AssetRec): void {
    if (!flagsOf(r).freezable) fail("x/asset", "ERROR_CODE_FLAG_NOT_ENABLED", "freezable is not set");
  }

  private freeze(m: A.MsgFreeze): A.MsgFreezeResponse {
    const r = this.rec(m.assetId);
    this.requireAgent(r, m.agent);
    this.requireFreezable(r);
    this.holderOf(r, m.holder).frozen = m.frozen;
    this.emit("qorechain.asset.v1.EventFrozen", A.EventFrozen.fromPartial({
      assetId: m.assetId, holder: m.holder, frozen: m.frozen, agent: m.agent,
    }));
    return {};
  }

  private freezePartial(m: A.MsgFreezePartial): A.MsgFreezePartialResponse {
    const r = this.rec(m.assetId);
    this.requireAgent(r, m.agent);
    this.requireFreezable(r);
    const amount = parseAmount("x/asset", m.frozenAmount, true);
    const h = this.peekHolder(r, m.holder);
    if (amount > h.balance) fail("x/asset", "ERROR_CODE_INSUFFICIENT_BALANCE", "frozen amount exceeds the balance");
    this.holderOf(r, m.holder).frozenAmount = amount;
    this.emit("qorechain.asset.v1.EventPartiallyFrozen", A.EventPartiallyFrozen.fromPartial({
      assetId: m.assetId, holder: m.holder, frozenAmount: String(amount), agent: m.agent,
    }));
    return {};
  }

  private pause(m: A.MsgPause): A.MsgPauseResponse {
    const r = this.rec(m.assetId);
    this.requireAgent(r, m.agent);
    if (r.asset.status === A.AssetStatus.ASSET_STATUS_RETIRED) fail("x/asset", "ERROR_CODE_ASSET_RETIRED", "asset is retired");
    if (m.paused && !flagsOf(r).pausable) fail("x/asset", "ERROR_CODE_FLAG_NOT_ENABLED", "pausable is not set");
    r.asset.status = m.paused ? A.AssetStatus.ASSET_STATUS_PAUSED : A.AssetStatus.ASSET_STATUS_ACTIVE;
    this.emit("qorechain.asset.v1.EventPaused", A.EventPaused.fromPartial({ assetId: m.assetId, paused: m.paused, agent: m.agent }));
    return {};
  }

  private clawback(m: A.MsgClawback): A.MsgClawbackResponse {
    const r = this.rec(m.assetId);
    this.requireAgent(r, m.agent);
    this.requireFreezable(r);
    const amount = parseAmount("x/asset", m.amount);
    if (this.peekHolder(r, m.from).balance < amount) fail("x/asset", "ERROR_CODE_INSUFFICIENT_BALANCE", `${m.from} balance is too low`);
    this.move(r, m.from, r.asset.issuer, amount);
    this.emit("qorechain.asset.v1.EventClawback", A.EventClawback.fromPartial({
      assetId: m.assetId, from: m.from, amount: String(amount), agent: m.agent, reason: m.reason,
    }));
    return {};
  }

  private forceTransfer(m: A.MsgForceTransfer): A.MsgForceTransferResponse {
    const r = this.rec(m.assetId);
    this.requireAgent(r, m.agent);
    this.requireFreezable(r);
    const amount = parseAmount("x/asset", m.amount);
    if (r.asset.status === A.AssetStatus.ASSET_STATUS_RETIRED) fail("x/asset", "ERROR_CODE_ASSET_RETIRED", "asset is retired");
    if (this.peekHolder(r, m.from).balance < amount) fail("x/asset", "ERROR_CODE_INSUFFICIENT_BALANCE", `${m.from} balance is too low`);
    const refusal = this.receiverRefusal(r, m.to) ?? this.complianceRefusal(m.assetId, m.from, m.to, amount);
    if (refusal) fail("x/asset", refusal.code, refusal.moduleId ? `${refusal.moduleId}: ${refusal.reason}` : refusal.reason);
    this.move(r, m.from, m.to, amount);
    this.emit("qorechain.asset.v1.EventForcedTransfer", A.EventForcedTransfer.fromPartial({
      assetId: m.assetId, from: m.from, to: m.to, amount: String(amount), agent: m.agent, reason: m.reason,
    }));
    return {};
  }

  private setTerms(m: A.MsgSetTerms): A.MsgSetTermsResponse {
    const r = this.rec(m.assetId);
    this.requireIssuer(r, m.issuer);
    r.asset.termsHash = m.termsHash;
    r.asset.termsUri = m.termsUri;
    this.emit("qorechain.asset.v1.EventTermsUpdated", A.EventTermsUpdated.fromPartial({
      assetId: m.assetId, termsHash: m.termsHash, termsUri: m.termsUri,
    }));
    return {};
  }

  private retire(m: A.MsgRetire): A.MsgRetireResponse {
    const r = this.rec(m.assetId);
    this.requireIssuer(r, m.issuer);
    r.asset.status = A.AssetStatus.ASSET_STATUS_RETIRED;
    this.emit("qorechain.asset.v1.EventRetired", A.EventRetired.fromPartial({ assetId: m.assetId }));
    return {};
  }

  private queryAsset(q: A.QueryAssetRequest): A.QueryAssetResponse {
    const r = this.rec(q.assetId);
    return A.QueryAssetResponse.fromPartial({
      asset: { ...r.asset, complianceModuleIds: this.bindingsOf(q.assetId).map((b) => b.moduleId) },
    });
  }

  private queryAssets(q: A.QueryAssetsRequest): A.QueryAssetsResponse {
    const assets = [...this.assetsById.values()]
      .filter((r) => !q.issuer || r.asset.issuer === q.issuer)
      .map((r) => this.queryAsset({ assetId: r.asset.assetId }).asset!)
      .sort((a, b) => cmp(a.assetId, b.assetId));
    return A.QueryAssetsResponse.fromPartial({ assets });
  }

  private holderState(assetId: string, address: string, h: Holder): A.HolderState {
    return A.HolderState.fromPartial({
      assetId,
      address,
      balance: String(h.balance),
      authorized: h.authorized,
      frozen: h.frozen,
      frozenAmount: String(h.frozenAmount),
    });
  }

  private queryHolder(q: A.QueryHolderRequest): A.QueryHolderResponse {
    const r = this.rec(q.assetId);
    return { holder: this.holderState(q.assetId, q.address, this.peekHolder(r, q.address)) };
  }

  private queryHolders(q: A.QueryHoldersRequest): A.QueryHoldersResponse {
    const r = this.rec(q.assetId);
    const holders = [...r.holders.entries()]
      .sort(([a], [b]) => cmp(a, b))
      .map(([addr, h]) => this.holderState(q.assetId, addr, h));
    return A.QueryHoldersResponse.fromPartial({ holders });
  }

  private queryRoles(q: A.QueryRolesRequest): A.QueryRolesResponse {
    const r = this.rec(q.assetId);
    const roles: A.RoleGrant[] = [];
    for (const [address, set] of r.roles) {
      for (const [role, height] of set) {
        roles.push(A.RoleGrant.fromPartial({ assetId: q.assetId, address, role, grantedHeight: String(height) }));
      }
    }
    roles.sort((a, b) => a.role - b.role || cmp(a.address, b.address));
    return { roles };
  }

  private queryCanTransfer(q: A.QueryCanTransferRequest): A.QueryCanTransferResponse {
    const no = (code: string, reason: string, moduleId = ""): A.QueryCanTransferResponse => A.QueryCanTransferResponse.fromPartial({
      allowed: false, code: A.errorCodeFromJSON(code), complianceModuleId: moduleId, reason,
    });
    if (!INTEGER.test(q.amount) || BigInt(q.amount) === 0n) return no("ERROR_CODE_INVALID_AMOUNT", "amount must be a positive integer");
    const r = this.assetsById.get(q.assetId);
    if (!r) return no("ERROR_CODE_ASSET_NOT_FOUND", `asset ${q.assetId} not found`);
    const refusal = this.transferRefusal(r, q.from, q.to, BigInt(q.amount));
    if (refusal) return no(refusal.code, refusal.reason, refusal.moduleId);
    return A.QueryCanTransferResponse.fromPartial({ allowed: true });
  }

  // ------------------------------------------------------------- x/identity

  private requireIdentityAgent(signer: string): void {
    if (signer !== this.authority && !this.identityParams.identityAgents.includes(signer)) {
      fail("x/identity", "ERROR_CODE_NOT_IDENTITY_AGENT", `${signer} is not an identity agent`);
    }
  }

  private ident(id: string): I.Identity {
    const x = this.identities.get(id);
    if (!x) fail("x/identity", "ERROR_CODE_IDENTITY_NOT_FOUND", `identity ${id} not found`);
    return x;
  }

  private registerIdentity(m: I.MsgRegisterIdentity): I.MsgRegisterIdentityResponse {
    this.requireIdentityAgent(m.agent);
    if (this.identities.has(m.identityId)) fail("x/identity", "ERROR_CODE_IDENTITY_EXISTS", `identity ${m.identityId} exists`);
    if (this.identityOf.has(m.address)) fail("x/identity", "ERROR_CODE_ADDRESS_ALREADY_BOUND", `${m.address} is already bound`);
    this.identities.set(m.identityId, I.Identity.fromPartial({
      identityId: m.identityId, addresses: [m.address], country: m.country, claims: [], registeredBy: m.agent,
    }));
    this.identityOf.set(m.address, m.identityId);
    this.emit("qorechain.identity.v1.EventIdentityRegistered", I.EventIdentityRegistered.fromPartial({
      identityId: m.identityId, address: m.address, country: m.country, agent: m.agent,
    }));
    return {};
  }

  private updateCountry(m: I.MsgUpdateCountry): I.MsgUpdateCountryResponse {
    this.requireIdentityAgent(m.agent);
    this.ident(m.identityId).country = m.country;
    this.emit("qorechain.identity.v1.EventCountryUpdated", I.EventCountryUpdated.fromPartial({
      identityId: m.identityId, country: m.country,
    }));
    return {};
  }

  private bindAddress(m: I.MsgBindAddress): I.MsgBindAddressResponse {
    this.requireIdentityAgent(m.agent);
    const x = this.ident(m.identityId);
    if (this.identityOf.has(m.address)) fail("x/identity", "ERROR_CODE_ADDRESS_ALREADY_BOUND", `${m.address} is already bound`);
    x.addresses.push(m.address);
    this.identityOf.set(m.address, m.identityId);
    this.emit("qorechain.identity.v1.EventAddressBound", I.EventAddressBound.fromPartial({
      identityId: m.identityId, address: m.address, bound: true,
    }));
    return {};
  }

  private unbindAddress(m: I.MsgUnbindAddress): I.MsgUnbindAddressResponse {
    this.requireIdentityAgent(m.agent);
    const x = this.ident(m.identityId);
    if (this.identityOf.get(m.address) !== m.identityId) {
      fail("x/identity", "ERROR_CODE_IDENTITY_NOT_FOUND", `${m.address} is not bound to ${m.identityId}`);
    }
    x.addresses = x.addresses.filter((a) => a !== m.address);
    this.identityOf.delete(m.address);
    this.emit("qorechain.identity.v1.EventAddressBound", I.EventAddressBound.fromPartial({
      identityId: m.identityId, address: m.address, bound: false,
    }));
    return {};
  }

  private addClaim(m: I.MsgAddClaim): I.MsgAddClaimResponse {
    const issuer = this.claimIssuersByAddress.get(m.claimIssuer);
    if (!issuer) fail("x/identity", "ERROR_CODE_CLAIM_ISSUER_NOT_TRUSTED", `${m.claimIssuer} is not a trusted claim issuer`);
    if (!issuer.topics.includes(m.topic)) fail("x/identity", "ERROR_CODE_CLAIM_TOPIC_NOT_ALLOWED", `topic ${m.topic} not allowed`);
    const x = this.ident(m.identityId);
    x.claims = x.claims.filter((c) => !(c.topic === m.topic && c.issuer === m.claimIssuer));
    x.claims.push(I.Claim.fromPartial({
      topic: m.topic, issuer: m.claimIssuer, dataHash: m.dataHash, validUntil: m.validUntil, revoked: false,
    }));
    this.emit("qorechain.identity.v1.EventClaimAdded", I.EventClaimAdded.fromPartial({
      identityId: m.identityId, topic: m.topic, claimIssuer: m.claimIssuer, validUntil: m.validUntil,
    }));
    return {};
  }

  private revokeClaim(m: I.MsgRevokeClaim): I.MsgRevokeClaimResponse {
    const x = this.ident(m.identityId);
    const c = x.claims.find((k) => k.topic === m.topic && k.issuer === m.claimIssuer && !k.revoked);
    if (!c) fail("x/identity", "ERROR_CODE_CLAIM_NOT_FOUND", `no claim for topic ${m.topic} from ${m.claimIssuer}`);
    c.revoked = true;
    this.emit("qorechain.identity.v1.EventClaimRevoked", I.EventClaimRevoked.fromPartial({
      identityId: m.identityId, topic: m.topic, claimIssuer: m.claimIssuer,
    }));
    return {};
  }

  private removeIdentity(m: I.MsgRemoveIdentity): I.MsgRemoveIdentityResponse {
    this.requireIdentityAgent(m.agent);
    const x = this.ident(m.identityId);
    for (const a of x.addresses) this.identityOf.delete(a);
    this.identities.delete(m.identityId);
    this.emit("qorechain.identity.v1.EventIdentityRemoved", I.EventIdentityRemoved.fromPartial({ identityId: m.identityId }));
    return {};
  }

  private setClaimIssuer(m: I.MsgSetClaimIssuer): I.MsgSetClaimIssuerResponse {
    if (m.authority !== this.authority) fail("x/identity", "ERROR_CODE_UNAUTHORIZED", `${m.authority} is not the governance authority`);
    const ci = I.ClaimIssuer.fromPartial(m.claimIssuer ?? {});
    if (m.remove) this.claimIssuersByAddress.delete(ci.address);
    else this.claimIssuersByAddress.set(ci.address, ci);
    this.emit("qorechain.identity.v1.EventClaimIssuerChanged", I.EventClaimIssuerChanged.fromPartial({
      address: ci.address, topics: ci.topics, removed: m.remove,
    }));
    return {};
  }

  private queryIdentity(q: I.QueryIdentityRequest): I.QueryIdentityResponse {
    return I.QueryIdentityResponse.fromPartial({ identity: this.ident(q.identityId) });
  }

  private queryIdentityByAddress(q: I.QueryIdentityByAddressRequest): I.QueryIdentityByAddressResponse {
    const id = this.identityOf.get(q.address);
    if (!id) fail("x/identity", "ERROR_CODE_IDENTITY_NOT_FOUND", `${q.address} has no identity`);
    return I.QueryIdentityByAddressResponse.fromPartial({ identity: this.ident(id) });
  }

  /** Topics, of those asked, for which the address holds no valid claim. */
  missingTopics(address: string, topics: number[]): number[] {
    const id = this.identityOf.get(address);
    const x = id ? this.identities.get(id) : undefined;
    return topics.filter((topic) => !x?.claims.some((c) => {
      const trusted = this.claimIssuersByAddress.get(c.issuer)?.topics.includes(topic) ?? false;
      const live = Number(c.validUntil) === 0 || Number(c.validUntil) > this._time;
      return c.topic === topic && !c.revoked && trusted && live;
    }));
  }

  private queryIsVerified(q: I.QueryIsVerifiedRequest): I.QueryIsVerifiedResponse {
    const missing = this.missingTopics(q.address, q.topics);
    const bound = this.identityOf.has(q.address);
    return I.QueryIsVerifiedResponse.fromPartial({ verified: bound && missing.length === 0, missingTopics: missing });
  }

  /** The identity country of an address, or undefined. */
  countryOf(address: string): number | undefined {
    const id = this.identityOf.get(address);
    return id ? this.identities.get(id)?.country : undefined;
  }

  // ----------------------------------------------------------- x/compliance

  private bindingsOf(assetId: string): C.Binding[] {
    return [...(this.bindingsByAsset.get(assetId) ?? [])].sort((a, b) => a.position - b.position).map((b) => C.Binding.fromPartial(b));
  }

  private registerModule(m: C.MsgRegisterModule): C.MsgRegisterModuleResponse {
    if (m.authority !== this.authority) fail("x/compliance", "ERROR_CODE_UNAUTHORIZED", `${m.authority} is not the governance authority`);
    const mod = C.ComplianceModule.fromPartial(m.module ?? {});
    if (!mod.moduleId || mod.version < 1) fail("x/compliance", "ERROR_CODE_INVALID_PARAMS", "module id and a version >= 1 are required");
    const latest = Math.max(0, ...[...this.registry.values()].filter((x) => x.moduleId === mod.moduleId).map((x) => x.version));
    if (mod.version <= latest) fail("x/compliance", "ERROR_CODE_MODULE_VERSION_EXISTS", `version must be greater than ${latest}`);
    if (mod.status === C.ModuleStatus.MODULE_STATUS_UNSPECIFIED) mod.status = C.ModuleStatus.MODULE_STATUS_ACTIVE;
    this.registry.set(`${mod.moduleId}@${mod.version}`, mod);
    this.emit("qorechain.compliance.v1.EventModuleRegistered", C.EventModuleRegistered.fromPartial({
      moduleId: mod.moduleId, version: mod.version, runtime: mod.runtime,
    }));
    return {};
  }

  private moduleVersion(moduleId: string, version: number): C.ComplianceModule {
    const mod = this.registry.get(`${moduleId}@${version}`);
    if (!mod) fail("x/compliance", "ERROR_CODE_MODULE_NOT_FOUND", `module ${moduleId} v${version} not found`);
    return mod;
  }

  private setModuleStatus(m: C.MsgSetModuleStatus): C.MsgSetModuleStatusResponse {
    if (m.authority !== this.authority) fail("x/compliance", "ERROR_CODE_UNAUTHORIZED", `${m.authority} is not the governance authority`);
    this.moduleVersion(m.moduleId, m.version).status = m.status;
    this.emit("qorechain.compliance.v1.EventModuleStatusChanged", C.EventModuleStatusChanged.fromPartial({
      moduleId: m.moduleId, version: m.version, status: m.status,
    }));
    return {};
  }

  private requireAssetIssuer(assetId: string, signer: string): void {
    const r = this.assetsById.get(assetId);
    if (!r || r.asset.issuer !== signer) fail("x/compliance", "ERROR_CODE_NOT_ISSUER", `${signer} is not the issuer of ${assetId}`);
  }

  private parseParams(moduleId: string, json: string): Record<string, unknown> {
    let v: unknown;
    try {
      v = JSON.parse(json === "" ? "{}" : json);
    } catch {
      fail("x/compliance", "ERROR_CODE_INVALID_PARAMS", "params_json is not valid JSON");
    }
    if (typeof v !== "object" || v === null || Array.isArray(v)) fail("x/compliance", "ERROR_CODE_INVALID_PARAMS", "params_json must be a JSON object");
    const p = v as Record<string, unknown>;
    const intList = (k: string) => Array.isArray(p[k]) && (p[k] as unknown[]).length > 0 &&
      (p[k] as unknown[]).every((x) => Number.isInteger(x) && (x as number) >= 0);
    const bad = (why: string): never => fail("x/compliance", "ERROR_CODE_INVALID_PARAMS", `${moduleId}: ${why}`);
    switch (moduleId) {
      case "identity-verified":
        if (!intList("topics")) bad("topics must be a non-empty list of integers");
        break;
      case "country-allowlist":
      case "country-blocklist":
        if (!intList("countries")) bad("countries must be a non-empty list of integers");
        break;
      case "max-holders":
        if (!Number.isInteger(p.max) || (p.max as number) < 1) bad("max must be a positive integer");
        break;
      case "max-balance":
        if (typeof p.max !== "string" || !INTEGER.test(p.max)) bad("max must be an integer string");
        break;
      case "attestation-fresh": {
        const k = typeof p.kind === "string" ? T.attestationKindFromJSON(p.kind) : -1;
        if (k <= 0) bad("kind must be an AttestationKind name");
        break;
      }
    }
    return p;
  }

  private bindModule(m: C.MsgBindModule): C.MsgBindModuleResponse {
    this.requireAssetIssuer(m.assetId, m.issuer);
    const mod = this.moduleVersion(m.moduleId, m.version);
    if (mod.status === C.ModuleStatus.MODULE_STATUS_DEPRECATED) fail("x/compliance", "ERROR_CODE_MODULE_DEPRECATED", "module version is deprecated");
    if (mod.status === C.ModuleStatus.MODULE_STATUS_DISABLED) fail("x/compliance", "ERROR_CODE_MODULE_DISABLED", "module version is disabled");
    this.parseParams(m.moduleId, m.paramsJson);
    const list = this.bindingsByAsset.get(m.assetId) ?? [];
    if (list.some((b) => b.moduleId === m.moduleId)) fail("x/compliance", "ERROR_CODE_BINDING_EXISTS", `${m.moduleId} is already bound`);
    if (list.length >= this.assetParams.maxComplianceModules) fail("x/compliance", "ERROR_CODE_TOO_MANY_BINDINGS", "too many bindings");
    const position = list.reduce((max, b) => Math.max(max, b.position + 1), 0);
    list.push(C.Binding.fromPartial({
      assetId: m.assetId, moduleId: m.moduleId, version: m.version, paramsJson: m.paramsJson || "{}", position,
    }));
    this.bindingsByAsset.set(m.assetId, list);
    this.emit("qorechain.compliance.v1.EventModuleBound", C.EventModuleBound.fromPartial({
      assetId: m.assetId, moduleId: m.moduleId, version: m.version,
    }));
    return {};
  }

  private unbindModule(m: C.MsgUnbindModule): C.MsgUnbindModuleResponse {
    this.requireAssetIssuer(m.assetId, m.issuer);
    const list = this.bindingsByAsset.get(m.assetId) ?? [];
    if (!list.some((b) => b.moduleId === m.moduleId)) fail("x/compliance", "ERROR_CODE_BINDING_NOT_FOUND", `${m.moduleId} is not bound`);
    this.bindingsByAsset.set(m.assetId, list.filter((b) => b.moduleId !== m.moduleId));
    this.emit("qorechain.compliance.v1.EventModuleUnbound", C.EventModuleUnbound.fromPartial({ assetId: m.assetId, moduleId: m.moduleId }));
    return {};
  }

  private migrateBinding(m: C.MsgMigrateBinding): C.MsgMigrateBindingResponse {
    this.requireAssetIssuer(m.assetId, m.issuer);
    const b = (this.bindingsByAsset.get(m.assetId) ?? []).find((x) => x.moduleId === m.moduleId);
    if (!b) fail("x/compliance", "ERROR_CODE_BINDING_NOT_FOUND", `${m.moduleId} is not bound`);
    const mod = this.moduleVersion(m.moduleId, m.toVersion);
    if (mod.status !== C.ModuleStatus.MODULE_STATUS_ACTIVE) fail("x/compliance", "ERROR_CODE_MODULE_DEPRECATED", "target version is not active");
    const params = m.paramsJson || b.paramsJson;
    this.parseParams(m.moduleId, params);
    const from = b.version;
    b.version = m.toVersion;
    b.paramsJson = params;
    this.emit("qorechain.compliance.v1.EventBindingMigrated", C.EventBindingMigrated.fromPartial({
      assetId: m.assetId, moduleId: m.moduleId, fromVersion: from, toVersion: m.toVersion,
    }));
    return {};
  }

  private queryModules(q: C.QueryModulesRequest): C.QueryModulesResponse {
    const modules = [...this.registry.values()]
      .filter((x) => !q.moduleId || x.moduleId === q.moduleId)
      .sort((a, b) => cmp(a.moduleId, b.moduleId) || a.version - b.version);
    return C.QueryModulesResponse.fromPartial({ modules });
  }

  private queryModule(q: C.QueryModuleRequest): C.QueryModuleResponse {
    return C.QueryModuleResponse.fromPartial({ module: this.moduleVersion(q.moduleId, q.version) });
  }

  private builtinLogic(moduleId: string): ModuleLogic | undefined {
    switch (moduleId) {
      case "identity-verified":
        return ({ chain, to, params }) => {
          const missing = chain.missingTopics(to, params.topics as number[]);
          return missing.length ? `${to} is not verified for topics ${missing.join(",")}` : undefined;
        };
      case "country-allowlist":
        return ({ chain, to, params }) => {
          const c = chain.countryOf(to);
          if (c === undefined) return `${to} has no identity`;
          return (params.countries as number[]).includes(c) ? undefined : `country ${c} is not allowed`;
        };
      case "country-blocklist":
        return ({ chain, to, params }) => {
          const c = chain.countryOf(to);
          return c !== undefined && (params.countries as number[]).includes(c) ? `country ${c} is blocked` : undefined;
        };
      case "max-holders":
        return ({ assetId, from, to, amount, params }) => {
          const r = this.assetsById.get(assetId)!;
          const count = [...r.holders.values()].filter((h) => h.balance > 0n).length;
          const joins = this.peekHolder(r, to).balance === 0n && amount > 0n ? 1 : 0;
          const leaves = from && from !== to && this.peekHolder(r, from).balance === amount ? 1 : 0;
          return count + joins - leaves > (params.max as number) ? `more than ${params.max} holders` : undefined;
        };
      case "max-balance":
        return ({ assetId, to, amount, params }) => {
          const r = this.assetsById.get(assetId)!;
          return this.peekHolder(r, to).balance + amount > BigInt(params.max as string) ? `balance of ${to} would exceed ${params.max}` : undefined;
        };
      case "attestation-fresh":
        return ({ chain, assetId, params }) => {
          const kind = T.attestationKindFromJSON(params.kind);
          const f = chain.freshness(assetId, kind).freshness;
          return f === T.Freshness.FRESHNESS_FRESH ? undefined : `latest ${params.kind} attestation is ${T.freshnessToJSON(f)}`;
        };
      default:
        return undefined;
    }
  }

  private runCompliance(assetId: string, from: string, to: string, amount: bigint): { moduleId: string; version: number; reason: string } | undefined {
    for (const b of this.bindingsOf(assetId)) {
      const mod = this.registry.get(`${b.moduleId}@${b.version}`);
      if (!mod || mod.status === C.ModuleStatus.MODULE_STATUS_DISABLED) {
        return { moduleId: b.moduleId, version: b.version, reason: "module version is disabled" };
      }
      const logic = this.customLogic.get(b.moduleId) ?? this.builtinLogic(b.moduleId);
      if (!logic) return { moduleId: b.moduleId, version: b.version, reason: "no logic for this module in MockChain" };
      const reason = logic({ chain: this, assetId, from, to, amount, params: JSON.parse(b.paramsJson) });
      if (reason !== undefined) return { moduleId: b.moduleId, version: b.version, reason };
    }
    return undefined;
  }

  private queryCheck(q: C.QueryCheckRequest): C.QueryCheckResponse {
    const amount = INTEGER.test(q.amount) ? BigInt(q.amount) : 0n;
    const c = this.runCompliance(q.assetId, q.from, q.to, amount);
    return C.QueryCheckResponse.fromPartial(c ? { allowed: false, moduleId: c.moduleId, version: c.version, reason: c.reason } : { allowed: true });
  }

  // ----------------------------------------------------------- x/settlement

  private createVenue(m: S.MsgCreateVenue): S.MsgCreateVenueResponse {
    if (this.venues.has(m.venueId)) fail("x/settlement", "ERROR_CODE_VENUE_EXISTS", `venue ${m.venueId} exists`);
    this.venues.set(m.venueId, S.Venue.fromPartial({
      venueId: m.venueId, operator: m.operator, description: m.description, allowedCreators: m.allowedCreators,
    }));
    this.emit("qorechain.settlement.v1.EventVenueCreated", S.EventVenueCreated.fromPartial({ venueId: m.venueId, operator: m.operator }));
    return {};
  }

  private createInstruction(m: S.MsgCreateInstruction): S.MsgCreateInstructionResponse {
    if (m.legs.length === 0) fail("x/settlement", "ERROR_CODE_INVALID_LEG", "an instruction needs at least one leg");
    if (m.legs.length > this.settlementParams.maxLegs) fail("x/settlement", "ERROR_CODE_TOO_MANY_LEGS", "too many legs");
    for (const [i, leg] of m.legs.entries()) {
      if (!leg.from || !leg.to || leg.from === leg.to || !leg.denom || !INTEGER.test(leg.amount) || BigInt(leg.amount) === 0n) {
        fail("x/settlement", "ERROR_CODE_INVALID_LEG", `leg ${i} is invalid`);
      }
    }
    if (m.venueId) {
      const v = this.venues.get(m.venueId);
      if (!v) fail("x/settlement", "ERROR_CODE_VENUE_NOT_FOUND", `venue ${m.venueId} not found`);
      if (v.allowedCreators.length > 0 && !v.allowedCreators.includes(m.creator)) {
        fail("x/settlement", "ERROR_CODE_NOT_ALLOWED_IN_VENUE", `${m.creator} may not create instructions in ${m.venueId}`);
      }
    }
    const deadline = Number(m.deadline);
    if (deadline <= this._time) fail("x/settlement", "ERROR_CODE_DEADLINE_PASSED", "deadline is not in the future");
    if (deadline - this._time > Number(this.settlementParams.maxDeadlineSeconds)) {
      fail("x/settlement", "ERROR_CODE_DEADLINE_TOO_FAR", "deadline is too far in the future");
    }
    const type = m.settlementType === S.SettlementType.SETTLEMENT_TYPE_UNSPECIFIED ? S.SettlementType.SETTLEMENT_TYPE_ON_AFFIRMATION : m.settlementType;
    if (type === S.SettlementType.SETTLEMENT_TYPE_ON_BLOCK && Number(m.settleHeight) <= this._height) {
      fail("x/settlement", "ERROR_CODE_INVALID_STATUS", "settle_height must be in the future");
    }
    const parties: string[] = [];
    for (const leg of m.legs) for (const a of [leg.from, leg.to]) if (!parties.includes(a)) parties.push(a);
    const id = String(this.nextInstructionId++);
    const ins = S.Instruction.fromPartial({
      id,
      creator: m.creator,
      venueId: m.venueId,
      legs: m.legs,
      settlementType: type,
      settleHeight: m.settleHeight,
      deadline: m.deadline,
      status: S.InstructionStatus.INSTRUCTION_STATUS_PENDING,
      affirmations: parties.map((p) => ({ party: p, affirmed: p === m.creator, height: p === m.creator ? String(this._height) : "0" })),
      memo: m.memo,
    });
    this.instructions.set(id, ins);
    this.emit("qorechain.settlement.v1.EventInstructionCreated", S.EventInstructionCreated.fromPartial({
      id, creator: m.creator, venueId: m.venueId, legs: m.legs, settlementType: type, deadline: m.deadline,
    }));
    if (parties.includes(m.creator)) {
      this.emit("qorechain.settlement.v1.EventAffirmed", S.EventAffirmed.fromPartial({ id, party: m.creator }));
    }
    return { id };
  }

  private ins(id: string): S.Instruction {
    const x = this.instructions.get(id);
    if (!x) fail("x/settlement", "ERROR_CODE_INSTRUCTION_NOT_FOUND", `instruction ${id} not found`);
    return x;
  }

  private affirm(m: S.MsgAffirm): S.MsgAffirmResponse {
    const ins = this.ins(m.id);
    const a = ins.affirmations.find((x) => x.party === m.party);
    if (!a) fail("x/settlement", "ERROR_CODE_NOT_A_PARTY", `${m.party} is not a party`);
    if (ins.status !== S.InstructionStatus.INSTRUCTION_STATUS_PENDING) {
      fail("x/settlement", "ERROR_CODE_INVALID_STATUS", `instruction is ${S.instructionStatusToJSON(ins.status)}`);
    }
    if (this._time > Number(ins.deadline)) fail("x/settlement", "ERROR_CODE_DEADLINE_PASSED", "deadline passed");
    if (!a.affirmed) {
      a.affirmed = true;
      a.height = String(this._height);
      this.emit("qorechain.settlement.v1.EventAffirmed", S.EventAffirmed.fromPartial({ id: ins.id, party: m.party }));
    }
    if (ins.affirmations.every((x) => x.affirmed)) {
      ins.status = S.InstructionStatus.INSTRUCTION_STATUS_AFFIRMED;
      if (ins.settlementType === S.SettlementType.SETTLEMENT_TYPE_ON_AFFIRMATION) this.execute(ins);
    }
    return { executed: (ins.status as S.InstructionStatus) === S.InstructionStatus.INSTRUCTION_STATUS_EXECUTED };
  }

  private withdrawAffirmation(m: S.MsgWithdrawAffirmation): S.MsgWithdrawAffirmationResponse {
    const ins = this.ins(m.id);
    const a = ins.affirmations.find((x) => x.party === m.party);
    if (!a) fail("x/settlement", "ERROR_CODE_NOT_A_PARTY", `${m.party} is not a party`);
    if (FINAL.has(ins.status)) fail("x/settlement", "ERROR_CODE_INVALID_STATUS", `instruction is ${S.instructionStatusToJSON(ins.status)}`);
    a.affirmed = false;
    a.height = "0";
    ins.status = S.InstructionStatus.INSTRUCTION_STATUS_PENDING;
    this.emit("qorechain.settlement.v1.EventAffirmationWithdrawn", S.EventAffirmationWithdrawn.fromPartial({ id: ins.id, party: m.party }));
    return {};
  }

  private executeInstruction(m: S.MsgExecuteInstruction): S.MsgExecuteInstructionResponse {
    const ins = this.ins(m.id);
    const operator = ins.venueId ? this.venues.get(ins.venueId)?.operator : undefined;
    if (!ins.affirmations.some((x) => x.party === m.signer) && operator !== m.signer) {
      fail("x/settlement", "ERROR_CODE_NOT_A_PARTY", `${m.signer} is not a party or the venue operator`);
    }
    if (!ins.affirmations.every((x) => x.affirmed)) fail("x/settlement", "ERROR_CODE_NOT_FULLY_AFFIRMED", "not every party affirmed");
    const retry = ins.status === S.InstructionStatus.INSTRUCTION_STATUS_FAILED;
    const manual = ins.status === S.InstructionStatus.INSTRUCTION_STATUS_AFFIRMED &&
      ins.settlementType === S.SettlementType.SETTLEMENT_TYPE_MANUAL;
    if (!retry && !manual) fail("x/settlement", "ERROR_CODE_INVALID_STATUS", `instruction is ${S.instructionStatusToJSON(ins.status)}`);
    if (this._time > Number(ins.deadline)) fail("x/settlement", "ERROR_CODE_DEADLINE_PASSED", "deadline passed");
    this.execute(ins);
    return { status: ins.status };
  }

  private cancelInstruction(m: S.MsgCancelInstruction): S.MsgCancelInstructionResponse {
    const ins = this.ins(m.id);
    const operator = ins.venueId ? this.venues.get(ins.venueId)?.operator : undefined;
    if (m.signer !== ins.creator && operator !== m.signer && !ins.affirmations.some((x) => x.party === m.signer)) {
      fail("x/settlement", "ERROR_CODE_NOT_A_PARTY", `${m.signer} may not cancel`);
    }
    if (FINAL.has(ins.status)) fail("x/settlement", "ERROR_CODE_INVALID_STATUS", `instruction is ${S.instructionStatusToJSON(ins.status)}`);
    ins.status = S.InstructionStatus.INSTRUCTION_STATUS_CANCELLED;
    this.emit("qorechain.settlement.v1.EventInstructionCancelled", S.EventInstructionCancelled.fromPartial({ id: ins.id, signer: m.signer }));
    return {};
  }

  /** Saves balances and the event log; the returned function restores them. */
  private snapshot(): () => void {
    const holders = new Map([...this.assetsById].map(([id, r]) => [id, new Map([...r.holders].map(([a, h]) => [a, { ...h }]))]));
    const bank = new Map([...this.bank].map(([a, m]) => [a, new Map(m)]));
    const events = this.log.length;
    return () => {
      for (const [id, r] of this.assetsById) r.holders = holders.get(id) ?? new Map();
      this.bank = bank;
      this.log.length = events;
    };
  }

  /** Applies every leg, or none. Leaves the instruction EXECUTED or FAILED. */
  private execute(ins: S.Instruction): void {
    const restore = this.snapshot();
    for (const [i, leg] of ins.legs.entries()) {
      const reason = this.applyLeg(leg);
      if (reason !== undefined) {
        restore();
        ins.status = S.InstructionStatus.INSTRUCTION_STATUS_FAILED;
        ins.failureReason = `leg ${i}: ${reason}`;
        this.emit("qorechain.settlement.v1.EventInstructionFailed", S.EventInstructionFailed.fromPartial({
          id: ins.id, legIndex: i, reason,
        }));
        return;
      }
    }
    ins.status = S.InstructionStatus.INSTRUCTION_STATUS_EXECUTED;
    ins.failureReason = "";
    this.emit("qorechain.settlement.v1.EventInstructionExecuted", S.EventInstructionExecuted.fromPartial({ id: ins.id }));
  }

  private applyLeg(leg: S.Leg): string | undefined {
    const amount = BigInt(leg.amount);
    if (leg.denom.startsWith("asset/")) {
      const assetId = leg.denom.slice("asset/".length);
      const r = this.assetsById.get(assetId);
      if (!r) return "ERROR_CODE_ASSET_NOT_FOUND";
      const refusal = this.transferRefusal(r, leg.from, leg.to, amount);
      if (refusal) return refusal.moduleId ? `${refusal.code} (${refusal.moduleId})` : refusal.code;
      this.move(r, leg.from, leg.to, amount);
      this.emit("qorechain.asset.v1.EventTransferred", A.EventTransferred.fromPartial({
        assetId, from: leg.from, to: leg.to, amount: leg.amount,
      }));
      return undefined;
    }
    const bal = BigInt(this.bankBalance(leg.from, leg.denom));
    if (bal < amount) return `insufficient ${leg.denom} balance`;
    this.bank.get(leg.from)!.set(leg.denom, bal - amount);
    this.fundBank(leg.to, leg.denom, amount);
    return undefined;
  }

  private queryInstruction(q: S.QueryInstructionRequest): S.QueryInstructionResponse {
    return S.QueryInstructionResponse.fromPartial({ instruction: this.ins(q.id) });
  }

  private queryInstructionsByParty(q: S.QueryInstructionsByPartyRequest): S.QueryInstructionsByPartyResponse {
    const instructions = [...this.instructions.values()]
      .filter((x) => x.affirmations.some((a) => a.party === q.party))
      .filter((x) => q.status === S.InstructionStatus.INSTRUCTION_STATUS_UNSPECIFIED || x.status === q.status)
      .sort((a, b) => Number(a.id) - Number(b.id));
    return S.QueryInstructionsByPartyResponse.fromPartial({ instructions });
  }

  private queryVenue(q: S.QueryVenueRequest): S.QueryVenueResponse {
    const v = this.venues.get(q.venueId);
    if (!v) fail("x/settlement", "ERROR_CODE_VENUE_NOT_FOUND", `venue ${q.venueId} not found`);
    return S.QueryVenueResponse.fromPartial({ venue: v });
  }

  // --------------------------------------------------------------- x/attest

  private setAttester(m: T.MsgSetAttester): T.MsgSetAttesterResponse {
    const at = T.Attester.fromPartial(m.attester ?? {});
    const r = this.assetsById.get(at.assetId);
    if (!r || r.asset.issuer !== m.issuer) fail("x/attest", "ERROR_CODE_NOT_ISSUER", `${m.issuer} is not the issuer of ${at.assetId}`);
    const map = this.attestersByAsset.get(at.assetId) ?? new Map<string, T.Attester>();
    if (m.remove) map.delete(at.address);
    else map.set(at.address, at);
    this.attestersByAsset.set(at.assetId, map);
    this.emit("qorechain.attest.v1.EventAttesterChanged", T.EventAttesterChanged.fromPartial({
      assetId: at.assetId, address: at.address, kinds: at.kinds, removed: m.remove,
    }));
    return {};
  }

  private latestOf(assetId: string, kind: T.AttestationKind): T.Attestation | undefined {
    return this.attestations
      .filter((a) => a.assetId === assetId && a.kind === kind && !a.revoked)
      .sort((a, b) => Number(b.observedAt) - Number(a.observedAt) || Number(b.id) - Number(a.id))[0];
  }

  private submitAttestation(m: T.MsgSubmit): T.MsgSubmitResponse {
    const at = this.attestersByAsset.get(m.assetId)?.get(m.attester);
    if (!at) fail("x/attest", "ERROR_CODE_NOT_AN_ATTESTER", `${m.attester} is not an attester of ${m.assetId}`);
    if (!at.kinds.includes(m.kind)) fail("x/attest", "ERROR_CODE_KIND_NOT_ALLOWED", `${T.attestationKindToJSON(m.kind)} not allowed`);
    if (m.kind === T.AttestationKind.ATTESTATION_KIND_AUDIT_REPORT) {
      const r = this.assetsById.get(m.assetId);
      if (!r || !this.hasRole(r, m.attester, A.Role.ROLE_AUDITOR)) {
        fail("x/attest", "ERROR_CODE_KIND_NOT_ALLOWED", "AUDIT_REPORT requires the auditor role");
      }
    }
    const observed = Number(m.observedAt);
    const validFor = Number(m.validForSeconds);
    if (observed > this._time) fail("x/attest", "ERROR_CODE_OBSERVATION_IN_FUTURE", "observed_at is in the future");
    if (this._time - observed > Number(this.attestParams.maxObservationLagSeconds)) {
      fail("x/attest", "ERROR_CODE_OBSERVATION_TOO_OLD", "observed_at is too old");
    }
    if (validFor <= 0 || validFor > Number(this.attestParams.maxValiditySeconds)) {
      fail("x/attest", "ERROR_CODE_VALIDITY_TOO_LONG", "valid_for_seconds is out of range");
    }
    const latest = this.latestOf(m.assetId, m.kind);
    if (latest && observed < Number(latest.observedAt)) fail("x/attest", "ERROR_CODE_OLDER_THAN_LATEST", "older than the latest attestation");
    const id = String(this.nextAttestationId++);
    this.attestations.push(T.Attestation.fromPartial({
      id, assetId: m.assetId, kind: m.kind, attester: m.attester, value: m.value, unit: m.unit,
      reportHash: m.reportHash, reportUri: m.reportUri, observedAt: m.observedAt, validForSeconds: m.validForSeconds,
      acceptedAt: String(this._time), revoked: false,
    }));
    this.emit("qorechain.attest.v1.EventAttestationSubmitted", T.EventAttestationSubmitted.fromPartial({
      id, assetId: m.assetId, kind: m.kind, attester: m.attester, value: m.value,
      observedAt: m.observedAt, validForSeconds: m.validForSeconds,
    }));
    return { id };
  }

  private revokeAttestation(m: T.MsgRevoke): T.MsgRevokeResponse {
    const a = this.attestations.find((x) => x.id === m.id);
    if (!a) fail("x/attest", "ERROR_CODE_ATTESTATION_NOT_FOUND", `attestation ${m.id} not found`);
    if (m.signer !== a.attester && this.assetsById.get(a.assetId)?.asset.issuer !== m.signer) {
      fail("x/attest", "ERROR_CODE_NOT_AN_ATTESTER", `${m.signer} may not revoke`);
    }
    a.revoked = true;
    this.emit("qorechain.attest.v1.EventAttestationRevoked", T.EventAttestationRevoked.fromPartial({
      id: m.id, signer: m.signer, reason: m.reason,
    }));
    return {};
  }

  /** Freshness of the latest attestation of a kind, at the current block time. */
  freshness(assetId: string, kind: T.AttestationKind): T.QueryLatestResponse {
    const a = this.latestOf(assetId, kind);
    if (!a) return T.QueryLatestResponse.fromPartial({ freshness: T.Freshness.FRESHNESS_MISSING });
    const staleAt = Number(a.observedAt) + Number(a.validForSeconds);
    return T.QueryLatestResponse.fromPartial({
      attestation: a,
      freshness: this._time < staleAt ? T.Freshness.FRESHNESS_FRESH : T.Freshness.FRESHNESS_STALE,
      staleAt: String(staleAt),
    });
  }

  private queryLatest(q: T.QueryLatestRequest): T.QueryLatestResponse {
    return this.freshness(q.assetId, q.kind);
  }

  private queryHistory(q: T.QueryHistoryRequest): T.QueryHistoryResponse {
    const all = this.attestations
      .filter((a) => a.assetId === q.assetId && a.kind === q.kind)
      .sort((a, b) => Number(b.observedAt) - Number(a.observedAt) || Number(b.id) - Number(a.id));
    return T.QueryHistoryResponse.fromPartial({ attestations: q.limit > 0 ? all.slice(0, q.limit) : all });
  }
}

function cmp(a: string, b: string): number {
  return a < b ? -1 : a > b ? 1 : 0;
}


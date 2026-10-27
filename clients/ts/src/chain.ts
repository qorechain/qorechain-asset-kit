// SPDX-License-Identifier: Apache-2.0

import type { AssetApi, AssetKit, AttestApi, ComplianceApi, IdentityApi, SettlementApi } from "./api.js";
import { ChainUpgradeRequired, type ModuleName } from "./errors.js";

const ASSET_METHODS = [
  "createAsset", "updateFlags", "setRole", "proposeIssuer", "acceptIssuer", "authorizeHolder", "mint", "burn",
  "transfer", "freeze", "freezePartial", "pause", "clawback", "forceTransfer", "setTerms", "retire",
  "params", "asset", "assets", "holder", "holders", "roles", "canTransfer",
] as const satisfies readonly (keyof AssetApi)[];

const IDENTITY_METHODS = [
  "registerIdentity", "updateCountry", "bindAddress", "unbindAddress", "addClaim", "revokeClaim", "removeIdentity",
  "setClaimIssuer", "params", "identity", "identityByAddress", "claimIssuers", "isVerified",
] as const satisfies readonly (keyof IdentityApi)[];

const COMPLIANCE_METHODS = [
  "registerModule", "setModuleStatus", "bindModule", "unbindModule", "migrateBinding",
  "params", "modules", "module", "bindings", "check",
] as const satisfies readonly (keyof ComplianceApi)[];

const SETTLEMENT_METHODS = [
  "createVenue", "createInstruction", "affirm", "withdrawAffirmation", "executeInstruction", "cancelInstruction",
  "params", "instruction", "instructionsByParty", "venue",
] as const satisfies readonly (keyof SettlementApi)[];

const ATTEST_METHODS = [
  "setAttester", "submit", "revoke", "params", "latest", "history", "attesters",
] as const satisfies readonly (keyof AttestApi)[];

function unavailable<T>(module: ModuleName, methods: readonly string[]): T {
  const api: Record<string, () => Promise<never>> = {};
  for (const m of methods) {
    api[m] = () => Promise.reject(new ChainUpgradeRequired(module));
  }
  return Object.freeze(api) as T;
}

/** Options kept for the day the modules exist; nothing is contacted today. */
export interface ChainClientOptions {
  /** REST endpoint, for example https://api-testnet.qore.host. */
  restUrl?: string;
  chainId?: string;
}

/**
 * The client for the real chain. The modules are a proposal, so every call
 * rejects with {@link ChainUpgradeRequired} without any network request.
 */
export class ChainClient implements AssetKit {
  readonly asset = unavailable<AssetApi>("x/asset", ASSET_METHODS);
  readonly identity = unavailable<IdentityApi>("x/identity", IDENTITY_METHODS);
  readonly compliance = unavailable<ComplianceApi>("x/compliance", COMPLIANCE_METHODS);
  readonly settlement = unavailable<SettlementApi>("x/settlement", SETTLEMENT_METHODS);
  readonly attest = unavailable<AttestApi>("x/attest", ATTEST_METHODS);

  constructor(readonly options: ChainClientOptions = {}) {}
}

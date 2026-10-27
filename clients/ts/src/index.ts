// SPDX-License-Identifier: Apache-2.0
//
// @qorechain/asset-kit: client for the PROPOSED QoreChain regulated-asset
// modules (x/asset, x/identity, x/compliance, x/settlement, x/attest).
// None of these modules exists on QoreChain and no upgrade adding them is
// scheduled. ChainClient therefore rejects every call with
// ChainUpgradeRequired; MockChain implements the proposed rules in memory.

export const VERSION = "0.1.0";

export type { AssetKit, AssetApi, IdentityApi, ComplianceApi, SettlementApi, AttestApi, In } from "./api.js";
export { ChainClient, type ChainClientOptions } from "./chain.js";
export { MockChain, type MockChainOptions, type MockEvent, type ModuleContext, type ModuleLogic } from "./mock.js";
export { AssetKitError, ChainUpgradeRequired, MockChainError, type ModuleName } from "./errors.js";

/** Generated types and codecs, one namespace per proposed module. */
export * as asset from "./gen/asset.js";
export * as identity from "./gen/identity.js";
export * as compliance from "./gen/compliance.js";
export * as settlement from "./gen/settlement.js";
export * as attest from "./gen/attest.js";

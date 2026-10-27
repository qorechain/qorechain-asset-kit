// SPDX-License-Identifier: Apache-2.0
//
// The facade over the proposed modules. ChainClient and MockChain both
// implement AssetKit; an application written against AssetKit runs on the
// mock today and would run on the chain if the modules were ever added.

import type * as asset from "./gen/asset.js";
import type * as identity from "./gen/identity.js";
import type * as compliance from "./gen/compliance.js";
import type * as settlement from "./gen/settlement.js";
import type * as attest from "./gen/attest.js";

/** Every field optional, recursively; missing fields take proto defaults. */
export type In<T> = T extends Uint8Array | string | number | boolean | undefined
  ? T
  : T extends Array<infer U>
    ? Array<In<U>>
    : T extends object
      ? { [K in keyof T]?: In<T[K]> }
      : T;

export interface AssetApi {
  createAsset(msg: In<asset.MsgCreateAsset>): Promise<asset.MsgCreateAssetResponse>;
  updateFlags(msg: In<asset.MsgUpdateFlags>): Promise<asset.MsgUpdateFlagsResponse>;
  setRole(msg: In<asset.MsgSetRole>): Promise<asset.MsgSetRoleResponse>;
  proposeIssuer(msg: In<asset.MsgProposeIssuer>): Promise<asset.MsgProposeIssuerResponse>;
  acceptIssuer(msg: In<asset.MsgAcceptIssuer>): Promise<asset.MsgAcceptIssuerResponse>;
  authorizeHolder(msg: In<asset.MsgAuthorizeHolder>): Promise<asset.MsgAuthorizeHolderResponse>;
  mint(msg: In<asset.MsgMint>): Promise<asset.MsgMintResponse>;
  burn(msg: In<asset.MsgBurn>): Promise<asset.MsgBurnResponse>;
  transfer(msg: In<asset.MsgTransfer>): Promise<asset.MsgTransferResponse>;
  freeze(msg: In<asset.MsgFreeze>): Promise<asset.MsgFreezeResponse>;
  freezePartial(msg: In<asset.MsgFreezePartial>): Promise<asset.MsgFreezePartialResponse>;
  pause(msg: In<asset.MsgPause>): Promise<asset.MsgPauseResponse>;
  clawback(msg: In<asset.MsgClawback>): Promise<asset.MsgClawbackResponse>;
  forceTransfer(msg: In<asset.MsgForceTransfer>): Promise<asset.MsgForceTransferResponse>;
  setTerms(msg: In<asset.MsgSetTerms>): Promise<asset.MsgSetTermsResponse>;
  retire(msg: In<asset.MsgRetire>): Promise<asset.MsgRetireResponse>;

  params(req?: In<asset.QueryParamsRequest>): Promise<asset.QueryParamsResponse>;
  asset(req: In<asset.QueryAssetRequest>): Promise<asset.QueryAssetResponse>;
  assets(req?: In<asset.QueryAssetsRequest>): Promise<asset.QueryAssetsResponse>;
  holder(req: In<asset.QueryHolderRequest>): Promise<asset.QueryHolderResponse>;
  holders(req: In<asset.QueryHoldersRequest>): Promise<asset.QueryHoldersResponse>;
  roles(req: In<asset.QueryRolesRequest>): Promise<asset.QueryRolesResponse>;
  canTransfer(req: In<asset.QueryCanTransferRequest>): Promise<asset.QueryCanTransferResponse>;
}

export interface IdentityApi {
  registerIdentity(msg: In<identity.MsgRegisterIdentity>): Promise<identity.MsgRegisterIdentityResponse>;
  updateCountry(msg: In<identity.MsgUpdateCountry>): Promise<identity.MsgUpdateCountryResponse>;
  bindAddress(msg: In<identity.MsgBindAddress>): Promise<identity.MsgBindAddressResponse>;
  unbindAddress(msg: In<identity.MsgUnbindAddress>): Promise<identity.MsgUnbindAddressResponse>;
  addClaim(msg: In<identity.MsgAddClaim>): Promise<identity.MsgAddClaimResponse>;
  revokeClaim(msg: In<identity.MsgRevokeClaim>): Promise<identity.MsgRevokeClaimResponse>;
  removeIdentity(msg: In<identity.MsgRemoveIdentity>): Promise<identity.MsgRemoveIdentityResponse>;
  setClaimIssuer(msg: In<identity.MsgSetClaimIssuer>): Promise<identity.MsgSetClaimIssuerResponse>;

  params(req?: In<identity.QueryParamsRequest>): Promise<identity.QueryParamsResponse>;
  identity(req: In<identity.QueryIdentityRequest>): Promise<identity.QueryIdentityResponse>;
  identityByAddress(req: In<identity.QueryIdentityByAddressRequest>): Promise<identity.QueryIdentityByAddressResponse>;
  claimIssuers(req?: In<identity.QueryClaimIssuersRequest>): Promise<identity.QueryClaimIssuersResponse>;
  isVerified(req: In<identity.QueryIsVerifiedRequest>): Promise<identity.QueryIsVerifiedResponse>;
}

export interface ComplianceApi {
  registerModule(msg: In<compliance.MsgRegisterModule>): Promise<compliance.MsgRegisterModuleResponse>;
  setModuleStatus(msg: In<compliance.MsgSetModuleStatus>): Promise<compliance.MsgSetModuleStatusResponse>;
  bindModule(msg: In<compliance.MsgBindModule>): Promise<compliance.MsgBindModuleResponse>;
  unbindModule(msg: In<compliance.MsgUnbindModule>): Promise<compliance.MsgUnbindModuleResponse>;
  migrateBinding(msg: In<compliance.MsgMigrateBinding>): Promise<compliance.MsgMigrateBindingResponse>;

  params(req?: In<compliance.QueryParamsRequest>): Promise<compliance.QueryParamsResponse>;
  modules(req?: In<compliance.QueryModulesRequest>): Promise<compliance.QueryModulesResponse>;
  module(req: In<compliance.QueryModuleRequest>): Promise<compliance.QueryModuleResponse>;
  bindings(req: In<compliance.QueryBindingsRequest>): Promise<compliance.QueryBindingsResponse>;
  check(req: In<compliance.QueryCheckRequest>): Promise<compliance.QueryCheckResponse>;
}

export interface SettlementApi {
  createVenue(msg: In<settlement.MsgCreateVenue>): Promise<settlement.MsgCreateVenueResponse>;
  createInstruction(msg: In<settlement.MsgCreateInstruction>): Promise<settlement.MsgCreateInstructionResponse>;
  affirm(msg: In<settlement.MsgAffirm>): Promise<settlement.MsgAffirmResponse>;
  withdrawAffirmation(msg: In<settlement.MsgWithdrawAffirmation>): Promise<settlement.MsgWithdrawAffirmationResponse>;
  executeInstruction(msg: In<settlement.MsgExecuteInstruction>): Promise<settlement.MsgExecuteInstructionResponse>;
  cancelInstruction(msg: In<settlement.MsgCancelInstruction>): Promise<settlement.MsgCancelInstructionResponse>;

  params(req?: In<settlement.QueryParamsRequest>): Promise<settlement.QueryParamsResponse>;
  instruction(req: In<settlement.QueryInstructionRequest>): Promise<settlement.QueryInstructionResponse>;
  instructionsByParty(req: In<settlement.QueryInstructionsByPartyRequest>): Promise<settlement.QueryInstructionsByPartyResponse>;
  venue(req: In<settlement.QueryVenueRequest>): Promise<settlement.QueryVenueResponse>;
}

export interface AttestApi {
  setAttester(msg: In<attest.MsgSetAttester>): Promise<attest.MsgSetAttesterResponse>;
  submit(msg: In<attest.MsgSubmit>): Promise<attest.MsgSubmitResponse>;
  revoke(msg: In<attest.MsgRevoke>): Promise<attest.MsgRevokeResponse>;

  params(req?: In<attest.QueryParamsRequest>): Promise<attest.QueryParamsResponse>;
  latest(req: In<attest.QueryLatestRequest>): Promise<attest.QueryLatestResponse>;
  history(req: In<attest.QueryHistoryRequest>): Promise<attest.QueryHistoryResponse>;
  attesters(req: In<attest.QueryAttestersRequest>): Promise<attest.QueryAttestersResponse>;
}

/** The facade over the five proposed modules. */
export interface AssetKit {
  readonly asset: AssetApi;
  readonly identity: IdentityApi;
  readonly compliance: ComplianceApi;
  readonly settlement: SettlementApi;
  readonly attest: AttestApi;
}

// SPDX-License-Identifier: Apache-2.0

// Package assetkit is the Go client for the PROPOSED QoreChain regulated-asset
// modules (x/asset, x/identity, x/compliance, x/settlement, x/attest).
//
// None of these modules exists on QoreChain and no upgrade adding them is
// scheduled. The client returned by NewChainClient therefore answers every call
// with *ChainUpgradeRequired; MockChain implements the proposed rules in memory
// (see docs/proposal.md) for building and testing applications.
package assetkit

import (
	"context"

	assetv1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/asset/v1"
	attestv1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/attest/v1"
	compliancev1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/compliance/v1"
	identityv1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/identity/v1"
	settlementv1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/settlement/v1"
)

// Version of this package.
const Version = "0.1.0"

// AssetAPI is the facade over x/asset.
type AssetAPI interface {
	CreateAsset(context.Context, *assetv1.MsgCreateAsset) (*assetv1.MsgCreateAssetResponse, error)
	UpdateFlags(context.Context, *assetv1.MsgUpdateFlags) (*assetv1.MsgUpdateFlagsResponse, error)
	SetRole(context.Context, *assetv1.MsgSetRole) (*assetv1.MsgSetRoleResponse, error)
	ProposeIssuer(context.Context, *assetv1.MsgProposeIssuer) (*assetv1.MsgProposeIssuerResponse, error)
	AcceptIssuer(context.Context, *assetv1.MsgAcceptIssuer) (*assetv1.MsgAcceptIssuerResponse, error)
	AuthorizeHolder(context.Context, *assetv1.MsgAuthorizeHolder) (*assetv1.MsgAuthorizeHolderResponse, error)
	Mint(context.Context, *assetv1.MsgMint) (*assetv1.MsgMintResponse, error)
	Burn(context.Context, *assetv1.MsgBurn) (*assetv1.MsgBurnResponse, error)
	Transfer(context.Context, *assetv1.MsgTransfer) (*assetv1.MsgTransferResponse, error)
	Freeze(context.Context, *assetv1.MsgFreeze) (*assetv1.MsgFreezeResponse, error)
	FreezePartial(context.Context, *assetv1.MsgFreezePartial) (*assetv1.MsgFreezePartialResponse, error)
	Pause(context.Context, *assetv1.MsgPause) (*assetv1.MsgPauseResponse, error)
	Clawback(context.Context, *assetv1.MsgClawback) (*assetv1.MsgClawbackResponse, error)
	ForceTransfer(context.Context, *assetv1.MsgForceTransfer) (*assetv1.MsgForceTransferResponse, error)
	SetTerms(context.Context, *assetv1.MsgSetTerms) (*assetv1.MsgSetTermsResponse, error)
	Retire(context.Context, *assetv1.MsgRetire) (*assetv1.MsgRetireResponse, error)

	Params(context.Context, *assetv1.QueryParamsRequest) (*assetv1.QueryParamsResponse, error)
	Asset(context.Context, *assetv1.QueryAssetRequest) (*assetv1.QueryAssetResponse, error)
	Assets(context.Context, *assetv1.QueryAssetsRequest) (*assetv1.QueryAssetsResponse, error)
	Holder(context.Context, *assetv1.QueryHolderRequest) (*assetv1.QueryHolderResponse, error)
	Holders(context.Context, *assetv1.QueryHoldersRequest) (*assetv1.QueryHoldersResponse, error)
	Roles(context.Context, *assetv1.QueryRolesRequest) (*assetv1.QueryRolesResponse, error)
	CanTransfer(context.Context, *assetv1.QueryCanTransferRequest) (*assetv1.QueryCanTransferResponse, error)
}

// IdentityAPI is the facade over x/identity.
type IdentityAPI interface {
	RegisterIdentity(context.Context, *identityv1.MsgRegisterIdentity) (*identityv1.MsgRegisterIdentityResponse, error)
	UpdateCountry(context.Context, *identityv1.MsgUpdateCountry) (*identityv1.MsgUpdateCountryResponse, error)
	BindAddress(context.Context, *identityv1.MsgBindAddress) (*identityv1.MsgBindAddressResponse, error)
	UnbindAddress(context.Context, *identityv1.MsgUnbindAddress) (*identityv1.MsgUnbindAddressResponse, error)
	AddClaim(context.Context, *identityv1.MsgAddClaim) (*identityv1.MsgAddClaimResponse, error)
	RevokeClaim(context.Context, *identityv1.MsgRevokeClaim) (*identityv1.MsgRevokeClaimResponse, error)
	RemoveIdentity(context.Context, *identityv1.MsgRemoveIdentity) (*identityv1.MsgRemoveIdentityResponse, error)
	SetClaimIssuer(context.Context, *identityv1.MsgSetClaimIssuer) (*identityv1.MsgSetClaimIssuerResponse, error)

	Params(context.Context, *identityv1.QueryParamsRequest) (*identityv1.QueryParamsResponse, error)
	Identity(context.Context, *identityv1.QueryIdentityRequest) (*identityv1.QueryIdentityResponse, error)
	IdentityByAddress(context.Context, *identityv1.QueryIdentityByAddressRequest) (*identityv1.QueryIdentityByAddressResponse, error)
	ClaimIssuers(context.Context, *identityv1.QueryClaimIssuersRequest) (*identityv1.QueryClaimIssuersResponse, error)
	IsVerified(context.Context, *identityv1.QueryIsVerifiedRequest) (*identityv1.QueryIsVerifiedResponse, error)
}

// ComplianceAPI is the facade over x/compliance.
type ComplianceAPI interface {
	RegisterModule(context.Context, *compliancev1.MsgRegisterModule) (*compliancev1.MsgRegisterModuleResponse, error)
	SetModuleStatus(context.Context, *compliancev1.MsgSetModuleStatus) (*compliancev1.MsgSetModuleStatusResponse, error)
	BindModule(context.Context, *compliancev1.MsgBindModule) (*compliancev1.MsgBindModuleResponse, error)
	UnbindModule(context.Context, *compliancev1.MsgUnbindModule) (*compliancev1.MsgUnbindModuleResponse, error)
	MigrateBinding(context.Context, *compliancev1.MsgMigrateBinding) (*compliancev1.MsgMigrateBindingResponse, error)

	Params(context.Context, *compliancev1.QueryParamsRequest) (*compliancev1.QueryParamsResponse, error)
	Modules(context.Context, *compliancev1.QueryModulesRequest) (*compliancev1.QueryModulesResponse, error)
	Module(context.Context, *compliancev1.QueryModuleRequest) (*compliancev1.QueryModuleResponse, error)
	Bindings(context.Context, *compliancev1.QueryBindingsRequest) (*compliancev1.QueryBindingsResponse, error)
	Check(context.Context, *compliancev1.QueryCheckRequest) (*compliancev1.QueryCheckResponse, error)
}

// SettlementAPI is the facade over x/settlement.
type SettlementAPI interface {
	CreateVenue(context.Context, *settlementv1.MsgCreateVenue) (*settlementv1.MsgCreateVenueResponse, error)
	CreateInstruction(context.Context, *settlementv1.MsgCreateInstruction) (*settlementv1.MsgCreateInstructionResponse, error)
	Affirm(context.Context, *settlementv1.MsgAffirm) (*settlementv1.MsgAffirmResponse, error)
	WithdrawAffirmation(context.Context, *settlementv1.MsgWithdrawAffirmation) (*settlementv1.MsgWithdrawAffirmationResponse, error)
	ExecuteInstruction(context.Context, *settlementv1.MsgExecuteInstruction) (*settlementv1.MsgExecuteInstructionResponse, error)
	CancelInstruction(context.Context, *settlementv1.MsgCancelInstruction) (*settlementv1.MsgCancelInstructionResponse, error)

	Params(context.Context, *settlementv1.QueryParamsRequest) (*settlementv1.QueryParamsResponse, error)
	Instruction(context.Context, *settlementv1.QueryInstructionRequest) (*settlementv1.QueryInstructionResponse, error)
	InstructionsByParty(context.Context, *settlementv1.QueryInstructionsByPartyRequest) (*settlementv1.QueryInstructionsByPartyResponse, error)
	Venue(context.Context, *settlementv1.QueryVenueRequest) (*settlementv1.QueryVenueResponse, error)
}

// AttestAPI is the facade over x/attest.
type AttestAPI interface {
	SetAttester(context.Context, *attestv1.MsgSetAttester) (*attestv1.MsgSetAttesterResponse, error)
	Submit(context.Context, *attestv1.MsgSubmit) (*attestv1.MsgSubmitResponse, error)
	Revoke(context.Context, *attestv1.MsgRevoke) (*attestv1.MsgRevokeResponse, error)

	Params(context.Context, *attestv1.QueryParamsRequest) (*attestv1.QueryParamsResponse, error)
	Latest(context.Context, *attestv1.QueryLatestRequest) (*attestv1.QueryLatestResponse, error)
	History(context.Context, *attestv1.QueryHistoryRequest) (*attestv1.QueryHistoryResponse, error)
	Attesters(context.Context, *attestv1.QueryAttestersRequest) (*attestv1.QueryAttestersResponse, error)
}

// AssetKit is the facade over the five proposed modules. The chain client and
// MockChain both implement it.
type AssetKit interface {
	Asset() AssetAPI
	Identity() IdentityAPI
	Compliance() ComplianceAPI
	Settlement() SettlementAPI
	Attest() AttestAPI
}

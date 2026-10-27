// SPDX-License-Identifier: Apache-2.0

package assetkit

import (
	"context"

	assetv1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/asset/v1"
	attestv1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/attest/v1"
	compliancev1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/compliance/v1"
	identityv1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/identity/v1"
	settlementv1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/settlement/v1"
)

// ChainClientOptions are kept for the day the modules exist; nothing is
// contacted today.
type ChainClientOptions struct {
	// REST endpoint, for example https://api-testnet.qore.host.
	RESTURL string
	ChainID string
}

// ChainClient is the client for the real chain. The modules are a proposal, so
// every call returns *ChainUpgradeRequired without any network request.
type ChainClient struct {
	Options ChainClientOptions
}

// NewChainClient returns a ChainClient.
func NewChainClient(opts ...ChainClientOptions) *ChainClient {
	c := &ChainClient{}
	if len(opts) > 0 {
		c.Options = opts[0]
	}
	return c
}

var _ AssetKit = (*ChainClient)(nil)

// Asset returns the x/asset facade.
func (c *ChainClient) Asset() AssetAPI { return chainAsset{} }

// Identity returns the x/identity facade.
func (c *ChainClient) Identity() IdentityAPI { return chainIdentity{} }

// Compliance returns the x/compliance facade.
func (c *ChainClient) Compliance() ComplianceAPI { return chainCompliance{} }

// Settlement returns the x/settlement facade.
func (c *ChainClient) Settlement() SettlementAPI { return chainSettlement{} }

// Attest returns the x/attest facade.
func (c *ChainClient) Attest() AttestAPI { return chainAttest{} }

type chainAsset struct{}

func (chainAsset) CreateAsset(context.Context, *assetv1.MsgCreateAsset) (*assetv1.MsgCreateAssetResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleAsset}
}

func (chainAsset) UpdateFlags(context.Context, *assetv1.MsgUpdateFlags) (*assetv1.MsgUpdateFlagsResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleAsset}
}

func (chainAsset) SetRole(context.Context, *assetv1.MsgSetRole) (*assetv1.MsgSetRoleResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleAsset}
}

func (chainAsset) ProposeIssuer(context.Context, *assetv1.MsgProposeIssuer) (*assetv1.MsgProposeIssuerResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleAsset}
}

func (chainAsset) AcceptIssuer(context.Context, *assetv1.MsgAcceptIssuer) (*assetv1.MsgAcceptIssuerResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleAsset}
}

func (chainAsset) AuthorizeHolder(context.Context, *assetv1.MsgAuthorizeHolder) (*assetv1.MsgAuthorizeHolderResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleAsset}
}

func (chainAsset) Mint(context.Context, *assetv1.MsgMint) (*assetv1.MsgMintResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleAsset}
}

func (chainAsset) Burn(context.Context, *assetv1.MsgBurn) (*assetv1.MsgBurnResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleAsset}
}

func (chainAsset) Transfer(context.Context, *assetv1.MsgTransfer) (*assetv1.MsgTransferResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleAsset}
}

func (chainAsset) Freeze(context.Context, *assetv1.MsgFreeze) (*assetv1.MsgFreezeResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleAsset}
}

func (chainAsset) FreezePartial(context.Context, *assetv1.MsgFreezePartial) (*assetv1.MsgFreezePartialResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleAsset}
}

func (chainAsset) Pause(context.Context, *assetv1.MsgPause) (*assetv1.MsgPauseResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleAsset}
}

func (chainAsset) Clawback(context.Context, *assetv1.MsgClawback) (*assetv1.MsgClawbackResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleAsset}
}

func (chainAsset) ForceTransfer(context.Context, *assetv1.MsgForceTransfer) (*assetv1.MsgForceTransferResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleAsset}
}

func (chainAsset) SetTerms(context.Context, *assetv1.MsgSetTerms) (*assetv1.MsgSetTermsResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleAsset}
}

func (chainAsset) Retire(context.Context, *assetv1.MsgRetire) (*assetv1.MsgRetireResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleAsset}
}

func (chainAsset) Params(context.Context, *assetv1.QueryParamsRequest) (*assetv1.QueryParamsResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleAsset}
}

func (chainAsset) Asset(context.Context, *assetv1.QueryAssetRequest) (*assetv1.QueryAssetResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleAsset}
}

func (chainAsset) Assets(context.Context, *assetv1.QueryAssetsRequest) (*assetv1.QueryAssetsResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleAsset}
}

func (chainAsset) Holder(context.Context, *assetv1.QueryHolderRequest) (*assetv1.QueryHolderResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleAsset}
}

func (chainAsset) Holders(context.Context, *assetv1.QueryHoldersRequest) (*assetv1.QueryHoldersResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleAsset}
}

func (chainAsset) Roles(context.Context, *assetv1.QueryRolesRequest) (*assetv1.QueryRolesResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleAsset}
}

func (chainAsset) CanTransfer(context.Context, *assetv1.QueryCanTransferRequest) (*assetv1.QueryCanTransferResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleAsset}
}

type chainIdentity struct{}

func (chainIdentity) RegisterIdentity(context.Context, *identityv1.MsgRegisterIdentity) (*identityv1.MsgRegisterIdentityResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleIdentity}
}

func (chainIdentity) UpdateCountry(context.Context, *identityv1.MsgUpdateCountry) (*identityv1.MsgUpdateCountryResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleIdentity}
}

func (chainIdentity) BindAddress(context.Context, *identityv1.MsgBindAddress) (*identityv1.MsgBindAddressResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleIdentity}
}

func (chainIdentity) UnbindAddress(context.Context, *identityv1.MsgUnbindAddress) (*identityv1.MsgUnbindAddressResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleIdentity}
}

func (chainIdentity) AddClaim(context.Context, *identityv1.MsgAddClaim) (*identityv1.MsgAddClaimResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleIdentity}
}

func (chainIdentity) RevokeClaim(context.Context, *identityv1.MsgRevokeClaim) (*identityv1.MsgRevokeClaimResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleIdentity}
}

func (chainIdentity) RemoveIdentity(context.Context, *identityv1.MsgRemoveIdentity) (*identityv1.MsgRemoveIdentityResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleIdentity}
}

func (chainIdentity) SetClaimIssuer(context.Context, *identityv1.MsgSetClaimIssuer) (*identityv1.MsgSetClaimIssuerResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleIdentity}
}

func (chainIdentity) Params(context.Context, *identityv1.QueryParamsRequest) (*identityv1.QueryParamsResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleIdentity}
}

func (chainIdentity) Identity(context.Context, *identityv1.QueryIdentityRequest) (*identityv1.QueryIdentityResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleIdentity}
}

func (chainIdentity) IdentityByAddress(context.Context, *identityv1.QueryIdentityByAddressRequest) (*identityv1.QueryIdentityByAddressResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleIdentity}
}

func (chainIdentity) ClaimIssuers(context.Context, *identityv1.QueryClaimIssuersRequest) (*identityv1.QueryClaimIssuersResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleIdentity}
}

func (chainIdentity) IsVerified(context.Context, *identityv1.QueryIsVerifiedRequest) (*identityv1.QueryIsVerifiedResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleIdentity}
}

type chainCompliance struct{}

func (chainCompliance) RegisterModule(context.Context, *compliancev1.MsgRegisterModule) (*compliancev1.MsgRegisterModuleResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleCompliance}
}

func (chainCompliance) SetModuleStatus(context.Context, *compliancev1.MsgSetModuleStatus) (*compliancev1.MsgSetModuleStatusResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleCompliance}
}

func (chainCompliance) BindModule(context.Context, *compliancev1.MsgBindModule) (*compliancev1.MsgBindModuleResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleCompliance}
}

func (chainCompliance) UnbindModule(context.Context, *compliancev1.MsgUnbindModule) (*compliancev1.MsgUnbindModuleResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleCompliance}
}

func (chainCompliance) MigrateBinding(context.Context, *compliancev1.MsgMigrateBinding) (*compliancev1.MsgMigrateBindingResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleCompliance}
}

func (chainCompliance) Params(context.Context, *compliancev1.QueryParamsRequest) (*compliancev1.QueryParamsResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleCompliance}
}

func (chainCompliance) Modules(context.Context, *compliancev1.QueryModulesRequest) (*compliancev1.QueryModulesResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleCompliance}
}

func (chainCompliance) Module(context.Context, *compliancev1.QueryModuleRequest) (*compliancev1.QueryModuleResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleCompliance}
}

func (chainCompliance) Bindings(context.Context, *compliancev1.QueryBindingsRequest) (*compliancev1.QueryBindingsResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleCompliance}
}

func (chainCompliance) Check(context.Context, *compliancev1.QueryCheckRequest) (*compliancev1.QueryCheckResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleCompliance}
}

type chainSettlement struct{}

func (chainSettlement) CreateVenue(context.Context, *settlementv1.MsgCreateVenue) (*settlementv1.MsgCreateVenueResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleSettlement}
}

func (chainSettlement) CreateInstruction(context.Context, *settlementv1.MsgCreateInstruction) (*settlementv1.MsgCreateInstructionResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleSettlement}
}

func (chainSettlement) Affirm(context.Context, *settlementv1.MsgAffirm) (*settlementv1.MsgAffirmResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleSettlement}
}

func (chainSettlement) WithdrawAffirmation(context.Context, *settlementv1.MsgWithdrawAffirmation) (*settlementv1.MsgWithdrawAffirmationResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleSettlement}
}

func (chainSettlement) ExecuteInstruction(context.Context, *settlementv1.MsgExecuteInstruction) (*settlementv1.MsgExecuteInstructionResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleSettlement}
}

func (chainSettlement) CancelInstruction(context.Context, *settlementv1.MsgCancelInstruction) (*settlementv1.MsgCancelInstructionResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleSettlement}
}

func (chainSettlement) Params(context.Context, *settlementv1.QueryParamsRequest) (*settlementv1.QueryParamsResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleSettlement}
}

func (chainSettlement) Instruction(context.Context, *settlementv1.QueryInstructionRequest) (*settlementv1.QueryInstructionResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleSettlement}
}

func (chainSettlement) InstructionsByParty(context.Context, *settlementv1.QueryInstructionsByPartyRequest) (*settlementv1.QueryInstructionsByPartyResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleSettlement}
}

func (chainSettlement) Venue(context.Context, *settlementv1.QueryVenueRequest) (*settlementv1.QueryVenueResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleSettlement}
}

type chainAttest struct{}

func (chainAttest) SetAttester(context.Context, *attestv1.MsgSetAttester) (*attestv1.MsgSetAttesterResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleAttest}
}

func (chainAttest) Submit(context.Context, *attestv1.MsgSubmit) (*attestv1.MsgSubmitResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleAttest}
}

func (chainAttest) Revoke(context.Context, *attestv1.MsgRevoke) (*attestv1.MsgRevokeResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleAttest}
}

func (chainAttest) Params(context.Context, *attestv1.QueryParamsRequest) (*attestv1.QueryParamsResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleAttest}
}

func (chainAttest) Latest(context.Context, *attestv1.QueryLatestRequest) (*attestv1.QueryLatestResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleAttest}
}

func (chainAttest) History(context.Context, *attestv1.QueryHistoryRequest) (*attestv1.QueryHistoryResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleAttest}
}

func (chainAttest) Attesters(context.Context, *attestv1.QueryAttestersRequest) (*attestv1.QueryAttestersResponse, error) {
	return nil, &ChainUpgradeRequired{Module: ModuleAttest}
}

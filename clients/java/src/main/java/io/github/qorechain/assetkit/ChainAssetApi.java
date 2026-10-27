// SPDX-License-Identifier: Apache-2.0
package io.github.qorechain.assetkit;

import io.github.qorechain.assetkit.proto.asset.v1.*;

/** x/asset on the real chain: every call throws {@link ChainUpgradeRequired}. */
final class ChainAssetApi implements AssetApi {
    private static final String MODULE = "x/asset";

    @Override
    public MsgCreateAssetResponse createAsset(MsgCreateAsset req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgUpdateFlagsResponse updateFlags(MsgUpdateFlags req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgSetRoleResponse setRole(MsgSetRole req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgProposeIssuerResponse proposeIssuer(MsgProposeIssuer req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgAcceptIssuerResponse acceptIssuer(MsgAcceptIssuer req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgAuthorizeHolderResponse authorizeHolder(MsgAuthorizeHolder req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgMintResponse mint(MsgMint req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgBurnResponse burn(MsgBurn req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgTransferResponse transfer(MsgTransfer req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgFreezeResponse freeze(MsgFreeze req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgFreezePartialResponse freezePartial(MsgFreezePartial req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgPauseResponse pause(MsgPause req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgClawbackResponse clawback(MsgClawback req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgForceTransferResponse forceTransfer(MsgForceTransfer req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgSetTermsResponse setTerms(MsgSetTerms req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgRetireResponse retire(MsgRetire req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public QueryParamsResponse params(QueryParamsRequest req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public QueryAssetResponse asset(QueryAssetRequest req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public QueryAssetsResponse assets(QueryAssetsRequest req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public QueryHolderResponse holder(QueryHolderRequest req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public QueryHoldersResponse holders(QueryHoldersRequest req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public QueryRolesResponse roles(QueryRolesRequest req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public QueryCanTransferResponse canTransfer(QueryCanTransferRequest req) {
        throw new ChainUpgradeRequired(MODULE);
    }
}

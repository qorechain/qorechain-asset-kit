// SPDX-License-Identifier: Apache-2.0
package io.github.qorechain.assetkit;

import io.github.qorechain.assetkit.proto.asset.v1.*;

/** Messages and queries of the proposed x/asset module (not on chain; see docs/proposal.md). */
public interface AssetApi {
    MsgCreateAssetResponse createAsset(MsgCreateAsset req);
    MsgUpdateFlagsResponse updateFlags(MsgUpdateFlags req);
    MsgSetRoleResponse setRole(MsgSetRole req);
    MsgProposeIssuerResponse proposeIssuer(MsgProposeIssuer req);
    MsgAcceptIssuerResponse acceptIssuer(MsgAcceptIssuer req);
    MsgAuthorizeHolderResponse authorizeHolder(MsgAuthorizeHolder req);
    MsgMintResponse mint(MsgMint req);
    MsgBurnResponse burn(MsgBurn req);
    MsgTransferResponse transfer(MsgTransfer req);
    MsgFreezeResponse freeze(MsgFreeze req);
    MsgFreezePartialResponse freezePartial(MsgFreezePartial req);
    MsgPauseResponse pause(MsgPause req);
    MsgClawbackResponse clawback(MsgClawback req);
    MsgForceTransferResponse forceTransfer(MsgForceTransfer req);
    MsgSetTermsResponse setTerms(MsgSetTerms req);
    MsgRetireResponse retire(MsgRetire req);
    QueryParamsResponse params(QueryParamsRequest req);
    QueryAssetResponse asset(QueryAssetRequest req);
    QueryAssetsResponse assets(QueryAssetsRequest req);
    QueryHolderResponse holder(QueryHolderRequest req);
    QueryHoldersResponse holders(QueryHoldersRequest req);
    QueryRolesResponse roles(QueryRolesRequest req);
    QueryCanTransferResponse canTransfer(QueryCanTransferRequest req);
}

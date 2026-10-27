// SPDX-License-Identifier: Apache-2.0
package io.github.qorechain.assetkit;

import io.github.qorechain.assetkit.proto.identity.v1.*;

/** Messages and queries of the proposed x/identity module (not on chain; see docs/proposal.md). */
public interface IdentityApi {
    MsgRegisterIdentityResponse registerIdentity(MsgRegisterIdentity req);
    MsgUpdateCountryResponse updateCountry(MsgUpdateCountry req);
    MsgBindAddressResponse bindAddress(MsgBindAddress req);
    MsgUnbindAddressResponse unbindAddress(MsgUnbindAddress req);
    MsgAddClaimResponse addClaim(MsgAddClaim req);
    MsgRevokeClaimResponse revokeClaim(MsgRevokeClaim req);
    MsgRemoveIdentityResponse removeIdentity(MsgRemoveIdentity req);
    MsgSetClaimIssuerResponse setClaimIssuer(MsgSetClaimIssuer req);
    QueryParamsResponse params(QueryParamsRequest req);
    QueryIdentityResponse identity(QueryIdentityRequest req);
    QueryIdentityByAddressResponse identityByAddress(QueryIdentityByAddressRequest req);
    QueryClaimIssuersResponse claimIssuers(QueryClaimIssuersRequest req);
    QueryIsVerifiedResponse isVerified(QueryIsVerifiedRequest req);
}

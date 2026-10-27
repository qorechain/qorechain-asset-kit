// SPDX-License-Identifier: Apache-2.0
package io.github.qorechain.assetkit;

import io.github.qorechain.assetkit.proto.identity.v1.*;

/** x/identity on the real chain: every call throws {@link ChainUpgradeRequired}. */
final class ChainIdentityApi implements IdentityApi {
    private static final String MODULE = "x/identity";

    @Override
    public MsgRegisterIdentityResponse registerIdentity(MsgRegisterIdentity req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgUpdateCountryResponse updateCountry(MsgUpdateCountry req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgBindAddressResponse bindAddress(MsgBindAddress req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgUnbindAddressResponse unbindAddress(MsgUnbindAddress req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgAddClaimResponse addClaim(MsgAddClaim req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgRevokeClaimResponse revokeClaim(MsgRevokeClaim req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgRemoveIdentityResponse removeIdentity(MsgRemoveIdentity req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgSetClaimIssuerResponse setClaimIssuer(MsgSetClaimIssuer req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public QueryParamsResponse params(QueryParamsRequest req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public QueryIdentityResponse identity(QueryIdentityRequest req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public QueryIdentityByAddressResponse identityByAddress(QueryIdentityByAddressRequest req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public QueryClaimIssuersResponse claimIssuers(QueryClaimIssuersRequest req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public QueryIsVerifiedResponse isVerified(QueryIsVerifiedRequest req) {
        throw new ChainUpgradeRequired(MODULE);
    }
}

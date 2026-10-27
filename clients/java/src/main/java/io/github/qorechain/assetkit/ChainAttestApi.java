// SPDX-License-Identifier: Apache-2.0
package io.github.qorechain.assetkit;

import io.github.qorechain.assetkit.proto.attest.v1.*;

/** x/attest on the real chain: every call throws {@link ChainUpgradeRequired}. */
final class ChainAttestApi implements AttestApi {
    private static final String MODULE = "x/attest";

    @Override
    public MsgSetAttesterResponse setAttester(MsgSetAttester req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgSubmitResponse submit(MsgSubmit req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgRevokeResponse revoke(MsgRevoke req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public QueryParamsResponse params(QueryParamsRequest req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public QueryLatestResponse latest(QueryLatestRequest req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public QueryHistoryResponse history(QueryHistoryRequest req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public QueryAttestersResponse attesters(QueryAttestersRequest req) {
        throw new ChainUpgradeRequired(MODULE);
    }
}

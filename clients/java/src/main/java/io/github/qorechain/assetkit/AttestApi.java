// SPDX-License-Identifier: Apache-2.0
package io.github.qorechain.assetkit;

import io.github.qorechain.assetkit.proto.attest.v1.*;

/** Messages and queries of the proposed x/attest module (not on chain; see docs/proposal.md). */
public interface AttestApi {
    MsgSetAttesterResponse setAttester(MsgSetAttester req);
    MsgSubmitResponse submit(MsgSubmit req);
    MsgRevokeResponse revoke(MsgRevoke req);
    QueryParamsResponse params(QueryParamsRequest req);
    QueryLatestResponse latest(QueryLatestRequest req);
    QueryHistoryResponse history(QueryHistoryRequest req);
    QueryAttestersResponse attesters(QueryAttestersRequest req);
}

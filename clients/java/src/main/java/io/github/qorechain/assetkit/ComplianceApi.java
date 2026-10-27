// SPDX-License-Identifier: Apache-2.0
package io.github.qorechain.assetkit;

import io.github.qorechain.assetkit.proto.compliance.v1.*;

/** Messages and queries of the proposed x/compliance module (not on chain; see docs/proposal.md). */
public interface ComplianceApi {
    MsgRegisterModuleResponse registerModule(MsgRegisterModule req);
    MsgSetModuleStatusResponse setModuleStatus(MsgSetModuleStatus req);
    MsgBindModuleResponse bindModule(MsgBindModule req);
    MsgUnbindModuleResponse unbindModule(MsgUnbindModule req);
    MsgMigrateBindingResponse migrateBinding(MsgMigrateBinding req);
    QueryParamsResponse params(QueryParamsRequest req);
    QueryModulesResponse modules(QueryModulesRequest req);
    QueryModuleResponse module(QueryModuleRequest req);
    QueryBindingsResponse bindings(QueryBindingsRequest req);
    QueryCheckResponse check(QueryCheckRequest req);
}

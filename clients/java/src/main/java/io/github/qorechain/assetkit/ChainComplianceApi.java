// SPDX-License-Identifier: Apache-2.0
package io.github.qorechain.assetkit;

import io.github.qorechain.assetkit.proto.compliance.v1.*;

/** x/compliance on the real chain: every call throws {@link ChainUpgradeRequired}. */
final class ChainComplianceApi implements ComplianceApi {
    private static final String MODULE = "x/compliance";

    @Override
    public MsgRegisterModuleResponse registerModule(MsgRegisterModule req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgSetModuleStatusResponse setModuleStatus(MsgSetModuleStatus req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgBindModuleResponse bindModule(MsgBindModule req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgUnbindModuleResponse unbindModule(MsgUnbindModule req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgMigrateBindingResponse migrateBinding(MsgMigrateBinding req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public QueryParamsResponse params(QueryParamsRequest req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public QueryModulesResponse modules(QueryModulesRequest req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public QueryModuleResponse module(QueryModuleRequest req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public QueryBindingsResponse bindings(QueryBindingsRequest req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public QueryCheckResponse check(QueryCheckRequest req) {
        throw new ChainUpgradeRequired(MODULE);
    }
}

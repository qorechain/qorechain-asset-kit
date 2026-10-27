// SPDX-License-Identifier: Apache-2.0
package io.github.qorechain.assetkit;

import io.github.qorechain.assetkit.proto.settlement.v1.*;

/** x/settlement on the real chain: every call throws {@link ChainUpgradeRequired}. */
final class ChainSettlementApi implements SettlementApi {
    private static final String MODULE = "x/settlement";

    @Override
    public MsgCreateVenueResponse createVenue(MsgCreateVenue req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgCreateInstructionResponse createInstruction(MsgCreateInstruction req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgAffirmResponse affirm(MsgAffirm req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgWithdrawAffirmationResponse withdrawAffirmation(MsgWithdrawAffirmation req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgExecuteInstructionResponse executeInstruction(MsgExecuteInstruction req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public MsgCancelInstructionResponse cancelInstruction(MsgCancelInstruction req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public QueryParamsResponse params(QueryParamsRequest req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public QueryInstructionResponse instruction(QueryInstructionRequest req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public QueryInstructionsByPartyResponse instructionsByParty(QueryInstructionsByPartyRequest req) {
        throw new ChainUpgradeRequired(MODULE);
    }

    @Override
    public QueryVenueResponse venue(QueryVenueRequest req) {
        throw new ChainUpgradeRequired(MODULE);
    }
}

// SPDX-License-Identifier: Apache-2.0
package io.github.qorechain.assetkit;

import io.github.qorechain.assetkit.proto.settlement.v1.*;

/** Messages and queries of the proposed x/settlement module (not on chain; see docs/proposal.md). */
public interface SettlementApi {
    MsgCreateVenueResponse createVenue(MsgCreateVenue req);
    MsgCreateInstructionResponse createInstruction(MsgCreateInstruction req);
    MsgAffirmResponse affirm(MsgAffirm req);
    MsgWithdrawAffirmationResponse withdrawAffirmation(MsgWithdrawAffirmation req);
    MsgExecuteInstructionResponse executeInstruction(MsgExecuteInstruction req);
    MsgCancelInstructionResponse cancelInstruction(MsgCancelInstruction req);
    QueryParamsResponse params(QueryParamsRequest req);
    QueryInstructionResponse instruction(QueryInstructionRequest req);
    QueryInstructionsByPartyResponse instructionsByParty(QueryInstructionsByPartyRequest req);
    QueryVenueResponse venue(QueryVenueRequest req);
}

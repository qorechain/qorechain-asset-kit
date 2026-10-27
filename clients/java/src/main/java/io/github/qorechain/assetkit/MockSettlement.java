// SPDX-License-Identifier: Apache-2.0
package io.github.qorechain.assetkit;

import static io.github.qorechain.assetkit.MockChain.fail;

import io.github.qorechain.assetkit.proto.asset.v1.EventTransferred;
import io.github.qorechain.assetkit.proto.settlement.v1.*;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.EnumSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

/** x/settlement in {@link MockChain}. */
final class MockSettlement implements SettlementApi {
    private static final String M = "x/settlement";
    private static final Set<InstructionStatus> FINAL = EnumSet.of(
            InstructionStatus.INSTRUCTION_STATUS_EXECUTED,
            InstructionStatus.INSTRUCTION_STATUS_CANCELLED,
            InstructionStatus.INSTRUCTION_STATUS_EXPIRED);

    private final MockChain chain;
    private final Params params = Params.newBuilder().setMaxLegs(10).setMaxDeadlineSeconds(30L * 86400).build();
    private final Map<Long, Instruction.Builder> instructions = new LinkedHashMap<>();
    private long nextId = 1;
    private final Map<String, Venue> venues = new LinkedHashMap<>();

    MockSettlement(MockChain chain) {
        this.chain = chain;
    }

    /** End blocker: ON_BLOCK settlement, then expiry. Instructions are kept in id order. */
    void endBlock() {
        for (Instruction.Builder ins : instructions.values()) {
            boolean due = ins.getSettlementType() == SettlementType.SETTLEMENT_TYPE_ON_BLOCK && ins.getSettleHeight() <= chain.height;
            if (due && ins.getStatus() == InstructionStatus.INSTRUCTION_STATUS_AFFIRMED && chain.time <= ins.getDeadline()) {
                execute(ins);
            } else if (due && ins.getStatus() == InstructionStatus.INSTRUCTION_STATUS_PENDING) {
                ins.setStatus(InstructionStatus.INSTRUCTION_STATUS_FAILED).setFailureReason("not fully affirmed at settle height");
                chain.emit("qorechain.settlement.v1.EventInstructionFailed", EventInstructionFailed.newBuilder()
                        .setId(ins.getId()).setLegIndex(0).setReason(ins.getFailureReason()).build());
            }
        }
        for (Instruction.Builder ins : instructions.values()) {
            if (!FINAL.contains(ins.getStatus()) && chain.time > ins.getDeadline()) {
                ins.setStatus(InstructionStatus.INSTRUCTION_STATUS_EXPIRED);
                chain.emit("qorechain.settlement.v1.EventInstructionExpired", EventInstructionExpired.newBuilder()
                        .setId(ins.getId()).build());
            }
        }
    }

    @Override
    public MsgCreateVenueResponse createVenue(MsgCreateVenue m) {
        if (venues.containsKey(m.getVenueId())) {
            throw fail(M, "ERROR_CODE_VENUE_EXISTS", "venue " + m.getVenueId() + " exists");
        }
        venues.put(m.getVenueId(), Venue.newBuilder()
                .setVenueId(m.getVenueId()).setOperator(m.getOperator()).setDescription(m.getDescription())
                .addAllAllowedCreators(m.getAllowedCreatorsList()).build());
        chain.emit("qorechain.settlement.v1.EventVenueCreated", EventVenueCreated.newBuilder()
                .setVenueId(m.getVenueId()).setOperator(m.getOperator()).build());
        return MsgCreateVenueResponse.getDefaultInstance();
    }

    @Override
    public MsgCreateInstructionResponse createInstruction(MsgCreateInstruction m) {
        if (m.getLegsCount() == 0) {
            throw fail(M, "ERROR_CODE_INVALID_LEG", "an instruction needs at least one leg");
        }
        if (m.getLegsCount() > params.getMaxLegs()) {
            throw fail(M, "ERROR_CODE_TOO_MANY_LEGS", "too many legs");
        }
        for (int i = 0; i < m.getLegsCount(); i++) {
            Leg leg = m.getLegs(i);
            if (leg.getFrom().isEmpty() || leg.getTo().isEmpty() || leg.getFrom().equals(leg.getTo())
                    || leg.getDenom().isEmpty() || !MockChain.isPositiveInteger(leg.getAmount())) {
                throw fail(M, "ERROR_CODE_INVALID_LEG", "leg " + i + " is invalid");
            }
        }
        if (!m.getVenueId().isEmpty()) {
            Venue v = venues.get(m.getVenueId());
            if (v == null) {
                throw fail(M, "ERROR_CODE_VENUE_NOT_FOUND", "venue " + m.getVenueId() + " not found");
            }
            if (v.getAllowedCreatorsCount() > 0 && !v.getAllowedCreatorsList().contains(m.getCreator())) {
                throw fail(M, "ERROR_CODE_NOT_ALLOWED_IN_VENUE", m.getCreator() + " may not create instructions in " + m.getVenueId());
            }
        }
        long deadline = m.getDeadline();
        if (deadline <= chain.time) {
            throw fail(M, "ERROR_CODE_DEADLINE_PASSED", "deadline is not in the future");
        }
        if (deadline - chain.time > params.getMaxDeadlineSeconds()) {
            throw fail(M, "ERROR_CODE_DEADLINE_TOO_FAR", "deadline is too far in the future");
        }
        SettlementType type = m.getSettlementType() == SettlementType.SETTLEMENT_TYPE_UNSPECIFIED
                ? SettlementType.SETTLEMENT_TYPE_ON_AFFIRMATION : m.getSettlementType();
        if (type == SettlementType.SETTLEMENT_TYPE_ON_BLOCK && m.getSettleHeight() <= chain.height) {
            throw fail(M, "ERROR_CODE_INVALID_STATUS", "settle_height must be in the future");
        }
        List<String> parties = new ArrayList<>();
        for (Leg leg : m.getLegsList()) {
            for (String a : new String[] {leg.getFrom(), leg.getTo()}) {
                if (!parties.contains(a)) {
                    parties.add(a);
                }
            }
        }
        long id = nextId++;
        Instruction.Builder ins = Instruction.newBuilder()
                .setId(id)
                .setCreator(m.getCreator())
                .setVenueId(m.getVenueId())
                .addAllLegs(m.getLegsList())
                .setSettlementType(type)
                .setSettleHeight(m.getSettleHeight())
                .setDeadline(m.getDeadline())
                .setStatus(InstructionStatus.INSTRUCTION_STATUS_PENDING)
                .setMemo(m.getMemo());
        for (String p : parties) {
            boolean creator = p.equals(m.getCreator());
            ins.addAffirmations(Affirmation.newBuilder().setParty(p).setAffirmed(creator).setHeight(creator ? chain.height : 0));
        }
        instructions.put(id, ins);
        chain.emit("qorechain.settlement.v1.EventInstructionCreated", EventInstructionCreated.newBuilder()
                .setId(id).setCreator(m.getCreator()).setVenueId(m.getVenueId()).addAllLegs(m.getLegsList())
                .setSettlementType(type).setDeadline(m.getDeadline()).build());
        if (parties.contains(m.getCreator())) {
            chain.emit("qorechain.settlement.v1.EventAffirmed", EventAffirmed.newBuilder().setId(id).setParty(m.getCreator()).build());
        }
        return MsgCreateInstructionResponse.newBuilder().setId(id).build();
    }

    private Instruction.Builder ins(long id) {
        Instruction.Builder x = instructions.get(id);
        if (x == null) {
            throw fail(M, "ERROR_CODE_INSTRUCTION_NOT_FOUND", "instruction " + id + " not found");
        }
        return x;
    }

    private static int partyIndex(Instruction.Builder ins, String party) {
        for (int i = 0; i < ins.getAffirmationsCount(); i++) {
            if (ins.getAffirmations(i).getParty().equals(party)) {
                return i;
            }
        }
        return -1;
    }

    private static boolean allAffirmed(Instruction.Builder ins) {
        return ins.getAffirmationsList().stream().allMatch(Affirmation::getAffirmed);
    }

    private String operatorOf(Instruction.Builder ins) {
        if (ins.getVenueId().isEmpty()) {
            return null;
        }
        Venue v = venues.get(ins.getVenueId());
        return v == null ? null : v.getOperator();
    }

    @Override
    public MsgAffirmResponse affirm(MsgAffirm m) {
        Instruction.Builder ins = ins(m.getId());
        int idx = partyIndex(ins, m.getParty());
        if (idx < 0) {
            throw fail(M, "ERROR_CODE_NOT_A_PARTY", m.getParty() + " is not a party");
        }
        if (ins.getStatus() != InstructionStatus.INSTRUCTION_STATUS_PENDING) {
            throw fail(M, "ERROR_CODE_INVALID_STATUS", "instruction is " + ins.getStatus().name());
        }
        if (chain.time > ins.getDeadline()) {
            throw fail(M, "ERROR_CODE_DEADLINE_PASSED", "deadline passed");
        }
        if (!ins.getAffirmations(idx).getAffirmed()) {
            ins.getAffirmationsBuilder(idx).setAffirmed(true).setHeight(chain.height);
            chain.emit("qorechain.settlement.v1.EventAffirmed", EventAffirmed.newBuilder()
                    .setId(ins.getId()).setParty(m.getParty()).build());
        }
        if (allAffirmed(ins)) {
            ins.setStatus(InstructionStatus.INSTRUCTION_STATUS_AFFIRMED);
            if (ins.getSettlementType() == SettlementType.SETTLEMENT_TYPE_ON_AFFIRMATION) {
                execute(ins);
            }
        }
        return MsgAffirmResponse.newBuilder()
                .setExecuted(ins.getStatus() == InstructionStatus.INSTRUCTION_STATUS_EXECUTED).build();
    }

    @Override
    public MsgWithdrawAffirmationResponse withdrawAffirmation(MsgWithdrawAffirmation m) {
        Instruction.Builder ins = ins(m.getId());
        int idx = partyIndex(ins, m.getParty());
        if (idx < 0) {
            throw fail(M, "ERROR_CODE_NOT_A_PARTY", m.getParty() + " is not a party");
        }
        if (FINAL.contains(ins.getStatus())) {
            throw fail(M, "ERROR_CODE_INVALID_STATUS", "instruction is " + ins.getStatus().name());
        }
        ins.getAffirmationsBuilder(idx).setAffirmed(false).setHeight(0);
        ins.setStatus(InstructionStatus.INSTRUCTION_STATUS_PENDING);
        chain.emit("qorechain.settlement.v1.EventAffirmationWithdrawn", EventAffirmationWithdrawn.newBuilder()
                .setId(ins.getId()).setParty(m.getParty()).build());
        return MsgWithdrawAffirmationResponse.getDefaultInstance();
    }

    @Override
    public MsgExecuteInstructionResponse executeInstruction(MsgExecuteInstruction m) {
        Instruction.Builder ins = ins(m.getId());
        String operator = operatorOf(ins);
        if (partyIndex(ins, m.getSigner()) < 0 && !m.getSigner().equals(operator)) {
            throw fail(M, "ERROR_CODE_NOT_A_PARTY", m.getSigner() + " is not a party or the venue operator");
        }
        if (!allAffirmed(ins)) {
            throw fail(M, "ERROR_CODE_NOT_FULLY_AFFIRMED", "not every party affirmed");
        }
        boolean retry = ins.getStatus() == InstructionStatus.INSTRUCTION_STATUS_FAILED;
        boolean manual = ins.getStatus() == InstructionStatus.INSTRUCTION_STATUS_AFFIRMED
                && ins.getSettlementType() == SettlementType.SETTLEMENT_TYPE_MANUAL;
        if (!retry && !manual) {
            throw fail(M, "ERROR_CODE_INVALID_STATUS", "instruction is " + ins.getStatus().name());
        }
        if (chain.time > ins.getDeadline()) {
            throw fail(M, "ERROR_CODE_DEADLINE_PASSED", "deadline passed");
        }
        execute(ins);
        return MsgExecuteInstructionResponse.newBuilder().setStatus(ins.getStatus()).build();
    }

    @Override
    public MsgCancelInstructionResponse cancelInstruction(MsgCancelInstruction m) {
        Instruction.Builder ins = ins(m.getId());
        String operator = operatorOf(ins);
        if (!m.getSigner().equals(ins.getCreator()) && !m.getSigner().equals(operator) && partyIndex(ins, m.getSigner()) < 0) {
            throw fail(M, "ERROR_CODE_NOT_A_PARTY", m.getSigner() + " may not cancel");
        }
        if (FINAL.contains(ins.getStatus())) {
            throw fail(M, "ERROR_CODE_INVALID_STATUS", "instruction is " + ins.getStatus().name());
        }
        ins.setStatus(InstructionStatus.INSTRUCTION_STATUS_CANCELLED);
        chain.emit("qorechain.settlement.v1.EventInstructionCancelled", EventInstructionCancelled.newBuilder()
                .setId(ins.getId()).setSigner(m.getSigner()).build());
        return MsgCancelInstructionResponse.getDefaultInstance();
    }

    /** Applies every leg, or none. Leaves the instruction EXECUTED or FAILED. */
    private void execute(Instruction.Builder ins) {
        Runnable restore = chain.snapshot();
        for (int i = 0; i < ins.getLegsCount(); i++) {
            String reason = applyLeg(ins.getLegs(i));
            if (reason != null) {
                restore.run();
                ins.setStatus(InstructionStatus.INSTRUCTION_STATUS_FAILED).setFailureReason("leg " + i + ": " + reason);
                chain.emit("qorechain.settlement.v1.EventInstructionFailed", EventInstructionFailed.newBuilder()
                        .setId(ins.getId()).setLegIndex(i).setReason(reason).build());
                return;
            }
        }
        ins.setStatus(InstructionStatus.INSTRUCTION_STATUS_EXECUTED).setFailureReason("");
        chain.emit("qorechain.settlement.v1.EventInstructionExecuted", EventInstructionExecuted.newBuilder()
                .setId(ins.getId()).build());
    }

    private String applyLeg(Leg leg) {
        BigInteger amount = new BigInteger(leg.getAmount());
        if (leg.getDenom().startsWith("asset/")) {
            String assetId = leg.getDenom().substring("asset/".length());
            MockAsset.Rec r = chain.asset.assets.get(assetId);
            if (r == null) {
                return "ERROR_CODE_ASSET_NOT_FOUND";
            }
            MockAsset.Refusal refusal = chain.asset.transferRefusal(r, leg.getFrom(), leg.getTo(), amount);
            if (refusal != null) {
                return refusal.moduleId() != null ? refusal.code() + " (" + refusal.moduleId() + ")" : refusal.code();
            }
            chain.asset.move(r, leg.getFrom(), leg.getTo(), amount);
            chain.emit("qorechain.asset.v1.EventTransferred", EventTransferred.newBuilder()
                    .setAssetId(assetId).setFrom(leg.getFrom()).setTo(leg.getTo()).setAmount(leg.getAmount()).build());
            return null;
        }
        BigInteger bal = chain.bankBig(leg.getFrom(), leg.getDenom());
        if (bal.compareTo(amount) < 0) {
            return "insufficient " + leg.getDenom() + " balance";
        }
        chain.bank.get(leg.getFrom()).put(leg.getDenom(), bal.subtract(amount));
        chain.fundBank(leg.getTo(), leg.getDenom(), amount);
        return null;
    }

    @Override
    public QueryParamsResponse params(QueryParamsRequest req) {
        return QueryParamsResponse.newBuilder().setParams(params).build();
    }

    @Override
    public QueryInstructionResponse instruction(QueryInstructionRequest q) {
        return QueryInstructionResponse.newBuilder().setInstruction(ins(q.getId()).build()).build();
    }

    @Override
    public QueryInstructionsByPartyResponse instructionsByParty(QueryInstructionsByPartyRequest q) {
        QueryInstructionsByPartyResponse.Builder b = QueryInstructionsByPartyResponse.newBuilder();
        for (Instruction.Builder x : instructions.values()) {
            if (partyIndex(x, q.getParty()) >= 0
                    && (q.getStatus() == InstructionStatus.INSTRUCTION_STATUS_UNSPECIFIED || x.getStatus() == q.getStatus())) {
                b.addInstructions(x.build());
            }
        }
        return b.build();
    }

    @Override
    public QueryVenueResponse venue(QueryVenueRequest q) {
        Venue v = venues.get(q.getVenueId());
        if (v == null) {
            throw fail(M, "ERROR_CODE_VENUE_NOT_FOUND", "venue " + q.getVenueId() + " not found");
        }
        return QueryVenueResponse.newBuilder().setVenue(v).build();
    }
}

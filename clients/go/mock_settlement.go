// SPDX-License-Identifier: Apache-2.0

package assetkit

import (
	"context"
	"fmt"
	"math/big"
	"sort"
	"strings"

	"google.golang.org/protobuf/proto"

	assetv1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/asset/v1"
	settlementv1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/settlement/v1"
)

func isFinal(s settlementv1.InstructionStatus) bool {
	switch s {
	case settlementv1.InstructionStatus_INSTRUCTION_STATUS_EXECUTED,
		settlementv1.InstructionStatus_INSTRUCTION_STATUS_CANCELLED,
		settlementv1.InstructionStatus_INSTRUCTION_STATUS_EXPIRED:
		return true
	}
	return false
}

func (c *MockChain) instructionIDs() []uint64 {
	ids := make([]uint64, 0, len(c.instructions))
	for id := range c.instructions {
		ids = append(ids, id)
	}
	sort.Slice(ids, func(i, j int) bool { return ids[i] < ids[j] })
	return ids
}

func (c *MockChain) createVenue(m *settlementv1.MsgCreateVenue) (*settlementv1.MsgCreateVenueResponse, error) {
	if _, ok := c.venues[m.VenueId]; ok {
		return nil, fail(ModuleSettlement, "ERROR_CODE_VENUE_EXISTS", "venue %s exists", m.VenueId)
	}
	c.venues[m.VenueId] = &settlementv1.Venue{
		VenueId: m.VenueId, Operator: m.Operator, Description: m.Description, AllowedCreators: append([]string(nil), m.AllowedCreators...),
	}
	c.emit("qorechain.settlement.v1.EventVenueCreated", &settlementv1.EventVenueCreated{VenueId: m.VenueId, Operator: m.Operator})
	return &settlementv1.MsgCreateVenueResponse{}, nil
}

func cloneLegs(legs []*settlementv1.Leg) []*settlementv1.Leg {
	out := make([]*settlementv1.Leg, len(legs))
	for i, l := range legs {
		out[i] = proto.Clone(l).(*settlementv1.Leg)
	}
	return out
}

func (c *MockChain) createInstruction(m *settlementv1.MsgCreateInstruction) (*settlementv1.MsgCreateInstructionResponse, error) {
	if len(m.Legs) == 0 {
		return nil, fail(ModuleSettlement, "ERROR_CODE_INVALID_LEG", "an instruction needs at least one leg")
	}
	if uint32(len(m.Legs)) > c.settlementParams.MaxLegs {
		return nil, fail(ModuleSettlement, "ERROR_CODE_TOO_MANY_LEGS", "too many legs")
	}
	for i, leg := range m.Legs {
		_, positive := positiveInteger(leg.GetAmount())
		if leg == nil || leg.From == "" || leg.To == "" || leg.From == leg.To || leg.Denom == "" || !positive {
			return nil, fail(ModuleSettlement, "ERROR_CODE_INVALID_LEG", "leg %d is invalid", i)
		}
	}
	if m.VenueId != "" {
		v, ok := c.venues[m.VenueId]
		if !ok {
			return nil, fail(ModuleSettlement, "ERROR_CODE_VENUE_NOT_FOUND", "venue %s not found", m.VenueId)
		}
		if len(v.AllowedCreators) > 0 && !contains(v.AllowedCreators, m.Creator) {
			return nil, fail(ModuleSettlement, "ERROR_CODE_NOT_ALLOWED_IN_VENUE", "%s may not create instructions in %s", m.Creator, m.VenueId)
		}
	}
	if m.Deadline <= c.time {
		return nil, fail(ModuleSettlement, "ERROR_CODE_DEADLINE_PASSED", "deadline is not in the future")
	}
	if m.Deadline-c.time > c.settlementParams.MaxDeadlineSeconds {
		return nil, fail(ModuleSettlement, "ERROR_CODE_DEADLINE_TOO_FAR", "deadline is too far in the future")
	}
	typ := m.SettlementType
	if typ == settlementv1.SettlementType_SETTLEMENT_TYPE_UNSPECIFIED {
		typ = settlementv1.SettlementType_SETTLEMENT_TYPE_ON_AFFIRMATION
	}
	if typ == settlementv1.SettlementType_SETTLEMENT_TYPE_ON_BLOCK && m.SettleHeight <= c.height {
		return nil, fail(ModuleSettlement, "ERROR_CODE_INVALID_STATUS", "settle_height must be in the future")
	}
	var parties []string
	for _, leg := range m.Legs {
		for _, a := range []string{leg.From, leg.To} {
			if !contains(parties, a) {
				parties = append(parties, a)
			}
		}
	}
	id := c.nextInstructionID
	c.nextInstructionID++
	ins := &settlementv1.Instruction{
		Id:             id,
		Creator:        m.Creator,
		VenueId:        m.VenueId,
		Legs:           cloneLegs(m.Legs),
		SettlementType: typ,
		SettleHeight:   m.SettleHeight,
		Deadline:       m.Deadline,
		Status:         settlementv1.InstructionStatus_INSTRUCTION_STATUS_PENDING,
		Memo:           m.Memo,
	}
	for _, p := range parties {
		a := &settlementv1.Affirmation{Party: p}
		if p == m.Creator {
			a.Affirmed = true
			a.Height = c.height
		}
		ins.Affirmations = append(ins.Affirmations, a)
	}
	c.instructions[id] = ins
	c.emit("qorechain.settlement.v1.EventInstructionCreated", &settlementv1.EventInstructionCreated{
		Id: id, Creator: m.Creator, VenueId: m.VenueId, Legs: cloneLegs(m.Legs), SettlementType: typ, Deadline: m.Deadline,
	})
	if contains(parties, m.Creator) {
		c.emit("qorechain.settlement.v1.EventAffirmed", &settlementv1.EventAffirmed{Id: id, Party: m.Creator})
	}
	return &settlementv1.MsgCreateInstructionResponse{Id: id}, nil
}

func (c *MockChain) ins(id uint64) (*settlementv1.Instruction, error) {
	x, ok := c.instructions[id]
	if !ok {
		return nil, fail(ModuleSettlement, "ERROR_CODE_INSTRUCTION_NOT_FOUND", "instruction %d not found", id)
	}
	return x, nil
}

func affirmationOf(ins *settlementv1.Instruction, party string) *settlementv1.Affirmation {
	for _, a := range ins.Affirmations {
		if a.Party == party {
			return a
		}
	}
	return nil
}

func allAffirmed(ins *settlementv1.Instruction) bool {
	for _, a := range ins.Affirmations {
		if !a.Affirmed {
			return false
		}
	}
	return true
}

func (c *MockChain) affirm(m *settlementv1.MsgAffirm) (*settlementv1.MsgAffirmResponse, error) {
	ins, err := c.ins(m.Id)
	if err != nil {
		return nil, err
	}
	a := affirmationOf(ins, m.Party)
	if a == nil {
		return nil, fail(ModuleSettlement, "ERROR_CODE_NOT_A_PARTY", "%s is not a party", m.Party)
	}
	if ins.Status != settlementv1.InstructionStatus_INSTRUCTION_STATUS_PENDING {
		return nil, fail(ModuleSettlement, "ERROR_CODE_INVALID_STATUS", "instruction is %s", ins.Status)
	}
	if c.time > ins.Deadline {
		return nil, fail(ModuleSettlement, "ERROR_CODE_DEADLINE_PASSED", "deadline passed")
	}
	if !a.Affirmed {
		a.Affirmed = true
		a.Height = c.height
		c.emit("qorechain.settlement.v1.EventAffirmed", &settlementv1.EventAffirmed{Id: ins.Id, Party: m.Party})
	}
	if allAffirmed(ins) {
		ins.Status = settlementv1.InstructionStatus_INSTRUCTION_STATUS_AFFIRMED
		if ins.SettlementType == settlementv1.SettlementType_SETTLEMENT_TYPE_ON_AFFIRMATION {
			c.execute(ins)
		}
	}
	return &settlementv1.MsgAffirmResponse{Executed: ins.Status == settlementv1.InstructionStatus_INSTRUCTION_STATUS_EXECUTED}, nil
}

func (c *MockChain) withdrawAffirmation(m *settlementv1.MsgWithdrawAffirmation) (*settlementv1.MsgWithdrawAffirmationResponse, error) {
	ins, err := c.ins(m.Id)
	if err != nil {
		return nil, err
	}
	a := affirmationOf(ins, m.Party)
	if a == nil {
		return nil, fail(ModuleSettlement, "ERROR_CODE_NOT_A_PARTY", "%s is not a party", m.Party)
	}
	if isFinal(ins.Status) {
		return nil, fail(ModuleSettlement, "ERROR_CODE_INVALID_STATUS", "instruction is %s", ins.Status)
	}
	a.Affirmed = false
	a.Height = 0
	ins.Status = settlementv1.InstructionStatus_INSTRUCTION_STATUS_PENDING
	c.emit("qorechain.settlement.v1.EventAffirmationWithdrawn", &settlementv1.EventAffirmationWithdrawn{Id: ins.Id, Party: m.Party})
	return &settlementv1.MsgWithdrawAffirmationResponse{}, nil
}

func (c *MockChain) venueOperator(ins *settlementv1.Instruction) (string, bool) {
	if ins.VenueId == "" {
		return "", false
	}
	v, ok := c.venues[ins.VenueId]
	if !ok {
		return "", false
	}
	return v.Operator, true
}

func (c *MockChain) executeInstruction(m *settlementv1.MsgExecuteInstruction) (*settlementv1.MsgExecuteInstructionResponse, error) {
	ins, err := c.ins(m.Id)
	if err != nil {
		return nil, err
	}
	op, hasOp := c.venueOperator(ins)
	if affirmationOf(ins, m.Signer) == nil && !(hasOp && op == m.Signer) {
		return nil, fail(ModuleSettlement, "ERROR_CODE_NOT_A_PARTY", "%s is not a party or the venue operator", m.Signer)
	}
	if !allAffirmed(ins) {
		return nil, fail(ModuleSettlement, "ERROR_CODE_NOT_FULLY_AFFIRMED", "not every party affirmed")
	}
	retry := ins.Status == settlementv1.InstructionStatus_INSTRUCTION_STATUS_FAILED
	manual := ins.Status == settlementv1.InstructionStatus_INSTRUCTION_STATUS_AFFIRMED &&
		ins.SettlementType == settlementv1.SettlementType_SETTLEMENT_TYPE_MANUAL
	if !retry && !manual {
		return nil, fail(ModuleSettlement, "ERROR_CODE_INVALID_STATUS", "instruction is %s", ins.Status)
	}
	if c.time > ins.Deadline {
		return nil, fail(ModuleSettlement, "ERROR_CODE_DEADLINE_PASSED", "deadline passed")
	}
	c.execute(ins)
	return &settlementv1.MsgExecuteInstructionResponse{Status: ins.Status}, nil
}

func (c *MockChain) cancelInstruction(m *settlementv1.MsgCancelInstruction) (*settlementv1.MsgCancelInstructionResponse, error) {
	ins, err := c.ins(m.Id)
	if err != nil {
		return nil, err
	}
	op, hasOp := c.venueOperator(ins)
	if m.Signer != ins.Creator && !(hasOp && op == m.Signer) && affirmationOf(ins, m.Signer) == nil {
		return nil, fail(ModuleSettlement, "ERROR_CODE_NOT_A_PARTY", "%s may not cancel", m.Signer)
	}
	if isFinal(ins.Status) {
		return nil, fail(ModuleSettlement, "ERROR_CODE_INVALID_STATUS", "instruction is %s", ins.Status)
	}
	ins.Status = settlementv1.InstructionStatus_INSTRUCTION_STATUS_CANCELLED
	c.emit("qorechain.settlement.v1.EventInstructionCancelled", &settlementv1.EventInstructionCancelled{Id: ins.Id, Signer: m.Signer})
	return &settlementv1.MsgCancelInstructionResponse{}, nil
}

// snapshot saves balances and the event log; the returned function restores them.
func (c *MockChain) snapshot() func() {
	holders := map[string]map[string]*holder{}
	for id, r := range c.assets {
		hs := map[string]*holder{}
		for a, h := range r.holders {
			hs[a] = h.clone()
		}
		holders[id] = hs
	}
	bank := map[string]map[string]*big.Int{}
	for a, m := range c.bank {
		mm := map[string]*big.Int{}
		for d, v := range m {
			mm[d] = new(big.Int).Set(v)
		}
		bank[a] = mm
	}
	events := len(c.log)
	return func() {
		for id, r := range c.assets {
			if hs, ok := holders[id]; ok {
				r.holders = hs
			} else {
				r.holders = map[string]*holder{}
			}
		}
		c.bank = bank
		c.log = c.log[:events]
	}
}

// execute applies every leg, or none. It leaves the instruction EXECUTED or FAILED.
func (c *MockChain) execute(ins *settlementv1.Instruction) {
	restore := c.snapshot()
	for i, leg := range ins.Legs {
		if reason, failed := c.applyLeg(leg); failed {
			restore()
			ins.Status = settlementv1.InstructionStatus_INSTRUCTION_STATUS_FAILED
			ins.FailureReason = fmt.Sprintf("leg %d: %s", i, reason)
			c.emit("qorechain.settlement.v1.EventInstructionFailed", &settlementv1.EventInstructionFailed{
				Id: ins.Id, LegIndex: uint32(i), Reason: reason,
			})
			return
		}
	}
	ins.Status = settlementv1.InstructionStatus_INSTRUCTION_STATUS_EXECUTED
	ins.FailureReason = ""
	c.emit("qorechain.settlement.v1.EventInstructionExecuted", &settlementv1.EventInstructionExecuted{Id: ins.Id})
}

func (c *MockChain) applyLeg(leg *settlementv1.Leg) (string, bool) {
	amount, _ := new(big.Int).SetString(leg.Amount, 10)
	if assetID, ok := strings.CutPrefix(leg.Denom, "asset/"); ok {
		r, found := c.assets[assetID]
		if !found {
			return "ERROR_CODE_ASSET_NOT_FOUND", true
		}
		if ref := c.transferRefusal(r, leg.From, leg.To, amount); ref != nil {
			if ref.moduleID != "" {
				return fmt.Sprintf("%s (%s)", ref.code, ref.moduleID), true
			}
			return ref.code, true
		}
		c.move(r, leg.From, leg.To, amount)
		c.emit("qorechain.asset.v1.EventTransferred", &assetv1.EventTransferred{
			AssetId: assetID, From: leg.From, To: leg.To, Amount: leg.Amount,
		})
		return "", false
	}
	bal := c.BankBalance(leg.From, leg.Denom)
	if bal.Cmp(amount) < 0 {
		return "insufficient " + leg.Denom + " balance", true
	}
	c.bank[leg.From][leg.Denom] = bal.Sub(bal, amount)
	c.FundBank(leg.To, leg.Denom, amount)
	return "", false
}

// mockSettlement adapts MockChain to SettlementAPI.
type mockSettlement struct{ c *MockChain }

func (s mockSettlement) CreateVenue(_ context.Context, m *settlementv1.MsgCreateVenue) (*settlementv1.MsgCreateVenueResponse, error) {
	return s.c.createVenue(orEmpty(m))
}

func (s mockSettlement) CreateInstruction(_ context.Context, m *settlementv1.MsgCreateInstruction) (*settlementv1.MsgCreateInstructionResponse, error) {
	return s.c.createInstruction(orEmpty(m))
}

func (s mockSettlement) Affirm(_ context.Context, m *settlementv1.MsgAffirm) (*settlementv1.MsgAffirmResponse, error) {
	return s.c.affirm(orEmpty(m))
}

func (s mockSettlement) WithdrawAffirmation(_ context.Context, m *settlementv1.MsgWithdrawAffirmation) (*settlementv1.MsgWithdrawAffirmationResponse, error) {
	return s.c.withdrawAffirmation(orEmpty(m))
}

func (s mockSettlement) ExecuteInstruction(_ context.Context, m *settlementv1.MsgExecuteInstruction) (*settlementv1.MsgExecuteInstructionResponse, error) {
	return s.c.executeInstruction(orEmpty(m))
}

func (s mockSettlement) CancelInstruction(_ context.Context, m *settlementv1.MsgCancelInstruction) (*settlementv1.MsgCancelInstructionResponse, error) {
	return s.c.cancelInstruction(orEmpty(m))
}

func (s mockSettlement) Params(context.Context, *settlementv1.QueryParamsRequest) (*settlementv1.QueryParamsResponse, error) {
	return &settlementv1.QueryParamsResponse{Params: proto.Clone(s.c.settlementParams).(*settlementv1.Params)}, nil
}

func (s mockSettlement) Instruction(_ context.Context, q *settlementv1.QueryInstructionRequest) (*settlementv1.QueryInstructionResponse, error) {
	ins, err := s.c.ins(orEmpty(q).Id)
	if err != nil {
		return nil, err
	}
	return &settlementv1.QueryInstructionResponse{Instruction: proto.Clone(ins).(*settlementv1.Instruction)}, nil
}

func (s mockSettlement) InstructionsByParty(_ context.Context, q *settlementv1.QueryInstructionsByPartyRequest) (*settlementv1.QueryInstructionsByPartyResponse, error) {
	q = orEmpty(q)
	out := &settlementv1.QueryInstructionsByPartyResponse{}
	for _, id := range s.c.instructionIDs() {
		ins := s.c.instructions[id]
		if affirmationOf(ins, q.Party) == nil {
			continue
		}
		if q.Status != settlementv1.InstructionStatus_INSTRUCTION_STATUS_UNSPECIFIED && ins.Status != q.Status {
			continue
		}
		out.Instructions = append(out.Instructions, proto.Clone(ins).(*settlementv1.Instruction))
	}
	return out, nil
}

func (s mockSettlement) Venue(_ context.Context, q *settlementv1.QueryVenueRequest) (*settlementv1.QueryVenueResponse, error) {
	q = orEmpty(q)
	v, ok := s.c.venues[q.VenueId]
	if !ok {
		return nil, fail(ModuleSettlement, "ERROR_CODE_VENUE_NOT_FOUND", "venue %s not found", q.VenueId)
	}
	return &settlementv1.QueryVenueResponse{Venue: proto.Clone(v).(*settlementv1.Venue)}, nil
}

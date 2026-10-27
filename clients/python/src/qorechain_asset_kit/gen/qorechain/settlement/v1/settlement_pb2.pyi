# SPDX-License-Identifier: Apache-2.0
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SettlementType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SETTLEMENT_TYPE_UNSPECIFIED: _ClassVar[SettlementType]
    SETTLEMENT_TYPE_ON_AFFIRMATION: _ClassVar[SettlementType]
    SETTLEMENT_TYPE_MANUAL: _ClassVar[SettlementType]
    SETTLEMENT_TYPE_ON_BLOCK: _ClassVar[SettlementType]

class InstructionStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INSTRUCTION_STATUS_UNSPECIFIED: _ClassVar[InstructionStatus]
    INSTRUCTION_STATUS_PENDING: _ClassVar[InstructionStatus]
    INSTRUCTION_STATUS_AFFIRMED: _ClassVar[InstructionStatus]
    INSTRUCTION_STATUS_EXECUTED: _ClassVar[InstructionStatus]
    INSTRUCTION_STATUS_FAILED: _ClassVar[InstructionStatus]
    INSTRUCTION_STATUS_CANCELLED: _ClassVar[InstructionStatus]
    INSTRUCTION_STATUS_EXPIRED: _ClassVar[InstructionStatus]

class ErrorCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ERROR_CODE_UNSPECIFIED: _ClassVar[ErrorCode]
    ERROR_CODE_INSTRUCTION_NOT_FOUND: _ClassVar[ErrorCode]
    ERROR_CODE_NOT_A_PARTY: _ClassVar[ErrorCode]
    ERROR_CODE_NOT_FULLY_AFFIRMED: _ClassVar[ErrorCode]
    ERROR_CODE_DEADLINE_PASSED: _ClassVar[ErrorCode]
    ERROR_CODE_INVALID_STATUS: _ClassVar[ErrorCode]
    ERROR_CODE_LEG_FAILED: _ClassVar[ErrorCode]
    ERROR_CODE_TOO_MANY_LEGS: _ClassVar[ErrorCode]
    ERROR_CODE_VENUE_NOT_FOUND: _ClassVar[ErrorCode]
    ERROR_CODE_NOT_ALLOWED_IN_VENUE: _ClassVar[ErrorCode]
    ERROR_CODE_INVALID_LEG: _ClassVar[ErrorCode]
    ERROR_CODE_VENUE_EXISTS: _ClassVar[ErrorCode]
    ERROR_CODE_DEADLINE_TOO_FAR: _ClassVar[ErrorCode]
SETTLEMENT_TYPE_UNSPECIFIED: SettlementType
SETTLEMENT_TYPE_ON_AFFIRMATION: SettlementType
SETTLEMENT_TYPE_MANUAL: SettlementType
SETTLEMENT_TYPE_ON_BLOCK: SettlementType
INSTRUCTION_STATUS_UNSPECIFIED: InstructionStatus
INSTRUCTION_STATUS_PENDING: InstructionStatus
INSTRUCTION_STATUS_AFFIRMED: InstructionStatus
INSTRUCTION_STATUS_EXECUTED: InstructionStatus
INSTRUCTION_STATUS_FAILED: InstructionStatus
INSTRUCTION_STATUS_CANCELLED: InstructionStatus
INSTRUCTION_STATUS_EXPIRED: InstructionStatus
ERROR_CODE_UNSPECIFIED: ErrorCode
ERROR_CODE_INSTRUCTION_NOT_FOUND: ErrorCode
ERROR_CODE_NOT_A_PARTY: ErrorCode
ERROR_CODE_NOT_FULLY_AFFIRMED: ErrorCode
ERROR_CODE_DEADLINE_PASSED: ErrorCode
ERROR_CODE_INVALID_STATUS: ErrorCode
ERROR_CODE_LEG_FAILED: ErrorCode
ERROR_CODE_TOO_MANY_LEGS: ErrorCode
ERROR_CODE_VENUE_NOT_FOUND: ErrorCode
ERROR_CODE_NOT_ALLOWED_IN_VENUE: ErrorCode
ERROR_CODE_INVALID_LEG: ErrorCode
ERROR_CODE_VENUE_EXISTS: ErrorCode
ERROR_CODE_DEADLINE_TOO_FAR: ErrorCode

class Leg(_message.Message):
    __slots__ = ("to", "denom", "amount")
    FROM_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    DENOM_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    to: str
    denom: str
    amount: str
    def __init__(self, to: _Optional[str] = ..., denom: _Optional[str] = ..., amount: _Optional[str] = ..., **kwargs) -> None: ...

class Affirmation(_message.Message):
    __slots__ = ("party", "affirmed", "height")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    AFFIRMED_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    party: str
    affirmed: bool
    height: int
    def __init__(self, party: _Optional[str] = ..., affirmed: _Optional[bool] = ..., height: _Optional[int] = ...) -> None: ...

class Instruction(_message.Message):
    __slots__ = ("id", "creator", "venue_id", "legs", "settlement_type", "settle_height", "deadline", "status", "affirmations", "failure_reason", "memo")
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATOR_FIELD_NUMBER: _ClassVar[int]
    VENUE_ID_FIELD_NUMBER: _ClassVar[int]
    LEGS_FIELD_NUMBER: _ClassVar[int]
    SETTLEMENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    SETTLE_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    DEADLINE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    AFFIRMATIONS_FIELD_NUMBER: _ClassVar[int]
    FAILURE_REASON_FIELD_NUMBER: _ClassVar[int]
    MEMO_FIELD_NUMBER: _ClassVar[int]
    id: int
    creator: str
    venue_id: str
    legs: _containers.RepeatedCompositeFieldContainer[Leg]
    settlement_type: SettlementType
    settle_height: int
    deadline: int
    status: InstructionStatus
    affirmations: _containers.RepeatedCompositeFieldContainer[Affirmation]
    failure_reason: str
    memo: str
    def __init__(self, id: _Optional[int] = ..., creator: _Optional[str] = ..., venue_id: _Optional[str] = ..., legs: _Optional[_Iterable[_Union[Leg, _Mapping]]] = ..., settlement_type: _Optional[_Union[SettlementType, str]] = ..., settle_height: _Optional[int] = ..., deadline: _Optional[int] = ..., status: _Optional[_Union[InstructionStatus, str]] = ..., affirmations: _Optional[_Iterable[_Union[Affirmation, _Mapping]]] = ..., failure_reason: _Optional[str] = ..., memo: _Optional[str] = ...) -> None: ...

class Venue(_message.Message):
    __slots__ = ("venue_id", "operator", "description", "allowed_creators")
    VENUE_ID_FIELD_NUMBER: _ClassVar[int]
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_CREATORS_FIELD_NUMBER: _ClassVar[int]
    venue_id: str
    operator: str
    description: str
    allowed_creators: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, venue_id: _Optional[str] = ..., operator: _Optional[str] = ..., description: _Optional[str] = ..., allowed_creators: _Optional[_Iterable[str]] = ...) -> None: ...

class Params(_message.Message):
    __slots__ = ("max_legs", "max_deadline_seconds")
    MAX_LEGS_FIELD_NUMBER: _ClassVar[int]
    MAX_DEADLINE_SECONDS_FIELD_NUMBER: _ClassVar[int]
    max_legs: int
    max_deadline_seconds: int
    def __init__(self, max_legs: _Optional[int] = ..., max_deadline_seconds: _Optional[int] = ...) -> None: ...

class GenesisState(_message.Message):
    __slots__ = ("params", "instructions", "venues", "next_instruction_id")
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    INSTRUCTIONS_FIELD_NUMBER: _ClassVar[int]
    VENUES_FIELD_NUMBER: _ClassVar[int]
    NEXT_INSTRUCTION_ID_FIELD_NUMBER: _ClassVar[int]
    params: Params
    instructions: _containers.RepeatedCompositeFieldContainer[Instruction]
    venues: _containers.RepeatedCompositeFieldContainer[Venue]
    next_instruction_id: int
    def __init__(self, params: _Optional[_Union[Params, _Mapping]] = ..., instructions: _Optional[_Iterable[_Union[Instruction, _Mapping]]] = ..., venues: _Optional[_Iterable[_Union[Venue, _Mapping]]] = ..., next_instruction_id: _Optional[int] = ...) -> None: ...

# SPDX-License-Identifier: Apache-2.0
from qorechain_asset_kit.gen.qorechain.settlement.v1 import settlement_pb2 as _settlement_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MsgCreateVenue(_message.Message):
    __slots__ = ("operator", "venue_id", "description", "allowed_creators")
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    VENUE_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_CREATORS_FIELD_NUMBER: _ClassVar[int]
    operator: str
    venue_id: str
    description: str
    allowed_creators: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, operator: _Optional[str] = ..., venue_id: _Optional[str] = ..., description: _Optional[str] = ..., allowed_creators: _Optional[_Iterable[str]] = ...) -> None: ...

class MsgCreateVenueResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MsgCreateInstruction(_message.Message):
    __slots__ = ("creator", "venue_id", "legs", "settlement_type", "settle_height", "deadline", "memo")
    CREATOR_FIELD_NUMBER: _ClassVar[int]
    VENUE_ID_FIELD_NUMBER: _ClassVar[int]
    LEGS_FIELD_NUMBER: _ClassVar[int]
    SETTLEMENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    SETTLE_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    DEADLINE_FIELD_NUMBER: _ClassVar[int]
    MEMO_FIELD_NUMBER: _ClassVar[int]
    creator: str
    venue_id: str
    legs: _containers.RepeatedCompositeFieldContainer[_settlement_pb2.Leg]
    settlement_type: _settlement_pb2.SettlementType
    settle_height: int
    deadline: int
    memo: str
    def __init__(self, creator: _Optional[str] = ..., venue_id: _Optional[str] = ..., legs: _Optional[_Iterable[_Union[_settlement_pb2.Leg, _Mapping]]] = ..., settlement_type: _Optional[_Union[_settlement_pb2.SettlementType, str]] = ..., settle_height: _Optional[int] = ..., deadline: _Optional[int] = ..., memo: _Optional[str] = ...) -> None: ...

class MsgCreateInstructionResponse(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class MsgAffirm(_message.Message):
    __slots__ = ("party", "id")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    party: str
    id: int
    def __init__(self, party: _Optional[str] = ..., id: _Optional[int] = ...) -> None: ...

class MsgAffirmResponse(_message.Message):
    __slots__ = ("executed",)
    EXECUTED_FIELD_NUMBER: _ClassVar[int]
    executed: bool
    def __init__(self, executed: _Optional[bool] = ...) -> None: ...

class MsgWithdrawAffirmation(_message.Message):
    __slots__ = ("party", "id")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    party: str
    id: int
    def __init__(self, party: _Optional[str] = ..., id: _Optional[int] = ...) -> None: ...

class MsgWithdrawAffirmationResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MsgExecuteInstruction(_message.Message):
    __slots__ = ("signer", "id")
    SIGNER_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    signer: str
    id: int
    def __init__(self, signer: _Optional[str] = ..., id: _Optional[int] = ...) -> None: ...

class MsgExecuteInstructionResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _settlement_pb2.InstructionStatus
    def __init__(self, status: _Optional[_Union[_settlement_pb2.InstructionStatus, str]] = ...) -> None: ...

class MsgCancelInstruction(_message.Message):
    __slots__ = ("signer", "id")
    SIGNER_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    signer: str
    id: int
    def __init__(self, signer: _Optional[str] = ..., id: _Optional[int] = ...) -> None: ...

class MsgCancelInstructionResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

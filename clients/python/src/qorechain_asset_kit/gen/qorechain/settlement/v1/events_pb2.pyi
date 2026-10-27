# SPDX-License-Identifier: Apache-2.0
from qorechain_asset_kit.gen.qorechain.settlement.v1 import settlement_pb2 as _settlement_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EventVenueCreated(_message.Message):
    __slots__ = ("venue_id", "operator")
    VENUE_ID_FIELD_NUMBER: _ClassVar[int]
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    venue_id: str
    operator: str
    def __init__(self, venue_id: _Optional[str] = ..., operator: _Optional[str] = ...) -> None: ...

class EventInstructionCreated(_message.Message):
    __slots__ = ("id", "creator", "venue_id", "legs", "settlement_type", "deadline")
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATOR_FIELD_NUMBER: _ClassVar[int]
    VENUE_ID_FIELD_NUMBER: _ClassVar[int]
    LEGS_FIELD_NUMBER: _ClassVar[int]
    SETTLEMENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    DEADLINE_FIELD_NUMBER: _ClassVar[int]
    id: int
    creator: str
    venue_id: str
    legs: _containers.RepeatedCompositeFieldContainer[_settlement_pb2.Leg]
    settlement_type: _settlement_pb2.SettlementType
    deadline: int
    def __init__(self, id: _Optional[int] = ..., creator: _Optional[str] = ..., venue_id: _Optional[str] = ..., legs: _Optional[_Iterable[_Union[_settlement_pb2.Leg, _Mapping]]] = ..., settlement_type: _Optional[_Union[_settlement_pb2.SettlementType, str]] = ..., deadline: _Optional[int] = ...) -> None: ...

class EventAffirmed(_message.Message):
    __slots__ = ("id", "party")
    ID_FIELD_NUMBER: _ClassVar[int]
    PARTY_FIELD_NUMBER: _ClassVar[int]
    id: int
    party: str
    def __init__(self, id: _Optional[int] = ..., party: _Optional[str] = ...) -> None: ...

class EventAffirmationWithdrawn(_message.Message):
    __slots__ = ("id", "party")
    ID_FIELD_NUMBER: _ClassVar[int]
    PARTY_FIELD_NUMBER: _ClassVar[int]
    id: int
    party: str
    def __init__(self, id: _Optional[int] = ..., party: _Optional[str] = ...) -> None: ...

class EventInstructionExecuted(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class EventInstructionFailed(_message.Message):
    __slots__ = ("id", "leg_index", "reason")
    ID_FIELD_NUMBER: _ClassVar[int]
    LEG_INDEX_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    id: int
    leg_index: int
    reason: str
    def __init__(self, id: _Optional[int] = ..., leg_index: _Optional[int] = ..., reason: _Optional[str] = ...) -> None: ...

class EventInstructionCancelled(_message.Message):
    __slots__ = ("id", "signer")
    ID_FIELD_NUMBER: _ClassVar[int]
    SIGNER_FIELD_NUMBER: _ClassVar[int]
    id: int
    signer: str
    def __init__(self, id: _Optional[int] = ..., signer: _Optional[str] = ...) -> None: ...

class EventInstructionExpired(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

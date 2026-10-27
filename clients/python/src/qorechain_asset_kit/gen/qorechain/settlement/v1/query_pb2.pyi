# SPDX-License-Identifier: Apache-2.0
from qorechain_asset_kit.gen.qorechain.settlement.v1 import settlement_pb2 as _settlement_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class QueryParamsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class QueryParamsResponse(_message.Message):
    __slots__ = ("params",)
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    params: _settlement_pb2.Params
    def __init__(self, params: _Optional[_Union[_settlement_pb2.Params, _Mapping]] = ...) -> None: ...

class QueryInstructionRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class QueryInstructionResponse(_message.Message):
    __slots__ = ("instruction",)
    INSTRUCTION_FIELD_NUMBER: _ClassVar[int]
    instruction: _settlement_pb2.Instruction
    def __init__(self, instruction: _Optional[_Union[_settlement_pb2.Instruction, _Mapping]] = ...) -> None: ...

class QueryInstructionsByPartyRequest(_message.Message):
    __slots__ = ("party", "status")
    PARTY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    party: str
    status: _settlement_pb2.InstructionStatus
    def __init__(self, party: _Optional[str] = ..., status: _Optional[_Union[_settlement_pb2.InstructionStatus, str]] = ...) -> None: ...

class QueryInstructionsByPartyResponse(_message.Message):
    __slots__ = ("instructions",)
    INSTRUCTIONS_FIELD_NUMBER: _ClassVar[int]
    instructions: _containers.RepeatedCompositeFieldContainer[_settlement_pb2.Instruction]
    def __init__(self, instructions: _Optional[_Iterable[_Union[_settlement_pb2.Instruction, _Mapping]]] = ...) -> None: ...

class QueryVenueRequest(_message.Message):
    __slots__ = ("venue_id",)
    VENUE_ID_FIELD_NUMBER: _ClassVar[int]
    venue_id: str
    def __init__(self, venue_id: _Optional[str] = ...) -> None: ...

class QueryVenueResponse(_message.Message):
    __slots__ = ("venue",)
    VENUE_FIELD_NUMBER: _ClassVar[int]
    venue: _settlement_pb2.Venue
    def __init__(self, venue: _Optional[_Union[_settlement_pb2.Venue, _Mapping]] = ...) -> None: ...

# SPDX-License-Identifier: Apache-2.0
from qorechain_asset_kit.gen.qorechain.attest.v1 import attest_pb2 as _attest_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EventAttesterChanged(_message.Message):
    __slots__ = ("asset_id", "address", "kinds", "removed")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    KINDS_FIELD_NUMBER: _ClassVar[int]
    REMOVED_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    address: str
    kinds: _containers.RepeatedScalarFieldContainer[_attest_pb2.AttestationKind]
    removed: bool
    def __init__(self, asset_id: _Optional[str] = ..., address: _Optional[str] = ..., kinds: _Optional[_Iterable[_Union[_attest_pb2.AttestationKind, str]]] = ..., removed: _Optional[bool] = ...) -> None: ...

class EventAttestationSubmitted(_message.Message):
    __slots__ = ("id", "asset_id", "kind", "attester", "value", "observed_at", "valid_for_seconds")
    ID_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    ATTESTER_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    OBSERVED_AT_FIELD_NUMBER: _ClassVar[int]
    VALID_FOR_SECONDS_FIELD_NUMBER: _ClassVar[int]
    id: int
    asset_id: str
    kind: _attest_pb2.AttestationKind
    attester: str
    value: str
    observed_at: int
    valid_for_seconds: int
    def __init__(self, id: _Optional[int] = ..., asset_id: _Optional[str] = ..., kind: _Optional[_Union[_attest_pb2.AttestationKind, str]] = ..., attester: _Optional[str] = ..., value: _Optional[str] = ..., observed_at: _Optional[int] = ..., valid_for_seconds: _Optional[int] = ...) -> None: ...

class EventAttestationRevoked(_message.Message):
    __slots__ = ("id", "signer", "reason")
    ID_FIELD_NUMBER: _ClassVar[int]
    SIGNER_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    id: int
    signer: str
    reason: str
    def __init__(self, id: _Optional[int] = ..., signer: _Optional[str] = ..., reason: _Optional[str] = ...) -> None: ...

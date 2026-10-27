# SPDX-License-Identifier: Apache-2.0
from qorechain_asset_kit.gen.qorechain.attest.v1 import attest_pb2 as _attest_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MsgSetAttester(_message.Message):
    __slots__ = ("issuer", "attester", "remove")
    ISSUER_FIELD_NUMBER: _ClassVar[int]
    ATTESTER_FIELD_NUMBER: _ClassVar[int]
    REMOVE_FIELD_NUMBER: _ClassVar[int]
    issuer: str
    attester: _attest_pb2.Attester
    remove: bool
    def __init__(self, issuer: _Optional[str] = ..., attester: _Optional[_Union[_attest_pb2.Attester, _Mapping]] = ..., remove: _Optional[bool] = ...) -> None: ...

class MsgSetAttesterResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MsgSubmit(_message.Message):
    __slots__ = ("attester", "asset_id", "kind", "value", "unit", "report_hash", "report_uri", "observed_at", "valid_for_seconds")
    ATTESTER_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    REPORT_HASH_FIELD_NUMBER: _ClassVar[int]
    REPORT_URI_FIELD_NUMBER: _ClassVar[int]
    OBSERVED_AT_FIELD_NUMBER: _ClassVar[int]
    VALID_FOR_SECONDS_FIELD_NUMBER: _ClassVar[int]
    attester: str
    asset_id: str
    kind: _attest_pb2.AttestationKind
    value: str
    unit: str
    report_hash: bytes
    report_uri: str
    observed_at: int
    valid_for_seconds: int
    def __init__(self, attester: _Optional[str] = ..., asset_id: _Optional[str] = ..., kind: _Optional[_Union[_attest_pb2.AttestationKind, str]] = ..., value: _Optional[str] = ..., unit: _Optional[str] = ..., report_hash: _Optional[bytes] = ..., report_uri: _Optional[str] = ..., observed_at: _Optional[int] = ..., valid_for_seconds: _Optional[int] = ...) -> None: ...

class MsgSubmitResponse(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class MsgRevoke(_message.Message):
    __slots__ = ("signer", "id", "reason")
    SIGNER_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    signer: str
    id: int
    reason: str
    def __init__(self, signer: _Optional[str] = ..., id: _Optional[int] = ..., reason: _Optional[str] = ...) -> None: ...

class MsgRevokeResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

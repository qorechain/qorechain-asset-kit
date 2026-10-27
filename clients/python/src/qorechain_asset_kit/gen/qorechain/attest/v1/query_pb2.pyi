# SPDX-License-Identifier: Apache-2.0
from qorechain_asset_kit.gen.qorechain.attest.v1 import attest_pb2 as _attest_pb2
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
    params: _attest_pb2.Params
    def __init__(self, params: _Optional[_Union[_attest_pb2.Params, _Mapping]] = ...) -> None: ...

class QueryLatestRequest(_message.Message):
    __slots__ = ("asset_id", "kind")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    kind: _attest_pb2.AttestationKind
    def __init__(self, asset_id: _Optional[str] = ..., kind: _Optional[_Union[_attest_pb2.AttestationKind, str]] = ...) -> None: ...

class QueryLatestResponse(_message.Message):
    __slots__ = ("attestation", "freshness", "stale_at")
    ATTESTATION_FIELD_NUMBER: _ClassVar[int]
    FRESHNESS_FIELD_NUMBER: _ClassVar[int]
    STALE_AT_FIELD_NUMBER: _ClassVar[int]
    attestation: _attest_pb2.Attestation
    freshness: _attest_pb2.Freshness
    stale_at: int
    def __init__(self, attestation: _Optional[_Union[_attest_pb2.Attestation, _Mapping]] = ..., freshness: _Optional[_Union[_attest_pb2.Freshness, str]] = ..., stale_at: _Optional[int] = ...) -> None: ...

class QueryHistoryRequest(_message.Message):
    __slots__ = ("asset_id", "kind", "limit")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    kind: _attest_pb2.AttestationKind
    limit: int
    def __init__(self, asset_id: _Optional[str] = ..., kind: _Optional[_Union[_attest_pb2.AttestationKind, str]] = ..., limit: _Optional[int] = ...) -> None: ...

class QueryHistoryResponse(_message.Message):
    __slots__ = ("attestations",)
    ATTESTATIONS_FIELD_NUMBER: _ClassVar[int]
    attestations: _containers.RepeatedCompositeFieldContainer[_attest_pb2.Attestation]
    def __init__(self, attestations: _Optional[_Iterable[_Union[_attest_pb2.Attestation, _Mapping]]] = ...) -> None: ...

class QueryAttestersRequest(_message.Message):
    __slots__ = ("asset_id",)
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    def __init__(self, asset_id: _Optional[str] = ...) -> None: ...

class QueryAttestersResponse(_message.Message):
    __slots__ = ("attesters",)
    ATTESTERS_FIELD_NUMBER: _ClassVar[int]
    attesters: _containers.RepeatedCompositeFieldContainer[_attest_pb2.Attester]
    def __init__(self, attesters: _Optional[_Iterable[_Union[_attest_pb2.Attester, _Mapping]]] = ...) -> None: ...

# SPDX-License-Identifier: Apache-2.0
from qorechain_asset_kit.gen.qorechain.identity.v1 import identity_pb2 as _identity_pb2
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
    params: _identity_pb2.Params
    def __init__(self, params: _Optional[_Union[_identity_pb2.Params, _Mapping]] = ...) -> None: ...

class QueryIdentityRequest(_message.Message):
    __slots__ = ("identity_id",)
    IDENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    identity_id: str
    def __init__(self, identity_id: _Optional[str] = ...) -> None: ...

class QueryIdentityResponse(_message.Message):
    __slots__ = ("identity",)
    IDENTITY_FIELD_NUMBER: _ClassVar[int]
    identity: _identity_pb2.Identity
    def __init__(self, identity: _Optional[_Union[_identity_pb2.Identity, _Mapping]] = ...) -> None: ...

class QueryIdentityByAddressRequest(_message.Message):
    __slots__ = ("address",)
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    address: str
    def __init__(self, address: _Optional[str] = ...) -> None: ...

class QueryIdentityByAddressResponse(_message.Message):
    __slots__ = ("identity",)
    IDENTITY_FIELD_NUMBER: _ClassVar[int]
    identity: _identity_pb2.Identity
    def __init__(self, identity: _Optional[_Union[_identity_pb2.Identity, _Mapping]] = ...) -> None: ...

class QueryClaimIssuersRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class QueryClaimIssuersResponse(_message.Message):
    __slots__ = ("claim_issuers",)
    CLAIM_ISSUERS_FIELD_NUMBER: _ClassVar[int]
    claim_issuers: _containers.RepeatedCompositeFieldContainer[_identity_pb2.ClaimIssuer]
    def __init__(self, claim_issuers: _Optional[_Iterable[_Union[_identity_pb2.ClaimIssuer, _Mapping]]] = ...) -> None: ...

class QueryIsVerifiedRequest(_message.Message):
    __slots__ = ("address", "topics")
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    TOPICS_FIELD_NUMBER: _ClassVar[int]
    address: str
    topics: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, address: _Optional[str] = ..., topics: _Optional[_Iterable[int]] = ...) -> None: ...

class QueryIsVerifiedResponse(_message.Message):
    __slots__ = ("verified", "missing_topics")
    VERIFIED_FIELD_NUMBER: _ClassVar[int]
    MISSING_TOPICS_FIELD_NUMBER: _ClassVar[int]
    verified: bool
    missing_topics: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, verified: _Optional[bool] = ..., missing_topics: _Optional[_Iterable[int]] = ...) -> None: ...

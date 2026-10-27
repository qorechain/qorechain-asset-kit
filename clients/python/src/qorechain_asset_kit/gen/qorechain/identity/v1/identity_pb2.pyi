# SPDX-License-Identifier: Apache-2.0
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ErrorCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ERROR_CODE_UNSPECIFIED: _ClassVar[ErrorCode]
    ERROR_CODE_IDENTITY_NOT_FOUND: _ClassVar[ErrorCode]
    ERROR_CODE_IDENTITY_EXISTS: _ClassVar[ErrorCode]
    ERROR_CODE_ADDRESS_ALREADY_BOUND: _ClassVar[ErrorCode]
    ERROR_CODE_NOT_IDENTITY_AGENT: _ClassVar[ErrorCode]
    ERROR_CODE_CLAIM_ISSUER_NOT_TRUSTED: _ClassVar[ErrorCode]
    ERROR_CODE_CLAIM_TOPIC_NOT_ALLOWED: _ClassVar[ErrorCode]
    ERROR_CODE_CLAIM_NOT_FOUND: _ClassVar[ErrorCode]
    ERROR_CODE_UNAUTHORIZED: _ClassVar[ErrorCode]
ERROR_CODE_UNSPECIFIED: ErrorCode
ERROR_CODE_IDENTITY_NOT_FOUND: ErrorCode
ERROR_CODE_IDENTITY_EXISTS: ErrorCode
ERROR_CODE_ADDRESS_ALREADY_BOUND: ErrorCode
ERROR_CODE_NOT_IDENTITY_AGENT: ErrorCode
ERROR_CODE_CLAIM_ISSUER_NOT_TRUSTED: ErrorCode
ERROR_CODE_CLAIM_TOPIC_NOT_ALLOWED: ErrorCode
ERROR_CODE_CLAIM_NOT_FOUND: ErrorCode
ERROR_CODE_UNAUTHORIZED: ErrorCode

class Claim(_message.Message):
    __slots__ = ("topic", "issuer", "data_hash", "valid_until", "revoked")
    TOPIC_FIELD_NUMBER: _ClassVar[int]
    ISSUER_FIELD_NUMBER: _ClassVar[int]
    DATA_HASH_FIELD_NUMBER: _ClassVar[int]
    VALID_UNTIL_FIELD_NUMBER: _ClassVar[int]
    REVOKED_FIELD_NUMBER: _ClassVar[int]
    topic: int
    issuer: str
    data_hash: bytes
    valid_until: int
    revoked: bool
    def __init__(self, topic: _Optional[int] = ..., issuer: _Optional[str] = ..., data_hash: _Optional[bytes] = ..., valid_until: _Optional[int] = ..., revoked: _Optional[bool] = ...) -> None: ...

class Identity(_message.Message):
    __slots__ = ("identity_id", "addresses", "country", "claims", "registered_by")
    IDENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    ADDRESSES_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    CLAIMS_FIELD_NUMBER: _ClassVar[int]
    REGISTERED_BY_FIELD_NUMBER: _ClassVar[int]
    identity_id: str
    addresses: _containers.RepeatedScalarFieldContainer[str]
    country: int
    claims: _containers.RepeatedCompositeFieldContainer[Claim]
    registered_by: str
    def __init__(self, identity_id: _Optional[str] = ..., addresses: _Optional[_Iterable[str]] = ..., country: _Optional[int] = ..., claims: _Optional[_Iterable[_Union[Claim, _Mapping]]] = ..., registered_by: _Optional[str] = ...) -> None: ...

class ClaimIssuer(_message.Message):
    __slots__ = ("address", "name", "topics")
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TOPICS_FIELD_NUMBER: _ClassVar[int]
    address: str
    name: str
    topics: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, address: _Optional[str] = ..., name: _Optional[str] = ..., topics: _Optional[_Iterable[int]] = ...) -> None: ...

class Params(_message.Message):
    __slots__ = ("identity_agents",)
    IDENTITY_AGENTS_FIELD_NUMBER: _ClassVar[int]
    identity_agents: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, identity_agents: _Optional[_Iterable[str]] = ...) -> None: ...

class GenesisState(_message.Message):
    __slots__ = ("params", "identities", "claim_issuers")
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    IDENTITIES_FIELD_NUMBER: _ClassVar[int]
    CLAIM_ISSUERS_FIELD_NUMBER: _ClassVar[int]
    params: Params
    identities: _containers.RepeatedCompositeFieldContainer[Identity]
    claim_issuers: _containers.RepeatedCompositeFieldContainer[ClaimIssuer]
    def __init__(self, params: _Optional[_Union[Params, _Mapping]] = ..., identities: _Optional[_Iterable[_Union[Identity, _Mapping]]] = ..., claim_issuers: _Optional[_Iterable[_Union[ClaimIssuer, _Mapping]]] = ...) -> None: ...

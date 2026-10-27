# SPDX-License-Identifier: Apache-2.0
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class EventIdentityRegistered(_message.Message):
    __slots__ = ("identity_id", "address", "country", "agent")
    IDENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    AGENT_FIELD_NUMBER: _ClassVar[int]
    identity_id: str
    address: str
    country: int
    agent: str
    def __init__(self, identity_id: _Optional[str] = ..., address: _Optional[str] = ..., country: _Optional[int] = ..., agent: _Optional[str] = ...) -> None: ...

class EventCountryUpdated(_message.Message):
    __slots__ = ("identity_id", "country")
    IDENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    identity_id: str
    country: int
    def __init__(self, identity_id: _Optional[str] = ..., country: _Optional[int] = ...) -> None: ...

class EventAddressBound(_message.Message):
    __slots__ = ("identity_id", "address", "bound")
    IDENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    BOUND_FIELD_NUMBER: _ClassVar[int]
    identity_id: str
    address: str
    bound: bool
    def __init__(self, identity_id: _Optional[str] = ..., address: _Optional[str] = ..., bound: _Optional[bool] = ...) -> None: ...

class EventClaimAdded(_message.Message):
    __slots__ = ("identity_id", "topic", "claim_issuer", "valid_until")
    IDENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    TOPIC_FIELD_NUMBER: _ClassVar[int]
    CLAIM_ISSUER_FIELD_NUMBER: _ClassVar[int]
    VALID_UNTIL_FIELD_NUMBER: _ClassVar[int]
    identity_id: str
    topic: int
    claim_issuer: str
    valid_until: int
    def __init__(self, identity_id: _Optional[str] = ..., topic: _Optional[int] = ..., claim_issuer: _Optional[str] = ..., valid_until: _Optional[int] = ...) -> None: ...

class EventClaimRevoked(_message.Message):
    __slots__ = ("identity_id", "topic", "claim_issuer")
    IDENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    TOPIC_FIELD_NUMBER: _ClassVar[int]
    CLAIM_ISSUER_FIELD_NUMBER: _ClassVar[int]
    identity_id: str
    topic: int
    claim_issuer: str
    def __init__(self, identity_id: _Optional[str] = ..., topic: _Optional[int] = ..., claim_issuer: _Optional[str] = ...) -> None: ...

class EventIdentityRemoved(_message.Message):
    __slots__ = ("identity_id",)
    IDENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    identity_id: str
    def __init__(self, identity_id: _Optional[str] = ...) -> None: ...

class EventClaimIssuerChanged(_message.Message):
    __slots__ = ("address", "topics", "removed")
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    TOPICS_FIELD_NUMBER: _ClassVar[int]
    REMOVED_FIELD_NUMBER: _ClassVar[int]
    address: str
    topics: _containers.RepeatedScalarFieldContainer[int]
    removed: bool
    def __init__(self, address: _Optional[str] = ..., topics: _Optional[_Iterable[int]] = ..., removed: _Optional[bool] = ...) -> None: ...

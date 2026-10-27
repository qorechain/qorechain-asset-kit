# SPDX-License-Identifier: Apache-2.0
from qorechain_asset_kit.gen.qorechain.identity.v1 import identity_pb2 as _identity_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MsgRegisterIdentity(_message.Message):
    __slots__ = ("agent", "identity_id", "address", "country")
    AGENT_FIELD_NUMBER: _ClassVar[int]
    IDENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    agent: str
    identity_id: str
    address: str
    country: int
    def __init__(self, agent: _Optional[str] = ..., identity_id: _Optional[str] = ..., address: _Optional[str] = ..., country: _Optional[int] = ...) -> None: ...

class MsgRegisterIdentityResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MsgUpdateCountry(_message.Message):
    __slots__ = ("agent", "identity_id", "country")
    AGENT_FIELD_NUMBER: _ClassVar[int]
    IDENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    agent: str
    identity_id: str
    country: int
    def __init__(self, agent: _Optional[str] = ..., identity_id: _Optional[str] = ..., country: _Optional[int] = ...) -> None: ...

class MsgUpdateCountryResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MsgBindAddress(_message.Message):
    __slots__ = ("agent", "identity_id", "address")
    AGENT_FIELD_NUMBER: _ClassVar[int]
    IDENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    agent: str
    identity_id: str
    address: str
    def __init__(self, agent: _Optional[str] = ..., identity_id: _Optional[str] = ..., address: _Optional[str] = ...) -> None: ...

class MsgBindAddressResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MsgUnbindAddress(_message.Message):
    __slots__ = ("agent", "identity_id", "address")
    AGENT_FIELD_NUMBER: _ClassVar[int]
    IDENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    agent: str
    identity_id: str
    address: str
    def __init__(self, agent: _Optional[str] = ..., identity_id: _Optional[str] = ..., address: _Optional[str] = ...) -> None: ...

class MsgUnbindAddressResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MsgAddClaim(_message.Message):
    __slots__ = ("claim_issuer", "identity_id", "topic", "data_hash", "valid_until")
    CLAIM_ISSUER_FIELD_NUMBER: _ClassVar[int]
    IDENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    TOPIC_FIELD_NUMBER: _ClassVar[int]
    DATA_HASH_FIELD_NUMBER: _ClassVar[int]
    VALID_UNTIL_FIELD_NUMBER: _ClassVar[int]
    claim_issuer: str
    identity_id: str
    topic: int
    data_hash: bytes
    valid_until: int
    def __init__(self, claim_issuer: _Optional[str] = ..., identity_id: _Optional[str] = ..., topic: _Optional[int] = ..., data_hash: _Optional[bytes] = ..., valid_until: _Optional[int] = ...) -> None: ...

class MsgAddClaimResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MsgRevokeClaim(_message.Message):
    __slots__ = ("claim_issuer", "identity_id", "topic")
    CLAIM_ISSUER_FIELD_NUMBER: _ClassVar[int]
    IDENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    TOPIC_FIELD_NUMBER: _ClassVar[int]
    claim_issuer: str
    identity_id: str
    topic: int
    def __init__(self, claim_issuer: _Optional[str] = ..., identity_id: _Optional[str] = ..., topic: _Optional[int] = ...) -> None: ...

class MsgRevokeClaimResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MsgRemoveIdentity(_message.Message):
    __slots__ = ("agent", "identity_id")
    AGENT_FIELD_NUMBER: _ClassVar[int]
    IDENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    agent: str
    identity_id: str
    def __init__(self, agent: _Optional[str] = ..., identity_id: _Optional[str] = ...) -> None: ...

class MsgRemoveIdentityResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MsgSetClaimIssuer(_message.Message):
    __slots__ = ("authority", "claim_issuer", "remove")
    AUTHORITY_FIELD_NUMBER: _ClassVar[int]
    CLAIM_ISSUER_FIELD_NUMBER: _ClassVar[int]
    REMOVE_FIELD_NUMBER: _ClassVar[int]
    authority: str
    claim_issuer: _identity_pb2.ClaimIssuer
    remove: bool
    def __init__(self, authority: _Optional[str] = ..., claim_issuer: _Optional[_Union[_identity_pb2.ClaimIssuer, _Mapping]] = ..., remove: _Optional[bool] = ...) -> None: ...

class MsgSetClaimIssuerResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

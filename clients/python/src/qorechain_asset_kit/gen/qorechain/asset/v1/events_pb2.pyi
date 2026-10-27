# SPDX-License-Identifier: Apache-2.0
from qorechain_asset_kit.gen.qorechain.asset.v1 import asset_pb2 as _asset_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EventAssetCreated(_message.Message):
    __slots__ = ("asset_id", "issuer", "flags", "max_supply")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    ISSUER_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    MAX_SUPPLY_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    issuer: str
    flags: _asset_pb2.RwaFlagsV0
    max_supply: str
    def __init__(self, asset_id: _Optional[str] = ..., issuer: _Optional[str] = ..., flags: _Optional[_Union[_asset_pb2.RwaFlagsV0, _Mapping]] = ..., max_supply: _Optional[str] = ...) -> None: ...

class EventFlagsUpdated(_message.Message):
    __slots__ = ("asset_id", "flags")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    flags: _asset_pb2.RwaFlagsV0
    def __init__(self, asset_id: _Optional[str] = ..., flags: _Optional[_Union[_asset_pb2.RwaFlagsV0, _Mapping]] = ...) -> None: ...

class EventRoleChanged(_message.Message):
    __slots__ = ("asset_id", "address", "role", "granted")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    GRANTED_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    address: str
    role: _asset_pb2.Role
    granted: bool
    def __init__(self, asset_id: _Optional[str] = ..., address: _Optional[str] = ..., role: _Optional[_Union[_asset_pb2.Role, str]] = ..., granted: _Optional[bool] = ...) -> None: ...

class EventIssuerTransferProposed(_message.Message):
    __slots__ = ("asset_id", "issuer", "new_issuer")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    ISSUER_FIELD_NUMBER: _ClassVar[int]
    NEW_ISSUER_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    issuer: str
    new_issuer: str
    def __init__(self, asset_id: _Optional[str] = ..., issuer: _Optional[str] = ..., new_issuer: _Optional[str] = ...) -> None: ...

class EventIssuerTransferred(_message.Message):
    __slots__ = ("asset_id", "previous_issuer", "new_issuer")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_ISSUER_FIELD_NUMBER: _ClassVar[int]
    NEW_ISSUER_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    previous_issuer: str
    new_issuer: str
    def __init__(self, asset_id: _Optional[str] = ..., previous_issuer: _Optional[str] = ..., new_issuer: _Optional[str] = ...) -> None: ...

class EventHolderAuthorized(_message.Message):
    __slots__ = ("asset_id", "holder", "authorized", "agent")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    HOLDER_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZED_FIELD_NUMBER: _ClassVar[int]
    AGENT_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    holder: str
    authorized: bool
    agent: str
    def __init__(self, asset_id: _Optional[str] = ..., holder: _Optional[str] = ..., authorized: _Optional[bool] = ..., agent: _Optional[str] = ...) -> None: ...

class EventMinted(_message.Message):
    __slots__ = ("asset_id", "to", "amount", "agent")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    AGENT_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    to: str
    amount: str
    agent: str
    def __init__(self, asset_id: _Optional[str] = ..., to: _Optional[str] = ..., amount: _Optional[str] = ..., agent: _Optional[str] = ...) -> None: ...

class EventBurned(_message.Message):
    __slots__ = ("asset_id", "amount", "agent")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    AGENT_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    amount: str
    agent: str
    def __init__(self, asset_id: _Optional[str] = ..., amount: _Optional[str] = ..., agent: _Optional[str] = ..., **kwargs) -> None: ...

class EventTransferred(_message.Message):
    __slots__ = ("asset_id", "to", "amount")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    to: str
    amount: str
    def __init__(self, asset_id: _Optional[str] = ..., to: _Optional[str] = ..., amount: _Optional[str] = ..., **kwargs) -> None: ...

class EventFrozen(_message.Message):
    __slots__ = ("asset_id", "holder", "frozen", "agent")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    HOLDER_FIELD_NUMBER: _ClassVar[int]
    FROZEN_FIELD_NUMBER: _ClassVar[int]
    AGENT_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    holder: str
    frozen: bool
    agent: str
    def __init__(self, asset_id: _Optional[str] = ..., holder: _Optional[str] = ..., frozen: _Optional[bool] = ..., agent: _Optional[str] = ...) -> None: ...

class EventPartiallyFrozen(_message.Message):
    __slots__ = ("asset_id", "holder", "frozen_amount", "agent")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    HOLDER_FIELD_NUMBER: _ClassVar[int]
    FROZEN_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    AGENT_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    holder: str
    frozen_amount: str
    agent: str
    def __init__(self, asset_id: _Optional[str] = ..., holder: _Optional[str] = ..., frozen_amount: _Optional[str] = ..., agent: _Optional[str] = ...) -> None: ...

class EventPaused(_message.Message):
    __slots__ = ("asset_id", "paused", "agent")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    PAUSED_FIELD_NUMBER: _ClassVar[int]
    AGENT_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    paused: bool
    agent: str
    def __init__(self, asset_id: _Optional[str] = ..., paused: _Optional[bool] = ..., agent: _Optional[str] = ...) -> None: ...

class EventClawback(_message.Message):
    __slots__ = ("asset_id", "amount", "agent", "reason")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    AGENT_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    amount: str
    agent: str
    reason: str
    def __init__(self, asset_id: _Optional[str] = ..., amount: _Optional[str] = ..., agent: _Optional[str] = ..., reason: _Optional[str] = ..., **kwargs) -> None: ...

class EventForcedTransfer(_message.Message):
    __slots__ = ("asset_id", "to", "amount", "agent", "reason")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    AGENT_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    to: str
    amount: str
    agent: str
    reason: str
    def __init__(self, asset_id: _Optional[str] = ..., to: _Optional[str] = ..., amount: _Optional[str] = ..., agent: _Optional[str] = ..., reason: _Optional[str] = ..., **kwargs) -> None: ...

class EventTermsUpdated(_message.Message):
    __slots__ = ("asset_id", "terms_hash", "terms_uri")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    TERMS_HASH_FIELD_NUMBER: _ClassVar[int]
    TERMS_URI_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    terms_hash: bytes
    terms_uri: str
    def __init__(self, asset_id: _Optional[str] = ..., terms_hash: _Optional[bytes] = ..., terms_uri: _Optional[str] = ...) -> None: ...

class EventRetired(_message.Message):
    __slots__ = ("asset_id",)
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    def __init__(self, asset_id: _Optional[str] = ...) -> None: ...

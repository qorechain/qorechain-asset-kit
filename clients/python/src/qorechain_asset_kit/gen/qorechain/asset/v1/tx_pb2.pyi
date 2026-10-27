# SPDX-License-Identifier: Apache-2.0
from qorechain_asset_kit.gen.qorechain.asset.v1 import asset_pb2 as _asset_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MsgCreateAsset(_message.Message):
    __slots__ = ("issuer", "asset_id", "name", "symbol", "decimals", "flags", "max_supply", "terms_hash", "terms_uri")
    ISSUER_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    DECIMALS_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    MAX_SUPPLY_FIELD_NUMBER: _ClassVar[int]
    TERMS_HASH_FIELD_NUMBER: _ClassVar[int]
    TERMS_URI_FIELD_NUMBER: _ClassVar[int]
    issuer: str
    asset_id: str
    name: str
    symbol: str
    decimals: int
    flags: _asset_pb2.RwaFlagsV0
    max_supply: str
    terms_hash: bytes
    terms_uri: str
    def __init__(self, issuer: _Optional[str] = ..., asset_id: _Optional[str] = ..., name: _Optional[str] = ..., symbol: _Optional[str] = ..., decimals: _Optional[int] = ..., flags: _Optional[_Union[_asset_pb2.RwaFlagsV0, _Mapping]] = ..., max_supply: _Optional[str] = ..., terms_hash: _Optional[bytes] = ..., terms_uri: _Optional[str] = ...) -> None: ...

class MsgCreateAssetResponse(_message.Message):
    __slots__ = ("denom",)
    DENOM_FIELD_NUMBER: _ClassVar[int]
    denom: str
    def __init__(self, denom: _Optional[str] = ...) -> None: ...

class MsgUpdateFlags(_message.Message):
    __slots__ = ("issuer", "asset_id", "flags")
    ISSUER_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    issuer: str
    asset_id: str
    flags: _asset_pb2.RwaFlagsV0
    def __init__(self, issuer: _Optional[str] = ..., asset_id: _Optional[str] = ..., flags: _Optional[_Union[_asset_pb2.RwaFlagsV0, _Mapping]] = ...) -> None: ...

class MsgUpdateFlagsResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MsgSetRole(_message.Message):
    __slots__ = ("issuer", "asset_id", "address", "role", "granted")
    ISSUER_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    GRANTED_FIELD_NUMBER: _ClassVar[int]
    issuer: str
    asset_id: str
    address: str
    role: _asset_pb2.Role
    granted: bool
    def __init__(self, issuer: _Optional[str] = ..., asset_id: _Optional[str] = ..., address: _Optional[str] = ..., role: _Optional[_Union[_asset_pb2.Role, str]] = ..., granted: _Optional[bool] = ...) -> None: ...

class MsgSetRoleResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MsgProposeIssuer(_message.Message):
    __slots__ = ("issuer", "asset_id", "new_issuer")
    ISSUER_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    NEW_ISSUER_FIELD_NUMBER: _ClassVar[int]
    issuer: str
    asset_id: str
    new_issuer: str
    def __init__(self, issuer: _Optional[str] = ..., asset_id: _Optional[str] = ..., new_issuer: _Optional[str] = ...) -> None: ...

class MsgProposeIssuerResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MsgAcceptIssuer(_message.Message):
    __slots__ = ("new_issuer", "asset_id")
    NEW_ISSUER_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    new_issuer: str
    asset_id: str
    def __init__(self, new_issuer: _Optional[str] = ..., asset_id: _Optional[str] = ...) -> None: ...

class MsgAcceptIssuerResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MsgAuthorizeHolder(_message.Message):
    __slots__ = ("agent", "asset_id", "holder", "authorized")
    AGENT_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    HOLDER_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZED_FIELD_NUMBER: _ClassVar[int]
    agent: str
    asset_id: str
    holder: str
    authorized: bool
    def __init__(self, agent: _Optional[str] = ..., asset_id: _Optional[str] = ..., holder: _Optional[str] = ..., authorized: _Optional[bool] = ...) -> None: ...

class MsgAuthorizeHolderResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MsgMint(_message.Message):
    __slots__ = ("agent", "asset_id", "to", "amount")
    AGENT_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    agent: str
    asset_id: str
    to: str
    amount: str
    def __init__(self, agent: _Optional[str] = ..., asset_id: _Optional[str] = ..., to: _Optional[str] = ..., amount: _Optional[str] = ...) -> None: ...

class MsgMintResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MsgBurn(_message.Message):
    __slots__ = ("agent", "asset_id", "amount")
    AGENT_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    agent: str
    asset_id: str
    amount: str
    def __init__(self, agent: _Optional[str] = ..., asset_id: _Optional[str] = ..., amount: _Optional[str] = ..., **kwargs) -> None: ...

class MsgBurnResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MsgTransfer(_message.Message):
    __slots__ = ("asset_id", "to", "amount")
    FROM_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    to: str
    amount: str
    def __init__(self, asset_id: _Optional[str] = ..., to: _Optional[str] = ..., amount: _Optional[str] = ..., **kwargs) -> None: ...

class MsgTransferResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MsgFreeze(_message.Message):
    __slots__ = ("agent", "asset_id", "holder", "frozen")
    AGENT_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    HOLDER_FIELD_NUMBER: _ClassVar[int]
    FROZEN_FIELD_NUMBER: _ClassVar[int]
    agent: str
    asset_id: str
    holder: str
    frozen: bool
    def __init__(self, agent: _Optional[str] = ..., asset_id: _Optional[str] = ..., holder: _Optional[str] = ..., frozen: _Optional[bool] = ...) -> None: ...

class MsgFreezeResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MsgFreezePartial(_message.Message):
    __slots__ = ("agent", "asset_id", "holder", "frozen_amount")
    AGENT_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    HOLDER_FIELD_NUMBER: _ClassVar[int]
    FROZEN_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    agent: str
    asset_id: str
    holder: str
    frozen_amount: str
    def __init__(self, agent: _Optional[str] = ..., asset_id: _Optional[str] = ..., holder: _Optional[str] = ..., frozen_amount: _Optional[str] = ...) -> None: ...

class MsgFreezePartialResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MsgPause(_message.Message):
    __slots__ = ("agent", "asset_id", "paused")
    AGENT_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    PAUSED_FIELD_NUMBER: _ClassVar[int]
    agent: str
    asset_id: str
    paused: bool
    def __init__(self, agent: _Optional[str] = ..., asset_id: _Optional[str] = ..., paused: _Optional[bool] = ...) -> None: ...

class MsgPauseResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MsgClawback(_message.Message):
    __slots__ = ("agent", "asset_id", "amount", "reason")
    AGENT_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    agent: str
    asset_id: str
    amount: str
    reason: str
    def __init__(self, agent: _Optional[str] = ..., asset_id: _Optional[str] = ..., amount: _Optional[str] = ..., reason: _Optional[str] = ..., **kwargs) -> None: ...

class MsgClawbackResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MsgForceTransfer(_message.Message):
    __slots__ = ("agent", "asset_id", "to", "amount", "reason")
    AGENT_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    agent: str
    asset_id: str
    to: str
    amount: str
    reason: str
    def __init__(self, agent: _Optional[str] = ..., asset_id: _Optional[str] = ..., to: _Optional[str] = ..., amount: _Optional[str] = ..., reason: _Optional[str] = ..., **kwargs) -> None: ...

class MsgForceTransferResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MsgSetTerms(_message.Message):
    __slots__ = ("issuer", "asset_id", "terms_hash", "terms_uri")
    ISSUER_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    TERMS_HASH_FIELD_NUMBER: _ClassVar[int]
    TERMS_URI_FIELD_NUMBER: _ClassVar[int]
    issuer: str
    asset_id: str
    terms_hash: bytes
    terms_uri: str
    def __init__(self, issuer: _Optional[str] = ..., asset_id: _Optional[str] = ..., terms_hash: _Optional[bytes] = ..., terms_uri: _Optional[str] = ...) -> None: ...

class MsgSetTermsResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MsgRetire(_message.Message):
    __slots__ = ("issuer", "asset_id")
    ISSUER_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    issuer: str
    asset_id: str
    def __init__(self, issuer: _Optional[str] = ..., asset_id: _Optional[str] = ...) -> None: ...

class MsgRetireResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

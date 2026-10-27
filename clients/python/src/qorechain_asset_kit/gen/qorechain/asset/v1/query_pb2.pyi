# SPDX-License-Identifier: Apache-2.0
from qorechain_asset_kit.gen.qorechain.asset.v1 import asset_pb2 as _asset_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PageRequest(_message.Message):
    __slots__ = ("key", "limit")
    KEY_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    key: bytes
    limit: int
    def __init__(self, key: _Optional[bytes] = ..., limit: _Optional[int] = ...) -> None: ...

class PageResponse(_message.Message):
    __slots__ = ("next_key",)
    NEXT_KEY_FIELD_NUMBER: _ClassVar[int]
    next_key: bytes
    def __init__(self, next_key: _Optional[bytes] = ...) -> None: ...

class QueryParamsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class QueryParamsResponse(_message.Message):
    __slots__ = ("params",)
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    params: _asset_pb2.Params
    def __init__(self, params: _Optional[_Union[_asset_pb2.Params, _Mapping]] = ...) -> None: ...

class QueryAssetRequest(_message.Message):
    __slots__ = ("asset_id",)
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    def __init__(self, asset_id: _Optional[str] = ...) -> None: ...

class QueryAssetResponse(_message.Message):
    __slots__ = ("asset",)
    ASSET_FIELD_NUMBER: _ClassVar[int]
    asset: _asset_pb2.Asset
    def __init__(self, asset: _Optional[_Union[_asset_pb2.Asset, _Mapping]] = ...) -> None: ...

class QueryAssetsRequest(_message.Message):
    __slots__ = ("issuer", "pagination")
    ISSUER_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    issuer: str
    pagination: PageRequest
    def __init__(self, issuer: _Optional[str] = ..., pagination: _Optional[_Union[PageRequest, _Mapping]] = ...) -> None: ...

class QueryAssetsResponse(_message.Message):
    __slots__ = ("assets", "pagination")
    ASSETS_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    assets: _containers.RepeatedCompositeFieldContainer[_asset_pb2.Asset]
    pagination: PageResponse
    def __init__(self, assets: _Optional[_Iterable[_Union[_asset_pb2.Asset, _Mapping]]] = ..., pagination: _Optional[_Union[PageResponse, _Mapping]] = ...) -> None: ...

class QueryHolderRequest(_message.Message):
    __slots__ = ("asset_id", "address")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    address: str
    def __init__(self, asset_id: _Optional[str] = ..., address: _Optional[str] = ...) -> None: ...

class QueryHolderResponse(_message.Message):
    __slots__ = ("holder",)
    HOLDER_FIELD_NUMBER: _ClassVar[int]
    holder: _asset_pb2.HolderState
    def __init__(self, holder: _Optional[_Union[_asset_pb2.HolderState, _Mapping]] = ...) -> None: ...

class QueryHoldersRequest(_message.Message):
    __slots__ = ("asset_id", "pagination")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    pagination: PageRequest
    def __init__(self, asset_id: _Optional[str] = ..., pagination: _Optional[_Union[PageRequest, _Mapping]] = ...) -> None: ...

class QueryHoldersResponse(_message.Message):
    __slots__ = ("holders", "pagination")
    HOLDERS_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    holders: _containers.RepeatedCompositeFieldContainer[_asset_pb2.HolderState]
    pagination: PageResponse
    def __init__(self, holders: _Optional[_Iterable[_Union[_asset_pb2.HolderState, _Mapping]]] = ..., pagination: _Optional[_Union[PageResponse, _Mapping]] = ...) -> None: ...

class QueryRolesRequest(_message.Message):
    __slots__ = ("asset_id",)
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    def __init__(self, asset_id: _Optional[str] = ...) -> None: ...

class QueryRolesResponse(_message.Message):
    __slots__ = ("roles",)
    ROLES_FIELD_NUMBER: _ClassVar[int]
    roles: _containers.RepeatedCompositeFieldContainer[_asset_pb2.RoleGrant]
    def __init__(self, roles: _Optional[_Iterable[_Union[_asset_pb2.RoleGrant, _Mapping]]] = ...) -> None: ...

class QueryCanTransferRequest(_message.Message):
    __slots__ = ("asset_id", "to", "amount")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    to: str
    amount: str
    def __init__(self, asset_id: _Optional[str] = ..., to: _Optional[str] = ..., amount: _Optional[str] = ..., **kwargs) -> None: ...

class QueryCanTransferResponse(_message.Message):
    __slots__ = ("allowed", "code", "compliance_module_id", "reason")
    ALLOWED_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    COMPLIANCE_MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    allowed: bool
    code: _asset_pb2.ErrorCode
    compliance_module_id: str
    reason: str
    def __init__(self, allowed: _Optional[bool] = ..., code: _Optional[_Union[_asset_pb2.ErrorCode, str]] = ..., compliance_module_id: _Optional[str] = ..., reason: _Optional[str] = ...) -> None: ...

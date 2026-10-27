# SPDX-License-Identifier: Apache-2.0
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Role(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ROLE_UNSPECIFIED: _ClassVar[Role]
    ROLE_ISSUER: _ClassVar[Role]
    ROLE_AGENT: _ClassVar[Role]
    ROLE_AUDITOR: _ClassVar[Role]

class AssetStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ASSET_STATUS_UNSPECIFIED: _ClassVar[AssetStatus]
    ASSET_STATUS_ACTIVE: _ClassVar[AssetStatus]
    ASSET_STATUS_PAUSED: _ClassVar[AssetStatus]
    ASSET_STATUS_RETIRED: _ClassVar[AssetStatus]

class ErrorCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ERROR_CODE_UNSPECIFIED: _ClassVar[ErrorCode]
    ERROR_CODE_ASSET_NOT_FOUND: _ClassVar[ErrorCode]
    ERROR_CODE_ASSET_EXISTS: _ClassVar[ErrorCode]
    ERROR_CODE_UNAUTHORIZED_ROLE: _ClassVar[ErrorCode]
    ERROR_CODE_HOLDER_NOT_AUTHORIZED: _ClassVar[ErrorCode]
    ERROR_CODE_ADDRESS_FROZEN: _ClassVar[ErrorCode]
    ERROR_CODE_INSUFFICIENT_UNFROZEN_BALANCE: _ClassVar[ErrorCode]
    ERROR_CODE_ASSET_PAUSED: _ClassVar[ErrorCode]
    ERROR_CODE_NON_TRANSFERABLE: _ClassVar[ErrorCode]
    ERROR_CODE_SUPPLY_CAP_EXCEEDED: _ClassVar[ErrorCode]
    ERROR_CODE_HYBRID_SIGNATURE_REQUIRED: _ClassVar[ErrorCode]
    ERROR_CODE_COMPLIANCE_REJECTED: _ClassVar[ErrorCode]
    ERROR_CODE_INSUFFICIENT_BALANCE: _ClassVar[ErrorCode]
    ERROR_CODE_FLAG_IMMUTABLE: _ClassVar[ErrorCode]
    ERROR_CODE_FLAG_NOT_ENABLED: _ClassVar[ErrorCode]
    ERROR_CODE_INVALID_AMOUNT: _ClassVar[ErrorCode]
    ERROR_CODE_ASSET_RETIRED: _ClassVar[ErrorCode]
    ERROR_CODE_TOO_MANY_AGENTS: _ClassVar[ErrorCode]
    ERROR_CODE_INVALID_ASSET_ID: _ClassVar[ErrorCode]
ROLE_UNSPECIFIED: Role
ROLE_ISSUER: Role
ROLE_AGENT: Role
ROLE_AUDITOR: Role
ASSET_STATUS_UNSPECIFIED: AssetStatus
ASSET_STATUS_ACTIVE: AssetStatus
ASSET_STATUS_PAUSED: AssetStatus
ASSET_STATUS_RETIRED: AssetStatus
ERROR_CODE_UNSPECIFIED: ErrorCode
ERROR_CODE_ASSET_NOT_FOUND: ErrorCode
ERROR_CODE_ASSET_EXISTS: ErrorCode
ERROR_CODE_UNAUTHORIZED_ROLE: ErrorCode
ERROR_CODE_HOLDER_NOT_AUTHORIZED: ErrorCode
ERROR_CODE_ADDRESS_FROZEN: ErrorCode
ERROR_CODE_INSUFFICIENT_UNFROZEN_BALANCE: ErrorCode
ERROR_CODE_ASSET_PAUSED: ErrorCode
ERROR_CODE_NON_TRANSFERABLE: ErrorCode
ERROR_CODE_SUPPLY_CAP_EXCEEDED: ErrorCode
ERROR_CODE_HYBRID_SIGNATURE_REQUIRED: ErrorCode
ERROR_CODE_COMPLIANCE_REJECTED: ErrorCode
ERROR_CODE_INSUFFICIENT_BALANCE: ErrorCode
ERROR_CODE_FLAG_IMMUTABLE: ErrorCode
ERROR_CODE_FLAG_NOT_ENABLED: ErrorCode
ERROR_CODE_INVALID_AMOUNT: ErrorCode
ERROR_CODE_ASSET_RETIRED: ErrorCode
ERROR_CODE_TOO_MANY_AGENTS: ErrorCode
ERROR_CODE_INVALID_ASSET_ID: ErrorCode

class RwaFlagsV0(_message.Message):
    __slots__ = ("require_auth", "freezable", "pausable", "non_transferable", "supply_cap", "require_hybrid_signature")
    REQUIRE_AUTH_FIELD_NUMBER: _ClassVar[int]
    FREEZABLE_FIELD_NUMBER: _ClassVar[int]
    PAUSABLE_FIELD_NUMBER: _ClassVar[int]
    NON_TRANSFERABLE_FIELD_NUMBER: _ClassVar[int]
    SUPPLY_CAP_FIELD_NUMBER: _ClassVar[int]
    REQUIRE_HYBRID_SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    require_auth: bool
    freezable: bool
    pausable: bool
    non_transferable: bool
    supply_cap: bool
    require_hybrid_signature: bool
    def __init__(self, require_auth: _Optional[bool] = ..., freezable: _Optional[bool] = ..., pausable: _Optional[bool] = ..., non_transferable: _Optional[bool] = ..., supply_cap: _Optional[bool] = ..., require_hybrid_signature: _Optional[bool] = ...) -> None: ...

class Asset(_message.Message):
    __slots__ = ("asset_id", "issuer", "pending_issuer", "name", "symbol", "decimals", "flags", "max_supply", "total_supply", "status", "terms_hash", "terms_uri", "compliance_module_ids", "created_height")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    ISSUER_FIELD_NUMBER: _ClassVar[int]
    PENDING_ISSUER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    DECIMALS_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    MAX_SUPPLY_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SUPPLY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TERMS_HASH_FIELD_NUMBER: _ClassVar[int]
    TERMS_URI_FIELD_NUMBER: _ClassVar[int]
    COMPLIANCE_MODULE_IDS_FIELD_NUMBER: _ClassVar[int]
    CREATED_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    issuer: str
    pending_issuer: str
    name: str
    symbol: str
    decimals: int
    flags: RwaFlagsV0
    max_supply: str
    total_supply: str
    status: AssetStatus
    terms_hash: bytes
    terms_uri: str
    compliance_module_ids: _containers.RepeatedScalarFieldContainer[str]
    created_height: int
    def __init__(self, asset_id: _Optional[str] = ..., issuer: _Optional[str] = ..., pending_issuer: _Optional[str] = ..., name: _Optional[str] = ..., symbol: _Optional[str] = ..., decimals: _Optional[int] = ..., flags: _Optional[_Union[RwaFlagsV0, _Mapping]] = ..., max_supply: _Optional[str] = ..., total_supply: _Optional[str] = ..., status: _Optional[_Union[AssetStatus, str]] = ..., terms_hash: _Optional[bytes] = ..., terms_uri: _Optional[str] = ..., compliance_module_ids: _Optional[_Iterable[str]] = ..., created_height: _Optional[int] = ...) -> None: ...

class RoleGrant(_message.Message):
    __slots__ = ("asset_id", "address", "role", "granted_height")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    GRANTED_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    address: str
    role: Role
    granted_height: int
    def __init__(self, asset_id: _Optional[str] = ..., address: _Optional[str] = ..., role: _Optional[_Union[Role, str]] = ..., granted_height: _Optional[int] = ...) -> None: ...

class HolderState(_message.Message):
    __slots__ = ("asset_id", "address", "balance", "authorized", "frozen", "frozen_amount")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZED_FIELD_NUMBER: _ClassVar[int]
    FROZEN_FIELD_NUMBER: _ClassVar[int]
    FROZEN_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    address: str
    balance: str
    authorized: bool
    frozen: bool
    frozen_amount: str
    def __init__(self, asset_id: _Optional[str] = ..., address: _Optional[str] = ..., balance: _Optional[str] = ..., authorized: _Optional[bool] = ..., frozen: _Optional[bool] = ..., frozen_amount: _Optional[str] = ...) -> None: ...

class Params(_message.Message):
    __slots__ = ("creation_fee", "max_agents", "max_compliance_modules")
    CREATION_FEE_FIELD_NUMBER: _ClassVar[int]
    MAX_AGENTS_FIELD_NUMBER: _ClassVar[int]
    MAX_COMPLIANCE_MODULES_FIELD_NUMBER: _ClassVar[int]
    creation_fee: str
    max_agents: int
    max_compliance_modules: int
    def __init__(self, creation_fee: _Optional[str] = ..., max_agents: _Optional[int] = ..., max_compliance_modules: _Optional[int] = ...) -> None: ...

class GenesisState(_message.Message):
    __slots__ = ("params", "assets", "roles", "holders")
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    ASSETS_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    HOLDERS_FIELD_NUMBER: _ClassVar[int]
    params: Params
    assets: _containers.RepeatedCompositeFieldContainer[Asset]
    roles: _containers.RepeatedCompositeFieldContainer[RoleGrant]
    holders: _containers.RepeatedCompositeFieldContainer[HolderState]
    def __init__(self, params: _Optional[_Union[Params, _Mapping]] = ..., assets: _Optional[_Iterable[_Union[Asset, _Mapping]]] = ..., roles: _Optional[_Iterable[_Union[RoleGrant, _Mapping]]] = ..., holders: _Optional[_Iterable[_Union[HolderState, _Mapping]]] = ...) -> None: ...

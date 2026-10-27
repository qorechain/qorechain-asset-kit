# SPDX-License-Identifier: Apache-2.0
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ModuleRuntime(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MODULE_RUNTIME_UNSPECIFIED: _ClassVar[ModuleRuntime]
    MODULE_RUNTIME_NATIVE: _ClassVar[ModuleRuntime]
    MODULE_RUNTIME_WASM: _ClassVar[ModuleRuntime]

class ModuleStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MODULE_STATUS_UNSPECIFIED: _ClassVar[ModuleStatus]
    MODULE_STATUS_ACTIVE: _ClassVar[ModuleStatus]
    MODULE_STATUS_DEPRECATED: _ClassVar[ModuleStatus]
    MODULE_STATUS_DISABLED: _ClassVar[ModuleStatus]

class ErrorCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ERROR_CODE_UNSPECIFIED: _ClassVar[ErrorCode]
    ERROR_CODE_MODULE_NOT_FOUND: _ClassVar[ErrorCode]
    ERROR_CODE_MODULE_VERSION_EXISTS: _ClassVar[ErrorCode]
    ERROR_CODE_MODULE_DEPRECATED: _ClassVar[ErrorCode]
    ERROR_CODE_MODULE_DISABLED: _ClassVar[ErrorCode]
    ERROR_CODE_INVALID_PARAMS: _ClassVar[ErrorCode]
    ERROR_CODE_BINDING_NOT_FOUND: _ClassVar[ErrorCode]
    ERROR_CODE_BINDING_EXISTS: _ClassVar[ErrorCode]
    ERROR_CODE_TRANSFER_REJECTED: _ClassVar[ErrorCode]
    ERROR_CODE_TOO_MANY_BINDINGS: _ClassVar[ErrorCode]
    ERROR_CODE_NOT_ISSUER: _ClassVar[ErrorCode]
    ERROR_CODE_UNAUTHORIZED: _ClassVar[ErrorCode]
MODULE_RUNTIME_UNSPECIFIED: ModuleRuntime
MODULE_RUNTIME_NATIVE: ModuleRuntime
MODULE_RUNTIME_WASM: ModuleRuntime
MODULE_STATUS_UNSPECIFIED: ModuleStatus
MODULE_STATUS_ACTIVE: ModuleStatus
MODULE_STATUS_DEPRECATED: ModuleStatus
MODULE_STATUS_DISABLED: ModuleStatus
ERROR_CODE_UNSPECIFIED: ErrorCode
ERROR_CODE_MODULE_NOT_FOUND: ErrorCode
ERROR_CODE_MODULE_VERSION_EXISTS: ErrorCode
ERROR_CODE_MODULE_DEPRECATED: ErrorCode
ERROR_CODE_MODULE_DISABLED: ErrorCode
ERROR_CODE_INVALID_PARAMS: ErrorCode
ERROR_CODE_BINDING_NOT_FOUND: ErrorCode
ERROR_CODE_BINDING_EXISTS: ErrorCode
ERROR_CODE_TRANSFER_REJECTED: ErrorCode
ERROR_CODE_TOO_MANY_BINDINGS: ErrorCode
ERROR_CODE_NOT_ISSUER: ErrorCode
ERROR_CODE_UNAUTHORIZED: ErrorCode

class ComplianceModule(_message.Message):
    __slots__ = ("module_id", "version", "runtime", "code_ref", "status", "params_schema", "description")
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_FIELD_NUMBER: _ClassVar[int]
    CODE_REF_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PARAMS_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    module_id: str
    version: int
    runtime: ModuleRuntime
    code_ref: str
    status: ModuleStatus
    params_schema: str
    description: str
    def __init__(self, module_id: _Optional[str] = ..., version: _Optional[int] = ..., runtime: _Optional[_Union[ModuleRuntime, str]] = ..., code_ref: _Optional[str] = ..., status: _Optional[_Union[ModuleStatus, str]] = ..., params_schema: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class Binding(_message.Message):
    __slots__ = ("asset_id", "module_id", "version", "params_json", "position")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    PARAMS_JSON_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    module_id: str
    version: int
    params_json: str
    position: int
    def __init__(self, asset_id: _Optional[str] = ..., module_id: _Optional[str] = ..., version: _Optional[int] = ..., params_json: _Optional[str] = ..., position: _Optional[int] = ...) -> None: ...

class ModuleState(_message.Message):
    __slots__ = ("asset_id", "module_id", "state")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    module_id: str
    state: bytes
    def __init__(self, asset_id: _Optional[str] = ..., module_id: _Optional[str] = ..., state: _Optional[bytes] = ...) -> None: ...

class Params(_message.Message):
    __slots__ = ("max_module_gas",)
    MAX_MODULE_GAS_FIELD_NUMBER: _ClassVar[int]
    max_module_gas: int
    def __init__(self, max_module_gas: _Optional[int] = ...) -> None: ...

class GenesisState(_message.Message):
    __slots__ = ("params", "modules", "bindings", "states")
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    MODULES_FIELD_NUMBER: _ClassVar[int]
    BINDINGS_FIELD_NUMBER: _ClassVar[int]
    STATES_FIELD_NUMBER: _ClassVar[int]
    params: Params
    modules: _containers.RepeatedCompositeFieldContainer[ComplianceModule]
    bindings: _containers.RepeatedCompositeFieldContainer[Binding]
    states: _containers.RepeatedCompositeFieldContainer[ModuleState]
    def __init__(self, params: _Optional[_Union[Params, _Mapping]] = ..., modules: _Optional[_Iterable[_Union[ComplianceModule, _Mapping]]] = ..., bindings: _Optional[_Iterable[_Union[Binding, _Mapping]]] = ..., states: _Optional[_Iterable[_Union[ModuleState, _Mapping]]] = ...) -> None: ...

# SPDX-License-Identifier: Apache-2.0
from qorechain_asset_kit.gen.qorechain.compliance.v1 import compliance_pb2 as _compliance_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EventModuleRegistered(_message.Message):
    __slots__ = ("module_id", "version", "runtime")
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_FIELD_NUMBER: _ClassVar[int]
    module_id: str
    version: int
    runtime: _compliance_pb2.ModuleRuntime
    def __init__(self, module_id: _Optional[str] = ..., version: _Optional[int] = ..., runtime: _Optional[_Union[_compliance_pb2.ModuleRuntime, str]] = ...) -> None: ...

class EventModuleStatusChanged(_message.Message):
    __slots__ = ("module_id", "version", "status")
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    module_id: str
    version: int
    status: _compliance_pb2.ModuleStatus
    def __init__(self, module_id: _Optional[str] = ..., version: _Optional[int] = ..., status: _Optional[_Union[_compliance_pb2.ModuleStatus, str]] = ...) -> None: ...

class EventModuleBound(_message.Message):
    __slots__ = ("asset_id", "module_id", "version")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    module_id: str
    version: int
    def __init__(self, asset_id: _Optional[str] = ..., module_id: _Optional[str] = ..., version: _Optional[int] = ...) -> None: ...

class EventModuleUnbound(_message.Message):
    __slots__ = ("asset_id", "module_id")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    module_id: str
    def __init__(self, asset_id: _Optional[str] = ..., module_id: _Optional[str] = ...) -> None: ...

class EventBindingMigrated(_message.Message):
    __slots__ = ("asset_id", "module_id", "from_version", "to_version")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_VERSION_FIELD_NUMBER: _ClassVar[int]
    TO_VERSION_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    module_id: str
    from_version: int
    to_version: int
    def __init__(self, asset_id: _Optional[str] = ..., module_id: _Optional[str] = ..., from_version: _Optional[int] = ..., to_version: _Optional[int] = ...) -> None: ...

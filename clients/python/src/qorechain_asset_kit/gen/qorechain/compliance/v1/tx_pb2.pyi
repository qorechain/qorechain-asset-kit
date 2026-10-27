# SPDX-License-Identifier: Apache-2.0
from qorechain_asset_kit.gen.qorechain.compliance.v1 import compliance_pb2 as _compliance_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MsgRegisterModule(_message.Message):
    __slots__ = ("authority", "module")
    AUTHORITY_FIELD_NUMBER: _ClassVar[int]
    MODULE_FIELD_NUMBER: _ClassVar[int]
    authority: str
    module: _compliance_pb2.ComplianceModule
    def __init__(self, authority: _Optional[str] = ..., module: _Optional[_Union[_compliance_pb2.ComplianceModule, _Mapping]] = ...) -> None: ...

class MsgRegisterModuleResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MsgSetModuleStatus(_message.Message):
    __slots__ = ("authority", "module_id", "version", "status")
    AUTHORITY_FIELD_NUMBER: _ClassVar[int]
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    authority: str
    module_id: str
    version: int
    status: _compliance_pb2.ModuleStatus
    def __init__(self, authority: _Optional[str] = ..., module_id: _Optional[str] = ..., version: _Optional[int] = ..., status: _Optional[_Union[_compliance_pb2.ModuleStatus, str]] = ...) -> None: ...

class MsgSetModuleStatusResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MsgBindModule(_message.Message):
    __slots__ = ("issuer", "asset_id", "module_id", "version", "params_json")
    ISSUER_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    PARAMS_JSON_FIELD_NUMBER: _ClassVar[int]
    issuer: str
    asset_id: str
    module_id: str
    version: int
    params_json: str
    def __init__(self, issuer: _Optional[str] = ..., asset_id: _Optional[str] = ..., module_id: _Optional[str] = ..., version: _Optional[int] = ..., params_json: _Optional[str] = ...) -> None: ...

class MsgBindModuleResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MsgUnbindModule(_message.Message):
    __slots__ = ("issuer", "asset_id", "module_id")
    ISSUER_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    issuer: str
    asset_id: str
    module_id: str
    def __init__(self, issuer: _Optional[str] = ..., asset_id: _Optional[str] = ..., module_id: _Optional[str] = ...) -> None: ...

class MsgUnbindModuleResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MsgMigrateBinding(_message.Message):
    __slots__ = ("issuer", "asset_id", "module_id", "to_version", "params_json")
    ISSUER_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    TO_VERSION_FIELD_NUMBER: _ClassVar[int]
    PARAMS_JSON_FIELD_NUMBER: _ClassVar[int]
    issuer: str
    asset_id: str
    module_id: str
    to_version: int
    params_json: str
    def __init__(self, issuer: _Optional[str] = ..., asset_id: _Optional[str] = ..., module_id: _Optional[str] = ..., to_version: _Optional[int] = ..., params_json: _Optional[str] = ...) -> None: ...

class MsgMigrateBindingResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

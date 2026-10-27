# SPDX-License-Identifier: Apache-2.0
from qorechain_asset_kit.gen.qorechain.compliance.v1 import compliance_pb2 as _compliance_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class QueryParamsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class QueryParamsResponse(_message.Message):
    __slots__ = ("params",)
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    params: _compliance_pb2.Params
    def __init__(self, params: _Optional[_Union[_compliance_pb2.Params, _Mapping]] = ...) -> None: ...

class QueryModulesRequest(_message.Message):
    __slots__ = ("module_id",)
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    module_id: str
    def __init__(self, module_id: _Optional[str] = ...) -> None: ...

class QueryModulesResponse(_message.Message):
    __slots__ = ("modules",)
    MODULES_FIELD_NUMBER: _ClassVar[int]
    modules: _containers.RepeatedCompositeFieldContainer[_compliance_pb2.ComplianceModule]
    def __init__(self, modules: _Optional[_Iterable[_Union[_compliance_pb2.ComplianceModule, _Mapping]]] = ...) -> None: ...

class QueryModuleRequest(_message.Message):
    __slots__ = ("module_id", "version")
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    module_id: str
    version: int
    def __init__(self, module_id: _Optional[str] = ..., version: _Optional[int] = ...) -> None: ...

class QueryModuleResponse(_message.Message):
    __slots__ = ("module",)
    MODULE_FIELD_NUMBER: _ClassVar[int]
    module: _compliance_pb2.ComplianceModule
    def __init__(self, module: _Optional[_Union[_compliance_pb2.ComplianceModule, _Mapping]] = ...) -> None: ...

class QueryBindingsRequest(_message.Message):
    __slots__ = ("asset_id",)
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    def __init__(self, asset_id: _Optional[str] = ...) -> None: ...

class QueryBindingsResponse(_message.Message):
    __slots__ = ("bindings",)
    BINDINGS_FIELD_NUMBER: _ClassVar[int]
    bindings: _containers.RepeatedCompositeFieldContainer[_compliance_pb2.Binding]
    def __init__(self, bindings: _Optional[_Iterable[_Union[_compliance_pb2.Binding, _Mapping]]] = ...) -> None: ...

class QueryCheckRequest(_message.Message):
    __slots__ = ("asset_id", "to", "amount")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    to: str
    amount: str
    def __init__(self, asset_id: _Optional[str] = ..., to: _Optional[str] = ..., amount: _Optional[str] = ..., **kwargs) -> None: ...

class QueryCheckResponse(_message.Message):
    __slots__ = ("allowed", "module_id", "version", "reason")
    ALLOWED_FIELD_NUMBER: _ClassVar[int]
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    allowed: bool
    module_id: str
    version: int
    reason: str
    def __init__(self, allowed: _Optional[bool] = ..., module_id: _Optional[str] = ..., version: _Optional[int] = ..., reason: _Optional[str] = ...) -> None: ...

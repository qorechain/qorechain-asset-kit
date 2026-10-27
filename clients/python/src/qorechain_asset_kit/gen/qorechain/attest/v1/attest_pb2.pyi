# SPDX-License-Identifier: Apache-2.0
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AttestationKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ATTESTATION_KIND_UNSPECIFIED: _ClassVar[AttestationKind]
    ATTESTATION_KIND_NAV: _ClassVar[AttestationKind]
    ATTESTATION_KIND_RESERVES: _ClassVar[AttestationKind]
    ATTESTATION_KIND_CUSTODY: _ClassVar[AttestationKind]
    ATTESTATION_KIND_AUDIT_REPORT: _ClassVar[AttestationKind]
    ATTESTATION_KIND_OTHER: _ClassVar[AttestationKind]

class Freshness(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FRESHNESS_UNSPECIFIED: _ClassVar[Freshness]
    FRESHNESS_FRESH: _ClassVar[Freshness]
    FRESHNESS_STALE: _ClassVar[Freshness]
    FRESHNESS_MISSING: _ClassVar[Freshness]

class ErrorCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ERROR_CODE_UNSPECIFIED: _ClassVar[ErrorCode]
    ERROR_CODE_NOT_AN_ATTESTER: _ClassVar[ErrorCode]
    ERROR_CODE_KIND_NOT_ALLOWED: _ClassVar[ErrorCode]
    ERROR_CODE_OBSERVATION_TOO_OLD: _ClassVar[ErrorCode]
    ERROR_CODE_OBSERVATION_IN_FUTURE: _ClassVar[ErrorCode]
    ERROR_CODE_VALIDITY_TOO_LONG: _ClassVar[ErrorCode]
    ERROR_CODE_ATTESTATION_NOT_FOUND: _ClassVar[ErrorCode]
    ERROR_CODE_NOT_ISSUER: _ClassVar[ErrorCode]
    ERROR_CODE_OLDER_THAN_LATEST: _ClassVar[ErrorCode]
ATTESTATION_KIND_UNSPECIFIED: AttestationKind
ATTESTATION_KIND_NAV: AttestationKind
ATTESTATION_KIND_RESERVES: AttestationKind
ATTESTATION_KIND_CUSTODY: AttestationKind
ATTESTATION_KIND_AUDIT_REPORT: AttestationKind
ATTESTATION_KIND_OTHER: AttestationKind
FRESHNESS_UNSPECIFIED: Freshness
FRESHNESS_FRESH: Freshness
FRESHNESS_STALE: Freshness
FRESHNESS_MISSING: Freshness
ERROR_CODE_UNSPECIFIED: ErrorCode
ERROR_CODE_NOT_AN_ATTESTER: ErrorCode
ERROR_CODE_KIND_NOT_ALLOWED: ErrorCode
ERROR_CODE_OBSERVATION_TOO_OLD: ErrorCode
ERROR_CODE_OBSERVATION_IN_FUTURE: ErrorCode
ERROR_CODE_VALIDITY_TOO_LONG: ErrorCode
ERROR_CODE_ATTESTATION_NOT_FOUND: ErrorCode
ERROR_CODE_NOT_ISSUER: ErrorCode
ERROR_CODE_OLDER_THAN_LATEST: ErrorCode

class Attester(_message.Message):
    __slots__ = ("asset_id", "address", "kinds", "name")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    KINDS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    address: str
    kinds: _containers.RepeatedScalarFieldContainer[AttestationKind]
    name: str
    def __init__(self, asset_id: _Optional[str] = ..., address: _Optional[str] = ..., kinds: _Optional[_Iterable[_Union[AttestationKind, str]]] = ..., name: _Optional[str] = ...) -> None: ...

class Attestation(_message.Message):
    __slots__ = ("id", "asset_id", "kind", "attester", "value", "unit", "report_hash", "report_uri", "observed_at", "valid_for_seconds", "accepted_at", "revoked")
    ID_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    ATTESTER_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    REPORT_HASH_FIELD_NUMBER: _ClassVar[int]
    REPORT_URI_FIELD_NUMBER: _ClassVar[int]
    OBSERVED_AT_FIELD_NUMBER: _ClassVar[int]
    VALID_FOR_SECONDS_FIELD_NUMBER: _ClassVar[int]
    ACCEPTED_AT_FIELD_NUMBER: _ClassVar[int]
    REVOKED_FIELD_NUMBER: _ClassVar[int]
    id: int
    asset_id: str
    kind: AttestationKind
    attester: str
    value: str
    unit: str
    report_hash: bytes
    report_uri: str
    observed_at: int
    valid_for_seconds: int
    accepted_at: int
    revoked: bool
    def __init__(self, id: _Optional[int] = ..., asset_id: _Optional[str] = ..., kind: _Optional[_Union[AttestationKind, str]] = ..., attester: _Optional[str] = ..., value: _Optional[str] = ..., unit: _Optional[str] = ..., report_hash: _Optional[bytes] = ..., report_uri: _Optional[str] = ..., observed_at: _Optional[int] = ..., valid_for_seconds: _Optional[int] = ..., accepted_at: _Optional[int] = ..., revoked: _Optional[bool] = ...) -> None: ...

class Params(_message.Message):
    __slots__ = ("max_observation_lag_seconds", "max_validity_seconds")
    MAX_OBSERVATION_LAG_SECONDS_FIELD_NUMBER: _ClassVar[int]
    MAX_VALIDITY_SECONDS_FIELD_NUMBER: _ClassVar[int]
    max_observation_lag_seconds: int
    max_validity_seconds: int
    def __init__(self, max_observation_lag_seconds: _Optional[int] = ..., max_validity_seconds: _Optional[int] = ...) -> None: ...

class GenesisState(_message.Message):
    __slots__ = ("params", "attesters", "attestations", "next_attestation_id")
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    ATTESTERS_FIELD_NUMBER: _ClassVar[int]
    ATTESTATIONS_FIELD_NUMBER: _ClassVar[int]
    NEXT_ATTESTATION_ID_FIELD_NUMBER: _ClassVar[int]
    params: Params
    attesters: _containers.RepeatedCompositeFieldContainer[Attester]
    attestations: _containers.RepeatedCompositeFieldContainer[Attestation]
    next_attestation_id: int
    def __init__(self, params: _Optional[_Union[Params, _Mapping]] = ..., attesters: _Optional[_Iterable[_Union[Attester, _Mapping]]] = ..., attestations: _Optional[_Iterable[_Union[Attestation, _Mapping]]] = ..., next_attestation_id: _Optional[int] = ...) -> None: ...

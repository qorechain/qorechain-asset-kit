# SPDX-License-Identifier: Apache-2.0
"""MockChain: an in-memory implementation of the PROPOSED modules.

It is for building and testing applications. It is not QoreChain and proves
nothing about how the chain would behave; it implements the rules written in
docs/proposal.md. Signer fields are trusted as given: there are no signatures
in the mock.
"""

from __future__ import annotations

import copy
import json
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, TypeVar

from google.protobuf.message import Message

from . import asset as A
from . import attest as T
from . import compliance as C
from . import identity as I
from . import settlement as S
from .errors import MockChainError

M = TypeVar("M", bound=Message)

_ASSET_ID = re.compile(r"^[a-z][a-z0-9-]{2,31}$")
_INTEGER = re.compile(r"^[0-9]+$")
_FINAL = {S.INSTRUCTION_STATUS_EXECUTED, S.INSTRUCTION_STATUS_CANCELLED, S.INSTRUCTION_STATUS_EXPIRED}


@dataclass
class MockEvent:
    """One recorded event, in emission order."""

    #: Full proto name, for example ``qorechain.asset.v1.EventMinted``.
    type: str
    height: int
    data: Message


@dataclass
class ModuleContext:
    """Context passed to a compliance module's logic."""

    chain: "MockChain"
    asset_id: str
    #: Empty for a mint.
    from_: str
    to: str
    amount: int
    #: The binding's parameters, parsed from JSON.
    params: dict


#: Returns a refusal reason, or None to allow.
ModuleLogic = Callable[[ModuleContext], Optional[str]]


@dataclass
class _Holder:
    balance: int = 0
    authorized: bool = False
    frozen: bool = False
    frozen_amount: int = 0


@dataclass
class _AssetRec:
    asset: Any
    #: address -> role -> granted height
    roles: dict = field(default_factory=dict)
    holders: dict = field(default_factory=dict)


@dataclass
class _Refusal:
    code: str
    reason: str
    module_id: str = ""


def _fail(module: str, code: str, message: str) -> None:
    raise MockChainError(message, code, module)


def _parse_amount(module: str, value: str, allow_zero: bool = False) -> int:
    s = value or ""
    if not _INTEGER.match(s):
        _fail(module, "ERROR_CODE_INVALID_AMOUNT", f'amount "{s}" is not a non-negative integer')
    n = int(s)
    if not allow_zero and n == 0:
        _fail(module, "ERROR_CODE_INVALID_AMOUNT", "amount must be greater than zero")
    return n


def _copy(msg: M) -> M:
    out = type(msg)()
    out.CopyFrom(msg)
    return out


def _from_alias(value: Any) -> Any:
    """Lets callers write ``from_`` for the proto field ``from`` (a Python keyword)."""
    if isinstance(value, dict):
        return {("from" if k == "from_" else k): _from_alias(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_from_alias(v) for v in value]
    return value


def _coerce(cls: type[M], msg: Any, kwargs: dict) -> M:
    kwargs = _from_alias(kwargs)
    if msg is None:
        return cls(**kwargs)
    if isinstance(msg, cls):
        out = _copy(msg)
        for k, v in kwargs.items():
            setattr(out, k, v)
        return out
    if isinstance(msg, dict):
        return cls(**{**_from_alias(msg), **kwargs})
    raise TypeError(f"expected {cls.__name__}, dict or keyword arguments")


def _flags_of(r: _AssetRec) -> Any:
    return r.asset.flags


_BUILTIN_MODULES = [
    (
        "identity-verified",
        '{"type":"object","required":["topics"],"properties":{"topics":{"type":"array","items":{"type":"integer"}}}}',
        "The receiver is verified in x/identity for every listed claim topic.",
    ),
    (
        "country-allowlist",
        '{"type":"object","required":["countries"],"properties":{"countries":{"type":"array","items":{"type":"integer"}}}}',
        "The receiver's identity country is in the list; no identity is refused.",
    ),
    (
        "country-blocklist",
        '{"type":"object","required":["countries"],"properties":{"countries":{"type":"array","items":{"type":"integer"}}}}',
        "The receiver's identity country is not in the list; no identity is allowed.",
    ),
    (
        "max-holders",
        '{"type":"object","required":["max"],"properties":{"max":{"type":"integer","minimum":1}}}',
        "The number of addresses with a positive balance never exceeds max.",
    ),
    (
        "max-balance",
        '{"type":"object","required":["max"],"properties":{"max":{"type":"string","pattern":"^[0-9]+$"}}}',
        "The receiver's balance after the transfer is at most max.",
    ),
    (
        "attestation-fresh",
        '{"type":"object","required":["kind"],"properties":{"kind":{"type":"string"}}}',
        "The latest attestation of the given kind for the asset is fresh.",
    ),
]


def _is_int(x: Any) -> bool:
    return isinstance(x, int) and not isinstance(x, bool)


class _Api:
    """Binds snake_case methods to MockChain handlers with message coercion."""

    def __init__(self, table: dict) -> None:
        for name, (cls, handler) in table.items():
            setattr(self, name, self._bind(cls, handler))

    @staticmethod
    def _bind(cls: Any, handler: Callable) -> Callable:
        def call(msg: Any = None, **kwargs: Any) -> Any:
            return handler(_coerce(cls, msg, kwargs))

        return call


class MockChain:
    """In-memory implementation of the proposed modules. See docs/proposal.md."""

    def __init__(
        self,
        authority: str = "authority",
        identity_agents: Optional[list[str]] = None,
        time: int = 1_767_225_600,
        height: int = 1,
    ) -> None:
        self.authority = authority
        self._time = time
        self._height = height
        self._log: list[MockEvent] = []
        self._keys: dict[str, tuple[bool, bool]] = {}
        self._bank: dict[str, dict[str, int]] = {}
        self._custom_logic: dict[str, ModuleLogic] = {}

        self._asset_params = A.Params(creation_fee="0", max_agents=10, max_compliance_modules=10)
        self._assets: dict[str, _AssetRec] = {}

        self._identity_params = I.Params(identity_agents=identity_agents or [])
        self._identities: dict[str, Any] = {}
        self._identity_of: dict[str, str] = {}
        self._claim_issuers: dict[str, Any] = {}

        self._compliance_params = C.Params(max_module_gas=1_000_000)
        self._registry: dict[str, Any] = {}
        self._bindings: dict[str, list] = {}

        self._settlement_params = S.Params(max_legs=10, max_deadline_seconds=30 * 86400)
        self._instructions: dict[int, Any] = {}
        self._next_instruction_id = 1
        self._venues: dict[str, Any] = {}

        self._attest_params = T.Params(max_observation_lag_seconds=7 * 86400, max_validity_seconds=400 * 86400)
        self._attesters: dict[str, dict[str, Any]] = {}
        self._attestations: list[Any] = []
        self._next_attestation_id = 1

        for module_id, schema, description in _BUILTIN_MODULES:
            self._registry[f"{module_id}@1"] = C.ComplianceModule(
                module_id=module_id,
                version=1,
                runtime=C.MODULE_RUNTIME_NATIVE,
                status=C.MODULE_STATUS_ACTIVE,
                params_schema=schema,
                description=description,
            )

        self.asset = _Api({
            "create_asset": (A.MsgCreateAsset, self._create_asset),
            "update_flags": (A.MsgUpdateFlags, self._update_flags),
            "set_role": (A.MsgSetRole, self._set_role),
            "propose_issuer": (A.MsgProposeIssuer, self._propose_issuer),
            "accept_issuer": (A.MsgAcceptIssuer, self._accept_issuer),
            "authorize_holder": (A.MsgAuthorizeHolder, self._authorize_holder),
            "mint": (A.MsgMint, self._mint),
            "burn": (A.MsgBurn, self._burn),
            "transfer": (A.MsgTransfer, self._transfer),
            "freeze": (A.MsgFreeze, self._freeze),
            "freeze_partial": (A.MsgFreezePartial, self._freeze_partial),
            "pause": (A.MsgPause, self._pause),
            "clawback": (A.MsgClawback, self._clawback),
            "force_transfer": (A.MsgForceTransfer, self._force_transfer),
            "set_terms": (A.MsgSetTerms, self._set_terms),
            "retire": (A.MsgRetire, self._retire),
            "params": (A.QueryParamsRequest, lambda q: A.QueryParamsResponse(params=self._asset_params)),
            "asset": (A.QueryAssetRequest, self._query_asset),
            "assets": (A.QueryAssetsRequest, self._query_assets),
            "holder": (A.QueryHolderRequest, self._query_holder),
            "holders": (A.QueryHoldersRequest, self._query_holders),
            "roles": (A.QueryRolesRequest, self._query_roles),
            "can_transfer": (A.QueryCanTransferRequest, self._query_can_transfer),
        })
        self.identity = _Api({
            "register_identity": (I.MsgRegisterIdentity, self._register_identity),
            "update_country": (I.MsgUpdateCountry, self._update_country),
            "bind_address": (I.MsgBindAddress, self._bind_address),
            "unbind_address": (I.MsgUnbindAddress, self._unbind_address),
            "add_claim": (I.MsgAddClaim, self._add_claim),
            "revoke_claim": (I.MsgRevokeClaim, self._revoke_claim),
            "remove_identity": (I.MsgRemoveIdentity, self._remove_identity),
            "set_claim_issuer": (I.MsgSetClaimIssuer, self._set_claim_issuer),
            "params": (I.QueryParamsRequest, lambda q: I.QueryParamsResponse(params=self._identity_params)),
            "identity": (I.QueryIdentityRequest, self._query_identity),
            "identity_by_address": (I.QueryIdentityByAddressRequest, self._query_identity_by_address),
            "claim_issuers": (I.QueryClaimIssuersRequest, lambda q: I.QueryClaimIssuersResponse(
                claim_issuers=[self._claim_issuers[a] for a in sorted(self._claim_issuers)])),
            "is_verified": (I.QueryIsVerifiedRequest, self._query_is_verified),
        })
        self.compliance = _Api({
            "register_module": (C.MsgRegisterModule, self._register_module),
            "set_module_status": (C.MsgSetModuleStatus, self._set_module_status),
            "bind_module": (C.MsgBindModule, self._bind_module),
            "unbind_module": (C.MsgUnbindModule, self._unbind_module),
            "migrate_binding": (C.MsgMigrateBinding, self._migrate_binding),
            "params": (C.QueryParamsRequest, lambda q: C.QueryParamsResponse(params=self._compliance_params)),
            "modules": (C.QueryModulesRequest, self._query_modules),
            "module": (C.QueryModuleRequest, self._query_module),
            "bindings": (C.QueryBindingsRequest, lambda q: C.QueryBindingsResponse(bindings=self._bindings_of(q.asset_id))),
            "check": (C.QueryCheckRequest, self._query_check),
        })
        self.settlement = _Api({
            "create_venue": (S.MsgCreateVenue, self._create_venue),
            "create_instruction": (S.MsgCreateInstruction, self._create_instruction),
            "affirm": (S.MsgAffirm, self._affirm),
            "withdraw_affirmation": (S.MsgWithdrawAffirmation, self._withdraw_affirmation),
            "execute_instruction": (S.MsgExecuteInstruction, self._execute_instruction),
            "cancel_instruction": (S.MsgCancelInstruction, self._cancel_instruction),
            "params": (S.QueryParamsRequest, lambda q: S.QueryParamsResponse(params=self._settlement_params)),
            "instruction": (S.QueryInstructionRequest, self._query_instruction),
            "instructions_by_party": (S.QueryInstructionsByPartyRequest, self._query_instructions_by_party),
            "venue": (S.QueryVenueRequest, self._query_venue),
        })
        self.attest = _Api({
            "set_attester": (T.MsgSetAttester, self._set_attester),
            "submit": (T.MsgSubmit, self._submit_attestation),
            "revoke": (T.MsgRevoke, self._revoke_attestation),
            "params": (T.QueryParamsRequest, lambda q: T.QueryParamsResponse(params=self._attest_params)),
            "latest": (T.QueryLatestRequest, lambda q: self.freshness(q.asset_id, q.kind)),
            "history": (T.QueryHistoryRequest, self._query_history),
            "attesters": (T.QueryAttestersRequest, lambda q: T.QueryAttestersResponse(attesters=[
                v for _, v in sorted(self._attesters.get(q.asset_id, {}).items())])),
        })

    # ------------------------------------------------------------------ chain

    @property
    def height(self) -> int:
        return self._height

    @property
    def time(self) -> int:
        """Block time, Unix seconds."""
        return self._time

    def advance(self, blocks: int, seconds: int) -> None:
        """Advances the chain by ``blocks`` blocks and ``seconds`` seconds, then
        runs the end blocker: ON_BLOCK instructions due at the new height settle
        (or fail if not fully affirmed), then instructions past their deadline
        expire."""
        if blocks < 0 or seconds < 0:
            raise ValueError("cannot go back in time")
        self._height += blocks
        self._time += seconds
        for _, ins in sorted(self._instructions.items()):
            due = ins.settlement_type == S.SETTLEMENT_TYPE_ON_BLOCK and ins.settle_height <= self._height
            if due and ins.status == S.INSTRUCTION_STATUS_AFFIRMED and self._time <= ins.deadline:
                self._execute(ins)
            elif due and ins.status == S.INSTRUCTION_STATUS_PENDING:
                ins.status = S.INSTRUCTION_STATUS_FAILED
                ins.failure_reason = "not fully affirmed at settle height"
                self._emit("qorechain.settlement.v1.EventInstructionFailed",
                           S.EventInstructionFailed(id=ins.id, leg_index=0, reason=ins.failure_reason))
        for _, ins in sorted(self._instructions.items()):
            if ins.status not in _FINAL and self._time > ins.deadline:
                ins.status = S.INSTRUCTION_STATUS_EXPIRED
                self._emit("qorechain.settlement.v1.EventInstructionExpired", S.EventInstructionExpired(id=ins.id))

    def set_hybrid_key(self, address: str, registered: bool, possession_proven: bool) -> None:
        """Sets what pqcKeyStatus would report for an address."""
        self._keys[address] = (registered, possession_proven)

    def has_hybrid_key(self, address: str) -> bool:
        """True when the address has a registered ML-DSA-87 key with proof of possession."""
        registered, proven = self._keys.get(address, (False, False))
        return registered and proven

    def fund_bank(self, address: str, denom: str, amount: int | str) -> None:
        """Credits a bank denom (for example "uqor") to an address: the cash side of DvP tests."""
        m = self._bank.setdefault(address, {})
        m[denom] = m.get(denom, 0) + int(amount)

    def bank_balance(self, address: str, denom: str) -> str:
        return str(self._bank.get(address, {}).get(denom, 0))

    def events(self, type: Optional[str] = None) -> list[MockEvent]:
        """Recorded events, optionally filtered by full type name. Copies."""
        return [MockEvent(e.type, e.height, _copy(e.data)) for e in self._log if type is None or e.type == type]

    def define_module_logic(self, module_id: str, logic: ModuleLogic) -> None:
        """Supplies the logic of a compliance module registered by governance (for example a WASM module)."""
        self._custom_logic[module_id] = logic

    def _emit(self, type: str, data: Message) -> None:
        self._log.append(MockEvent(type, self._height, data))

    # ---------------------------------------------------------------- x/asset

    def _rec(self, asset_id: str) -> _AssetRec:
        r = self._assets.get(asset_id)
        if r is None:
            _fail("x/asset", "ERROR_CODE_ASSET_NOT_FOUND", f"asset {asset_id} not found")
        return r

    @staticmethod
    def _holder_of(r: _AssetRec, address: str) -> _Holder:
        return r.holders.setdefault(address, _Holder())

    @staticmethod
    def _peek_holder(r: _AssetRec, address: str) -> _Holder:
        return r.holders.get(address) or _Holder()

    @staticmethod
    def _has_role(r: _AssetRec, address: str, role: int) -> bool:
        return role in r.roles.get(address, {})

    def _require_issuer(self, r: _AssetRec, signer: str) -> None:
        if r.asset.issuer != signer:
            _fail("x/asset", "ERROR_CODE_UNAUTHORIZED_ROLE", f"{signer} is not the issuer of {r.asset.asset_id}")
        self._require_signer_key(r, signer)

    def _require_agent(self, r: _AssetRec, signer: str) -> None:
        if r.asset.issuer != signer and not self._has_role(r, signer, A.ROLE_AGENT):
            _fail("x/asset", "ERROR_CODE_UNAUTHORIZED_ROLE", f"{signer} is not an agent of {r.asset.asset_id}")
        self._require_signer_key(r, signer)

    def _require_signer_key(self, r: _AssetRec, signer: str) -> None:
        if _flags_of(r).require_hybrid_signature and not self.has_hybrid_key(signer):
            _fail("x/asset", "ERROR_CODE_HYBRID_SIGNATURE_REQUIRED",
                  f"{signer} has no registered ML-DSA-87 key with proof of possession")

    def _create_asset(self, m: Any) -> Any:
        if not _ASSET_ID.match(m.asset_id):
            _fail("x/asset", "ERROR_CODE_INVALID_ASSET_ID", f'invalid asset id "{m.asset_id}"')
        if m.asset_id in self._assets:
            _fail("x/asset", "ERROR_CODE_ASSET_EXISTS", f"asset {m.asset_id} exists")
        flags = _copy(m.flags)
        max_supply = ""
        if flags.supply_cap:
            max_supply = str(_parse_amount("x/asset", m.max_supply))
        if flags.require_hybrid_signature and not self.has_hybrid_key(m.issuer):
            _fail("x/asset", "ERROR_CODE_HYBRID_SIGNATURE_REQUIRED",
                  f"{m.issuer} has no registered ML-DSA-87 key with proof of possession")
        asset = A.Asset(
            asset_id=m.asset_id, issuer=m.issuer, name=m.name, symbol=m.symbol, decimals=m.decimals,
            flags=flags, max_supply=max_supply, total_supply="0", status=A.ASSET_STATUS_ACTIVE,
            terms_hash=m.terms_hash, terms_uri=m.terms_uri, created_height=self._height,
        )
        self._assets[m.asset_id] = _AssetRec(asset=asset, roles={m.issuer: {A.ROLE_ISSUER: self._height}})
        self._emit("qorechain.asset.v1.EventAssetCreated",
                   A.EventAssetCreated(asset_id=m.asset_id, issuer=m.issuer, flags=flags, max_supply=max_supply))
        return A.MsgCreateAssetResponse(denom=f"asset/{m.asset_id}")

    def _update_flags(self, m: Any) -> Any:
        r = self._rec(m.asset_id)
        self._require_issuer(r, m.issuer)
        cur = _flags_of(r)
        nxt = m.flags
        for k in ("non_transferable", "supply_cap", "require_hybrid_signature"):
            if getattr(cur, k) != getattr(nxt, k):
                _fail("x/asset", "ERROR_CODE_FLAG_IMMUTABLE", f"{k} cannot change after creation")
        for k in ("require_auth", "freezable", "pausable"):
            if not getattr(cur, k) and getattr(nxt, k):
                _fail("x/asset", "ERROR_CODE_FLAG_IMMUTABLE", f"{k} can only be switched off")
        r.asset.flags.CopyFrom(nxt)
        self._emit("qorechain.asset.v1.EventFlagsUpdated", A.EventFlagsUpdated(asset_id=m.asset_id, flags=nxt))
        return A.MsgUpdateFlagsResponse()

    def _set_role(self, m: Any) -> Any:
        r = self._rec(m.asset_id)
        self._require_issuer(r, m.issuer)
        if m.role not in (A.ROLE_AGENT, A.ROLE_AUDITOR):
            _fail("x/asset", "ERROR_CODE_UNAUTHORIZED_ROLE", "only ROLE_AGENT and ROLE_AUDITOR can be granted")
        if m.granted:
            if m.role == A.ROLE_AGENT and not self._has_role(r, m.address, A.ROLE_AGENT):
                agents = sum(1 for roles in r.roles.values() if A.ROLE_AGENT in roles)
                if agents >= self._asset_params.max_agents:
                    _fail("x/asset", "ERROR_CODE_TOO_MANY_AGENTS", "too many agents")
            r.roles.setdefault(m.address, {}).setdefault(m.role, self._height)
        else:
            r.roles.get(m.address, {}).pop(m.role, None)
        self._emit("qorechain.asset.v1.EventRoleChanged", A.EventRoleChanged(
            asset_id=m.asset_id, address=m.address, role=m.role, granted=m.granted))
        return A.MsgSetRoleResponse()

    def _propose_issuer(self, m: Any) -> Any:
        r = self._rec(m.asset_id)
        self._require_issuer(r, m.issuer)
        r.asset.pending_issuer = m.new_issuer
        self._emit("qorechain.asset.v1.EventIssuerTransferProposed", A.EventIssuerTransferProposed(
            asset_id=m.asset_id, issuer=m.issuer, new_issuer=m.new_issuer))
        return A.MsgProposeIssuerResponse()

    def _accept_issuer(self, m: Any) -> Any:
        r = self._rec(m.asset_id)
        if not r.asset.pending_issuer or r.asset.pending_issuer != m.new_issuer:
            _fail("x/asset", "ERROR_CODE_UNAUTHORIZED_ROLE", f"{m.new_issuer} is not the pending issuer")
        self._require_signer_key(r, m.new_issuer)
        previous = r.asset.issuer
        r.roles.get(previous, {}).pop(A.ROLE_ISSUER, None)
        r.roles.setdefault(m.new_issuer, {})[A.ROLE_ISSUER] = self._height
        r.asset.issuer = m.new_issuer
        r.asset.pending_issuer = ""
        self._emit("qorechain.asset.v1.EventIssuerTransferred", A.EventIssuerTransferred(
            asset_id=m.asset_id, previous_issuer=previous, new_issuer=m.new_issuer))
        return A.MsgAcceptIssuerResponse()

    def _authorize_holder(self, m: Any) -> Any:
        r = self._rec(m.asset_id)
        self._require_agent(r, m.agent)
        if not _flags_of(r).require_auth:
            _fail("x/asset", "ERROR_CODE_FLAG_NOT_ENABLED", "require_auth is not set")
        self._holder_of(r, m.holder).authorized = m.authorized
        self._emit("qorechain.asset.v1.EventHolderAuthorized", A.EventHolderAuthorized(
            asset_id=m.asset_id, holder=m.holder, authorized=m.authorized, agent=m.agent))
        return A.MsgAuthorizeHolderResponse()

    def _receiver_refusal(self, r: _AssetRec, to: str) -> Optional[_Refusal]:
        """Checks on a receiving address shared by mint, transfer and forced transfer."""
        f = _flags_of(r)
        h = self._peek_holder(r, to)
        if h.frozen:
            return _Refusal("ERROR_CODE_ADDRESS_FROZEN", f"{to} is frozen")
        if f.require_auth and not h.authorized:
            return _Refusal("ERROR_CODE_HOLDER_NOT_AUTHORIZED", f"{to} is not authorized")
        if f.require_hybrid_signature and not self.has_hybrid_key(to):
            return _Refusal("ERROR_CODE_HYBRID_SIGNATURE_REQUIRED",
                            f"{to} has no registered ML-DSA-87 key with proof of possession")
        return None

    def _compliance_refusal(self, asset_id: str, from_: str, to: str, amount: int) -> Optional[_Refusal]:
        c = self._run_compliance(asset_id, from_, to, amount)
        if c is not None:
            return _Refusal("ERROR_CODE_COMPLIANCE_REJECTED", c[2], c[0])
        return None

    def _transfer_refusal(self, r: _AssetRec, from_: str, to: str, amount: int) -> Optional[_Refusal]:
        """The ordered checks of docs/proposal.md section 4.1, without the amount parse."""
        f = _flags_of(r)
        if r.asset.status == A.ASSET_STATUS_RETIRED:
            return _Refusal("ERROR_CODE_ASSET_RETIRED", "asset is retired")
        if r.asset.status == A.ASSET_STATUS_PAUSED:
            return _Refusal("ERROR_CODE_ASSET_PAUSED", "asset is paused")
        if f.non_transferable:
            return _Refusal("ERROR_CODE_NON_TRANSFERABLE", "asset is non-transferable")
        hf = self._peek_holder(r, from_)
        ht = self._peek_holder(r, to)
        if hf.frozen or ht.frozen:
            return _Refusal("ERROR_CODE_ADDRESS_FROZEN", f"{from_ if hf.frozen else to} is frozen")
        if f.require_auth and (not hf.authorized or not ht.authorized):
            return _Refusal("ERROR_CODE_HOLDER_NOT_AUTHORIZED", f"{from_ if not hf.authorized else to} is not authorized")
        if f.require_hybrid_signature and (not self.has_hybrid_key(from_) or not self.has_hybrid_key(to)):
            who = from_ if not self.has_hybrid_key(from_) else to
            return _Refusal("ERROR_CODE_HYBRID_SIGNATURE_REQUIRED",
                            f"{who} has no registered ML-DSA-87 key with proof of possession")
        if hf.balance < amount:
            return _Refusal("ERROR_CODE_INSUFFICIENT_BALANCE", f"{from_} balance is too low")
        if hf.balance - hf.frozen_amount < amount:
            return _Refusal("ERROR_CODE_INSUFFICIENT_UNFROZEN_BALANCE", f"{from_} unfrozen balance is too low")
        return self._compliance_refusal(r.asset.asset_id, from_, to, amount)

    def _move(self, r: _AssetRec, from_: str, to: str, amount: int) -> None:
        hf = self._holder_of(r, from_)
        hf.balance -= amount
        if hf.frozen_amount > hf.balance:
            hf.frozen_amount = hf.balance
        self._holder_of(r, to).balance += amount

    @staticmethod
    def _raise_refusal(ref: _Refusal) -> None:
        _fail("x/asset", ref.code, f"{ref.module_id}: {ref.reason}" if ref.module_id else ref.reason)

    def _mint(self, m: Any) -> Any:
        r = self._rec(m.asset_id)
        self._require_agent(r, m.agent)
        amount = _parse_amount("x/asset", m.amount)
        if r.asset.status == A.ASSET_STATUS_RETIRED:
            _fail("x/asset", "ERROR_CODE_ASSET_RETIRED", "asset is retired")
        ref = self._receiver_refusal(r, m.to)
        if ref is not None:
            self._raise_refusal(ref)
        total = int(r.asset.total_supply) + amount
        if _flags_of(r).supply_cap and total > int(r.asset.max_supply):
            _fail("x/asset", "ERROR_CODE_SUPPLY_CAP_EXCEEDED", f"supply would exceed {r.asset.max_supply}")
        ref = self._compliance_refusal(m.asset_id, "", m.to, amount)
        if ref is not None:
            self._raise_refusal(ref)
        self._holder_of(r, m.to).balance += amount
        r.asset.total_supply = str(total)
        self._emit("qorechain.asset.v1.EventMinted", A.EventMinted(
            asset_id=m.asset_id, to=m.to, amount=str(amount), agent=m.agent))
        return A.MsgMintResponse()

    def _burn(self, m: Any) -> Any:
        r = self._rec(m.asset_id)
        self._require_agent(r, m.agent)
        amount = _parse_amount("x/asset", m.amount)
        h = self._peek_holder(r, getattr(m, "from"))
        frm = getattr(m, "from")
        if h.frozen:
            _fail("x/asset", "ERROR_CODE_ADDRESS_FROZEN", f"{frm} is frozen")
        if h.balance < amount:
            _fail("x/asset", "ERROR_CODE_INSUFFICIENT_BALANCE", f"{frm} balance is too low")
        if h.balance - h.frozen_amount < amount:
            _fail("x/asset", "ERROR_CODE_INSUFFICIENT_UNFROZEN_BALANCE", f"{frm} unfrozen balance is too low")
        self._holder_of(r, frm).balance -= amount
        r.asset.total_supply = str(int(r.asset.total_supply) - amount)
        ev = A.EventBurned(asset_id=m.asset_id, amount=str(amount), agent=m.agent)
        setattr(ev, "from", frm)
        self._emit("qorechain.asset.v1.EventBurned", ev)
        return A.MsgBurnResponse()

    def _transfer(self, m: Any) -> Any:
        amount = _parse_amount("x/asset", m.amount)
        r = self._rec(m.asset_id)
        frm = getattr(m, "from")
        ref = self._transfer_refusal(r, frm, m.to, amount)
        if ref is not None:
            self._raise_refusal(ref)
        self._move(r, frm, m.to, amount)
        ev = A.EventTransferred(asset_id=m.asset_id, to=m.to, amount=str(amount))
        setattr(ev, "from", frm)
        self._emit("qorechain.asset.v1.EventTransferred", ev)
        return A.MsgTransferResponse()

    @staticmethod
    def _require_freezable(r: _AssetRec) -> None:
        if not _flags_of(r).freezable:
            _fail("x/asset", "ERROR_CODE_FLAG_NOT_ENABLED", "freezable is not set")

    def _freeze(self, m: Any) -> Any:
        r = self._rec(m.asset_id)
        self._require_agent(r, m.agent)
        self._require_freezable(r)
        self._holder_of(r, m.holder).frozen = m.frozen
        self._emit("qorechain.asset.v1.EventFrozen", A.EventFrozen(
            asset_id=m.asset_id, holder=m.holder, frozen=m.frozen, agent=m.agent))
        return A.MsgFreezeResponse()

    def _freeze_partial(self, m: Any) -> Any:
        r = self._rec(m.asset_id)
        self._require_agent(r, m.agent)
        self._require_freezable(r)
        amount = _parse_amount("x/asset", m.frozen_amount, allow_zero=True)
        if amount > self._peek_holder(r, m.holder).balance:
            _fail("x/asset", "ERROR_CODE_INSUFFICIENT_BALANCE", "frozen amount exceeds the balance")
        self._holder_of(r, m.holder).frozen_amount = amount
        self._emit("qorechain.asset.v1.EventPartiallyFrozen", A.EventPartiallyFrozen(
            asset_id=m.asset_id, holder=m.holder, frozen_amount=str(amount), agent=m.agent))
        return A.MsgFreezePartialResponse()

    def _pause(self, m: Any) -> Any:
        r = self._rec(m.asset_id)
        self._require_agent(r, m.agent)
        if r.asset.status == A.ASSET_STATUS_RETIRED:
            _fail("x/asset", "ERROR_CODE_ASSET_RETIRED", "asset is retired")
        if m.paused and not _flags_of(r).pausable:
            _fail("x/asset", "ERROR_CODE_FLAG_NOT_ENABLED", "pausable is not set")
        r.asset.status = A.ASSET_STATUS_PAUSED if m.paused else A.ASSET_STATUS_ACTIVE
        self._emit("qorechain.asset.v1.EventPaused", A.EventPaused(asset_id=m.asset_id, paused=m.paused, agent=m.agent))
        return A.MsgPauseResponse()

    def _clawback(self, m: Any) -> Any:
        r = self._rec(m.asset_id)
        self._require_agent(r, m.agent)
        self._require_freezable(r)
        amount = _parse_amount("x/asset", m.amount)
        frm = getattr(m, "from")
        if self._peek_holder(r, frm).balance < amount:
            _fail("x/asset", "ERROR_CODE_INSUFFICIENT_BALANCE", f"{frm} balance is too low")
        self._move(r, frm, r.asset.issuer, amount)
        ev = A.EventClawback(asset_id=m.asset_id, amount=str(amount), agent=m.agent, reason=m.reason)
        setattr(ev, "from", frm)
        self._emit("qorechain.asset.v1.EventClawback", ev)
        return A.MsgClawbackResponse()

    def _force_transfer(self, m: Any) -> Any:
        r = self._rec(m.asset_id)
        self._require_agent(r, m.agent)
        self._require_freezable(r)
        amount = _parse_amount("x/asset", m.amount)
        frm = getattr(m, "from")
        if r.asset.status == A.ASSET_STATUS_RETIRED:
            _fail("x/asset", "ERROR_CODE_ASSET_RETIRED", "asset is retired")
        if self._peek_holder(r, frm).balance < amount:
            _fail("x/asset", "ERROR_CODE_INSUFFICIENT_BALANCE", f"{frm} balance is too low")
        ref = self._receiver_refusal(r, m.to) or self._compliance_refusal(m.asset_id, frm, m.to, amount)
        if ref is not None:
            self._raise_refusal(ref)
        self._move(r, frm, m.to, amount)
        ev = A.EventForcedTransfer(asset_id=m.asset_id, to=m.to, amount=str(amount), agent=m.agent, reason=m.reason)
        setattr(ev, "from", frm)
        self._emit("qorechain.asset.v1.EventForcedTransfer", ev)
        return A.MsgForceTransferResponse()

    def _set_terms(self, m: Any) -> Any:
        r = self._rec(m.asset_id)
        self._require_issuer(r, m.issuer)
        r.asset.terms_hash = m.terms_hash
        r.asset.terms_uri = m.terms_uri
        self._emit("qorechain.asset.v1.EventTermsUpdated", A.EventTermsUpdated(
            asset_id=m.asset_id, terms_hash=m.terms_hash, terms_uri=m.terms_uri))
        return A.MsgSetTermsResponse()

    def _retire(self, m: Any) -> Any:
        r = self._rec(m.asset_id)
        self._require_issuer(r, m.issuer)
        r.asset.status = A.ASSET_STATUS_RETIRED
        self._emit("qorechain.asset.v1.EventRetired", A.EventRetired(asset_id=m.asset_id))
        return A.MsgRetireResponse()

    def _query_asset(self, q: Any) -> Any:
        r = self._rec(q.asset_id)
        a = _copy(r.asset)
        del a.compliance_module_ids[:]
        a.compliance_module_ids.extend(b.module_id for b in self._bindings_of(q.asset_id))
        return A.QueryAssetResponse(asset=a)

    def _query_assets(self, q: Any) -> Any:
        assets = [self._query_asset(A.QueryAssetRequest(asset_id=i)).asset
                  for i in sorted(self._assets) if not q.issuer or self._assets[i].asset.issuer == q.issuer]
        return A.QueryAssetsResponse(assets=assets)

    @staticmethod
    def _holder_state(asset_id: str, address: str, h: _Holder) -> Any:
        return A.HolderState(asset_id=asset_id, address=address, balance=str(h.balance), authorized=h.authorized,
                             frozen=h.frozen, frozen_amount=str(h.frozen_amount))

    def _query_holder(self, q: Any) -> Any:
        r = self._rec(q.asset_id)
        return A.QueryHolderResponse(holder=self._holder_state(q.asset_id, q.address, self._peek_holder(r, q.address)))

    def _query_holders(self, q: Any) -> Any:
        r = self._rec(q.asset_id)
        return A.QueryHoldersResponse(holders=[self._holder_state(q.asset_id, a, r.holders[a]) for a in sorted(r.holders)])

    def _query_roles(self, q: Any) -> Any:
        r = self._rec(q.asset_id)
        roles = [A.RoleGrant(asset_id=q.asset_id, address=addr, role=role, granted_height=h)
                 for addr, rs in r.roles.items() for role, h in rs.items()]
        roles.sort(key=lambda g: (g.role, g.address))
        return A.QueryRolesResponse(roles=roles)

    def _query_can_transfer(self, q: Any) -> Any:
        def no(code: str, reason: str, module_id: str = "") -> Any:
            return A.QueryCanTransferResponse(allowed=False, code=A.ErrorCode.Value(code),
                                              compliance_module_id=module_id, reason=reason)

        if not _INTEGER.match(q.amount) or int(q.amount) == 0:
            return no("ERROR_CODE_INVALID_AMOUNT", "amount must be a positive integer")
        r = self._assets.get(q.asset_id)
        if r is None:
            return no("ERROR_CODE_ASSET_NOT_FOUND", f"asset {q.asset_id} not found")
        ref = self._transfer_refusal(r, getattr(q, "from"), q.to, int(q.amount))
        if ref is not None:
            return no(ref.code, ref.reason, ref.module_id)
        return A.QueryCanTransferResponse(allowed=True)

    # ------------------------------------------------------------- x/identity

    def _require_identity_agent(self, signer: str) -> None:
        if signer != self.authority and signer not in self._identity_params.identity_agents:
            _fail("x/identity", "ERROR_CODE_NOT_IDENTITY_AGENT", f"{signer} is not an identity agent")

    def _ident(self, identity_id: str) -> Any:
        x = self._identities.get(identity_id)
        if x is None:
            _fail("x/identity", "ERROR_CODE_IDENTITY_NOT_FOUND", f"identity {identity_id} not found")
        return x

    def _register_identity(self, m: Any) -> Any:
        self._require_identity_agent(m.agent)
        if m.identity_id in self._identities:
            _fail("x/identity", "ERROR_CODE_IDENTITY_EXISTS", f"identity {m.identity_id} exists")
        if m.address in self._identity_of:
            _fail("x/identity", "ERROR_CODE_ADDRESS_ALREADY_BOUND", f"{m.address} is already bound")
        self._identities[m.identity_id] = I.Identity(
            identity_id=m.identity_id, addresses=[m.address], country=m.country, registered_by=m.agent)
        self._identity_of[m.address] = m.identity_id
        self._emit("qorechain.identity.v1.EventIdentityRegistered", I.EventIdentityRegistered(
            identity_id=m.identity_id, address=m.address, country=m.country, agent=m.agent))
        return I.MsgRegisterIdentityResponse()

    def _update_country(self, m: Any) -> Any:
        self._require_identity_agent(m.agent)
        self._ident(m.identity_id).country = m.country
        self._emit("qorechain.identity.v1.EventCountryUpdated",
                   I.EventCountryUpdated(identity_id=m.identity_id, country=m.country))
        return I.MsgUpdateCountryResponse()

    def _bind_address(self, m: Any) -> Any:
        self._require_identity_agent(m.agent)
        x = self._ident(m.identity_id)
        if m.address in self._identity_of:
            _fail("x/identity", "ERROR_CODE_ADDRESS_ALREADY_BOUND", f"{m.address} is already bound")
        x.addresses.append(m.address)
        self._identity_of[m.address] = m.identity_id
        self._emit("qorechain.identity.v1.EventAddressBound",
                   I.EventAddressBound(identity_id=m.identity_id, address=m.address, bound=True))
        return I.MsgBindAddressResponse()

    def _unbind_address(self, m: Any) -> Any:
        self._require_identity_agent(m.agent)
        x = self._ident(m.identity_id)
        if self._identity_of.get(m.address) != m.identity_id:
            _fail("x/identity", "ERROR_CODE_IDENTITY_NOT_FOUND", f"{m.address} is not bound to {m.identity_id}")
        x.addresses.remove(m.address)
        del self._identity_of[m.address]
        self._emit("qorechain.identity.v1.EventAddressBound",
                   I.EventAddressBound(identity_id=m.identity_id, address=m.address, bound=False))
        return I.MsgUnbindAddressResponse()

    def _add_claim(self, m: Any) -> Any:
        issuer = self._claim_issuers.get(m.claim_issuer)
        if issuer is None:
            _fail("x/identity", "ERROR_CODE_CLAIM_ISSUER_NOT_TRUSTED", f"{m.claim_issuer} is not a trusted claim issuer")
        if m.topic not in issuer.topics:
            _fail("x/identity", "ERROR_CODE_CLAIM_TOPIC_NOT_ALLOWED", f"topic {m.topic} not allowed")
        x = self._ident(m.identity_id)
        for c in [c for c in x.claims if c.topic == m.topic and c.issuer == m.claim_issuer]:
            x.claims.remove(c)
        x.claims.add(topic=m.topic, issuer=m.claim_issuer, data_hash=m.data_hash, valid_until=m.valid_until, revoked=False)
        self._emit("qorechain.identity.v1.EventClaimAdded", I.EventClaimAdded(
            identity_id=m.identity_id, topic=m.topic, claim_issuer=m.claim_issuer, valid_until=m.valid_until))
        return I.MsgAddClaimResponse()

    def _revoke_claim(self, m: Any) -> Any:
        x = self._ident(m.identity_id)
        c = next((k for k in x.claims if k.topic == m.topic and k.issuer == m.claim_issuer and not k.revoked), None)
        if c is None:
            _fail("x/identity", "ERROR_CODE_CLAIM_NOT_FOUND", f"no claim for topic {m.topic} from {m.claim_issuer}")
        c.revoked = True
        self._emit("qorechain.identity.v1.EventClaimRevoked", I.EventClaimRevoked(
            identity_id=m.identity_id, topic=m.topic, claim_issuer=m.claim_issuer))
        return I.MsgRevokeClaimResponse()

    def _remove_identity(self, m: Any) -> Any:
        self._require_identity_agent(m.agent)
        x = self._ident(m.identity_id)
        for a in x.addresses:
            self._identity_of.pop(a, None)
        del self._identities[m.identity_id]
        self._emit("qorechain.identity.v1.EventIdentityRemoved", I.EventIdentityRemoved(identity_id=m.identity_id))
        return I.MsgRemoveIdentityResponse()

    def _set_claim_issuer(self, m: Any) -> Any:
        if m.authority != self.authority:
            _fail("x/identity", "ERROR_CODE_UNAUTHORIZED", f"{m.authority} is not the governance authority")
        ci = _copy(m.claim_issuer)
        if m.remove:
            self._claim_issuers.pop(ci.address, None)
        else:
            self._claim_issuers[ci.address] = ci
        self._emit("qorechain.identity.v1.EventClaimIssuerChanged", I.EventClaimIssuerChanged(
            address=ci.address, topics=list(ci.topics), removed=m.remove))
        return I.MsgSetClaimIssuerResponse()

    def _query_identity(self, q: Any) -> Any:
        return I.QueryIdentityResponse(identity=self._ident(q.identity_id))

    def _query_identity_by_address(self, q: Any) -> Any:
        identity_id = self._identity_of.get(q.address)
        if identity_id is None:
            _fail("x/identity", "ERROR_CODE_IDENTITY_NOT_FOUND", f"{q.address} has no identity")
        return I.QueryIdentityByAddressResponse(identity=self._ident(identity_id))

    def missing_topics(self, address: str, topics: list[int]) -> list[int]:
        """Topics, of those asked, for which the address holds no valid claim."""
        identity_id = self._identity_of.get(address)
        x = self._identities.get(identity_id) if identity_id else None

        def valid(topic: int) -> bool:
            if x is None:
                return False
            for c in x.claims:
                issuer = self._claim_issuers.get(c.issuer)
                trusted = issuer is not None and topic in issuer.topics
                live = c.valid_until == 0 or c.valid_until > self._time
                if c.topic == topic and not c.revoked and trusted and live:
                    return True
            return False

        return [t for t in topics if not valid(t)]

    def _query_is_verified(self, q: Any) -> Any:
        missing = self.missing_topics(q.address, list(q.topics))
        return I.QueryIsVerifiedResponse(verified=q.address in self._identity_of and not missing, missing_topics=missing)

    def country_of(self, address: str) -> Optional[int]:
        """The identity country of an address, or None."""
        identity_id = self._identity_of.get(address)
        x = self._identities.get(identity_id) if identity_id else None
        return x.country if x is not None else None

    # ----------------------------------------------------------- x/compliance

    def _bindings_of(self, asset_id: str) -> list:
        return [_copy(b) for b in sorted(self._bindings.get(asset_id, []), key=lambda b: b.position)]

    def _register_module(self, m: Any) -> Any:
        if m.authority != self.authority:
            _fail("x/compliance", "ERROR_CODE_UNAUTHORIZED", f"{m.authority} is not the governance authority")
        mod = _copy(m.module)
        if not mod.module_id or mod.version < 1:
            _fail("x/compliance", "ERROR_CODE_INVALID_PARAMS", "module id and a version >= 1 are required")
        latest = max([x.version for x in self._registry.values() if x.module_id == mod.module_id], default=0)
        if mod.version <= latest:
            _fail("x/compliance", "ERROR_CODE_MODULE_VERSION_EXISTS", f"version must be greater than {latest}")
        if mod.status == C.MODULE_STATUS_UNSPECIFIED:
            mod.status = C.MODULE_STATUS_ACTIVE
        self._registry[f"{mod.module_id}@{mod.version}"] = mod
        self._emit("qorechain.compliance.v1.EventModuleRegistered", C.EventModuleRegistered(
            module_id=mod.module_id, version=mod.version, runtime=mod.runtime))
        return C.MsgRegisterModuleResponse()

    def _module_version(self, module_id: str, version: int) -> Any:
        mod = self._registry.get(f"{module_id}@{version}")
        if mod is None:
            _fail("x/compliance", "ERROR_CODE_MODULE_NOT_FOUND", f"module {module_id} v{version} not found")
        return mod

    def _set_module_status(self, m: Any) -> Any:
        if m.authority != self.authority:
            _fail("x/compliance", "ERROR_CODE_UNAUTHORIZED", f"{m.authority} is not the governance authority")
        self._module_version(m.module_id, m.version).status = m.status
        self._emit("qorechain.compliance.v1.EventModuleStatusChanged", C.EventModuleStatusChanged(
            module_id=m.module_id, version=m.version, status=m.status))
        return C.MsgSetModuleStatusResponse()

    def _require_asset_issuer(self, asset_id: str, signer: str) -> None:
        r = self._assets.get(asset_id)
        if r is None or r.asset.issuer != signer:
            _fail("x/compliance", "ERROR_CODE_NOT_ISSUER", f"{signer} is not the issuer of {asset_id}")

    @staticmethod
    def _parse_params(module_id: str, params_json: str) -> dict:
        try:
            v = json.loads(params_json or "{}")
        except ValueError:
            _fail("x/compliance", "ERROR_CODE_INVALID_PARAMS", "params_json is not valid JSON")
        if not isinstance(v, dict):
            _fail("x/compliance", "ERROR_CODE_INVALID_PARAMS", "params_json must be a JSON object")

        def bad(why: str) -> None:
            _fail("x/compliance", "ERROR_CODE_INVALID_PARAMS", f"{module_id}: {why}")

        def int_list(k: str) -> bool:
            x = v.get(k)
            return isinstance(x, list) and len(x) > 0 and all(_is_int(i) and i >= 0 for i in x)

        if module_id == "identity-verified":
            if not int_list("topics"):
                bad("topics must be a non-empty list of integers")
        elif module_id in ("country-allowlist", "country-blocklist"):
            if not int_list("countries"):
                bad("countries must be a non-empty list of integers")
        elif module_id == "max-holders":
            if not _is_int(v.get("max")) or v["max"] < 1:
                bad("max must be a positive integer")
        elif module_id == "max-balance":
            if not isinstance(v.get("max"), str) or not _INTEGER.match(v["max"]):
                bad("max must be an integer string")
        elif module_id == "attestation-fresh":
            kind = v.get("kind")
            if not isinstance(kind, str) or kind not in T.AttestationKind.keys() or T.AttestationKind.Value(kind) <= 0:
                bad("kind must be an AttestationKind name")
        return v

    def _bind_module(self, m: Any) -> Any:
        self._require_asset_issuer(m.asset_id, m.issuer)
        mod = self._module_version(m.module_id, m.version)
        if mod.status == C.MODULE_STATUS_DEPRECATED:
            _fail("x/compliance", "ERROR_CODE_MODULE_DEPRECATED", "module version is deprecated")
        if mod.status == C.MODULE_STATUS_DISABLED:
            _fail("x/compliance", "ERROR_CODE_MODULE_DISABLED", "module version is disabled")
        self._parse_params(m.module_id, m.params_json)
        lst = self._bindings.setdefault(m.asset_id, [])
        if any(b.module_id == m.module_id for b in lst):
            _fail("x/compliance", "ERROR_CODE_BINDING_EXISTS", f"{m.module_id} is already bound")
        if len(lst) >= self._asset_params.max_compliance_modules:
            _fail("x/compliance", "ERROR_CODE_TOO_MANY_BINDINGS", "too many bindings")
        position = max([b.position + 1 for b in lst], default=0)
        lst.append(C.Binding(asset_id=m.asset_id, module_id=m.module_id, version=m.version,
                             params_json=m.params_json or "{}", position=position))
        self._emit("qorechain.compliance.v1.EventModuleBound", C.EventModuleBound(
            asset_id=m.asset_id, module_id=m.module_id, version=m.version))
        return C.MsgBindModuleResponse()

    def _unbind_module(self, m: Any) -> Any:
        self._require_asset_issuer(m.asset_id, m.issuer)
        lst = self._bindings.get(m.asset_id, [])
        if not any(b.module_id == m.module_id for b in lst):
            _fail("x/compliance", "ERROR_CODE_BINDING_NOT_FOUND", f"{m.module_id} is not bound")
        self._bindings[m.asset_id] = [b for b in lst if b.module_id != m.module_id]
        self._emit("qorechain.compliance.v1.EventModuleUnbound",
                   C.EventModuleUnbound(asset_id=m.asset_id, module_id=m.module_id))
        return C.MsgUnbindModuleResponse()

    def _migrate_binding(self, m: Any) -> Any:
        self._require_asset_issuer(m.asset_id, m.issuer)
        b = next((x for x in self._bindings.get(m.asset_id, []) if x.module_id == m.module_id), None)
        if b is None:
            _fail("x/compliance", "ERROR_CODE_BINDING_NOT_FOUND", f"{m.module_id} is not bound")
        mod = self._module_version(m.module_id, m.to_version)
        if mod.status != C.MODULE_STATUS_ACTIVE:
            _fail("x/compliance", "ERROR_CODE_MODULE_DEPRECATED", "target version is not active")
        params = m.params_json or b.params_json
        self._parse_params(m.module_id, params)
        from_version = b.version
        b.version = m.to_version
        b.params_json = params
        self._emit("qorechain.compliance.v1.EventBindingMigrated", C.EventBindingMigrated(
            asset_id=m.asset_id, module_id=m.module_id, from_version=from_version, to_version=m.to_version))
        return C.MsgMigrateBindingResponse()

    def _query_modules(self, q: Any) -> Any:
        mods = [x for x in self._registry.values() if not q.module_id or x.module_id == q.module_id]
        mods.sort(key=lambda x: (x.module_id, x.version))
        return C.QueryModulesResponse(modules=mods)

    def _query_module(self, q: Any) -> Any:
        return C.QueryModuleResponse(module=self._module_version(q.module_id, q.version))

    def _builtin_logic(self, module_id: str) -> Optional[ModuleLogic]:
        if module_id == "identity-verified":
            def identity_verified(ctx: ModuleContext) -> Optional[str]:
                missing = ctx.chain.missing_topics(ctx.to, ctx.params["topics"])
                return f"{ctx.to} is not verified for topics {','.join(map(str, missing))}" if missing else None
            return identity_verified
        if module_id == "country-allowlist":
            def allowlist(ctx: ModuleContext) -> Optional[str]:
                c = ctx.chain.country_of(ctx.to)
                if c is None:
                    return f"{ctx.to} has no identity"
                return None if c in ctx.params["countries"] else f"country {c} is not allowed"
            return allowlist
        if module_id == "country-blocklist":
            def blocklist(ctx: ModuleContext) -> Optional[str]:
                c = ctx.chain.country_of(ctx.to)
                return f"country {c} is blocked" if c is not None and c in ctx.params["countries"] else None
            return blocklist
        if module_id == "max-holders":
            def max_holders(ctx: ModuleContext) -> Optional[str]:
                r = self._assets[ctx.asset_id]
                count = sum(1 for h in r.holders.values() if h.balance > 0)
                joins = 1 if self._peek_holder(r, ctx.to).balance == 0 and ctx.amount > 0 else 0
                leaves = 1 if ctx.from_ and ctx.from_ != ctx.to and self._peek_holder(r, ctx.from_).balance == ctx.amount else 0
                mx = ctx.params["max"]
                return f"more than {mx} holders" if count + joins - leaves > mx else None
            return max_holders
        if module_id == "max-balance":
            def max_balance(ctx: ModuleContext) -> Optional[str]:
                r = self._assets[ctx.asset_id]
                mx = ctx.params["max"]
                return f"balance of {ctx.to} would exceed {mx}" if self._peek_holder(r, ctx.to).balance + ctx.amount > int(mx) else None
            return max_balance
        if module_id == "attestation-fresh":
            def attestation_fresh(ctx: ModuleContext) -> Optional[str]:
                kind = T.AttestationKind.Value(ctx.params["kind"])
                f = ctx.chain.freshness(ctx.asset_id, kind).freshness
                return None if f == T.FRESHNESS_FRESH else f"latest {ctx.params['kind']} attestation is {T.Freshness.Name(f)}"
            return attestation_fresh
        return None

    def _run_compliance(self, asset_id: str, from_: str, to: str, amount: int) -> Optional[tuple[str, int, str]]:
        for b in self._bindings_of(asset_id):
            mod = self._registry.get(f"{b.module_id}@{b.version}")
            if mod is None or mod.status == C.MODULE_STATUS_DISABLED:
                return (b.module_id, b.version, "module version is disabled")
            logic = self._custom_logic.get(b.module_id) or self._builtin_logic(b.module_id)
            if logic is None:
                return (b.module_id, b.version, "no logic for this module in MockChain")
            reason = logic(ModuleContext(self, asset_id, from_, to, amount, json.loads(b.params_json)))
            if reason is not None:
                return (b.module_id, b.version, reason)
        return None

    def _query_check(self, q: Any) -> Any:
        amount = int(q.amount) if _INTEGER.match(q.amount) else 0
        c = self._run_compliance(q.asset_id, getattr(q, "from"), q.to, amount)
        if c is None:
            return C.QueryCheckResponse(allowed=True)
        return C.QueryCheckResponse(allowed=False, module_id=c[0], version=c[1], reason=c[2])

    # ----------------------------------------------------------- x/settlement

    def _create_venue(self, m: Any) -> Any:
        if m.venue_id in self._venues:
            _fail("x/settlement", "ERROR_CODE_VENUE_EXISTS", f"venue {m.venue_id} exists")
        self._venues[m.venue_id] = S.Venue(venue_id=m.venue_id, operator=m.operator, description=m.description,
                                           allowed_creators=list(m.allowed_creators))
        self._emit("qorechain.settlement.v1.EventVenueCreated", S.EventVenueCreated(venue_id=m.venue_id, operator=m.operator))
        return S.MsgCreateVenueResponse()

    def _create_instruction(self, m: Any) -> Any:
        if len(m.legs) == 0:
            _fail("x/settlement", "ERROR_CODE_INVALID_LEG", "an instruction needs at least one leg")
        if len(m.legs) > self._settlement_params.max_legs:
            _fail("x/settlement", "ERROR_CODE_TOO_MANY_LEGS", "too many legs")
        for i, leg in enumerate(m.legs):
            frm = getattr(leg, "from")
            if (not frm or not leg.to or frm == leg.to or not leg.denom
                    or not _INTEGER.match(leg.amount) or int(leg.amount) == 0):
                _fail("x/settlement", "ERROR_CODE_INVALID_LEG", f"leg {i} is invalid")
        if m.venue_id:
            v = self._venues.get(m.venue_id)
            if v is None:
                _fail("x/settlement", "ERROR_CODE_VENUE_NOT_FOUND", f"venue {m.venue_id} not found")
            if len(v.allowed_creators) > 0 and m.creator not in v.allowed_creators:
                _fail("x/settlement", "ERROR_CODE_NOT_ALLOWED_IN_VENUE",
                      f"{m.creator} may not create instructions in {m.venue_id}")
        if m.deadline <= self._time:
            _fail("x/settlement", "ERROR_CODE_DEADLINE_PASSED", "deadline is not in the future")
        if m.deadline - self._time > self._settlement_params.max_deadline_seconds:
            _fail("x/settlement", "ERROR_CODE_DEADLINE_TOO_FAR", "deadline is too far in the future")
        typ = m.settlement_type or S.SETTLEMENT_TYPE_ON_AFFIRMATION
        if typ == S.SETTLEMENT_TYPE_ON_BLOCK and m.settle_height <= self._height:
            _fail("x/settlement", "ERROR_CODE_INVALID_STATUS", "settle_height must be in the future")
        parties: list[str] = []
        for leg in m.legs:
            for a in (getattr(leg, "from"), leg.to):
                if a not in parties:
                    parties.append(a)
        iid = self._next_instruction_id
        self._next_instruction_id += 1
        ins = S.Instruction(
            id=iid, creator=m.creator, venue_id=m.venue_id, legs=list(m.legs), settlement_type=typ,
            settle_height=m.settle_height, deadline=m.deadline, status=S.INSTRUCTION_STATUS_PENDING,
            affirmations=[S.Affirmation(party=p, affirmed=p == m.creator, height=self._height if p == m.creator else 0)
                          for p in parties],
            memo=m.memo,
        )
        self._instructions[iid] = ins
        self._emit("qorechain.settlement.v1.EventInstructionCreated", S.EventInstructionCreated(
            id=iid, creator=m.creator, venue_id=m.venue_id, legs=list(m.legs), settlement_type=typ, deadline=m.deadline))
        if m.creator in parties:
            self._emit("qorechain.settlement.v1.EventAffirmed", S.EventAffirmed(id=iid, party=m.creator))
        return S.MsgCreateInstructionResponse(id=iid)

    def _ins(self, iid: int) -> Any:
        x = self._instructions.get(iid)
        if x is None:
            _fail("x/settlement", "ERROR_CODE_INSTRUCTION_NOT_FOUND", f"instruction {iid} not found")
        return x

    def _affirm(self, m: Any) -> Any:
        ins = self._ins(m.id)
        a = next((x for x in ins.affirmations if x.party == m.party), None)
        if a is None:
            _fail("x/settlement", "ERROR_CODE_NOT_A_PARTY", f"{m.party} is not a party")
        if ins.status != S.INSTRUCTION_STATUS_PENDING:
            _fail("x/settlement", "ERROR_CODE_INVALID_STATUS", f"instruction is {S.InstructionStatus.Name(ins.status)}")
        if self._time > ins.deadline:
            _fail("x/settlement", "ERROR_CODE_DEADLINE_PASSED", "deadline passed")
        if not a.affirmed:
            a.affirmed = True
            a.height = self._height
            self._emit("qorechain.settlement.v1.EventAffirmed", S.EventAffirmed(id=ins.id, party=m.party))
        if all(x.affirmed for x in ins.affirmations):
            ins.status = S.INSTRUCTION_STATUS_AFFIRMED
            if ins.settlement_type == S.SETTLEMENT_TYPE_ON_AFFIRMATION:
                self._execute(ins)
        return S.MsgAffirmResponse(executed=ins.status == S.INSTRUCTION_STATUS_EXECUTED)

    def _withdraw_affirmation(self, m: Any) -> Any:
        ins = self._ins(m.id)
        a = next((x for x in ins.affirmations if x.party == m.party), None)
        if a is None:
            _fail("x/settlement", "ERROR_CODE_NOT_A_PARTY", f"{m.party} is not a party")
        if ins.status in _FINAL:
            _fail("x/settlement", "ERROR_CODE_INVALID_STATUS", f"instruction is {S.InstructionStatus.Name(ins.status)}")
        a.affirmed = False
        a.height = 0
        ins.status = S.INSTRUCTION_STATUS_PENDING
        self._emit("qorechain.settlement.v1.EventAffirmationWithdrawn", S.EventAffirmationWithdrawn(id=ins.id, party=m.party))
        return S.MsgWithdrawAffirmationResponse()

    def _operator_of(self, ins: Any) -> Optional[str]:
        v = self._venues.get(ins.venue_id) if ins.venue_id else None
        return v.operator if v is not None else None

    def _execute_instruction(self, m: Any) -> Any:
        ins = self._ins(m.id)
        if not any(x.party == m.signer for x in ins.affirmations) and self._operator_of(ins) != m.signer:
            _fail("x/settlement", "ERROR_CODE_NOT_A_PARTY", f"{m.signer} is not a party or the venue operator")
        if not all(x.affirmed for x in ins.affirmations):
            _fail("x/settlement", "ERROR_CODE_NOT_FULLY_AFFIRMED", "not every party affirmed")
        retry = ins.status == S.INSTRUCTION_STATUS_FAILED
        manual = ins.status == S.INSTRUCTION_STATUS_AFFIRMED and ins.settlement_type == S.SETTLEMENT_TYPE_MANUAL
        if not retry and not manual:
            _fail("x/settlement", "ERROR_CODE_INVALID_STATUS", f"instruction is {S.InstructionStatus.Name(ins.status)}")
        if self._time > ins.deadline:
            _fail("x/settlement", "ERROR_CODE_DEADLINE_PASSED", "deadline passed")
        self._execute(ins)
        return S.MsgExecuteInstructionResponse(status=ins.status)

    def _cancel_instruction(self, m: Any) -> Any:
        ins = self._ins(m.id)
        if (m.signer != ins.creator and self._operator_of(ins) != m.signer
                and not any(x.party == m.signer for x in ins.affirmations)):
            _fail("x/settlement", "ERROR_CODE_NOT_A_PARTY", f"{m.signer} may not cancel")
        if ins.status in _FINAL:
            _fail("x/settlement", "ERROR_CODE_INVALID_STATUS", f"instruction is {S.InstructionStatus.Name(ins.status)}")
        ins.status = S.INSTRUCTION_STATUS_CANCELLED
        self._emit("qorechain.settlement.v1.EventInstructionCancelled", S.EventInstructionCancelled(id=ins.id, signer=m.signer))
        return S.MsgCancelInstructionResponse()

    def _snapshot(self) -> Callable[[], None]:
        """Saves balances and the event log; the returned function restores them."""
        holders = {i: copy.deepcopy(r.holders) for i, r in self._assets.items()}
        bank = copy.deepcopy(self._bank)
        n_events = len(self._log)

        def restore() -> None:
            for i, r in self._assets.items():
                r.holders = holders.get(i, {})
            self._bank = bank
            del self._log[n_events:]

        return restore

    def _execute(self, ins: Any) -> None:
        """Applies every leg, or none. Leaves the instruction EXECUTED or FAILED."""
        restore = self._snapshot()
        for i, leg in enumerate(ins.legs):
            reason = self._apply_leg(leg)
            if reason is not None:
                restore()
                ins.status = S.INSTRUCTION_STATUS_FAILED
                ins.failure_reason = f"leg {i}: {reason}"
                self._emit("qorechain.settlement.v1.EventInstructionFailed",
                           S.EventInstructionFailed(id=ins.id, leg_index=i, reason=reason))
                return
        ins.status = S.INSTRUCTION_STATUS_EXECUTED
        ins.failure_reason = ""
        self._emit("qorechain.settlement.v1.EventInstructionExecuted", S.EventInstructionExecuted(id=ins.id))

    def _apply_leg(self, leg: Any) -> Optional[str]:
        amount = int(leg.amount)
        frm = getattr(leg, "from")
        if leg.denom.startswith("asset/"):
            asset_id = leg.denom[len("asset/"):]
            r = self._assets.get(asset_id)
            if r is None:
                return "ERROR_CODE_ASSET_NOT_FOUND"
            ref = self._transfer_refusal(r, frm, leg.to, amount)
            if ref is not None:
                return f"{ref.code} ({ref.module_id})" if ref.module_id else ref.code
            self._move(r, frm, leg.to, amount)
            ev = A.EventTransferred(asset_id=asset_id, to=leg.to, amount=leg.amount)
            setattr(ev, "from", frm)
            self._emit("qorechain.asset.v1.EventTransferred", ev)
            return None
        bal = int(self.bank_balance(frm, leg.denom))
        if bal < amount:
            return f"insufficient {leg.denom} balance"
        self._bank[frm][leg.denom] = bal - amount
        self.fund_bank(leg.to, leg.denom, amount)
        return None

    def _query_instruction(self, q: Any) -> Any:
        return S.QueryInstructionResponse(instruction=self._ins(q.id))

    def _query_instructions_by_party(self, q: Any) -> Any:
        out = [x for _, x in sorted(self._instructions.items())
               if any(a.party == q.party for a in x.affirmations)
               and (q.status == S.INSTRUCTION_STATUS_UNSPECIFIED or x.status == q.status)]
        return S.QueryInstructionsByPartyResponse(instructions=out)

    def _query_venue(self, q: Any) -> Any:
        v = self._venues.get(q.venue_id)
        if v is None:
            _fail("x/settlement", "ERROR_CODE_VENUE_NOT_FOUND", f"venue {q.venue_id} not found")
        return S.QueryVenueResponse(venue=v)

    # --------------------------------------------------------------- x/attest

    def _set_attester(self, m: Any) -> Any:
        at = _copy(m.attester)
        r = self._assets.get(at.asset_id)
        if r is None or r.asset.issuer != m.issuer:
            _fail("x/attest", "ERROR_CODE_NOT_ISSUER", f"{m.issuer} is not the issuer of {at.asset_id}")
        mp = self._attesters.setdefault(at.asset_id, {})
        if m.remove:
            mp.pop(at.address, None)
        else:
            mp[at.address] = at
        self._emit("qorechain.attest.v1.EventAttesterChanged", T.EventAttesterChanged(
            asset_id=at.asset_id, address=at.address, kinds=list(at.kinds), removed=m.remove))
        return T.MsgSetAttesterResponse()

    def _latest_of(self, asset_id: str, kind: int) -> Optional[Any]:
        cands = [a for a in self._attestations if a.asset_id == asset_id and a.kind == kind and not a.revoked]
        cands.sort(key=lambda a: (a.observed_at, a.id), reverse=True)
        return cands[0] if cands else None

    def _submit_attestation(self, m: Any) -> Any:
        at = self._attesters.get(m.asset_id, {}).get(m.attester)
        if at is None:
            _fail("x/attest", "ERROR_CODE_NOT_AN_ATTESTER", f"{m.attester} is not an attester of {m.asset_id}")
        if m.kind not in at.kinds:
            _fail("x/attest", "ERROR_CODE_KIND_NOT_ALLOWED", f"{T.AttestationKind.Name(m.kind)} not allowed")
        if m.kind == T.ATTESTATION_KIND_AUDIT_REPORT:
            r = self._assets.get(m.asset_id)
            if r is None or not self._has_role(r, m.attester, A.ROLE_AUDITOR):
                _fail("x/attest", "ERROR_CODE_KIND_NOT_ALLOWED", "AUDIT_REPORT requires the auditor role")
        if m.observed_at > self._time:
            _fail("x/attest", "ERROR_CODE_OBSERVATION_IN_FUTURE", "observed_at is in the future")
        if self._time - m.observed_at > self._attest_params.max_observation_lag_seconds:
            _fail("x/attest", "ERROR_CODE_OBSERVATION_TOO_OLD", "observed_at is too old")
        if m.valid_for_seconds <= 0 or m.valid_for_seconds > self._attest_params.max_validity_seconds:
            _fail("x/attest", "ERROR_CODE_VALIDITY_TOO_LONG", "valid_for_seconds is out of range")
        latest = self._latest_of(m.asset_id, m.kind)
        if latest is not None and m.observed_at < latest.observed_at:
            _fail("x/attest", "ERROR_CODE_OLDER_THAN_LATEST", "older than the latest attestation")
        aid = self._next_attestation_id
        self._next_attestation_id += 1
        self._attestations.append(T.Attestation(
            id=aid, asset_id=m.asset_id, kind=m.kind, attester=m.attester, value=m.value, unit=m.unit,
            report_hash=m.report_hash, report_uri=m.report_uri, observed_at=m.observed_at,
            valid_for_seconds=m.valid_for_seconds, accepted_at=self._time, revoked=False,
        ))
        self._emit("qorechain.attest.v1.EventAttestationSubmitted", T.EventAttestationSubmitted(
            id=aid, asset_id=m.asset_id, kind=m.kind, attester=m.attester, value=m.value,
            observed_at=m.observed_at, valid_for_seconds=m.valid_for_seconds))
        return T.MsgSubmitResponse(id=aid)

    def _revoke_attestation(self, m: Any) -> Any:
        a = next((x for x in self._attestations if x.id == m.id), None)
        if a is None:
            _fail("x/attest", "ERROR_CODE_ATTESTATION_NOT_FOUND", f"attestation {m.id} not found")
        r = self._assets.get(a.asset_id)
        if m.signer != a.attester and (r is None or r.asset.issuer != m.signer):
            _fail("x/attest", "ERROR_CODE_NOT_AN_ATTESTER", f"{m.signer} may not revoke")
        a.revoked = True
        self._emit("qorechain.attest.v1.EventAttestationRevoked",
                   T.EventAttestationRevoked(id=m.id, signer=m.signer, reason=m.reason))
        return T.MsgRevokeResponse()

    def freshness(self, asset_id: str, kind: int) -> Any:
        """Freshness of the latest attestation of a kind, at the current block time."""
        a = self._latest_of(asset_id, kind)
        if a is None:
            return T.QueryLatestResponse(freshness=T.FRESHNESS_MISSING)
        stale_at = a.observed_at + a.valid_for_seconds
        return T.QueryLatestResponse(
            attestation=a,
            freshness=T.FRESHNESS_FRESH if self._time < stale_at else T.FRESHNESS_STALE,
            stale_at=stale_at,
        )

    def _query_history(self, q: Any) -> Any:
        allx = [a for a in self._attestations if a.asset_id == q.asset_id and a.kind == q.kind]
        allx.sort(key=lambda a: (a.observed_at, a.id), reverse=True)
        return T.QueryHistoryResponse(attestations=allx[: q.limit] if q.limit > 0 else allx)

# SPDX-License-Identifier: Apache-2.0
"""The client for the real chain.

The modules are a proposal, so every call raises :class:`ChainUpgradeRequired`
without any network request.
"""

from __future__ import annotations

from typing import Any, NoReturn

from .errors import ChainUpgradeRequired

ASSET_METHODS = (
    "create_asset", "update_flags", "set_role", "propose_issuer", "accept_issuer", "authorize_holder",
    "mint", "burn", "transfer", "freeze", "freeze_partial", "pause", "clawback", "force_transfer",
    "set_terms", "retire",
    "params", "asset", "assets", "holder", "holders", "roles", "can_transfer",
)

IDENTITY_METHODS = (
    "register_identity", "update_country", "bind_address", "unbind_address", "add_claim", "revoke_claim",
    "remove_identity", "set_claim_issuer",
    "params", "identity", "identity_by_address", "claim_issuers", "is_verified",
)

COMPLIANCE_METHODS = (
    "register_module", "set_module_status", "bind_module", "unbind_module", "migrate_binding",
    "params", "modules", "module", "bindings", "check",
)

SETTLEMENT_METHODS = (
    "create_venue", "create_instruction", "affirm", "withdraw_affirmation", "execute_instruction",
    "cancel_instruction",
    "params", "instruction", "instructions_by_party", "venue",
)

ATTEST_METHODS = ("set_attester", "submit", "revoke", "params", "latest", "history", "attesters")


class _Unavailable:
    """Every listed method raises ChainUpgradeRequired for one module."""

    def __init__(self, module: str, methods: tuple[str, ...]) -> None:
        self._module = module
        self._methods = frozenset(methods)

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_") or name not in self._methods:
            raise AttributeError(name)
        module = self._module

        def call(*_args: Any, **_kwargs: Any) -> NoReturn:
            raise ChainUpgradeRequired(module)

        call.__name__ = name
        return call

    def __dir__(self) -> list[str]:
        return sorted(self._methods)


class ChainClient:
    """Client for the proposed modules on QoreChain. Every call raises
    :class:`ChainUpgradeRequired`; nothing is contacted."""

    def __init__(self, rest_url: str | None = None, chain_id: str | None = None) -> None:
        #: Kept for the day the modules exist, for example https://api-testnet.qore.host.
        self.rest_url = rest_url
        self.chain_id = chain_id
        self.asset = _Unavailable("x/asset", ASSET_METHODS)
        self.identity = _Unavailable("x/identity", IDENTITY_METHODS)
        self.compliance = _Unavailable("x/compliance", COMPLIANCE_METHODS)
        self.settlement = _Unavailable("x/settlement", SETTLEMENT_METHODS)
        self.attest = _Unavailable("x/attest", ATTEST_METHODS)

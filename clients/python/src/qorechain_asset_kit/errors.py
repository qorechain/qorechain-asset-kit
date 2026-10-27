# SPDX-License-Identifier: Apache-2.0
"""Errors raised by qorechain_asset_kit."""

from __future__ import annotations

#: The five proposed modules. None of them exists on QoreChain.
MODULES = ("x/asset", "x/identity", "x/compliance", "x/settlement", "x/attest")


class AssetKitError(Exception):
    """Base class of every error raised by this package."""

    def __init__(self, message: str, code: str, module: str) -> None:
        super().__init__(message)
        #: Stable machine-readable code.
        self.code = code
        #: Module the error belongs to, for example "x/asset".
        self.module = module


class ChainUpgradeRequired(AssetKitError):
    """Raised by every call of :class:`ChainClient`: the module is a proposal,
    is not part of QoreChain, and needs a chain upgrade that is not scheduled."""

    def __init__(self, module: str) -> None:
        super().__init__(
            f"{module} is a proposal and does not exist on QoreChain; it requires a chain upgrade "
            "that is not scheduled. Use MockChain to build and test, or the EVM adapters "
            "(contracts/) for what works on QoreChain today.",
            "CHAIN_UPGRADE_REQUIRED",
            module,
        )


class MockChainError(AssetKitError):
    """A message refused by :class:`MockChain`. ``code`` is the name of the value
    in the module's proposed ``ErrorCode`` enum, for example
    ``ERROR_CODE_ADDRESS_FROZEN``."""

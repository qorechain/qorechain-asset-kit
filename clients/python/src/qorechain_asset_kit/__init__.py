# SPDX-License-Identifier: Apache-2.0
"""Client for the PROPOSED QoreChain regulated-asset modules.

x/asset, x/identity, x/compliance, x/settlement and x/attest do not exist on
QoreChain and no upgrade adding them is scheduled. :class:`ChainClient`
therefore raises :class:`ChainUpgradeRequired` on every call; :class:`MockChain`
implements the proposed rules (docs/proposal.md) in memory for development.

Generated types live in the ``asset``, ``identity``, ``compliance``,
``settlement`` and ``attest`` submodules.
"""

from . import asset, attest, compliance, identity, settlement
from .chain import ChainClient
from .errors import MODULES, AssetKitError, ChainUpgradeRequired, MockChainError
from .mock import MockChain, MockEvent, ModuleContext, ModuleLogic

__version__ = "0.1.0"

__all__ = [
    "MODULES",
    "AssetKitError",
    "ChainClient",
    "ChainUpgradeRequired",
    "MockChain",
    "MockChainError",
    "MockEvent",
    "ModuleContext",
    "ModuleLogic",
    "asset",
    "attest",
    "compliance",
    "identity",
    "settlement",
]

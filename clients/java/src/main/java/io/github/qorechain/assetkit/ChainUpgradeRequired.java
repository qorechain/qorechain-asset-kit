// SPDX-License-Identifier: Apache-2.0
package io.github.qorechain.assetkit;

/**
 * Thrown by every call of {@link ChainClient}: the module is a proposal, is not
 * part of QoreChain, and needs a chain upgrade that is not scheduled.
 */
public final class ChainUpgradeRequired extends AssetKitError {
    private static final long serialVersionUID = 1L;

    public ChainUpgradeRequired(String module) {
        super(module + " is a proposal and does not exist on QoreChain; it requires a chain upgrade that is not scheduled. "
                + "Use MockChain to build and test, or the EVM adapters (contracts/) for what works on QoreChain today.",
                "CHAIN_UPGRADE_REQUIRED", module);
    }
}

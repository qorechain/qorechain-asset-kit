// SPDX-License-Identifier: Apache-2.0
package io.github.qorechain.assetkit;

/**
 * A message refused by {@link MockChain}. {@link #code()} is the name of the value
 * in the module's proposed {@code ErrorCode} enum, for example
 * {@code ERROR_CODE_ADDRESS_FROZEN}.
 */
public final class MockChainError extends AssetKitError {
    private static final long serialVersionUID = 1L;

    public MockChainError(String message, String code, String module) {
        super(message, code, module);
    }
}

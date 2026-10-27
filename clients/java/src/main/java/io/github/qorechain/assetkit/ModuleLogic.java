// SPDX-License-Identifier: Apache-2.0
package io.github.qorechain.assetkit;

import java.math.BigInteger;
import java.util.Map;
import java.util.Optional;

/** Logic of a compliance module in {@link MockChain}: returns a refusal reason, or empty to allow. */
@FunctionalInterface
public interface ModuleLogic {
    Optional<String> check(Context ctx);

    /**
     * Context passed to a module.
     *
     * @param chain the mock chain
     * @param assetId the asset
     * @param from sender, empty for a mint
     * @param to receiver
     * @param amount amount moved
     * @param params the binding's parameters, parsed from JSON (numbers as Long or Double, lists as List)
     */
    record Context(MockChain chain, String assetId, String from, String to, BigInteger amount, Map<String, Object> params) {}
}

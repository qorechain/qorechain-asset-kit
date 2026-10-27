// SPDX-License-Identifier: Apache-2.0
package io.github.qorechain.assetkit;

/**
 * The facade over the five proposed modules. {@link ChainClient} and
 * {@link MockChain} both implement it; an application written against it runs
 * on the mock today.
 */
public interface AssetKit {
    AssetApi asset();

    IdentityApi identity();

    ComplianceApi compliance();

    SettlementApi settlement();

    AttestApi attest();
}

// SPDX-License-Identifier: Apache-2.0
package io.github.qorechain.assetkit;

/**
 * The client for the real chain. The modules are a proposal, so every call
 * throws {@link ChainUpgradeRequired} without any network request.
 */
public final class ChainClient implements AssetKit {
    /** Library version. */
    public static final String VERSION = "0.1.0";

    private final String restUrl;
    private final String chainId;
    private final AssetApi asset = new ChainAssetApi();
    private final IdentityApi identity = new ChainIdentityApi();
    private final ComplianceApi compliance = new ChainComplianceApi();
    private final SettlementApi settlement = new ChainSettlementApi();
    private final AttestApi attest = new ChainAttestApi();

    public ChainClient() {
        this("", "");
    }

    /** Options kept for the day the modules exist; nothing is contacted today. */
    public ChainClient(String restUrl, String chainId) {
        this.restUrl = restUrl;
        this.chainId = chainId;
    }

    public String restUrl() {
        return restUrl;
    }

    public String chainId() {
        return chainId;
    }

    @Override
    public AssetApi asset() {
        return asset;
    }

    @Override
    public IdentityApi identity() {
        return identity;
    }

    @Override
    public ComplianceApi compliance() {
        return compliance;
    }

    @Override
    public SettlementApi settlement() {
        return settlement;
    }

    @Override
    public AttestApi attest() {
        return attest;
    }
}

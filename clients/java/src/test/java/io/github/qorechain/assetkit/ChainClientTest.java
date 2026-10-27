// SPDX-License-Identifier: Apache-2.0
package io.github.qorechain.assetkit;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.github.qorechain.assetkit.proto.asset.v1.MsgCreateAsset;
import io.github.qorechain.assetkit.proto.asset.v1.QueryAssetRequest;
import io.github.qorechain.assetkit.proto.attest.v1.QueryLatestRequest;
import io.github.qorechain.assetkit.proto.compliance.v1.QueryCheckRequest;
import io.github.qorechain.assetkit.proto.identity.v1.QueryIsVerifiedRequest;
import io.github.qorechain.assetkit.proto.settlement.v1.MsgAffirm;
import java.util.LinkedHashMap;
import java.util.Map;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

class ChainClientTest {
    private final ChainClient chain = new ChainClient("https://api-testnet.qore.host", "qorechain-diana");

    @Test
    void rejectsEveryAssetCallWithChainUpgradeRequired() {
        ChainUpgradeRequired e = assertThrows(ChainUpgradeRequired.class, () -> chain.asset().createAsset(
                MsgCreateAsset.newBuilder().setIssuer("qor1issuer").setAssetId("bond-2030").build()));
        assertEquals("x/asset", e.module());
        assertEquals("CHAIN_UPGRADE_REQUIRED", e.code());
        assertTrue(e.getMessage().contains("not scheduled"));
    }

    @Test
    void namesTheModuleOfEachCall() {
        Map<String, Executable> calls = new LinkedHashMap<>();
        calls.put("x/asset", () -> chain.asset().asset(QueryAssetRequest.newBuilder().setAssetId("x").build()));
        calls.put("x/identity", () -> chain.identity().isVerified(
                QueryIsVerifiedRequest.newBuilder().setAddress("qor1a").addTopics(1).build()));
        calls.put("x/compliance", () -> chain.compliance().check(QueryCheckRequest.newBuilder().setAssetId("x").build()));
        calls.put("x/settlement", () -> chain.settlement().affirm(MsgAffirm.newBuilder().setParty("qor1a").setId(1).build()));
        calls.put("x/attest", () -> chain.attest().latest(QueryLatestRequest.newBuilder().setAssetId("x").build()));
        calls.forEach((module, call) -> {
            AssetKitError e = assertThrows(ChainUpgradeRequired.class, call);
            assertEquals(module, e.module());
        });
    }
}

// SPDX-License-Identifier: Apache-2.0

import { describe, expect, it } from "vitest";
import { ChainClient, ChainUpgradeRequired } from "../src/index.js";

describe("ChainClient", () => {
  const chain = new ChainClient({ restUrl: "https://api-testnet.qore.host" });

  it("rejects every x/asset call with ChainUpgradeRequired", async () => {
    const err = await chain.asset.createAsset({ issuer: "qor1issuer", assetId: "bond-2030" }).catch((e: unknown) => e);
    expect(err).toBeInstanceOf(ChainUpgradeRequired);
    expect((err as ChainUpgradeRequired).module).toBe("x/asset");
    expect((err as ChainUpgradeRequired).code).toBe("CHAIN_UPGRADE_REQUIRED");
    expect((err as Error).message).toContain("not scheduled");
  });

  it("names the module of each call", async () => {
    const cases: Array<[Promise<unknown>, string]> = [
      [chain.asset.asset({ assetId: "x" }), "x/asset"],
      [chain.identity.isVerified({ address: "qor1a", topics: [1] }), "x/identity"],
      [chain.compliance.check({ assetId: "x" }), "x/compliance"],
      [chain.settlement.affirm({ party: "qor1a", id: "1" }), "x/settlement"],
      [chain.attest.latest({ assetId: "x" }), "x/attest"],
    ];
    for (const [call, module] of cases) {
      await expect(call).rejects.toMatchObject({ name: "ChainUpgradeRequired", module });
    }
  });
});

<!-- SPDX-License-Identifier: Apache-2.0 -->

# @qorechain/asset-kit (TypeScript)

Client for the **proposed** QoreChain regulated-asset modules (`x/asset`, `x/identity`, `x/compliance`, `x/settlement`, `x/attest`).

> These modules do not exist on QoreChain, on mainnet or on the testnet, and no chain upgrade that would add them is scheduled. `ChainClient` rejects every call with `ChainUpgradeRequired`. Build and test against `MockChain`. For what works on QoreChain today, use the EVM adapters in [`contracts/`](https://github.com/qorechain/qorechain-asset-kit/tree/main/contracts).

```ts
import { ChainClient, ChainUpgradeRequired, MockChain, asset } from "@qorechain/asset-kit";

const issuer = "qor1issuer", alice = "qor1alice", bob = "qor1bob";

// Today: a controlled failure, no network request.
await new ChainClient().asset.mint({ agent: issuer, assetId: "bond-2030", to: alice, amount: "10" })
  .catch((e) => e instanceof ChainUpgradeRequired); // e.module === "x/asset"

// Development: the proposed rules, in memory.
const chain = new MockChain();
await chain.asset.createAsset({ issuer, assetId: "bond-2030", flags: { freezable: true, pausable: true } });
await chain.asset.mint({ agent: issuer, assetId: "bond-2030", to: alice, amount: "100" });
await chain.asset.freeze({ agent: issuer, assetId: "bond-2030", holder: alice, frozen: true });
const q = await chain.asset.canTransfer({ assetId: "bond-2030", from: alice, to: bob, amount: "1" });
// q.allowed === false, q.code === asset.ErrorCode.ERROR_CODE_ADDRESS_FROZEN
```

- Requests and responses are the types generated from [`proto/`](https://github.com/qorechain/qorechain-asset-kit/tree/main/proto) (namespaces `asset`, `identity`, `compliance`, `settlement`, `attest`); 64-bit integers are strings.
- `MockChain` refusals throw `MockChainError` with `code` set to the name of the proposed `ErrorCode` value and `module` set to the module.
- Mock helpers: `setHybridKey`, `fundBank`, `bankBalance`, `advance(blocks, seconds)`, `events(type?)`, `defineModuleLogic(moduleId, fn)`.
- The rules are described in [docs/proposal.md](https://github.com/qorechain/qorechain-asset-kit/blob/main/docs/proposal.md).

Regenerate the code with `pnpm gen` (needs `protoc` on the PATH). Build, typecheck and test with `pnpm build && pnpm typecheck && pnpm test`.

Licence: Apache-2.0.

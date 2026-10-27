<!-- SPDX-License-Identifier: Apache-2.0 -->

# QoreChain Asset Kit for Java

`io.github.qorechain:asset-kit` (Java 17+): types generated from the proposed regulated-asset modules in [`proto/`](https://github.com/qorechain/qorechain-asset-kit/tree/main/proto), a client facade, and an in-memory `MockChain`.

> **The modules are a proposal.** `x/asset`, `x/identity`, `x/compliance`, `x/settlement` and `x/attest` do not exist on QoreChain, and no chain upgrade that would add them is scheduled. See [docs/proposal.md](https://github.com/qorechain/qorechain-asset-kit/blob/main/docs/proposal.md).

| Class | What it does |
|---|---|
| `ChainClient` | The client for the real chain. Every call throws `ChainUpgradeRequired` (code `CHAIN_UPGRADE_REQUIRED`, `module()` such as `"x/asset"`) without any network request. |
| `MockChain` | Implements the proposed rules in memory, for building and testing applications. Refusals throw `MockChainError` whose `code()` is the name of the module's `ErrorCode` value, for example `ERROR_CODE_ADDRESS_FROZEN`. |

What works on QoreChain today is the set of EVM adapters in [`contracts/`](https://github.com/qorechain/qorechain-asset-kit/tree/main/contracts) (ERC-3643 and CMTAT tokens on the QoreChain EVM Engine).

## Example

```java
import io.github.qorechain.assetkit.MockChain;
import io.github.qorechain.assetkit.proto.asset.v1.*;

MockChain chain = new MockChain();
chain.asset().createAsset(MsgCreateAsset.newBuilder()
        .setIssuer("qor1issuer").setAssetId("bond-2030")
        .setFlags(RwaFlagsV0.newBuilder().setFreezable(true).setPausable(true))
        .build());
chain.asset().mint(MsgMint.newBuilder()
        .setAgent("qor1issuer").setAssetId("bond-2030").setTo("qor1alice").setAmount("100").build());
chain.asset().freeze(MsgFreeze.newBuilder()
        .setAgent("qor1issuer").setAssetId("bond-2030").setHolder("qor1alice").setFrozen(true).build());
// chain.asset().transfer(...) from qor1alice now throws MockChainError ERROR_CODE_ADDRESS_FROZEN
```

`MockChain` helpers: `setHybridKey`, `hasHybridKey`, `fundBank`, `bankBalance`, `advance(blocks, seconds)`, `height()`, `time()`, `events(type)`, `defineModuleLogic(moduleId, logic)`.

## Build and test

```bash
mvn -B test
```

The generated sources under `src/main/java/io/github/qorechain/assetkit/proto` are checked in; regenerate them with `scripts/gen.sh` (protoc 36.x, matching the `protobuf-java` 4.36.2 runtime).

## License

[Apache-2.0](https://github.com/qorechain/qorechain-asset-kit/blob/main/LICENSE).

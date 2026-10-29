<!-- SPDX-License-Identifier: Apache-2.0 -->

# QoreChain Asset Kit: Go client

`github.com/qorechain/qorechain-asset-kit/clients/go` (package `assetkit`) is the Go client for the **proposed** regulated-asset modules `x/asset`, `x/identity`, `x/compliance`, `x/settlement` and `x/attest`.

> These modules are a proposal. They do not exist on QoreChain, on mainnet or on the testnet, and no chain upgrade that would add them is scheduled.

| Part | What it does |
|---|---|
| `gen/qorechain/<module>/v1` | Go types generated from the proposed protos in [`proto/`](https://github.com/qorechain/qorechain-asset-kit/tree/main/proto) |
| `NewChainClient()` | the client for the real chain: every call returns `*ChainUpgradeRequired` (code `CHAIN_UPGRADE_REQUIRED`, field `Module`) without any network request |
| `NewMockChain()` | an in-memory implementation of the rules in [`docs/proposal.md`](https://github.com/qorechain/qorechain-asset-kit/blob/main/docs/proposal.md), for building and testing applications |

What works on QoreChain today are the EVM contracts in [`contracts/`](https://github.com/qorechain/qorechain-asset-kit/tree/main/contracts) (ERC-3643 and CMTAT deployments, the hybrid-holder guard, vault wrappers).

## Example

```go
ctx := context.Background()
chain := assetkit.NewMockChain()
_, err := chain.Asset().CreateAsset(ctx, &assetv1.MsgCreateAsset{
	Issuer: "qor1issuer", AssetId: "bond-2030", Flags: &assetv1.RwaFlagsV0{Freezable: true},
})
_, err = chain.Asset().Mint(ctx, &assetv1.MsgMint{Agent: "qor1issuer", AssetId: "bond-2030", To: "qor1alice", Amount: "100"})

// A refused message returns *assetkit.MockChainError (Module, Code such as ERROR_CODE_ADDRESS_FROZEN, Message).
_, err = assetkit.NewChainClient().Asset().Mint(ctx, &assetv1.MsgMint{})
var upgrade *assetkit.ChainUpgradeRequired
errors.As(err, &upgrade) // true, upgrade.Module == "x/asset"
```

`MockChain` trusts the signer fields of messages (there are no signatures). Helpers: `SetHybridKey`, `FundBank`, `BankBalance`, `Advance(blocks, seconds)`, `Events(type)`, `DefineModuleLogic(moduleID, logic)`.

## Development

```bash
go vet ./... && go test ./...
scripts/gen.sh   # regenerate gen/ (protoc and protoc-gen-go v1.36.12 on PATH)
```

## License

[Apache-2.0](https://github.com/qorechain/qorechain-asset-kit/blob/main/LICENSE).

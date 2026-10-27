# QoreChain Asset Kit

Open-source tooling from the QoreChain Association for issuing and managing regulated tokenized assets (real-world assets) on [QoreChain](https://www.qorechain.io).

**What works on QoreChain today is EVM contracts.** Native regulated-asset modules (`x/asset`, `x/identity`, `x/compliance`, `x/settlement`, `x/attest`) do not exist on QoreChain, on mainnet or on the testnet, and no chain upgrade that would add them is scheduled. This repository publishes them as a **proposal**, with clients that report the missing upgrade and an in-memory mock for building applications against the proposed rules.

## What works today and what needs a chain upgrade

| Capability | Today on QoreChain (EVM Engine) | Native module (proposal) |
|---|---|---|
| Issue a permissioned token | Yes: ERC-3643 (T-REX 4.1.6) or CMTAT 3.2.0, as dependencies | `x/asset`: requires a chain upgrade (not scheduled) |
| Holder allowlist, identity and claims | Yes: ERC-3643 identity registry with ONCHAINID; CMTAT rules | `x/identity`: requires a chain upgrade (not scheduled) |
| Freeze, partial freeze, pause, forced transfer, clawback | Yes: provided by ERC-3643 and CMTAT | `x/asset`: requires a chain upgrade (not scheduled) |
| Require a registered ML-DSA-87 key with proof of possession for holders | **Testnet only**: `QoreChainHybridHolderGuard`, through a CMTAT rule or an ERC-3643 module. It reads the `pqcKeyStatus` precompile (`0x0A02`), which is not active on mainnet; activation is undecided. On mainnet the guard fails closed. | `require_hybrid_signature` flag of `x/asset`: requires a chain upgrade (not scheduled) |
| Pluggable compliance rules | Yes: ERC-3643 modular compliance, CMTAT rule engine | `x/compliance` registry with versioned modules: requires a chain upgrade (not scheduled) |
| Fund shares with sync or async subscriptions | Yes: ERC-4626 and ERC-7540 vaults with restricted shares | not proposed |
| Partitions (classes, tranches) | Interface only (ERC-7518 sketch); one token per class works today | not proposed |
| Delivery versus payment with bilateral affirmation | Not provided by this kit on EVM | `x/settlement`: requires a chain upgrade (not scheduled) |
| NAV, reserves and audit attestations with staleness | Not provided by this kit on EVM | `x/attest`: requires a chain upgrade (not scheduled) |
| Issuer console | Yes: `packages/issuer-console` (EIP-6963 wallets, testnet) | n/a |

Every EVM transaction on QoreChain needs the sender's registered ML-DSA-87 key and an open EVM authorization window, opened by a hybrid-signed transaction on the native lane. See [docs/evm-adapters.md](docs/evm-adapters.md).

## Contents

| Path | Contents | Status |
|---|---|---|
| [`contracts/`](contracts) | Foundry project: hybrid-holder guard, CMTAT rule, ERC-3643 module, ERC-4626 and ERC-7540 vaults, ERC-7518 interface, deployment scripts | Works on the testnet (dry-run scripts; nothing deployed by this repository) |
| [`packages/issuer-console`](packages/issuer-console) | React app over the EVM adapters, no backend | Testnet |
| [`proto/`](proto) | Proposed protobuf interfaces of the five modules | Proposal, not on chain |
| [`clients/ts`](clients/ts), [`clients/python`](clients/python), [`clients/go`](clients/go), [`clients/java`](clients/java) | Code generated from the proposed protos, a `ChainClient` that throws `ChainUpgradeRequired`, and a `MockChain` implementing the proposed rules | Proposal; mock for development |
| [`docs/proposal.md`](docs/proposal.md) | Semantics of the proposed modules and their design references | Proposal |
| [`docs/evm-adapters.md`](docs/evm-adapters.md) | The EVM adapters, upstream licences, testnet deployment | |
| [`docs/technology-standards.md`](docs/technology-standards.md) | Reliability, governance, upgrade authority, MEV, observability, incidents, key management, from verifiable sources | |
| [`legal/`](legal) | Templates for a Swiss ledger-based security, a Liechtenstein TVTG token, and an EU DLT Pilot Regime engagement | **Drafts for discussion, not reviewed by counsel. Not legal advice.** |

## Quick start

```bash
git clone --recurse-submodules https://github.com/qorechain/qorechain-asset-kit
cd qorechain-asset-kit

# EVM adapters
cd contracts && forge build && forge test && cd ..

# TypeScript client (mock) and issuer console
pnpm install && pnpm -r build && pnpm -r test

# Other clients
(cd clients/python && python -m pip install -r requirements-dev.txt && python -m pip install -e . && pytest)
(cd clients/go && go test ./...)
(cd clients/java && mvn -B test)
```

```ts
import { ChainClient, ChainUpgradeRequired, MockChain } from "@qorechain/asset-kit";

await new ChainClient().asset.createAsset({ issuer, assetId: "bond-2030" }); // rejects: ChainUpgradeRequired("x/asset")

const chain = new MockChain(); // the proposed rules, in memory
await chain.asset.createAsset({ issuer, assetId: "bond-2030", flags: { freezable: true } });
```

## Legal templates

The documents in [`legal/`](legal) are templates for discussion. They are not legal advice, have not been reviewed by counsel, and must be reviewed by qualified counsel in the relevant jurisdiction before any use.

## Versioning

Pre-1.0. The proposed protos may change in any minor version; the [changelog](CHANGELOG.md) lists every change.

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md). Report vulnerabilities privately as described in [SECURITY.md](SECURITY.md).

## License

Code: [Apache-2.0](LICENSE), except the files that compile together with the GPL-3.0 ERC-3643 reference implementation (`contracts/script/erc3643/`, `contracts/test/erc3643/`), which are GPL-3.0-or-later ([LICENSES/GPL-3.0.txt](LICENSES/GPL-3.0.txt)). Documentation in `docs/` and `legal/`: Apache-2.0 as well. Dependencies keep their own licences; see [NOTICE](NOTICE). Copyright 2026 QoreChain Association.

# EVM adapters (Foundry)

Contracts that run on the QoreChain EVM Engine today: a hybrid-holder guard over the `pqcKeyStatus` precompile (testnet only until it is active on mainnet), a CMTAT v3 rule and an ERC-3643 compliance module mapped to it, and ERC-4626 / ERC-7540 vaults with restricted shares.

```bash
git submodule update --init          # dependencies, pinned (not their nested submodules)
forge build && forge test            # 33 tests, no network
forge script script/DeployCmtat.s.sol --rpc-url qorechain_testnet --sender <deployer>   # dry run
```

Read [docs/evm-adapters.md](../docs/evm-adapters.md) before deploying: it covers the licences of the upstream contracts, the testnet-only status of the guard, and the native-lane steps (registered ML-DSA-87 key, EVM authorization window) every broadcast needs.

Licences: everything here is Apache-2.0 except `script/erc3643/*.sol` and `test/erc3643/*.sol`, which compile together with the GPL-3.0 ERC-3643 reference implementation and are GPL-3.0-or-later (full text in [`LICENSES/GPL-3.0.txt`](../LICENSES/GPL-3.0.txt)). Dependencies under `lib/` keep their own licences.

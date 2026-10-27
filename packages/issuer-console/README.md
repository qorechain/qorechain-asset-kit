<!-- SPDX-License-Identifier: Apache-2.0 -->

# Issuer console

A small single-page app over the EVM adapters of this repository, for issuers and agents testing regulated tokens on the **QoreChain Testnet** (EVM chain id 9800). No backend: the page talks only to your wallet.

- **Connect** through EIP-6963 (any wallet that announces itself), add or switch to the QoreChain Testnet.
- **Create** a CMTAT v3.2.0 token gated by the hybrid-holder guard: three deployments (guard, CMTAT rule, token), the same as `contracts/script/DeployCmtat.s.sol`.
- **Open** an existing CMTAT or ERC-3643 token by address (ERC-3643 tokens are deployed with the Foundry script `contracts/script/erc3643/DeployErc3643.s.sol`).
- **Identity**: ERC-3643 identity registry (register, delete, is verified); for CMTAT tokens, the guard's key status and exemptions for contract holders.
- **Agent actions**: mint, burn, freeze, unfreeze, forced transfer, pause, unpause.
- **Holders and audit log** from chain events (Transfer, AddressFrozen in both layouts, TokensFrozen and TokensUnfrozen, Paused, Unpaused, Mint, Burn, RecoverySuccess, IdentityRegistered, IdentityRemoved, ExemptionSet), read in block chunks from a start block you choose; every holder balance is confirmed with `balanceOf`.

## Testnet only

The hybrid-holder guard reads the `pqcKeyStatus` precompile at `0x0A02`, which is active on the testnet only. On mainnet (chain 9801) the console shows a warning and disables token creation: there the guard fails closed. See [docs/evm-adapters.md](https://github.com/qorechain/qorechain-asset-kit/blob/main/docs/evm-adapters.md).

## Before any transaction

Every EVM transaction on QoreChain needs, on the native lane:

1. a registered ML-DSA-87 key for the sending account (`MsgRegisterPQCKeyV2` with a proof of possession), and
2. an open EVM authorization window, opened by a hybrid-signed `/qorechain.pqc.v1.MsgOpenEVMWindow`. For deployments, leave `allowed_targets` empty (a window with targets refuses contract creation) and size `max_value` to cover the value plus the maximum fee of every transaction.

The console does not open windows. Reads (`eth_call`, logs) need no window.

**Wallets:** any EIP-6963 wallet that can sign EVM transactions on the QoreChain Testnet.

## Run

```bash
pnpm install              # from the repository root
pnpm --filter @qorechain/issuer-console dev
pnpm --filter @qorechain/issuer-console build    # static files in dist/, no source maps
pnpm --filter @qorechain/issuer-console test
```

The production build sets a Content-Security-Policy with `connect-src 'none'`: the page itself makes no network request, everything goes through the wallet's injected provider. If a wallet's injected script needs to fetch from the page context, serve the files with a looser policy of your own.

After changing the contracts, refresh the deployable artifacts (ABI and creation bytecode only):

```bash
(cd contracts && forge build) && pnpm --filter @qorechain/issuer-console sync-artifacts
```

## Not covered

- Opening EVM windows or registering keys (native-lane, hybrid-signed transactions).
- Deploying ERC-3643 suites (use the Foundry script), ONCHAINID creation and claims, compliance module configuration.
- CMTAT role management (grant minter, burner, enforcer, pauser roles with the token's `grantRole`), partial freezes, documents, snapshots.
- Vault deployment and operation (use `contracts/script/DeployVaults.s.sol`).
- The proposed native modules (`x/asset` and others): they do not exist on chain.

## Licences

The console is Apache-2.0. `src/artifacts/CMTATStandalone.json` contains the compiled bytecode of CMTAT 3.2.0 (Capital Markets and Technology Association), which is licensed under MPL-2.0; its source is at <https://github.com/CMTA/CMTAT>. The built app ships the repository's `NOTICE` file next to `index.html`, listing every dependency and its licence.

<!-- SPDX-License-Identifier: Apache-2.0 -->

# EVM adapters

The contracts in [`contracts/`](../contracts) run on the QoreChain EVM Engine today. They let an issuer use two open token standards for regulated assets, ERC-3643 and CMTAT, and add one QoreChain-specific control: a holder check against the account's registered ML-DSA-87 key.

| Contract | What it is | Licence |
|---|---|---|
| `QoreChainHybridHolderGuard` | Reads the `pqcKeyStatus` precompile (`0x0A02`) and says whether an address has a registered ML-DSA-87 key (algorithm id 1) **with proof of possession**. Strict decoding of the answer. Owner-managed exemptions for contracts (vaults, escrows). Fails closed. | Apache-2.0 |
| `QoreChainHybridHolderRule` | CMTAT v3 rule mapped to the guard. Usable directly as a CMTAT `ruleEngine`, or as one rule inside a CMTA RuleEngine. | Apache-2.0 |
| `QoreChainHybridHolderModule` | ERC-3643 (T-REX v4) modular-compliance module mapped to the guard. Plug and play. | Apache-2.0 |
| `QoreChainRwaVault` | ERC-4626 vault (OpenZeppelin) whose shares are restricted by the guard or any `IHolderEligibility` policy. | Apache-2.0 |
| `QoreChainRwaAsyncVault` | ERC-7540 vault with asynchronous deposits and redemptions processed in batches by an operator, shares restricted the same way. The price at fulfilment is the vault's own share price (asset balance per share); there is no NAV input. | Apache-2.0 |
| `IERC7518` | Interface sketch for ERC-7518 partitions. No implementation. | Apache-2.0 |

## Testnet only, for now

The guard depends on the `pqcKeyStatus` precompile at `0x0A02`. It is active on the QoreChain testnet (`qorechain-diana`, EVM chain id 9800). On mainnet (`qorechain-vladi`, EVM chain id 9801) it is not active: `eth_call` to `0x0A02` returns empty data, and activating it is a governance decision that has not been taken. On a network without the precompile the guard **fails closed**: every address that is not explicitly exempt is ineligible, so a token using the rule or the module cannot move between ordinary holders. The deployment scripts refuse to run against chain id 9801.

The precompile's answer is `pqcKeyStatus(address) returns (bool registered, uint8 algorithmId, bytes pubkey, bool possessionProven)`. The guard requires `registered && possessionProven`: a key that was registered without a proof of possession could belong to someone else, so it is not enough. An answer in the older three-field layout (no `possessionProven`) is treated as "not proven".

## How the pieces fit

```
                 CMTAT v3 token  ── ruleEngine ──>  QoreChainHybridHolderRule ──┐
                                                                                ├──> QoreChainHybridHolderGuard ──> 0x0A02 pqcKeyStatus
ERC-3643 token ─> ModularCompliance ─ module ──>  QoreChainHybridHolderModule ──┤         (exemptions for contracts)
                                                                                │
       ERC-4626 / ERC-7540 vault shares ─────────── IHolderEligibility ─────────┘
```

The QoreChain check is additive. Every control of the upstream standard still applies: ERC-3643 identity registry, claim topics, trusted issuers, freeze, partial freeze, pause, forced transfer and recovery; CMTAT freeze, partial freeze, pause, forced transfer, documents, snapshots and its other modules.

**What the check covers, and what it does not.**

- **Receiving is what matters.** A mint or transfer to an address without a registered, possession-proven key is refused (fail closed). Burns are never refused by the CMTAT rule, so a holder who lost eligibility can still be redeemed. In ERC-3643, `burn` does not consult the compliance modules at all, so the same holds there.
- **Senders.** For transfers, the CMTAT rule also checks the sender and, for `transferFrom`, the spender (code 62). The ERC-3643 module checks sender and receiver; ERC-3643 does not pass the spender to compliance, so a `transferFrom` spender is not checked there.
- **Agent powers bypass the guard.** In both standards, forced transfer and wallet recovery by an agent do not go through the transfer rules: CMTAT `forcedTransfer` and ERC-3643 `forcedTransfer` / `recoveryAddress` move balances without asking the rule or the module. An agent can therefore place tokens on an address that has no key. Restrict who holds the agent roles accordingly.

**Vault shares are restricted too.** A vault over a restricted token would otherwise turn it into an unrestricted one: anyone could buy shares from a holder. Both vaults check the receiving side of every share movement with the same policy (`maxDeposit` and `maxMint` return zero for an ineligible receiver); redemptions are never refused, so a holder who lost eligibility can still exit. Pending ERC-7540 requests cannot be cancelled in 0.1.0. If an agent of the underlying token moves assets out of the asynchronous vault, `totalAssets` reads zero instead of reverting, and claims that need the missing assets fail until the issuer restores the vault's balance. The vault contract itself must be allowed to hold the underlying asset: register it in the ERC-3643 identity registry (or the CMTAT rule's allowlist, if you add one) and exempt it in the guard. `script/DeployVaults.s.sol` does the guard exemption.

## Licences of the upstream contracts

| Upstream | Version | Licence | How it is used |
|---|---|---|---|
| ERC-3643 reference implementation (T-REX), Tokeny | 4.1.6 | GPL-3.0 (or later) | git submodule, unmodified. Only the deployment script `script/erc3643/*.sol` and the integration test `test/erc3643/TrexIntegration.t.sol` import it; those files are GPL-3.0-or-later and say so in their header; the licence text is in [`LICENSES/GPL-3.0.txt`](../LICENSES/GPL-3.0.txt). Nothing under `src/` imports it: the module declares the compliance-module functions in its own interface (`IERC3643ComplianceModule`). |
| ONCHAINID, ONCHAINID / Tokeny | 2.2.1 | GPL-3.0 | git submodule, unmodified, used by the T-REX deployment and test only. |
| OpenZeppelin Contracts | 4.9.6 | MIT | git submodule, required by T-REX and ONCHAINID. |
| OpenZeppelin Contracts Upgradeable | 4.9.6 | MIT | git submodule, required by T-REX. |
| CMTAT, Capital Markets and Technology Association | 3.2.0 | MPL-2.0 | git submodule, unmodified. The rule imports CMTAT interfaces; `script/DeployCmtat.s.sol` and the CMTAT test deploy `CMTATStandalone`. MPL-2.0 is file-level copyleft: our files stay Apache-2.0, CMTAT files stay MPL-2.0. |
| OpenZeppelin Contracts | 5.5.0 | MIT | git submodule; base of the vaults and the guard, and required by CMTAT. |
| OpenZeppelin Contracts Upgradeable | 5.5.0 | MIT | git submodule, required by CMTAT. |
| forge-std | 1.17.0 | MIT OR Apache-2.0 | git submodule, tests and scripts only. |

No GPL-3.0 or MPL-2.0 source is copied into this repository. A deployed ERC-3643 token is the T-REX code and carries the T-REX licence; a deployed CMTAT token carries the MPL-2.0. The [NOTICE](../NOTICE) file lists every dependency.

**CMTA RuleEngine.** The CMTA RuleEngine v3 is still published as release candidates. The rule therefore works without it (as the token's `ruleEngine` directly) and also implements the RuleEngine rule interface (`canReturnTransferRestrictionCode`; it advertises both ERC-165 ids in use, `0x2497d6cb` from the v3 release candidates and `0xb1a69752` from the current development line), so it can be added with `addRule` once a final RuleEngine v3 is released.

**ERC-7518.** The ERC is in Review and its optional extensions are still changing. No maintained reference implementation was selected; this repository ships an interface only. `src/partitions/IERC7518.sol` is the core interface transcribed from the ERC text; a test checks that its ERC-165 id is `0x5a264a5d`, the value the ERC specifies. Partitions can be modelled today with one CMTAT or ERC-3643 token per class or tranche, sharing one identity registry or rule.

## Deploying on the testnet

Run every script as a **dry run first**. Without `--broadcast`, Foundry simulates against a fork of the testnet state and spends nothing.

```bash
cd contracts
forge build
forge script script/DeployCmtat.s.sol            --rpc-url qorechain_testnet --sender <deployer>
forge script script/erc3643/DeployErc3643.s.sol  --rpc-url qorechain_testnet --sender <deployer>
forge script script/DeployVaults.s.sol           --rpc-url qorechain_testnet --sender <deployer>
```

`script/QoreChainTestnet.sol` prints whether the precompile answers on the real node (read with `eth_call`, because a local fork does not run QoreChain precompiles) and the deployer's key status.

Gas used by the dry runs on 27 October 2026, as estimated by Foundry for the whole script:

| Script | Estimated gas |
|---|---|
| `DeployCmtat` (guard, rule, CMTAT token) | 8,341,780 |
| `DeployErc3643` (T-REX implementations, authorities, factories, guard, module, one token suite) | 33,532,142 |
| `DeployVaults` (example CMTAT token, two vaults, two exemptions) | 12,889,700 |

### Before `--broadcast`

Every EVM transaction on QoreChain is admitted only if, on the native (Cosmos SDK) lane:

1. **the sender has a registered ML-DSA-87 key**, registered with `MsgRegisterPQCKeyV2` and a proof of possession; and
2. **the sender has an open EVM authorization window**, opened by `/qorechain.pqc.v1.MsgOpenEVMWindow` in a transaction signed with the hybrid (secp256k1 + ML-DSA-87) signature.

Set the window for a deployment like this:

- `blocks`: long enough for the script (at most 17,280 blocks).
- `max_txs`: at least the number of transactions the script sends.
- `max_value`: the value sent **plus the maximum fee** of every transaction (gas limit times max fee per gas), in uqor. At the network's 112.5 gwei gas price, 33.5 million gas is about 3.8 QOR; leave a margin.
- `allowed_targets`: **empty**. A window restricted to targets refuses contract creation.
- `native_only`: false.

Opening the window advances the account sequence, which is also the EVM nonce. Open the window first, then run the script. The QoreChain SDK builds the message (`pqc.openEvmWindow` in TypeScript, `qorsdk.msg.pqc.open_evm_window` in Python) and reads the window (`fetchEvmWindow`, `get_evm_window`). Calls and gas estimation need no window.

Then exempt every contract that must hold the asset (vaults, escrows) in the guard, register holders in the token's own compliance (ERC-3643 identity registry; CMTAT allowlist or RuleEngine rules), and check holders with `guard.isHybridHolder(address)` before minting.

### Network behaviour to keep in mind

- `PREVRANDAO` is a constant on QoreChain. None of these contracts uses it; do not add randomness that depends on it.
- Blob transactions (type 3) are refused; types 0, 1, 2 and 4 are accepted.
- EIP-7702 delegations need the authority's own post-quantum consent (`MsgAuthorizeEVMDelegation`); the sponsor's window is not consent.

## Tests

`forge test` runs 33 tests with a test double of the precompile etched at `0x0A02`:

- the guard: inactive precompile, registered without proof, registered with proof, algorithm id other than ML-DSA-87, legacy and malformed answers (strict decoding), exemptions;
- the CMTAT rule on a real CMTAT v3.2.0 token: mint, transfer, refusal codes, burns from a holder who lost eligibility, fail-closed without the precompile, CMTAT freeze and pause still applying, both RuleEngine interface ids;
- the ERC-3643 module, alone and bound to a full T-REX 4.1.6 suite (identity registry, modular compliance, freeze, forced transfer, contract exemption);
- the ERC-4626 and ERC-7540 vaults: restricted receivers, redemption by a holder who lost eligibility, asynchronous deposit and redemption with a change in the vault's asset balance, operators, reverting previews, zero-share fulfilment, zero admin, `totalAssets` after assets are moved out of the vault, interface ids;
- the ERC-7518 interface id.

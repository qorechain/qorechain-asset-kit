<!-- SPDX-License-Identifier: Apache-2.0 -->

# QoreChain Technology Standards for Tokenized Assets

Version 0.1.0 (draft). Facts checked on 27 October 2026.

This document describes the QoreChain networks as an issuer, transfer agent, auditor or regulator would need to see them before putting a regulated asset on them. It covers reliability, governance, upgrade authority, transaction ordering, observability, incident handling and key management. It is written from public, checkable sources only: the live REST, RPC and EVM JSON-RPC endpoints of the two public networks, and the public documentation at <https://docs.qorechain.io>. Every figure carries its source. Where a figure is not measured or a policy is not published, the document says so instead of estimating.

## 1. Scope and how to read this document

### 1.1 What this document covers

- The QoreChain mainnet, chain id `qorechain-vladi`, and the public testnet, chain id `qorechain-diana`.
- The properties of those networks that matter to a tokenized-asset programme: how blocks are produced and finalised, who can change the rules and how, what the EVM execution environment does differently from Ethereum, how transactions are ordered, what can be observed from outside, how incidents are reported, and how keys are held.
- The EVM adapters in this repository (ERC-3643, CMTAT, ERC-4626 and ERC-7540 wrappers) run on the QoreChain EVM Engine today. Sections 7 and 11 describe the constraints that apply to them.

### 1.2 What this document does not cover

- **Native asset modules.** The modules proposed in this repository (`x/asset`, `x/identity`, `x/compliance`, `x/settlement`, `x/attest`) do not exist on any QoreChain network and no chain upgrade that would add them is scheduled. Nothing in this document describes them as available. See [proposal.md](proposal.md).
- **Legal qualification.** Whether a token on QoreChain qualifies as a ledger-based security, a token container or a DLT financial instrument in a given jurisdiction is a legal question. The templates in `legal/` are drafts for discussion with counsel, not advice.
- **Service levels.** QoreChain publishes no service level agreement for its public endpoints. Nothing here is an SLA.

### 1.3 Labels

Each fact is marked, explicitly or by its source column, with one of four labels.

| Label | Meaning |
| --- | --- |
| **Verified** | Read from a live public endpoint on 27 October 2026. The query is listed in section 15 and can be repeated. |
| **Documented** | Stated in the public documentation at docs.qorechain.io. The page is named. |
| **Not measured** | Nobody has published a measurement that this document could cite. No number is given. |
| **Not published** | No public policy or commitment exists that this document could cite. |

Values read from a live chain change. Governance can change any parameter quoted here. Before relying on a value, read it again from the endpoint named in the source.

## 2. Network facts

| Property | Mainnet | Testnet | Source |
| --- | --- | --- | --- |
| Chain id | `qorechain-vladi` | `qorechain-diana` | Verified: RPC `/status` (`node_info.network`) on both networks |
| EVM chain id | 9801 (`0x2649`) | 9800 (`0x2648`) | Verified: `eth_chainId` on both EVM endpoints |
| Live since | 7 June 2026 | (testnet) | Documented: REST and gRPC Endpoints page |
| Node release in force | v3.2.4 | v3.2.6 | Verified: `applied_plan`, release manifests |
| Fee and staking denomination | `uqor` (1 QOR = 10^6 uqor on the native lane) | same | Verified: staking params, EVM config `decimals: 6` |
| EVM extended denomination | `aqor` (18 decimals on the EVM lane) | same | Verified: EVM params `extended_denom_options` |
| Consensus REST (LCD) | `https://api.qore.host` | `https://api-testnet.qore.host` | Verified |
| Consensus RPC | `https://rpc.qore.host` | `https://rpc-testnet.qore.host` | Verified: `/status` |
| EVM JSON-RPC | `https://evm.qore.host` | `https://evm-testnet.qore.host` | Verified |
| Public gRPC | none | none | Documented: REST and gRPC Endpoints page ("There is no public gRPC endpoint") |
| Block explorer | `https://explore.qore.network` | | Verified (HTTP 200) |
| Release manifest | `https://download.qore.host/mainnet/latest.json` | `https://download.qore.host/testnet/latest.json` | Verified |

The public endpoints are a convenience. An issuer that needs independent confirmation of balances, events or finality should run its own node and compare (see section 10).

## 3. Consensus, finality and the validator set

### 3.1 Block production and finality

QoreChain uses a Byzantine fault tolerant consensus engine with stake-weighted voting. A block is committed when validators holding more than two thirds of the voting power have voted for it, and a committed block is not reorganised: there is no probabilistic finality and no fork choice rule that could replace a committed block. The documentation states that the triple-pool selection logic of the `x/qca` module is "not yet wired into block production, rewards, slashing or the governance tally", and that today the proposer rotation is the standard stake-weighted rotation (Documented: Consensus Mechanism page).

Consequences for an issuer:

- A transfer, mint, freeze or forced transfer is final once its block is committed. There is no confirmation-depth policy to choose.
- Liveness (whether new blocks are produced) depends on more than two thirds of voting power being online and in agreement. Safety (no conflicting committed blocks) holds as long as less than one third of voting power is faulty.

### 3.2 Consensus parameters

| Parameter | Value (both networks) | Source |
| --- | --- | --- |
| Validator consensus key types accepted | `ed25519` only | Verified: `/cosmos/consensus/v1/params` |
| Vote extensions | off (`vote_extensions_enable_height` = 0) | Verified: same |
| Maximum block size | 22,020,096 bytes | Verified: same |
| Maximum block gas (consensus level) | unlimited (`-1`) | Verified: same |
| Evidence maximum age | 100,000 blocks or 172,800 s (48 hours) | Verified: same |

Validator consensus keys are classical ed25519 keys. The ML-DSA-87 post-quantum keys described in section 11 apply to accounts and transactions, not to consensus votes.

### 3.3 Validator set on 27 October 2026

| Property | Mainnet | Testnet | Source |
| --- | --- | --- | --- |
| Bonded validators | 8 | 4 | Verified: `/cosmos/staking/v1beta1/validators?status=BOND_STATUS_BONDED` |
| Jailed among bonded | 0 | 0 | Verified: same |
| Consensus key type of every bonded validator | ed25519 | ed25519 | Verified: same |
| Maximum validator set size | 100 | 100 | Verified: staking params |
| Unbonding time | 1,814,400 s (21 days) | same | Verified: staking params |

Voting power in the consensus engine is proportional to bonded tokens. The distribution of bonded stake changes with delegations; an issuer that needs it for a risk assessment should compute it from the `tokens` field of the bonded validators (same endpoint) on the date of the assessment. Any validator or group of validators holding more than one third of voting power can stop new blocks from being committed by going offline or refusing to vote; it cannot, on its own, commit a block or rewrite a committed one.

Validator admission is gated: creating a validator requires a self-bond of at least 100,000 QOR and an active `validator_operator` licence on the operator account (Documented: Consensus Mechanism page, "Validator admission and staking rules in force").

### 3.4 Slashing

| Parameter | Value (both networks) | Source |
| --- | --- | --- |
| Downtime window | 10,000 blocks | Verified: `/cosmos/slashing/v1beta1/params` |
| Minimum signed per window | 5 % | Verified: same |
| Downtime jail duration | 600 s | Verified: same |
| Slash fraction, double sign | 5 % | Verified: same |
| Slash fraction, downtime | 1 % | Verified: same |

## 4. Reliability

### 4.1 What is measured

The only reliability figure this document could measure from public data is the observed average block interval. Method: read the latest height and block time from the consensus RPC `/status` (`https://rpc.qore.host`, `https://rpc-testnet.qore.host`), then the header 10,000 and 100,000 blocks earlier from `/block?height={height}` on the same RPC, and divide the time difference by the height difference.

| Network | Window (heights) | Window (UTC) | Observed average block interval |
| --- | --- | --- | --- |
| Mainnet | 3,846,987 to 3,856,987 | 27 Oct 2026 11:48 to 20:31 | 3.138 s |
| Mainnet | 3,756,987 to 3,856,987 | 24 Oct 2026 04:40 to 27 Oct 2026 20:31 | 3.163 s |
| Testnet | 8,970,294 to 8,980,294 | 27 Oct 2026 16:49 to 20:31 | 1.331 s |
| Testnet | 8,880,294 to 8,980,294 | 26 Oct 2026 10:59 to 27 Oct 2026 20:31 | 1.208 s |

An average hides gaps. A 100,000-block average does not show whether the chain stopped for a period inside the window. Block time is set by the validators' node configuration (Documented: PRISM Consensus Engine page) and the testnet block time varies (Documented: EVM Development page). Express any time-based limit in a contract or an operating procedure in blocks, and convert to wall-clock time only with a block time measured close to when it matters.

### 4.2 What is not measured

| Metric | Status |
| --- | --- |
| Network availability (share of time blocks were produced within a bound) | Not measured |
| Number and duration of past block production halts outside planned upgrades | Not measured |
| Downtime during planned upgrades (time from halt height to the next block) | Not measured |
| Public endpoint availability (REST, RPC, EVM JSON-RPC) | Not measured |
| Recovery time objective (RTO) for the network or the public endpoints | Not published |
| Recovery point objective (RPO) | Not published. For committed blocks, finality means committed state is not rolled back by the consensus protocol; this is a property of the protocol, not an operational RPO. |
| Public endpoint rate limits | Not published as a number. The node bounds its own JSON-RPC server (section 10.3). |
| Status page | Not published |

An issuer that needs an availability figure for its own risk assessment should measure it independently, for example by recording the latest block height and time from two or more independent nodes at a fixed interval.

### 4.3 Planned halts

Coordinated upgrades halt every node at a named height and restart it on the new release (section 6). These are planned and announced through governance. The time the network is stopped at each upgrade is not measured.

## 5. Governance

### 5.1 Who can change the rules

Parameters, software upgrades, circuit-breaker settings and module-specific administrative actions are executed by the governance module account on the result of an on-chain vote by bonded stake. A proposal is a list of messages that the governance module executes if it passes (Documented: Governance page). There is no other upgrade key: a chain upgrade happens only through a passed `MsgSoftwareUpgrade` proposal.

### 5.2 Governance parameters on 27 October 2026

| Parameter | Mainnet | Testnet | Source |
| --- | --- | --- | --- |
| Minimum deposit | 10,000,000 uqor (10 QOR) | same | Verified: `/cosmos/gov/v1/params/deposit` |
| Maximum deposit period | 172,800 s (48 hours) | same | Verified: same |
| Voting period | 172,800 s (48 hours) | 14,400 s (4 hours) | Verified: `/cosmos/gov/v1/params/voting` |
| Quorum | 33.4 % of bonded stake | same | Verified: `/cosmos/gov/v1/params/tallying` |
| Pass threshold | 50 % of non-abstain votes | same | Verified: same |
| Veto threshold | 33.4 % | same | Verified: same |
| Expedited voting period | 86,400 s (24 hours) | 3,600 s (1 hour) | Verified: `/cosmos/gov/v1/params/voting` |
| Expedited pass threshold | 66.7 % | same | Verified: same |
| Expedited minimum deposit | 50,000,000 uqor (50 QOR) | same | Verified: same |
| Deposit burned on veto | yes | yes | Verified: `burn_vote_veto` |

### 5.3 How governance has been used

On 27 October 2026 the mainnet had 14 governance proposals, numbered 1 to 14 (Verified: `/cosmos/gov/v1/proposals`). All 14 were submitted as expedited proposals, so each ran a 24-hour voting period with a two-thirds pass threshold. Thirteen had passed. The documentation states that proposals 7 to 13 passed (Documented: Version History page, "Mainnet governance timeline").

An issuer should plan for the fact that a rule change affecting the EVM lane can be proposed and applied within about a day of submission, plus the time to the named upgrade height.

### 5.4 Circuit breaker

The chain runs the circuit module, which lets governance disable individual message types without a software upgrade. On 27 October 2026 the mainnet disabled list held 16 message types (Verified: `/cosmos/circuit/v1/disable_list`), among them vesting-account creation, CosmWasm code upload and instantiation, AMM pool pause and resume, cross-VM calls, post-quantum algorithm deprecation and disabling, and the control messages of the consensus parameter agent. The testnet list held one, CosmWasm code upload. None of the disabled message types is an EVM transaction; the EVM lane is not switched by this list.

### 5.5 Parameter agent

The chain contains a parameter-optimisation agent (`x/rlconsensus`, documented as PRISM). On mainnet it has no policy loaded, has taken no step and applies no change, and the messages that would load a policy or change its mode are on the circuit-breaker list (Documented: PRISM Consensus Engine page; Verified: disabled list). On the testnet it runs in shadow mode, recording proposed actions without applying them (Documented: same page). Any future change to this would itself need governance.

### 5.6 Permissionless and governed surfaces relevant to issuers

| Surface | Mainnet | Testnet | Source |
| --- | --- | --- | --- |
| EVM contract creation | permissionless | permissionless | Verified: EVM params `access_control.create` |
| EVM contract calls | permissionless | permissionless | Verified: EVM params `access_control.call` |
| Registering an ERC-20 as a native token pair | governance only | governance only | Verified: `/cosmos/evm/erc20/v1/params` (`permissionless_registration: false`) |
| CosmWasm code upload | nobody (and on the disabled list) | nobody (governance stores reviewed code) | Verified: `/cosmwasm/wasm/v1/codes/params`, disabled list |
| CosmWasm instantiation | nobody (and on the disabled list) | everybody | Verified: same |
| Smart accounts (`x/abstractaccount`) | disabled | enabled | Verified: `/qorechain/abstractaccount/v1/config` |

On mainnet, regulated-asset logic therefore runs as EVM contracts. That is the model this repository's adapters follow.

## 6. Upgrade authority

### 6.1 Mechanism

Consensus-affecting changes arrive as coordinated governance upgrades. A passed proposal names a plan and a block height; at that height every node running the old release halts, and nodes restart on the release that carries the upgrade handler (Documented: Running a Node page, "Upgrades"). Node-local releases that do not change consensus can be rolled out node by node without a height; the release manifest says which kind a release is (`upgradeType` `height` or `rolling`).

The release archive, its SHA-256 checksum, the genesis file and a state-sync trust point are published in the manifest at `download.qore.host`; the proposal text also publishes the binary's checksum (Documented: Running a Node page). The documentation states that a binary built from the public source repository refuses to start on either public network from v3.2.3 on, and that node operators must use the release archive (Documented: Running a Node page). Reproducible builds of the release archive from public source are not published.

### 6.2 Applied upgrades

Each height below was read from `/cosmos/upgrade/v1beta1/applied_plan/{name}` on 27 October 2026; a value of `0` means the plan was not applied on that network. Proposal numbers are from `/cosmos/gov/v1/proposals`.

| Plan | Mainnet height (proposal) | Testnet height (proposal) |
| --- | --- | --- |
| v3.1.94 | 2,122,074 (4) | not applied |
| v3.1.98 | not applied under this name | 5,746,000 (5) |
| v3.2.0 | 2,981,742 (6) | 5,920,000 (6) |
| v3.2.1 | node-local release, no height | node-local release, no height |
| v3.2.2 | 3,556,788 (7) | 6,905,034 (7) |
| v3.2.3 | 3,662,051 (11) | 8,003,746 (11) |
| v3.2.4 | 3,742,566 (13) | 8,337,253 (13) |
| v3.2.5 | not applied on 27 October 2026 (governance proposal in progress) | 8,890,800 (15) |
| v3.2.6 | not applied | 8,970,638 (28) |

Releases before v3.1.94 were not checked for this document.

### 6.3 Pending upgrade

On 27 October 2026 `/cosmos/upgrade/v1beta1/current_plan` returned `null` on both networks. A governance proposal for v3.2.5 on mainnet is in progress; check the explorer (<https://explore.qore.network>) or `/cosmos/gov/v1/proposals` for its status. This document does not state its outcome. Until mainnet applies a release, anything that release adds is testnet only.

### 6.4 Practice for issuers

- Testnet receives each release before mainnet. Run the asset's contracts and monitoring against the testnet after each testnet upgrade.
- Watch `current_plan` and new `MsgSoftwareUpgrade` proposals. A plan height is a planned halt (section 4.3); avoid scheduling settlement deadlines, corporate actions or redemption windows across it.
- Record the node release in force with every compliance-relevant snapshot (applied plan names and heights), so that the rules in force at a given block can be reconstructed.

## 7. EVM engine behaviour relevant to issuers

The QoreChain EVM Engine runs Solidity contracts with ordinary tooling. It differs from Ethereum mainnet in ways that matter for regulated-asset contracts. Unless marked, each item applies to both networks and was confirmed on 27 October 2026 by live checks.

### 7.1 Fork level and transaction types

| Item | Behaviour | Source |
| --- | --- | --- |
| Fork schedule | All forks through London at block 0; Shanghai, Cancun and Prague active from time 0; Osaka not active | Verified: `/cosmos/evm/vm/v1/config` |
| Extra EIPs | none (`extra_eips: []`) | Verified: EVM params |
| Accepted transaction types | 0, 1, 2 and 4. Type 3 (blob) transactions are refused | Live check |
| Blob fields | `blobGasUsed` and `excessBlobGas` are always 0; `eth_blobBaseFee` does not exist | Live check |
| Unprotected (pre-EIP-155) transactions | refused on mainnet since v3.2.2 | Documented: EVM Development page |
| `PREVRANDAO` | returns a constant (all bits set), not a random value; the header `mixHash` shows zero and does not match the opcode | Live check |
| `eth_getProof` | returns IAVL proofs of the native state store, not Merkle-Patricia proofs | Live check |
| `web3_clientVersion` | `Version dev ()...`; do not use it to identify a release | Verified |

Consequences: never use `PREVRANDAO` or `block.prevrandao` for randomness (for example, lotteries for allocation or sampling for audits); do not depend on blob data; do not verify state proofs from this chain with Ethereum Merkle-Patricia proof libraries.

### 7.2 Every EVM transaction needs a post-quantum key and a window

Since v3.2.0 (mainnet height 2,981,742, testnet height 5,920,000), the EVM lane admits a transaction only from an account that has a registered ML-DSA-87 key and an open EVM authorisation window with room for it (Documented: EVM Development page). The window is opened with `MsgOpenEVMWindow`, an ordinary native-lane transaction carrying the account's hybrid signature, and is bounded by:

| Bound | Range | Meaning |
| --- | --- | --- |
| `blocks` | 1 to 17,280 | Lifetime in blocks from the opening block |
| `max_txs` | 1 to 1,000 | Number of EVM transactions admitted |
| `max_value` | above 0, in uqor | Total native QOR outflow admitted: transferred value plus the maximum fee each transaction could pay |
| `native_only` (optional) | flag | Admits plain QOR transfers only |
| `allowed_targets` (optional) | up to 16 addresses | Admits only transactions to those addresses; contract creation refused |

Source: EVM Development page, "EVM authorisation window"; the maximum target count is from the QoreChain SDK constants.

There are no per-account exceptions. `eth_call` and gas estimation need no window. Opening a window advances the account's sequence, which is also its EVM nonce, so the nonce must be read after the window is open. Value bounds count native QOR only: a token transfer or approval carries value zero and is bounded only by `max_txs`, the fee and the scope (Documented: same page). Section 11.4 turns this into key-management practice.

Consequences for issuer operations: every operational account that sends EVM transactions (deployer, issuer, agent, transfer-agent bot, oracle, multisig executor) needs its own registered ML-DSA-87 key and a window. A holder who only receives tokens needs neither. A holder who transfers tokens needs both.

### 7.3 EIP-7702 delegation needs post-quantum consent

Type-4 transactions are accepted with consent rules. At most 8 authorisations per transaction; a duplicate authority in one transaction is refused. Every authorisation that would take effect needs the authority's own registered post-quantum key and a live single-use consent recorded with the native-lane message `MsgAuthorizeEVMDelegation` for exactly that delegate, valid for 1 to 17,280 blocks. The sponsor's window is not consent for the authorities. `MsgClearEVMDelegation` removes a delegation from the native lane (Documented: EVM Development page, "EIP-7702 delegations").

Consequence: a token contract that relies on `msg.sender` code checks or on EOA-only assumptions should not assume that an EOA has no code; the consent requirement narrows, but does not remove, delegated accounts.

### 7.4 Precompiles

| Address | Precompile | Mainnet | Testnet | Source |
| --- | --- | --- | --- | --- |
| `0x0A01` | `pqcVerify` (ML-DSA signature check) | not active | active | Verified: `active_static_precompiles` |
| `0x0A02` | `pqcKeyStatus(address)` | not active | active | Verified: same; `eth_call` returns `0x` on mainnet |
| `0x0C01` | `rlConsensusParams` | not active | active | Verified: same |

`pqcKeyStatus(address)` returns `(bool registered, uint8 algorithmId, bytes pubkey, bool possessionProven)` at a flat 2,500 gas. The fourth value was added in v3.2.4 and comes after the dynamic `pubkey`, so callers that decode three values still work (Documented: EVM Precompiles page). A contract that trusts the returned key must also require `possessionProven == true`. The testnet precompiles were activated by testnet governance proposal 21 on 27 October 2026 (Verified: proposals list). Activation on mainnet requires a governance decision; no date is set.

Consequence for this repository: `QoreChainHybridHolderGuard`, which requires a holder to have a registered and possession-proven post-quantum key, works on the testnet only. On mainnet the call returns empty data, and a contract that does not handle that case reverts or, worse, decodes defaults. The guard in this repository fails closed when the precompile returns no data.

### 7.5 Fees

| Item | Value | Source |
| --- | --- | --- |
| `eth_gasPrice` | 112.5 gwei (`0x1a3185c500`) on both networks | Verified |
| Base fee | 0.1 uqor per gas (100 gwei), at the floor | Verified: `/cosmos/evm/feemarket/v1/params` |
| Minimum gas price | 0.1 uqor per gas | Verified: same |
| Base fee change denominator | 8 | Verified: same |
| Elasticity multiplier | 2 | Verified: same |
| Minimum gas multiplier | 0.5 | Verified: same |

### 7.6 JSON-RPC surface

Public namespaces are `eth`, `net`, `web3` and `txpool`. `eth_feeHistory`, `eth_createAccessList`, `eth_getBlockReceipts` and `txpool_status` work. `txpool_content` and `txpool_inspect` are refused on the public endpoints. `debug_*`, `personal_*`, `admin_*` and `miner_*` are not served (Documented: JSON-RPC `eth_` namespace page; live check). Tracing a failed issuer transaction therefore needs a node you run yourself with the relevant namespaces enabled.

## 8. Transaction ordering and MEV

### 8.1 What is verifiable

- **Fee market.** The EVM fee market runs with a base fee at the 100 gwei floor and a priority fee on top (section 7.5). Verified.
- **Encrypted mempool.** The `x/fairblock` design for threshold-encrypted transactions is disabled on both networks (`enabled = false`); the node serves no FairBlock transaction or query service (Documented: MEV Protection (FairBlock) page).
- **Block-space lanes.** Five lane definitions exist as configuration only; they are not enforced by the live mempool or proposal handler (Documented: same page; Key Features page).
- **Mempool visibility.** `txpool_content` and `txpool_inspect` are refused on the public endpoints. This hides pending transactions from users of the public endpoint only; any node operator, including every validator, can see its own mempool. Documented: JSON-RPC `eth_` namespace page.
- **AMM swaps.** The native AMM applies a price-impact cap and a block-open price check to swaps that set no slippage bound (Documented: MEV Protection page, linking to the AMM page). This does not apply to EVM contracts.

### 8.2 What is not published

| Item | Status |
| --- | --- |
| A policy binding validators to a transaction ordering rule (for example first-in-first-out or fee priority) | Not published |
| A commitment that validators do not reorder, insert or censor transactions for profit | Not published |
| Measurements of front-running, sandwiching or back-running on the EVM lane | Not measured |
| Private transaction submission (a relay that does not expose a transaction before inclusion) | Not published |

### 8.3 Practice for issuers

- Treat any pending transaction as visible to the block proposer.
- Do not design primary issuance, redemption or settlement so that the price is fixed by the first transaction to arrive. Use pre-agreed prices, commit and reveal, or allocation after a closed subscription window.
- For delivery against payment, prefer contracts that settle both legs atomically in one transaction, so that ordering cannot separate them.
- Use scoped EVM windows (`allowed_targets`) on operational accounts so that a compromised classical key cannot be used to submit unrelated transactions (section 11.4).

## 9. Native asset modules: status

The modules this repository proposes (`x/asset`, `x/identity`, `x/compliance`, `x/settlement`, `x/attest`) do not exist on either network. No release in the upgrade history of section 6 contains them and no upgrade that would add them is scheduled. Freezing an address, pausing a token, forced transfers, identity registries and delivery-versus-payment are available today only as EVM contract logic, which is what the adapters in this repository provide. A native implementation would require a chain upgrade approved by governance, following the process in section 6.

## 10. Observability

### 10.1 Sources of truth

| Source | Use | Notes |
| --- | --- | --- |
| EVM JSON-RPC (`eth_getLogs`, `eth_getTransactionReceipt`, `eth_getBlockByNumber`) | Token events, receipts, holder history | Logs are the primary audit trail for EVM adapters |
| Consensus REST | Governance, upgrade plans, PQC key records, EVM windows, validator set | No public gRPC |
| Consensus RPC (HTTP and WebSocket) | Block headers, transaction results, event subscription | WebSocket at `wss://rpc.qore.host/websocket` (Documented: Connecting to Mainnet page) |
| Block explorer `explore.qore.network` | Human inspection | Not a source of record |
| Your own node | Independent confirmation | Recommended for any regulated programme |

### 10.2 Events and records to index

For the EVM adapters in this repository, index at least: ERC-20 `Transfer` and `Approval`; the ERC-3643 events for identity registration, address freezing, partial token freezing, pausing, recovery and compliance module changes; the CMTAT events for enforcement, freezing, pausing, rule engine changes, mint and burn; the `QoreChainHybridHolderGuard` `ExemptionSet` events (the guard itself is a view: its decisions show up as refused transfers); and vault `Deposit`, `Withdraw`, `DepositRequest` and `RedeemRequest` events.

From the native lane, index the post-quantum account record (`GET /qorechain/pqc/v1/account/{address}`, including `possession_proven`), the window state (`GET /qorechain/pqc/v1/evm_window/{address}`), the `pqc_evm_window_opened` event, EIP-7702 consent (`GET /qorechain/pqc/v1/evm_delegation_consent/{address}`), governance proposals and the upgrade plan (Documented: REST and gRPC Endpoints page; EVM Development page).

### 10.3 Node-side limits

From v3.2.4 a node bounds its JSON-RPC server: request bodies over 256 KiB are refused (HTTP 413), at most 256 requests are served at once (HTTP 503 beyond that), and a log filter with more than 4 topic positions, 1,000 alternatives in one position or 1,000 addresses is refused (Documented: EVM Development page). An indexer should page `eth_getLogs` by block range and by contract address.

### 10.4 What to monitor

| Signal | Why | How |
| --- | --- | --- |
| Latest block height and time | Detect a halt or slowdown | RPC `/status` or REST `blocks/latest`, from two independent sources |
| `current_plan` and new upgrade proposals | Planned halts and rule changes | REST `/cosmos/upgrade/v1beta1/current_plan`, `/cosmos/gov/v1/proposals` |
| Circuit-breaker list | Message types switched off | REST `/cosmos/circuit/v1/disable_list` |
| EVM window state of every operational account | Avoid failed operations; detect unexpected consumption | REST `/qorechain/pqc/v1/evm_window/{address}` |
| Post-quantum record of every operational account | Detect a key rotation you did not perform | REST `/qorechain/pqc/v1/account/{address}` |
| Bonded validator count and stake concentration | Liveness risk | REST validators endpoint |
| Token contract events | Unauthorised mint, freeze, forced transfer or role change | `eth_getLogs` |
| `active_static_precompiles` | Know when the guard can work on a network | REST `/cosmos/evm/vm/v1/params` |

## 11. Key management

### 11.1 Account model

Native-lane transactions carry a hybrid signature: a classical secp256k1 signature plus an ML-DSA-87 (FIPS 204) signature from the account's registered post-quantum key. Hybrid signatures are required by default (`hybrid_signature_mode = required`, `allow_classical_fallback = false`; Documented: Post-Quantum Signing page; Verified on the testnet via `/qorechain/pqc/v1/params`). An account without a post-quantum key may sign classically only to register its key (or to unjail). An account with a registered key has no classical path, so key maintenance is hybrid too.

EVM transactions are signed with the secp256k1 key alone, with ordinary wallets and tools. The post-quantum key authorises the EVM window ahead of them (section 7.2). A stolen classical key alone cannot open a window, so it can move only what an already-open window admits (Documented: EVM Development page).

### 11.2 Registration and proof of possession

The post-quantum key is registered with `MsgRegisterPQCKeyV2`. A registration may carry a proof of possession: the new key signs `qorechain-pqc-pop-v1|<chain-id>|<algorithm id>|<address>|<public key hex>`. The chain verifies a proof when it is present and refuses the registration if it does not verify; a registration without a proof is still accepted. Since v3.2.4 the account record reports `possession_proven`, true when the key was registered with a verified proof or installed by a rotation (Documented: Post-Quantum Signing page).

Requirement for issuers: register every operational key with a proof of possession, and check `possession_proven` before relying on a counterparty's key. The `QoreChainHybridHolderGuard` in this repository requires it on-chain where the precompile is active.

### 11.3 Rotation and recovery

`MsgRotatePQCKey` rotates an account's ML-DSA-87 key within the same algorithm. Both the old and the new key sign the rotation, and the transaction itself is hybrid-signed. Rotation is a root-key operation that cannot be delegated (Documented: Post-Quantum Signing page, "Key rotation"). If the classical key is suspected exposed, close the EVM window (`MsgCloseEVMWindow`); whatever it still admitted is refused from the next block (Documented: EVM Development page).

### 11.4 Recommendations for issuer and agent keys

| Role | Recommendation |
| --- | --- |
| Contract owner or admin (upgrade, role grants) | Hold in an EVM multisig contract, not in a single EOA. The multisig's signers each need a post-quantum key and a window when they execute. |
| Issuer (mint, burn) | Separate account. Open short windows with `allowed_targets` set to the token contract only, and `max_txs` sized to the operation. |
| Agent (freeze, forced transfer, recovery) | Separate account from the issuer. Same scoped windows. |
| Compliance or identity operator (whitelist, identity registry) | Separate account, windows scoped to the registry and compliance contracts. |
| Automated bots | Separate account per bot, smallest `max_value` that covers fees, windows renewed on a schedule rather than left open for the maximum 17,280 blocks. |
| Treasury of the issuing entity | Not on an operational account. |

For each account, back up the post-quantum key as carefully as the mnemonic; anyone who reads the key file can co-sign together with the classical key (Documented: Post-Quantum Signing page).

### 11.5 Multisig

- **EVM lane.** Multisig wallets are ordinary contracts deployed with standard tooling. No canonical multisig deployment on QoreChain is published; deploy and verify your own. Each signer that submits an EVM transaction needs a registered key and a window.
- **Native-lane smart accounts.** `x/abstractaccount` supports a multisig account type but is disabled on mainnet (Verified: `/qorechain/abstractaccount/v1/config`). Testnet only.
- **CosmWasm multisig.** A reviewed `cw3-fixed-multisig` contract is stored on the testnet only; mainnet has no stored code (Documented: CosmWasm Development page).

### 11.6 Hardware security modules and hardware wallets

| Capability | Status | Source |
| --- | --- | --- |
| secp256k1 signing in an HSM or hardware wallet | Standard; supported by common HSMs and hardware wallets | General industry fact; not specific to QoreChain |
| ML-DSA-87 signing in an HSM | Possible with an HSM that implements FIPS 204 ML-DSA-87 and a custom signer that assembles QoreChain's hybrid extension; the documentation points HSM integrators to the `qorechain-pqc` libraries | Documented: Exchange Integration page |
| A list of HSM models validated with QoreChain | Not published | |
| Hardware wallet signing of the ML-DSA-87 layer | Not published. QoreSign does not sign on hardware wallets | Documented: QoreSign overview |
| Threshold or MPC signing of the ML-DSA-87 layer | Not published | Documented: QoreSign overview (QoreSign does not do threshold or MPC signing) |

## 12. Incident handling

### 12.1 Reporting channel

Security vulnerabilities are reported privately to **security@qore.network**. The public security page at <https://www.qorechain.io/security> describes a standing bug bounty with severity classes (Critical, High, Medium, Low, Insight), reward tiers, triage and payment deadlines, and a public season with a published scope (Verified: page fetched on 27 October 2026).

### 12.2 Documented precedents

| Date | Event | Source |
| --- | --- | --- |
| 22 August 2026 (v3.1.89) | Following an incident, the SVM execution lane was disabled network-wide for transaction submission by a compile-time switch, not a governance parameter; it stays off until an external audit clears it | Documented: SVM Development page |
| 25 August 2026 | Mainnet expedited proposal 3 tripped the circuit breaker for a set of administrative message types; proposal 4 applied v3.1.94 at height 2,122,074 | Verified: `/cosmos/gov/v1/proposals` |
| 4 September 2026 | Mainnet expedited proposal 5 restricted CosmWasm code upload and instantiation | Verified: same |

These show the instruments available in an incident: an expedited proposal (24-hour vote on mainnet), the circuit breaker (disables message types without a release), and a coordinated release at a named height.

### 12.3 What is not published

| Item | Status |
| --- | --- |
| Incident communication timeline (time from detection to public notice) | Not published |
| Post-incident report policy | Not published |
| A status page for the networks or endpoints | Not published |
| An on-call or escalation contact for issuers other than the security address | Not published |
| Emergency powers outside governance | None documented. Every chain-level change in section 6 went through a governance proposal. |

### 12.4 Practice for issuers

Write the asset's own incident plan around the instruments the contracts give the issuer: pause, address freeze, partial freeze, forced transfer and recovery in ERC-3643 and CMTAT. These act within the token and do not depend on chain governance. Chain-level events (a halt, an upgrade, a circuit-breaker change) should be detected by the monitoring in section 10.4 and handled by pausing the token where the asset's terms allow it.

## 13. Summary of validator, network and EVM facts

| Fact | Mainnet | Testnet |
| --- | --- | --- |
| Bonded validators | 8 | 4 |
| Validator key type | ed25519 | ed25519 |
| Observed block interval (100,000 blocks) | 3.163 s | 1.208 s |
| Release | v3.2.4 | v3.2.6 |
| Pending plan | none set (v3.2.5 proposal in progress) | none set |
| `pqcKeyStatus` (`0x0A02`) | not active | active |
| Native asset modules | do not exist | do not exist |

## 14. Not measured or not published

| Item | Status |
| --- | --- |
| Network availability or uptime | Not measured |
| Historical unplanned halts (count and duration) | Not measured |
| Time stopped during planned upgrades | Not measured |
| Public endpoint availability | Not measured |
| Public endpoint rate limits (as numbers) | Not published |
| Recovery time objective | Not published |
| Recovery point objective (operational) | Not published |
| Service level agreement for public endpoints | Not published |
| Status page | Not published |
| Transaction ordering policy binding validators | Not published |
| MEV measurements on the EVM lane | Not measured |
| Private transaction submission | Not published |
| Incident communication timeline and post-incident reports | Not published |
| Issuer escalation contact other than security@qore.network | Not published |
| Reproducible builds of the release archive from public source | Not published |
| Validated HSM models; hardware wallet or MPC signing of the ML-DSA-87 layer | Not published |
| Canonical EVM multisig deployment | Not published |
| Mainnet activation date of `pqcVerify` and `pqcKeyStatus` | Not published (requires a governance decision) |
| Native asset, identity, compliance, settlement and attestation modules | Do not exist; not scheduled |

## 15. Sources

All queries were made on 27 October 2026 (UTC). The `/cosmos/base/.../v1beta1` block and node-info paths are the standard REST identifiers of the consensus engine.

### 15.1 Live endpoints

Mainnet REST, `https://api.qore.host`, and testnet REST, `https://api-testnet.qore.host`, each queried at:

- `/cosmos/gov/v1/params/voting`
- `/cosmos/gov/v1/params/tallying`
- `/cosmos/gov/v1/params/deposit`
- `/cosmos/gov/v1/proposals?pagination.limit=200`
- `/cosmos/upgrade/v1beta1/current_plan`
- `/cosmos/upgrade/v1beta1/applied_plan/v3.1.94` (mainnet), `/v3.1.98`, `/v3.2.0`, `/v3.2.1`, `/v3.2.2`, `/v3.2.3`, `/v3.2.4`, `/v3.2.5`, `/v3.2.6`
- `/cosmos/staking/v1beta1/params`
- `/cosmos/staking/v1beta1/validators?status=BOND_STATUS_BONDED&pagination.limit=200`
- `/cosmos/slashing/v1beta1/params`
- `/cosmos/consensus/v1/params`
- `/cosmos/circuit/v1/disable_list`
- `/cosmos/evm/feemarket/v1/params`
- `/cosmos/evm/vm/v1/params`
- `/cosmos/evm/vm/v1/config` (mainnet)
- `/cosmos/evm/erc20/v1/params`
- `/cosmwasm/wasm/v1/codes/params`
- `/qorechain/abstractaccount/v1/config`
- `/qorechain/pqc/v1/params` (returned "Not Implemented" on the mainnet public endpoint; the testnet returned the params quoted in section 11.1)
Consensus RPC: `https://rpc.qore.host/status`, `https://rpc-testnet.qore.host/status`, and `/block?height=3846987`, `/block?height=3756987` (mainnet), `/block?height=8970294`, `/block?height=8880294` (testnet) on the same hosts.

EVM JSON-RPC, `https://evm.qore.host` and `https://evm-testnet.qore.host`: `eth_chainId`, `eth_gasPrice`, `web3_clientVersion`, and `eth_call` to `0x0000000000000000000000000000000000000A02` with `pqcKeyStatus(address)`.

Release manifests: `https://download.qore.host/mainnet/latest.json`, `https://download.qore.host/testnet/latest.json`.

Web: `https://www.qorechain.io/security`, `https://explore.qore.network`.

### 15.2 Public documentation (docs.qorechain.io)

- EVM Development: <https://docs.qorechain.io/developer-guide/evm-development>
- EVM Precompiles: <https://docs.qorechain.io/developer-guide/evm-precompiles>
- Post-Quantum Signing: <https://docs.qorechain.io/developer-guide/post-quantum-signing>
- Running a Node: <https://docs.qorechain.io/developer-guide/running-a-node>
- Exchange Integration: <https://docs.qorechain.io/developer-guide/exchange-integration>
- CosmWasm Development: <https://docs.qorechain.io/developer-guide/cosmwasm-development>
- SVM Development: <https://docs.qorechain.io/developer-guide/svm-development>
- Consensus Mechanism: <https://docs.qorechain.io/architecture/consensus-mechanism>
- PRISM Consensus Engine: <https://docs.qorechain.io/architecture/prism-consensus-engine>
- MEV Protection (FairBlock): <https://docs.qorechain.io/architecture/mev-protection-fairblock>
- Key Features: <https://docs.qorechain.io/introduction/key-features>
- Version History: <https://docs.qorechain.io/appendix/version-history>
- Governance: <https://docs.qorechain.io/user-guide/governance>
- Connecting to Mainnet: <https://docs.qorechain.io/getting-started/connecting-to-mainnet>
- REST and gRPC Endpoints: <https://docs.qorechain.io/api-reference/rest-grpc-endpoints>
- JSON-RPC `eth_` namespace: <https://docs.qorechain.io/api-reference/json-rpc-eth_-namespace>
- QoreSign overview: <https://docs.qorechain.io/qoresign/overview>

Items marked "live check" in section 7 (accepted transaction types, blob fields, `PREVRANDAO`, `eth_getProof` proof format, EIP-7702 limits, JSON-RPC namespaces) were confirmed against both live networks on 27 October 2026 by the QoreChain network team; where the public documentation states the same behaviour, the page is cited.

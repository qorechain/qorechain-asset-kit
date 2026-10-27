<!-- SPDX-License-Identifier: Apache-2.0 -->

# Proposed native modules for regulated assets

> **Status: proposal.** None of the modules below exists on QoreChain, on mainnet or on the testnet, and no chain upgrade that would add them is scheduled. The interfaces in [`proto/`](../proto) are published for discussion and so that applications can be built and tested today against the in-memory `MockChain` of the clients. Every client call that would reach the chain throws `ChainUpgradeRequired`. What works on QoreChain today is the set of EVM contracts in [`contracts/`](../contracts), described in the [README](../README.md).

This document describes the intended behaviour of five modules:

| Module | Purpose |
|---|---|
| `x/asset` | issuance, roles, holder controls (authorization, freeze, pause), clawback and forced transfer |
| `x/identity` | identity records and claims from trusted claim issuers, with no personal data on chain |
| `x/compliance` | a governance-maintained registry of versioned compliance modules, bound per asset by the issuer |
| `x/settlement` | delivery versus payment (DvP) instructions with bilateral affirmation, all legs or none |
| `x/attest` | statements about an asset (NAV, reserves, custody, audit) with a validity period and staleness |

The `MockChain` in each client language (TypeScript, Python, Go, Java) implements the rules in this document. Where this text and the mock disagree, this text is the intended behaviour and the mock has a bug.

## 1. Conventions

- **Signers.** Every message names its signer in a field (`issuer`, `agent`, `from`, `party`, `authority`, ...). On chain the signer would be authenticated by the transaction signature. The mock trusts the field.
- **Amounts** are non-negative integer strings in the smallest unit (no decimals on the wire). A transfer, mint, burn, clawback or leg amount must be greater than zero.
- **Denoms.** An asset with id `bond-2030` would have the bank denom `asset/bond-2030`. Settlement legs may also use any bank denom (for example `uqor`) as the cash leg.
- **Time** is the block time in Unix seconds; **height** is the block height.
- **Errors** are listed per module in an `ErrorCode` enum in the module's main `.proto` file. The clients report them by enum name (for example `ERROR_CODE_ADDRESS_FROZEN`) together with the module (`x/asset`).
- **Governance authority.** Messages signed by `authority` would be executed by the governance module account through a passed proposal.

## 2. Flags (`RwaFlagsV0`)

Flags are set when the asset is created.

| Flag | Effect | Can change after creation |
|---|---|---|
| `require_auth` | An address must be authorized by an agent before it can receive or send the asset. | true to false only |
| `freezable` | Agents may freeze a whole address or part of a balance, and may claw back and force transfers. An asset created without it has no agent control over balances. | true to false only |
| `pausable` | Agents may pause all transfers. | true to false only |
| `non_transferable` | Holders cannot transfer. Balances move only by mint, burn, clawback, forced transfer. | never |
| `supply_cap` | Total supply can never exceed `max_supply`. | never |
| `require_hybrid_signature` | Every signer of an asset message and every holder must have a registered ML-DSA-87 key with proof of possession, and asset messages must arrive on the native lane with a hybrid signature. | never |

Relaxing a flag is one way: an issuer can give up a control but cannot take a new control over holders who acquired the asset without it. This follows the Stellar `AUTH_IMMUTABLE` reasoning and the XRPL MPT rule that capability flags are fixed at issuance.

`require_hybrid_signature` has an EVM counterpart available today on the testnet: the `QoreChainHybridHolderGuard` contract (see [`contracts/`](../contracts)) reads the `pqcKeyStatus` precompile at `0x0A02` and requires `registered && possessionProven`. That precompile is active on the testnet only; its activation on mainnet is a governance decision that has not been taken.

## 3. Roles

| Role | Holder | Powers |
|---|---|---|
| Issuer | exactly one address per asset | update flags (relax only), grant and revoke agents and auditors, bind compliance modules, set terms, register attesters, retire the asset, transfer the issuer role in two steps (propose, accept). The issuer may also perform every agent operation. |
| Agent | zero or more addresses (bounded by `max_agents`) | mint, burn, authorize holders, freeze and partially freeze, pause, claw back, force transfer |
| Auditor | zero or more addresses | read access in off-chain tooling; submit attestations of kind `AUDIT_REPORT` (with an attester registration) |
| Identity agent | addresses in `x/identity` params | register identities, bind addresses, update the country |
| Claim issuer | registered by governance | add and revoke claims for its topics |
| Attester | registered per asset by the issuer | submit attestations of its kinds |

Role separation mirrors ERC-3643 (owner and agents) and CMTAT (role-based access control with separate minter, burner, pauser and enforcer roles). The proposal keeps three asset roles to stay small; finer roles could be added in a later version without changing the existing ones.

## 4. x/asset

### 4.1 Transfer checks

`MsgTransfer` and the dry run `Query/CanTransfer` apply these checks in this order and fail with the first error:

1. `amount` is a positive integer, else `INVALID_AMOUNT`.
2. The asset exists (`ASSET_NOT_FOUND`) and is not retired (`ASSET_RETIRED`).
3. The asset is not paused (`ASSET_PAUSED`).
4. The asset is not `non_transferable` (`NON_TRANSFERABLE`).
5. Neither sender nor receiver is frozen (`ADDRESS_FROZEN`).
6. With `require_auth`, both are authorized (`HOLDER_NOT_AUTHORIZED`).
7. With `require_hybrid_signature`, both have a registered key with proof of possession (`HYBRID_SIGNATURE_REQUIRED`).
8. The sender's balance covers the amount (`INSUFFICIENT_BALANCE`), and so does the unfrozen part of it (`INSUFFICIENT_UNFROZEN_BALANCE`).
9. Every bound compliance module allows the transfer (`COMPLIANCE_REJECTED`, with the module id and its reason).

### 4.2 Issuance and redemption

- **Mint** (agent): the receiver must not be frozen, must be authorized under `require_auth`, must hold a hybrid key under `require_hybrid_signature`, the cap must hold under `supply_cap` (`SUPPLY_CAP_EXCEEDED`), and the compliance modules see the mint as a transfer from the empty address. Mint is allowed while the asset is paused (pause stops holder transfers, not the agent's issuance) and refused once retired.
- **Burn** (agent): redemption from a holder. Refused if the holder is frozen as a whole (unfreeze first, or use clawback); limited to the unfrozen balance. Allowed on a retired asset, so that holders can be redeemed after retirement.

### 4.3 Freeze, clawback, forced transfer

- **Freeze** (agent, requires `freezable`): a frozen address can neither send nor receive.
- **Partial freeze** (agent, requires `freezable`): sets the frozen amount of a balance (absolute value, at most the balance). Only the part above it can move. This is the ERC-3643 `freezePartialTokens` model.
- **Pause** (agent): pausing requires `pausable`; unpausing is always allowed.
- **Clawback** (agent, requires `freezable`): moves units from a holder to the issuer, ignoring freeze, pause and authorization. If the remaining balance falls below the frozen amount, the frozen amount is reduced to the remaining balance. Use: regulatory seizure, reversal of an erroneous issuance.
- **Forced transfer** (agent, requires `freezable`): moves units between two holders, ignoring the sender's freeze and the pause. The receiver must not be frozen, must be authorized under `require_auth`, must hold a hybrid key under `require_hybrid_signature`, and must pass the compliance modules. Uses: recovery to a new wallet after a lost key, court-ordered transfer, succession. This corresponds to ERC-3643 `forcedTransfer` and CMTAT `forcedTransfer`.

Each operation records a free-text `reason` in its event so that the audit log explains why an agent moved a holder's balance.

### 4.4 Lifecycle

`ACTIVE` and `PAUSED` alternate through `MsgPause`. `MsgRetire` (issuer) moves the asset to `RETIRED`: no further mint or transfer; burns remain possible.

The issuer role moves in two steps (`MsgProposeIssuer`, then `MsgAcceptIssuer` signed by the new issuer), so a typo cannot hand the asset to an address nobody controls.

## 5. x/identity

An identity is an id, one or more bound addresses, an ISO 3166-1 numeric country code and a list of claims. A claim has a topic (a number registered per network), the claim issuer, the hash of the off-chain evidence and an expiry. No name, document or date of birth is stored on chain; only the evidence hash.

An address is **verified** for a list of topics if it is bound to an identity that holds, for every topic, a claim that is not revoked, not expired, and issued by an address that governance currently trusts for that topic. Removing a claim issuer therefore invalidates its claims at once, without touching every identity.

Several addresses can be bound to one identity, which supports wallet recovery: the identity agent binds the new address, an asset agent force-transfers the balance, and the old address is unbound.

This is the ONCHAINID and Identity Registry model of ERC-3643, reduced to what a native module needs.

## 6. x/compliance

### 6.1 Registry

The registry holds versioned compliance modules. A module version is either **native** (compiled into the chain, added by a software upgrade) or **wasm** (a CosmWasm contract with a fixed query interface, registered by governance). Each version has a status:

| Status | Effect |
|---|---|
| `ACTIVE` | can be bound |
| `DEPRECATED` | existing bindings keep working; new bindings are refused |
| `DISABLED` | every transfer of an asset bound to it fails closed until the issuer migrates the binding |

A new version never replaces an old one silently. Bindings are pinned to a version; the issuer moves with `MsgMigrateBinding`, and the module's per-asset state is carried over. Governance can disable a version found to be unsafe, which stops transfers (fail closed) rather than letting them through unchecked.

### 6.2 Bindings and checks

The issuer binds module versions to an asset with JSON parameters validated against the module's schema. Bound modules are evaluated in binding order; the first refusal wins and is returned with the module id and a reason. Mints are checked as transfers from the empty address.

The initial native modules proposed, all implemented by the `MockChain`:

| Module id | Parameters | Rule (receiver = `to`) |
|---|---|---|
| `identity-verified` | `{"topics":[1]}` | the receiver is verified for every topic |
| `country-allowlist` | `{"countries":[756,438]}` | the receiver's identity country is in the list (no identity: refused) |
| `country-blocklist` | `{"countries":[408]}` | the receiver's identity country is not in the list (no identity: allowed) |
| `max-holders` | `{"max":100}` | a receiver with a zero balance would not raise the number of holders above `max` |
| `max-balance` | `{"max":"1000000"}` | the receiver's balance after the transfer is at most `max` |
| `attestation-fresh` | `{"kind":"ATTESTATION_KIND_NAV"}` | the latest attestation of that kind for the asset is fresh |

The model follows ERC-3643 modular compliance (`ModularCompliance` with `canTransfer` and post-transfer hooks) and the CMTAT RuleEngine (an external contract with ordered rules and ERC-1404 restriction codes).

## 7. x/settlement

### 7.1 Instructions and affirmation

An instruction contains one or more legs (`from`, `to`, `denom`, `amount`), a settlement type, an optional venue and a deadline. The **parties** are all distinct `from` and `to` addresses of its legs. The creator, if a party, is affirmed at creation; every other party must sign `MsgAffirm`. Affirming does not lock funds. A party may withdraw its affirmation until the instruction executes.

| Settlement type | Execution |
|---|---|
| `ON_AFFIRMATION` (default) | in the same transaction as the last affirmation |
| `MANUAL` | by `MsgExecuteInstruction` from any party or the venue operator |
| `ON_BLOCK` | in the end blocker at `settle_height`; if not fully affirmed by then, the instruction fails |

### 7.2 All or nothing

Execution applies every leg with the full rules of its denom: an asset leg is checked exactly like a `MsgTransfer` signed by the leg's `from` (freeze, pause, authorization, hybrid key, compliance); a bank leg is a bank send. If any leg fails, no balance moves, the instruction becomes `FAILED` with the index and reason of the failing leg, and the transaction that attempted it still succeeds so that the failure is recorded. A `FAILED` instruction can be executed again before its deadline once the cause is fixed (for example after a top-up), or cancelled.

### 7.3 Deadline, cancellation, venues

An instruction cannot execute after its deadline; the end blocker marks it `EXPIRED`. The creator, any party or the venue operator can cancel an instruction that has not executed. A venue is an operator (for example a DLT trading facility) that can restrict who creates instructions in it.

The model follows Polymesh settlement (instructions, legs, venues, affirmations, settle on affirmation, manual or at a block).

## 8. x/attest

An issuer registers attesters per asset and per kind (`NAV`, `RESERVES`, `CUSTODY`, `AUDIT_REPORT`, `OTHER`). An attestation carries a value, a unit, the hash and URI of the underlying report, the observation time and a validity period. `AUDIT_REPORT` attestations also require the attester to hold the auditor role on the asset.

Rules on submission: the observation time cannot be in the future, nor older than `max_observation_lag_seconds`; the validity cannot exceed `max_validity_seconds`; an attestation older than the latest accepted one of the same kind is refused. The attester or the issuer can revoke an attestation.

**Staleness.** The latest unrevoked attestation of a kind is `FRESH` while the block time is before `observed_at + valid_for_seconds`, `STALE` after that, and `MISSING` if there is none. Wallets display the freshness next to the value; the `attestation-fresh` compliance module can stop transfers while a statement is stale, which makes "no current NAV, no trading" enforceable on chain.

## 9. Events and audit log

Every state change emits a typed event (`events.proto` in each module) carrying the asset id, the actor, the amounts and, for clawback and forced transfer, the reason. An indexer can rebuild a complete audit log of an asset from events alone. The `MockChain` records the same events in order, with the height, so that application tests can assert on them.

## 10. What would be needed to ship

1. Review of this proposal by the QoreChain network developers and the community.
2. Implementation in the chain, with the ante handler enforcing `require_hybrid_signature` on the native lane.
3. A governance software upgrade with a named plan and height. None is scheduled.

Until then, issuers use the EVM adapters in this repository, which run on the QoreChain EVM Engine today.

## References

- Stellar, "Controlling access to assets with flags": <https://developers.stellar.org/docs/tokens/control-asset-access>
- XRP Ledger, "Multi-Purpose Tokens": <https://xrpl.org/docs/concepts/tokens/fungible-tokens/multi-purpose-tokens>, and the XLS-33 specification: <https://github.com/XRPLF/XRPL-Standards/tree/master/XLS-0033-multi-purpose-tokens>
- ERC-3643, "T-REX: Token for Regulated EXchanges": <https://eips.ethereum.org/EIPS/eip-3643>, reference implementation: <https://github.com/ERC-3643/ERC-3643>
- ONCHAINID: <https://docs.onchainid.com>, <https://github.com/onchain-id/solidity>
- CMTA Token (CMTAT): <https://cmta.ch/standards/cmta-token-cmtat>, <https://github.com/CMTA/CMTAT>, RuleEngine: <https://github.com/CMTA/RuleEngine>
- Polymesh settlement: <https://developers.polymesh.network/polymesh-docs/primitives/settlement>
- ERC-4626 (tokenized vaults): <https://eips.ethereum.org/EIPS/eip-4626>; ERC-7540 (asynchronous vaults): <https://eips.ethereum.org/EIPS/eip-7540>; ERC-7518 (partitions): <https://eips.ethereum.org/EIPS/eip-7518>; ERC-7943 (universal RWA interface): <https://eips.ethereum.org/EIPS/eip-7943>

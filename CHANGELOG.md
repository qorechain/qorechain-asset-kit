# Changelog

All notable changes are listed here. Versions follow [Semantic Versioning](https://semver.org); before 1.0, a minor version may contain breaking changes, which are always called out.

## [0.1.0] - 2026-10-27

First version. Nothing is deployed on mainnet.

### Added

- Proposed protobuf interfaces for `x/asset`, `x/identity`, `x/compliance`, `x/settlement` and `x/attest`, with the v0 flags `require_auth`, `freezable`, `pausable`, `non_transferable`, `supply_cap` and `require_hybrid_signature`. These modules do not exist on QoreChain and need a chain upgrade that is not scheduled.
- `docs/proposal.md`: semantics of the proposed modules (roles, freeze, clawback, forced transfer, versioned compliance registry, DvP with bilateral affirmation, attestations with staleness) and design references.
- Clients in TypeScript, Python, Go and Java: generated code, a `ChainClient` that throws `ChainUpgradeRequired` for every call, and a `MockChain` that implements the proposed rules in memory.
- EVM adapters (Foundry): `QoreChainHybridHolderGuard` over the `pqcKeyStatus` precompile (testnet only until it is active on mainnet; fails closed), a CMTAT v3 rule and an ERC-3643 compliance module mapped to it, ERC-4626 and ERC-7540 vaults with restricted shares, and an ERC-7518 interface sketch. CMTAT, the ERC-3643 reference implementation and ONCHAINID are used as git submodules under their own licences.
- Deployment scripts with testnet dry runs and a description of the native-lane steps (registered ML-DSA-87 key, EVM authorization window) that broadcasting needs.
- Issuer console: React app over the EVM adapters, connecting through EIP-6963.
- `docs/technology-standards.md`: reliability, governance, upgrade authority, MEV, observability, incident handling and key management, from verifiable sources.
- Legal templates (drafts, not legal advice): Swiss ledger-based security, Liechtenstein TVTG token terms, EU DLT Pilot Regime engagement outline.

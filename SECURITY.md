# Security Policy

## Reporting a vulnerability

Please **do not** report vulnerabilities through public issues, discussions or pull requests. Email:

**security@qore.network**

Include, as far as you can: a description and the impact, steps to reproduce or a proof of concept, the affected component (contracts, issuer console, a client, a proposed interface) and version, and a suggested fix.

Qualifying reports are eligible for the QoreChain bug bounty; scope and rules are published at <https://www.qorechain.io/security>.

## What to expect

- We acknowledge your report and keep you informed while we investigate.
- We coordinate disclosure with you once a fix is released.

## Scope notes

- The contracts in `contracts/` have not been audited. Do not use them to hold real value without an independent review.
- `QoreChainHybridHolderGuard` depends on the `pqcKeyStatus` precompile, which is active on the QoreChain testnet only.
- The native modules in `proto/` are a proposal and do not exist on chain; the `MockChain` implementations are development tools, not security boundaries.
- Issues in upstream dependencies (CMTAT, the ERC-3643 reference implementation, ONCHAINID, OpenZeppelin) should also be reported to their maintainers.

## Supported versions

The kit is pre-1.0. Security fixes go into the latest minor version.

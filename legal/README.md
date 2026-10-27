<!-- SPDX-License-Identifier: Apache-2.0 -->

> **Template for discussion. Not legal advice. Must be reviewed by qualified counsel in the relevant jurisdiction before any use.**

# Legal templates

This folder holds draft templates. Issuers, their counsel and infrastructure operators can use them to structure the legal side of a tokenized asset issued with the QoreChain asset kit. They are **drafts that no lawyer has reviewed yet**, published for discussion. They are not a legal opinion, and they create no client relationship with anyone. The QoreChain Association publishes this kit. It does not act as issuer, registrar, custodian, trading facility or legal adviser for any asset, and it does not claim any licence or authorisation.

Every statutory reference was checked against an official or official-mirror text on the date shown in each file. Laws change. Re-check every reference against the official publication (Fedlex, gesetze.li, EUR-Lex) before relying on it. Where a reference could not be verified, the text says **[article to be verified by counsel]**.

## Templates

| File | Jurisdiction and instrument | Status |
|---|---|---|
| [swiss-dlt-act-ledger-based-security.md](swiss-dlt-act-ledger-based-security.md) | Switzerland: ledger-based security (*Registerwertrecht*) under Art. 973d to 973i of the Code of Obligations, introduced by the DLT Act of 25 September 2020 | Draft, not reviewed by counsel |
| [liechtenstein-tvtg-token-container.md](liechtenstein-tvtg-token-container.md) | Liechtenstein: token terms under the Token and TT Service Provider Act (TVTG), the "token container" approach | Draft, not reviewed by counsel |
| [eu-dlt-pilot-regime-engagement.md](eu-dlt-pilot-regime-engagement.md) | European Union: engagement outline for an operator of a DLT market infrastructure under Regulation (EU) 2022/858 (DLT Pilot Regime) | Draft, not reviewed by counsel |

## How the templates relate to the kit

The templates describe legal arrangements. The kit provides the technical controls those arrangements rely on. Who is entitled, who may transfer, who may freeze or reallocate, and how holders verify the register are legal questions here. In the kit they are technical controls.

What exists **today**:

- **EVM adapters on the QoreChain EVM Engine.** These are tokens built on the ERC-3643 (T-REX) reference contracts or on CMTAT. The upstream contracts are used as dependencies under their own licences. The kit adds a hybrid-holder check (`QoreChainHybridHolderGuard`, used through the CMTAT rule `QoreChainHybridHolderRule` or the ERC-3643 module `QoreChainHybridHolderModule`), ERC-4626 and ERC-7540 vault wrappers and an issuer console. Issuer and agent roles, allowlists or identity registries, freeze, pause, forced transfer, and mint and burn come from these contracts.
- **QoreChain EVM requirements.** Every EVM transaction on QoreChain needs a sender with a registered ML-DSA-87 key and a live EVM authorization window. A hybrid (classical plus ML-DSA-87) transaction on the native lane opens that window. Any registration agreement, token terms or participant rules must describe this step, because it changes how a holder "exercises power of disposal" in practice.
- **Hybrid holder check, testnet only.** The `pqcKeyStatus` precompile lets a contract require that a holder has a registered ML-DSA-87 key with proven possession. It is active on the QoreChain testnet only. Activation on mainnet has not been decided, so a mainnet deployment cannot rely on it yet.

What is **not available**:

- Native asset, identity, compliance, settlement and attestation modules (`x/asset`, `x/identity`, `x/compliance`, `x/settlement`, `x/attest`). The proto files in `proto/` and the document `docs/proposal.md` are a **proposal**. These modules are not implemented on QoreChain. They would require a chain upgrade, and no such upgrade is scheduled. The templates must not describe them as available.

## Using a template

1. Pick the template for the jurisdiction where the instrument is created and governed. That may differ from where it is offered.
2. Replace every `[placeholder]`.
3. Fill in the technical mapping section with the deployed contract addresses, roles and network (testnet or mainnet).
4. Have qualified counsel in that jurisdiction review the whole document, including every statutory reference. Do the same with the supervisory authority where a licence, registration or notification may be needed.
5. Keep the reviewed version under version control next to the deployment record. The token terms should commit to it by hash, for example via the CMTAT `terms` document or an ERC-3643 compliance document reference.

## Licence

The templates in this folder are licensed under Apache-2.0, like the rest of the repository. See `NOTICE`.

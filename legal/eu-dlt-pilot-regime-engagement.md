<!-- SPDX-License-Identifier: Apache-2.0 -->

> **Template for discussion. Not legal advice. Must be reviewed by qualified counsel in the relevant jurisdiction before any use.**

# EU DLT Pilot Regime: engagement outline for an operator using QoreChain

Status: draft, not reviewed by counsel. References were checked on 27 October 2026 against the text of Regulation (EU) 2022/858 as published in the Official Journal. Counsel must also check the current consolidated version, including any amendment that follows the review under Art. 14, and the ESMA guidelines and Q&A in force.

## Contents

- Part A. Legal basis (verified references)
- Part B. Who this outline is for
- Part C. Choosing the infrastructure type (Art. 2)
- Part D. Admissible instruments and thresholds (Art. 3)
- Part E. Exemptions to request (Art. 4 to 6)
- Part F. Additional requirements (Art. 7) mapped to QoreChain
- Part G. Custody and settlement design
- Part H. Application, cooperation with the competent authority and ESMA (Art. 8 to 13)
- Part I. Indicative timeline
- Part J. Questionnaire for the operator
- Part K. Gap list
- Sources

---

## Part A. Legal basis (verified references)

**Regulation (EU) 2022/858** of the European Parliament and of the Council of 30 May 2022 on a pilot regime for market infrastructures based on distributed ledger technology, and amending Regulations (EU) No 600/2014 and (EU) No 909/2014 and Directive 2014/65/EU. OJ L 151, 2.6.2022, p. 1. It applies from 23 March 2023 (Art. 19 para. 2), with earlier dates for Art. 8(5), 9(5), 10(6), 16 and 17.

| Article | Heading | Use in this outline |
|---|---|---|
| 1 | Subject matter and scope | Scope |
| 2 | Definitions | DLT, distributed ledger, consensus mechanism, DLT network node, DLT market infrastructure, DLT MTF, DLT SS, DLT TSS, DLT financial instrument (points 1 to 7, 10, 11) |
| 3 | Limitations on the financial instruments admitted to trading or recorded on DLT market infrastructure | Instrument and aggregate thresholds |
| 4 | Requirements and exemptions regarding DLT MTFs | Exemptions for a DLT MTF |
| 5 | Requirements and exemptions regarding DLT SSs | Exemptions for a DLT SS |
| 6 | Requirements and exemptions regarding DLT TSSs | Combined trading and settlement |
| 7 | Additional requirements for DLT market infrastructures | Business plan, rules, DLT functioning, IT and cyber, safekeeping, liability, transition strategy |
| 8, 9, 10 | Specific permission to operate DLT MTF / DLT SS / DLT TSS | Application content and procedure |
| 11 | Cooperation between operators of DLT market infrastructures, competent authorities and ESMA | Notifications, six-monthly reports |
| 12, 13 | Designation and notification of competent authorities | Which authority |
| 14, 15 | Report and review; interim reports | Future of the regime |

Related acts referred to by the Regulation: Directive 2014/65/EU (MiFID II), Regulation (EU) No 600/2014 (MiFIR), Regulation (EU) No 909/2014 (CSDR), Directive 98/26/EC (Settlement Finality), Regulation (EU) No 596/2014 (Market Abuse, applies under Art. 3 para. 7). Regulation (EU) 2023/1114 (MiCA) does not apply to crypto-assets that qualify as financial instruments (MiCA Art. 2 para. 4 let. a). DLT financial instruments under the Pilot Regime are therefore outside MiCA. Digital operational resilience obligations under Regulation (EU) 2022/2554 (DORA) may apply to the operator [articles to be verified by counsel].

---

## Part B. Who this outline is for

An investment firm, market operator or CSD that is authorised under MiFID II or CSDR, or applies for that authorisation at the same time, and wants to operate a DLT market infrastructure that records DLT financial instruments on QoreChain.

The QoreChain Association publishes software. It is not an applicant, operator, CSD or investment firm, and it does not provide the services described here. Operators remain solely responsible for their application.

---

## Part C. Choosing the infrastructure type (Art. 2)

| Type | Definition (paraphrase of Art. 2) | Who may apply (Art. 8 to 10) | Fits when |
|---|---|---|---|
| **DLT MTF** (point 6) | A multilateral trading facility that only admits DLT financial instruments to trading | Investment firm or market operator authorised under MiFID II | Trading on QoreChain, with settlement done elsewhere |
| **DLT SS** (point 7) | A settlement system that settles transactions in DLT financial instruments against payment or delivery and allows initial recording or safekeeping of DLT financial instruments | CSD authorised under CSDR | Issuance (initial recording) and settlement on QoreChain without a trading venue |
| **DLT TSS** (point 10) | A DLT MTF or DLT SS that combines the services of both | Investment firm, market operator or CSD | Trading, initial recording and settlement on one QoreChain-based system |

[Operator to state its choice and the reasons.]

---

## Part D. Admissible instruments and thresholds (Art. 3)

At admission or recording, a DLT financial instrument must be one of the following (Art. 3 para. 1):

- (a) **shares** of an issuer with a market capitalisation, or tentative market capitalisation, of less than EUR 500 million;
- (b) **bonds**, other securitised debt (including depositary receipts) or money market instruments with an issue size of less than EUR 1 billion. Instruments that embed a derivative, or have a structure that makes the risk hard for the client to understand, are excluded. Corporate bonds of issuers with a market capitalisation of no more than EUR 200 million at issuance do not count towards this threshold;
- (c) **units in collective investment undertakings** covered by Art. 25(4), point (a)(iv), MiFID II, with assets under management of less than EUR 500 million.

Aggregate limits:

- **EUR 6 billion**: the aggregate market value of all DLT financial instruments on the infrastructure must not exceed this at the admission or initial recording of a new instrument (Art. 3 para. 2).
- **EUR 9 billion**: on reaching this, the operator must activate its transition strategy and notify the competent authority (Art. 3 para. 3).
- The operator calculates a monthly average aggregate market value (Art. 3 para. 4) and reports monthly (Art. 3 para. 5). The competent authority may set lower thresholds (Art. 3 para. 6).

Kit mapping: issue size, holder caps and instrument metadata can be enforced or recorded at contract level (supply cap, `tokenId` or ISIN field). The aggregate monitoring across instruments is an operator process. The kit's proposed `supply_cap` flag for a native module is only a proposal and is not available.

---

## Part E. Exemptions to request (Art. 4 to 6)

For each exemption, the operator must show that it is proportionate to, and justified by, the use of DLT, and that it is limited to the DLT market infrastructure (Art. 4 para. 4, Art. 5 para. 10). Compensatory measures may be imposed.

### E.1 DLT MTF (Art. 4)

| Exemption | Conditions (paraphrase) | Request? |
|---|---|---|
| Admit natural and legal persons to deal on own account as members (Art. 4 para. 2) | Good repute, competence including DLT knowledge, not market makers, no high-frequency algorithmic trading, no direct electronic access for others, no own-account dealing when executing client orders, informed consent | [Yes / No] |
| Transaction reporting under Art. 26 MiFIR (Art. 4 para. 3) | The DLT MTF keeps records with the relevant Art. 26(3) details. The competent authority gets direct, immediate access as a regulatory observer participant. | [Yes / No] |

### E.2 DLT SS (Art. 5)

| Exemption | Conditions (paraphrase) | Request? |
|---|---|---|
| Securities account and book-entry form: CSDR Art. 2(1) points (4), (9), (28), Art. 3, 37, 38 (Art. 5 para. 2) | Show incompatibility with the DLT used. Ensure instruments are recorded on the ledger, the number recorded equals the issue, holdings can be segregated at any time, and there are no overdrafts, debit balances or improper creation or deletion. | [Yes / No] |
| CSDR Art. 6, 7 (settlement discipline) (Art. 5 para. 3) | Clear, accurate, timely confirmation. Prevent or address settlement fails. | [Yes / No] |
| CSDR Art. 19 outsourcing of a core service (Art. 5 para. 4) | Only where Art. 19 is incompatible with the DLT used | [Yes / No] |
| Admission of natural and legal persons as participants (Art. 5 para. 5) | Good repute, competence, informed consent to the pilot | [Yes / No] |
| CSDR Art. 33 to 35 (access, participation, transparency) (Art. 5 para. 6) | Public, fair, objective participation criteria. Public prices and fees. | [Yes / No] |
| CSDR Art. 39 (settlement finality) (Art. 5 para. 7) | Settlement close to real time or intraday, and no later than T+2. Public settlement rules. Mitigation of non-designation under Directive 98/26/EC, in particular for insolvency. | [Yes / No] |
| CSDR Art. 40 (cash settlement) (Art. 5 para. 8) | Delivery versus payment. Payment in central bank money including tokenised, where practical and available. Otherwise through the CSD's account or commercial bank money including tokenised, or e-money tokens, with risk management. | [Yes / No] |
| CSDR Art. 50, 51, 53 (links and access) (Art. 5 para. 9) | Incompatibility with legacy systems, or disproportionate cost. The operator must then give other DLT SS / DLT TSS operators access. | [Yes / No] |

### E.3 DLT TSS (Art. 6)

A DLT TSS operated by an investment firm or market operator is subject to MiFID II and MiFIR MTF rules and, mutatis mutandis, to CSDR, with the listed CSDR articles excluded (Art. 6 para. 1). A CSD operating a DLT TSS is subject to CSDR and, mutatis mutandis, to MTF rules, excluding Art. 5 to 13 MiFID II (Art. 6 para. 2). The exemptions in Art. 4 para. 2 and 3 and Art. 5 para. 2 to 9 are available.

---

## Part F. Additional requirements (Art. 7) mapped to QoreChain

| Art. 7 | Requirement (paraphrase) | QoreChain / kit input | Operator to supply |
|---|---|---|---|
| Para. 1 | Business plan (critical staff, technical aspects and use of DLT). Public rules and legal terms: governing law, pre-litigation dispute settlement, insolvency protection under Directive 98/26/EC, jurisdictions. | `docs/technology-standards.md` (network facts, governance, upgrade authority) | Business plan, rulebook, legal terms |
| Para. 2 | Rules on the functioning of the DLT: access to the ledger, participation of validating nodes, conflicts of interest, risk management | Public facts on the validator set, consensus and on-chain governance (see the technology standards document). Native-lane transactions use hybrid secp256k1 plus ML-DSA-87 signatures. EVM transactions need a registered ML-DSA-87 key and an authorization window. | The operator's own position on a public, permissionless validator set it does not control. Node operation, if any. Conflict of interest policy. |
| Para. 3 | Clear information on how services differ from a non-DLT MTF or SSS, including the type of DLT used | Network description, EVM differences (for example: PREVRANDAO is a constant and not random; blob transactions are not accepted; `eth_getProof` returns IAVL proofs) | Website disclosure |
| Para. 4 | IT and cyber arrangements proportionate to the business. Continuity, transparency, availability, reliability, security, including smart contract reliability. Data integrity, security, confidentiality. Operational risk procedures for DLT and crypto-asset risks. Possible independent audit at the operator's cost. | Contract test suites in `contracts/`. Upstream audited libraries (CMTAT, ERC-3643, OpenZeppelin) used as dependencies. | Smart contract audits of the exact deployment. Key management. Monitoring. Incident plan. Availability and recovery figures: give measured values with sources or state "not measured". |
| Para. 5 | Safekeeping of client funds, collateral, DLT financial instruments and access means (including cryptographic keys). No use on own account without consent. Records. Segregation. Protection against unauthorised access, hacking, loss and similar. | Holders can self-custody. Contracts support freeze and forced transfer for recovery. | Custody model, key ceremony, segregation records |
| Para. 6 | Liability for loss up to market value, except external events beyond reasonable control. Investor protection, complaints and redress. Possible extra own funds or insurance. | n/a | Liability framework, complaints procedure, insurance |
| Para. 7 to 10 | Public transition strategy (thresholds exceeded, permission withdrawn, cessation). Best-efforts arrangements with a conventional MTF or CSD to take over within five years where applicable. | Contracts can be paused and balances exported from public state. A snapshot of holders at a block height is reproducible from chain data. | Transition strategy, takeover arrangements |

---

## Part G. Custody and settlement design

1. **Recording.** Each DLT financial instrument is one token contract (CMTAT or ERC-3643) on the QoreChain EVM Engine, with ISIN and terms recorded in contract metadata. The instruments recorded must always equal the issue (Art. 5 para. 2 let. b (ii)). Use a fixed supply or role-restricted mint with event reconciliation.
2. **Participants and eligibility.** Participant allowlist or identity registry. If the operator requires hybrid-signature participants, the `QoreChainHybridHolderGuard` can enforce a registered, possession-proven ML-DSA-87 key. This works **on testnet only** until the `pqcKeyStatus` precompile is activated on mainnet. Activation has not been decided.
3. **Delivery versus payment.** On the EVM today: an atomic swap contract that moves the DLT financial instrument and the cash leg (a tokenised payment instrument permitted under Art. 5 para. 8) in one transaction, or reverts both. Bilateral affirmation can come before execution. The native `x/settlement` module with bilateral affirmation described in `docs/proposal.md` is **a proposal only** and does not exist on QoreChain.
4. **Settlement finality.** Define the moment of finality in the rules: for example, inclusion in a committed block. Address the risks of non-designation under Directive 98/26/EC (Art. 5 para. 7 let. c).
5. **Operational prerequisite.** Every EVM transaction, including those of the operator and its agents, needs the sender's registered ML-DSA-87 key and a live EVM authorization window opened from the native lane. Build window management into the operating procedures, and decide who signs window-opening transactions for operator accounts.
6. **Recovery.** Freeze and forced transfer for lost keys or court orders, governed by the rulebook and logged on chain.

---

## Part H. Application, cooperation with the competent authority and ESMA (Art. 8 to 13)

1. **Competent authority** (Art. 12): for an investment firm, the authority of the home Member State under MiFID II. For a market operator, the authority where its registered office (or head office) is. For a CSD, the authority under CSDR Art. 2(1) point (23).
2. **Application content** (Art. 8 para. 4 for a DLT MTF, with matching content for a DLT SS in Art. 9 and a DLT TSS in Art. 10): business plan, rules and legal terms, functioning of the DLT, IT and cyber arrangements, prudential safeguards, safekeeping arrangements where applicable, investor protection and complaints, transition strategy, and the exemptions requested with justification and compensatory measures. Use the ESMA standard forms (Art. 8 para. 5).
3. **Procedure** (Art. 8 para. 6 to 9). Completeness check within 30 working days. A copy goes to ESMA, which may give a non-binding opinion within 30 calendar days. Decision within 90 working days of a complete application, which may be extended when applying at the same time for MiFID II authorisation.
4. **Permission** (Art. 8 para. 11). Valid throughout the Union for up to six years. It specifies exemptions, compensatory measures and any lower thresholds. ESMA publishes the list.
5. **Withdrawal** (Art. 8 para. 12). Grounds include a flaw in the DLT that poses risks outweighing the benefits, breach of exemption conditions, ineligible instruments, thresholds exceeded, and misleading information.
6. **Material changes** (Art. 8 para. 13, Art. 11 para. 1). Notify proposed material changes to the business plan, critical staff, rules or legal terms at least four months in advance. A material change to the DLT used may need a new permission or exemption. **A QoreChain network upgrade decided by on-chain governance may be a change to "the functioning of the distributed ledger technology used".** The operator needs a process to assess every announced network upgrade.
7. **Notifications without delay** (Art. 11 para. 1): unauthorised access, material malfunction, loss, cyber-attacks, fraud, technical or operational difficulties, and unanticipated risks.
8. **Six-monthly report** (Art. 11 para. 4): summary of notifications, number and value of instruments and transactions, difficulties in applying the law, actions taken.
9. **Review** (Art. 14, 15). ESMA's report was due by 24 March 2026, and the Commission's report within three months of receiving it. That report may extend, widen, amend, make permanent or end the regime. **Counsel must check the outcome and any amending act before filing.**

---

## Part I. Indicative timeline

All durations except the statutory ones are placeholders for the operator to set.

| Phase | Duration | Content |
|---|---|---|
| 0. Scoping | [weeks] | Infrastructure type, instruments, Member State, authority pre-meeting |
| 1. Design | [weeks] | Rulebook, legal terms, custody and DvP design, exemptions list, transition strategy |
| 2. Technical build and testnet trial | [weeks] | Contracts from this kit on the QoreChain testnet, audits, operational runbooks, window management |
| 3. Application | Statutory: 30 working days completeness check, then 90 working days decision (Art. 8 para. 6 and 9) | Filing with ESMA forms. ESMA opinion within 30 calendar days of receiving the copy. |
| 4. Launch | [weeks] | Mainnet deployment (only features active on mainnet), first instrument recorded |
| 5. Operation | Permission up to six years | Monthly threshold reports, six-monthly reports, notifications |

---

## Part J. Questionnaire for the operator

1. Which entity applies, in which Member State, under which existing or parallel authorisation (MiFID II, CSDR)?
2. DLT MTF, DLT SS or DLT TSS? Why?
3. Which instruments (Art. 3 para. 1 categories), expected issue sizes, expected aggregate value over time?
4. Which exemptions (Part E), with what compensatory measures?
5. Will the operator run QoreChain nodes, become a validator, or only use public endpoints? How will it get independent access to ledger data?
6. How will participants register ML-DSA-87 keys and open EVM authorization windows? Who supports participants who cannot?
7. Will the operator require hybrid-signature holders? Mainnet cannot enforce this in a contract until the precompile is activated. What is the interim control?
8. Cash leg: central bank money, tokenised deposits, e-money tokens, or commercial bank money through which institution?
9. Custody: self-custody by participants, custody by the operator, or a third-party custodian? How are keys segregated and recorded?
10. How will the operator follow and assess QoreChain governance proposals and network upgrades for Art. 8 para. 13 and Art. 11 purposes?
11. Smart contract audit plan for the exact deployed bytecode.
12. Incident response: who is called when the network halts, a contract defect is found, or keys are compromised?
13. Transition strategy: which conventional MTF or CSD would take over, and how are holder records exported?
14. Data protection: what personal data is on chain (ideally none), and where are identity data held?

---

## Part K. Gap list

| Gap | Owner | Status |
|---|---|---|
| Native asset, compliance, settlement, identity and attestation modules | QoreChain governance | Not implemented. Proposal only. Requires a chain upgrade that is not scheduled. |
| Hybrid holder check on mainnet (`pqcKeyStatus` precompile) | QoreChain governance | Active on testnet only. Mainnet activation not decided. |
| Measured availability, recovery time and recovery point figures for the network | Operator, with network data | Not measured. Do not state figures without a source. |
| Ethereum-style state proofs for light verification | n/a | `eth_getProof` returns IAVL proofs, so Ethereum Merkle-Patricia verifiers do not apply directly |
| Independent smart contract audit of the kit's own contracts (guard, vault wrappers) | Operator | Not done |
| Designation under Directive 98/26/EC | Member State / operator | To assess |
| ESMA forms, guidelines and the outcome of the Art. 14 review | Counsel | To check before filing |
| DORA applicability and ICT third-party risk treatment of a public blockchain | Counsel | To assess [articles to be verified by counsel] |

---

## Sources

- Regulation (EU) 2022/858, OJ L 151, 2.6.2022, p. 1, EUR-Lex: https://eur-lex.europa.eu/eli/reg/2022/858/oj (text read through the Publications Office repository: https://publications.europa.eu/resource/celex/32022R0858)
- Regulation (EU) 2023/1114 (MiCA), OJ L 150, 9.6.2023, p. 40, Art. 2 para. 4: https://eur-lex.europa.eu/eli/reg/2023/1114/oj (text read through https://publications.europa.eu/resource/celex/32023R1114)
- ESMA, DLT Pilot Regime page (forms, guidelines, list of permitted infrastructures): https://www.esma.europa.eu/esmas-activities/digital-finance-and-innovation/dlt-pilot-regime

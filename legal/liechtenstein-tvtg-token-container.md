<!-- SPDX-License-Identifier: Apache-2.0 -->

> **Template for discussion. Not legal advice. Must be reviewed by qualified counsel in the relevant jurisdiction before any use.**

# Liechtenstein token terms under the TVTG (token container approach): template

Status: draft, not reviewed by counsel. References were checked on 27 October 2026 against the consolidated text on gesetze.li (version dated 1 September 2026). Only the official publication is legally binding.

## Contents

- Part A. Legal basis (verified references)
- Part B. Token terms (the "container" document)
- Part C. Basic information (Basisinformationen) pointer
- Part D. TT service provider roles and registration pointers
- Part E. Technical mapping to the kit
- Part F. Open points for counsel
- Sources

A note on terms. The "token container model" describes the TVTG's approach. A token is a piece of information on a TT system that **can represent** a right (Art. 2 para. 1 let. c TVTG). The token is the "container" and the represented right is its content. The phrase "token container model" does not itself appear in the statutory text checked.

---

## Part A. Legal basis (verified references)

**Statute.** Gesetz vom 3. Oktober 2019 über Token und VT-Dienstleister (Token- und VT-Dienstleister-Gesetz; TVTG), LGBl. 2019 Nr. 301, LR 950.6. English working name: Token and TT Service Provider Act. The German text is authentic. Any English wording below is a working translation. "VT" (vertrauenswürdige Technologien) is rendered "TT" (trustworthy technologies).

| Article | Heading (German) | Use in this template |
|---|---|---|
| Art. 1 | Gegenstand und Zweck | Purpose and scope |
| Art. 2 para. 1 | Begriffsbestimmungen | Definitions: let. a TT, let. b TT systems, let. c token, let. d TT identifier, let. e TT key, let. f user, let. h basic information, let. i TT service provider, let. k to v service provider types, let. z^bis tokenisation marking |
| Art. 3 | Gegenstand und Geltungsbereich | When the civil law chapter applies (para. 2 let. a to c), including by express choice of the parties (let. b) |
| Art. 4 | Qualifikation von Token | Token treated as an asset located in Liechtenstein where Liechtenstein law applies |
| Art. 5 | Verfügungsgewalt und Verfügungsberechtigung | The holder of the TT key has power of disposal. Power of disposal raises a presumption of entitlement. |
| Art. 6 | Verfügungen über Token | Disposal: transfer of entitlement, or creation of a security interest or usufruct. Requirements are completion under the TT system rules, matching declarations of intent, and entitlement. Unjust enrichment applies (§§ 1431 ff. ABGB). |
| Art. 7 | Wirkungen der Verfügung | Disposal over the token disposes over the represented right. If that does not follow by law, the obligor must ensure it by suitable measures and exclude competing dispositions. Effectiveness in enforcement proceedings (para. 3). |
| Art. 8 | Legitimations- und Befreiungswirkung | The person shown by the TT system is deemed the lawful holder towards the obligor. Performance to that person discharges the obligor unless the obligor knew, or should have known with due care, otherwise. |
| Art. 9 | Erwerb kraft guten Glaubens | Good-faith acquisition for value |
| Art. 9a | Anspruch auf Schadenersatz | Liability of the tokenisation service provider and the physical validator |
| Art. 10 | Kraftloserklärung von Token | Court declaration that a token is void (cancellation) after loss of the TT key or loss of function, in non-contentious proceedings before the Landgericht. The entitled person may then assert the right without the token or ask for a new token at their own cost. |
| Art. 11 to 23 | Registration of TT service providers | Registration duty (Art. 12), conditions (Art. 13), reliability, expertise, minimum capital, internal controls (Art. 14 to 17), application and entry (Art. 18, 19), simplified registration for licensed institutions (Art. 19a to 19c), register (Art. 23) |
| Art. 25 | Sicherungsanforderungen | Segregation of tokens and TT keys held for clients in enforcement and insolvency of the TT service provider |
| Art. 30 to 38 | Basisinformationen | Duty to prepare, publish and notify basic information for token issues outside the scope of Regulation (EU) 2023/1114, with exemptions (Art. 31), form (Art. 32), content (Art. 33), supplements (Art. 34), liability (Art. 35) |

Interaction with EU law: Liechtenstein applies Regulation (EU) 2023/1114 (MiCA) through the EEA. The TVTG definitions of token issue, basic information and token issuer (Art. 2 para. 1 let. g, h, k) are now limited to tokens outside MiCA's scope. MiCA Art. 2 para. 4 let. a excludes crypto-assets that qualify as financial instruments. A token representing a security is therefore generally governed by securities law (prospectus, MiFID) for offering and trading. The TVTG governs its civil law representation and transfer. Counsel to confirm the classification of each instrument.

---

## Part B. Token terms (the "container" document)

### B.1 Parties and choice of law

1. **Obligor / Issuer.** [Issuer name], [legal form], registered office at [address], registered in the Liechtenstein commercial register under [FL number] (the "Issuer").
2. **Tokenisation service provider** (Art. 2 para. 1 let. m TVTG). [Name, registration number in the TT service provider register], responsible for the legal and technical requirements for effective representation and transfer of rights by the tokens.
3. **Token generator** (Art. 2 para. 1 let. l TVTG), if different. [Name, registration number.]
4. **Choice of law.** The parties expressly declare the civil law provisions of the TVTG (Art. 3 to 10) applicable to the tokens and to all legal transactions concerning them (Art. 3 para. 2 let. b TVTG). These token terms are governed by Liechtenstein law.

### B.2 Tokenisation marking (Art. 2 para. 1 let. z^bis TVTG)

> **Tokenised right.** The rights described in clause B.3 can be transferred only by means of the tokens described in clause B.4. Performance discharges the Issuer only if made to the person shown by the TT system as entitled to the token.

[Place this marking in the articles, the instrument and every offering document.]

### B.3 Rights represented

1. **Represented right.** [Describe: e.g. a claim for repayment of [amount] plus interest of [rate] / a membership right (share) in the Issuer / a co-ownership share in [asset] / a contractual profit participation], each token representing [fraction or unit].
2. **Rights in things** (if the token represents rights in a physical asset): the physical validator (Art. 2 para. 1 let. p TVTG) [name, registration number] ensures contractual enforcement of the represented rights in [asset]. [Asset description, location, custody arrangement.]
3. **Effect of disposal** (Art. 7 TVTG). Disposal over a token disposes over the right it represents. To the extent this does not follow by law (Art. 7 para. 2 TVTG), the Issuer undertakes to ensure, by [describe measures: e.g. a provision in the articles that recognises only the person shown by the TT system; a share register kept to match the token ledger; refusal of any transfer made outside the TT system], that (a) a disposal over a token disposes over the represented right, and (b) no competing disposal over the represented right is possible.

### B.4 TT system, TT identifier and TT key

1. **TT system.** QoreChain [mainnet `qorechain-vladi`, EVM chain ID 9801 / testnet `qorechain-diana`, EVM chain ID 9800], token contract at [0x address], standard [CMTAT version / ERC-3643 T-REX version].
2. **TT identifier** (Art. 2 para. 1 let. d TVTG). The holder's EVM address (20 bytes, `0x...`). The same account also has a native-lane address (`qor1...`).
3. **TT key** (Art. 2 para. 1 let. e TVTG). On QoreChain, disposal over a token through an EVM transaction requires **two** key materials: (a) the secp256k1 key that signs the EVM transaction, and (b) the account's registered ML-DSA-87 key, which signs the hybrid native-lane transaction that opens the EVM authorization window. Without a registered ML-DSA-87 key and a live window, the network does not accept the EVM transaction. These terms treat the combination of both keys as the TT key.
4. **Power of disposal** (Art. 5 TVTG). The holder of the TT key has power of disposal over the token. The holder of power of disposal is presumed entitled.
5. **Hybrid holder requirement** (optional). [If the Token uses `QoreChainHybridHolderGuard`: tokens can only be transferred to TT identifiers with a registered, possession-proven ML-DSA-87 key. This check depends on the `pqcKeyStatus` precompile, which is active on the QoreChain testnet only. On mainnet the guard cannot be used today: it fails closed and refuses every transfer to a non-exempt address. Until activation, the requirement is [checked off-chain at onboarding / not applied] on mainnet.]

### B.5 Disposal and transfer (Art. 6 TVTG)

1. A disposal takes effect when (a) the transfer is complete under the rules of the TT system, meaning the transaction is included in a committed block and recorded in the token contract state; (b) transferor and transferee agree to transfer the entitlement (by signing and submitting the transfer, the transferor declares its intent, and by having accepted these terms at onboarding, the transferee declares its intent); and (c) the transferor is entitled under Art. 5 TVTG, subject to Art. 9 TVTG.
2. **Transfer restrictions.** Transfers succeed only to TT identifiers that meet the eligibility rules: [identity registry claims (ERC-3643) / RuleEngine rules (CMTAT)], [investor category, jurisdictions, holding limits]. A rejected transfer does not complete under the TT system rules, so no disposal takes place.
3. **Security interests and usufruct** (Art. 6 para. 1 let. b and para. 2 let. a TVTG). A limited right in rem can be created without transfer if it is visible to third parties and its time of creation is clear. Implementation: [partial freeze in favour of a named pledgee, recorded with an event and reason code].
4. **Without legal ground** (Art. 6 para. 3 TVTG). Reversal follows the law of unjust enrichment (§§ 1431 ff. ABGB). The Issuer's forced transfer power (B.7) may only be used to carry out a court decision or a written agreement of both parties.

### B.6 Legitimation, discharge and good faith (Art. 8 and 9 TVTG)

1. The person shown by the TT system as entitled is deemed the lawful holder of the represented right towards the Issuer.
2. The Issuer is discharged by performance to that person unless it knew, or with due care should have known, that the person is not the lawful holder.
3. Record time for distributions and voting: [block height or timestamp rule].
4. A transferee who receives a token in good faith and for value is protected under Art. 9 TVTG unless it knew, or with due care should have known, that the transferor lacked entitlement.

### B.7 Issuer and agent powers

| Power | Contract function | Permitted only when |
|---|---|---|
| Freeze (full or partial) | `setAddressFrozen`, `freezePartialTokens` | Court or authority order, sanctions, reported key compromise, a pledge under B.5 para. 3. [Complete.] |
| Forced transfer | `forcedTransfer` | Execution of a declaration of voidness under Art. 10 TVTG, an enforceable court decision, or a reversal agreed by both parties. |
| Mint / burn | `mint`, `burn` | Issue, redemption, or replacement after Art. 10 TVTG. |
| Pause | `pause` | Corporate actions, security incidents, court order. |
| Change of compliance configuration | `setRuleEngine` / compliance modules | Within the disclosed eligibility criteria, with [notice period] notice. |

Every use is recorded on chain with a reason code and reported to holders within [period].

### B.8 Loss of the TT key and declaration of voidness (Art. 10 TVTG)

1. If the TT key is missing or the token is otherwise non-functional, the person entitled at the time may apply to the Landgericht for a declaration that the token is void, in non-contentious proceedings (Ausserstreitverfahren). The applicant must show credible evidence of its entitlement and of the loss or loss of function. The respondent is the obligor of the represented right.
2. After the declaration, the applicant may assert the right without the token, or ask for a new token at its own cost.
3. **Technical execution.** On presentation of the final decision, the Issuer freezes the voided token, burns it, and mints a replacement to a new eligible TT identifier of the applicant. The court reference goes in the event `data` field.
4. **Loss of the ML-DSA-87 key alone.** [Describe whether the network's key rotation or recovery messages can restore the holder's ability to open windows without a court procedure. Counsel and the Issuer to decide whether this counts as "non-functional" under Art. 10 TVTG.]

### B.9 Liability

The tokenisation service provider is liable under Art. 9a para. 1 TVTG if the token does not meet the legal or technical requirements for effective representation and transfer, unless it proves it ensured them. The physical validator is liable under Art. 9a para. 2 TVTG where relevant. [Add contractual allocation between Issuer, tokenisation service provider and TT system providers, without excluding statutory liability.]

### B.10 Jurisdiction, notices, amendments

- Jurisdiction: courts of the Principality of Liechtenstein, [Vaduz], without prejudice to mandatory venues.
- Notices: [website], plus a hash-linked document reference on chain.
- Amendments: [procedure, holder consent threshold]. Every amendment is published with a new hash.

---

## Part C. Basic information (Basisinformationen) pointer

- **Duty** (Art. 30 TVTG). Before a token issue, the token issuer must prepare basic information, publish it in an easily accessible way, and notify the issue to the FMA. Under the current text, "token issue", "token issuer" and "basic information" cover tokens **outside** the scope of Regulation (EU) 2023/1114 (Art. 2 para. 1 let. g, h, k TVTG).
- **Exemptions** (Art. 31 TVTG). The duties in Art. 30 let. a and b do not apply where (a) all acquirers have verifiably waived the basic information, (b) the offer is addressed to fewer than 150 users, (c) the total sale price does not exceed CHF 5 million or equivalent, or (d) there is already a duty to publish qualified information on the public offer under other laws. Art. 31 para. 2 covers resale.
- **Form and language** (Art. 32 TVTG). Easy to analyse and understand. One or more documents, with a summary if there are several. German or English.
- **Content** (Art. 33 TVTG). At least: information on the tokens and related rights, the name of the TT system used, the purpose and type of the underlying transaction, acquisition and transfer conditions, risks, and for rights in things a proof of ownership and an enforceability confirmation (for example by a registered physical validator). Also a summary with the statutory warnings, the persons responsible with a responsibility statement, and the persons responsible for technical and legal functionality. Add the issue date and ensure the document cannot be altered.
- **Supplements and liability** (Art. 34, 35 TVTG).
- **Securities.** If the token is a financial instrument, prospectus law probably applies (see Art. 31 para. 1 let. d TVTG), and the basic information duty may not apply. Prospectus law means Regulation (EU) 2017/1129 as applied in the EEA and Liechtenstein implementing law [articles to be verified by counsel].

For a QoreChain token, the "name of the TT system" item (Art. 33 para. 1 let. b) should describe: the QoreChain network and chain ID, the EVM Engine, the token standard and contract address, the need for a registered ML-DSA-87 key and an EVM authorization window, and the testnet-only status of the hybrid holder check.

---

## Part D. TT service provider roles and registration pointers

Registration duty (Art. 12 TVTG): persons with seat or residence in Liechtenstein who intend to provide TT services professionally in Liechtenstein must apply in writing to the FMA for entry in the TT service provider register (Art. 23) before they first provide the service. Conditions are in Art. 13 to 17. Licensed banks, e-money institutions, CSDs, investment firms, asset managers, fund managers and MiCA institutions use the simplified procedure of Art. 19a to 19c for the activities listed there.

| Role (Art. 2 para. 1 TVTG) | Likely holder in an issue using the kit | Register entry needed? |
|---|---|---|
| Token issuer (let. k), for tokens outside MiCA | [Issuer or placement agent] | [Counsel to assess; depends on scope and Art. 12] |
| Token generator (let. l) | [Entity deploying the token contract for the issuer] | [Counsel to assess] |
| Tokenisation service provider (let. m) | [Entity ensuring legal and technical representation] | [Counsel to assess] |
| TT custodian (let. n), for tokens outside MiCA that are not financial instruments | [Custodian, if any] | [Counsel to assess; financial instrument custody falls under other law] |
| Physical validator (let. p) | [For rights in things] | [Counsel to assess] |
| TT verification service (let. r) | [Entity checking legal capacity and disposal requirements] | [Counsel to assess] |
| TT identity service provider (let. t) | [KYC provider issuing identity claims for ERC-3643 or allowlist entries] | [Counsel to assess] |
| TT price service provider (let. s), token lending (let. v) | Not expected | n/a |

Neither the QoreChain Association nor the kit acts in any of these roles. The kit is software.

Client asset protection (Art. 25 TVTG): tokens or TT keys that a TT service provider holds in trust or in the client's name are segregated in enforcement and insolvency. Pooled custody is covered if the provider has undertaken to keep them available at all times and its records show each client's share.

---

## Part E. Technical mapping to the kit

| TVTG concept | CMTAT | ERC-3643 (T-REX) | QoreChain note |
|---|---|---|---|
| Token (Art. 2 let. c) | ERC-20 balance unit | ERC-20 balance unit | Contract on the QoreChain EVM Engine |
| TT identifier (let. d) | Holder address | Holder address linked to an identity | EVM address, also usable on the native lane |
| TT key (let. e) | Holder's signing key | Holder's signing key | secp256k1 EVM key plus registered ML-DSA-87 key (window opening) |
| Completion under TT system rules (Art. 6 para. 2 let. a) | Successful `transfer` with RuleEngine approval | Successful `transfer` with identity and compliance checks | Needs a live EVM authorization window for the sender |
| Exclusion of competing disposal (Art. 7 para. 2 let. b) | Off-chain register reconciliation; no transfer outside the contract | Same | Contract is the only transfer path |
| Legitimation (Art. 8) | `balanceOf` at record time | `balanceOf` at record time | Read from public JSON-RPC |
| Declaration of voidness (Art. 10) | `forcedTransfer`, `burn`, `mint` | `forcedTransfer`, `recoveryAddress`, `burn`, `mint` | Agent key also needs a window |
| Hybrid holder requirement | `QoreChainHybridHolderRule` (CMTAT rule mapped to `QoreChainHybridHolderGuard`) | Compliance module `QoreChainHybridHolderModule` (mapped to `QoreChainHybridHolderGuard`) | Testnet only until `pqcKeyStatus` is active on mainnet. Must require `registered` and `possessionProven`. |
| Native asset modules | Not available | Not available | Proposal only. Not implemented. Requires a chain upgrade that is not scheduled. |

---

## Part F. Open points for counsel

1. Does the two-key requirement (secp256k1 plus registered ML-DSA-87 key and window) fit the TVTG concept of a TT key and of power of disposal (Art. 5)?
2. Are the measures in B.3 para. 3 enough under Art. 7 para. 2 TVTG for the chosen type of right, in particular for shares?
3. Which TT service provider registrations apply to each party in Part D?
4. Securities classification of the token, and the prospectus regime as opposed to basic information.
5. Treating loss of the ML-DSA-87 key alone under Art. 10 TVTG (B.8 para. 4).
6. Effect of a network halt, fork or contract migration on the "rules of the TT system" (Art. 6 para. 2 let. a) and on Art. 7 para. 3 TVTG.

---

## Sources

- TVTG, consolidated text (LR 950.6, version 1 September 2026): https://www.gesetze.li/konso/2019301000
- TVTG, consolidated PDF used for verification: https://www.gesetze.li/konso/pdf/2019301000?version=7
- Regulation (EU) 2023/1114 on markets in crypto-assets, OJ L 150, 9.6.2023, p. 40, Art. 2 para. 4: https://eur-lex.europa.eu/eli/reg/2023/1114/oj

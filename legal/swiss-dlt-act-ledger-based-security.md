<!-- SPDX-License-Identifier: Apache-2.0 -->

> **Template for discussion. Not legal advice. Must be reviewed by qualified counsel in the relevant jurisdiction before any use.**

# Swiss ledger-based security (Registerwertrecht): template set

Status: draft, not reviewed by counsel. References checked on 27 October 2026 against Fedlex consolidated texts and the bilingual mirror listed under Sources. Only the publication of the Federal Chancellery (Fedlex) is legally binding.

## Contents

- Part A. Legal basis (verified references)
- Part B. Registration agreement and terms of the ledger-based security
- Part C. Securities ledger requirements checklist (Art. 973d para. 2 CO)
- Part D. Issuer information document (Art. 973i CO)
- Part E. Transfer, collateral and cancellation procedures (Art. 973f to 973h CO)
- Part F. Insolvency and segregation notes (Art. 973f para. 2 CO, Art. 242a DEBA)
- Part G. Trading venue pointer (DLT trading facility, FinMIA)
- Part H. Technical mapping to the kit (CMTAT or ERC-3643 on the QoreChain EVM Engine)
- Part I. Open points for counsel
- Sources

---

## Part A. Legal basis (verified references)

| Instrument | Official reference | What it provides here |
|---|---|---|
| Federal Act of 30 March 1911 on the Amendment of the Swiss Civil Code (Part Five: The Code of Obligations), "CO" | SR 220 | Art. 973d (establishment), 973e (effects), 973f (transfer), 973g (collateral), 973h (cancellation), 973i (information and liability). Art. 973h refers to Art. 982 to 986 CO for the cancellation procedure. |
| Federal Act of 25 September 2020 on the Adaptation of Federal Law to Developments in Distributed Electronic Ledger Technology ("DLT Act") | AS 2021 33 | Amending act that inserted Art. 973d to 973i CO (in force 1 February 2021) and Art. 242a DEBA (in force 1 August 2021). |
| Federal Act of 11 April 1889 on Debt Enforcement and Bankruptcy, "DEBA" (SchKG) | SR 281.1 | Art. 242a: release of crypto-based assets from the bankrupt estate. |
| Federal Act of 19 June 2015 on Financial Market Infrastructures and Market Conduct in Securities and Derivatives Trading, "FinMIA" (FinfraG) | SR 958.1 | Art. 2 let. b^bis (DLT securities), Art. 73a to 73f (DLT trading facility). |
| Swiss Civil Code, "CC" | SR 210 | Art. 895 to 898 (special lien) and 899 to 906 (pledge of claims and other rights), applied by Art. 973g para. 2 CO. |

Summary of the operative provisions (paraphrased, not the official wording):

- **Art. 973d CO, establishment.** Para. 1: a ledger-based security is a right that, by agreement between the parties, (1) is registered in a securities ledger meeting para. 2, and (2) can be exercised and transferred only through that ledger. Para. 2: the ledger must (1) give the creditors, and not the obligor, power of disposal over their rights by technological processes; (2) have its integrity secured by adequate technical and organisational measures, such as joint management by several independent participants, against unauthorised modification; (3) record, in the ledger or in linked accompanying data, the content of the rights, the functioning of the ledger and the registration agreement; (4) let creditors view relevant information and ledger entries and check the integrity of the ledger content relating to themselves without a third party. Para. 3: the obligor must ensure the ledger is organised for its purpose and works at all times in line with the registration agreement.
- **Art. 973e CO, effects.** The obligor may only perform to the creditor shown in the ledger, and is discharged by performing at maturity to that person unless it acted with malice or gross negligence. An acquirer from the creditor shown in the ledger is protected even if the transferor lacked power of disposal, unless the acquirer acted in bad faith or with gross negligence. The objections the obligor may raise are limited (validity of the registration, the ledger or accompanying data, personal defences, and defences against a former creditor where the current creditor knowingly acted to the obligor's detriment).
- **Art. 973f CO, transfer.** Para. 1: the registration agreement governs transfer. Para. 2: if the creditor becomes bankrupt, has assets attached, or is granted a debt restructuring moratorium, the creditor's dispositions remain legally binding and effective against third parties if they were made before the event, became irrevocable under the rules of the securities ledger or another trading facility, and were actually recorded in the ledger within 24 hours. Para. 3: in a conflict between a good-faith acquirer of a certificated security and a good-faith acquirer of a ledger-based security for the same right, the acquirer of the certificated security prevails.
- **Art. 973g CO, collateral.** Collateral may be created without transferring the ledger-based security if the collateral is visible in the ledger and only the collateral taker can dispose of the security on default. Otherwise CC Art. 895 to 898 and 899 to 906 apply as for certificated securities.
- **Art. 973h CO, cancellation.** Para. 1: a person entitled may apply to the court for cancellation by showing credible evidence of the original power of disposal and its loss. After cancellation, the right can be exercised outside the ledger, or the obligor can be required, at the applicant's cost, to allocate a new ledger-based security. Art. 982 to 986 CO apply to procedure and effect. Para. 2: the parties may agree a simplified cancellation (fewer public calls for presentation, shorter time limits).
- **Art. 973i CO, information and liability.** Para. 1: the obligor must inform each acquirer about the content of the ledger-based security and the functioning of the securities ledger, including measures that protect its functioning and integrity. Para. 2: the obligor is liable for loss caused by inaccurate, misleading or non-compliant information unless it proves due diligence. Para. 3: agreements excluding or limiting this liability are void.

---

## Part B. Registration agreement and terms of the ledger-based security

The registration agreement (Art. 973d para. 1 CO) is the parties' agreement that the right is registered in the securities ledger and can be exercised and transferred only through it. It is usually built into the terms of issue, and each acquirer accepts it when acquiring the token.

### B.1 Parties and instrument

1. **Issuer (obligor).** [Issuer name], [legal form], registered office at [address], registered in the commercial register of [canton] under [UID number] (the "Issuer").
2. **Instrument.** [Type of right: e.g. registered shares of the Issuer / bond / participation certificate / profit participation / other claim], ISIN [ISIN, if any], aggregate nominal amount [amount and currency], denomination [amount], number of units [number] (the "Ledger-Based Securities").
3. **Corporate or contractual basis.** [Board resolution / general meeting resolution / articles of association provision / bond terms] dated [date]. If the rights are shares, cite the articles of association provision that permits their issue as ledger-based securities [article to be verified by counsel].
4. **Token representation.** Each Ledger-Based Security is represented by [one / a fixed number of] unit(s) of the token contract at address [0x contract address] on [QoreChain mainnet, EVM chain ID 9801 / QoreChain testnet, EVM chain ID 9800] (the "Token"). [Decimals: 0 recommended where each unit is one security.]

### B.2 Registration agreement (core clause)

> 1. The Issuer and each holder agree that the rights described in clause B.1 are registered in the securities ledger described in Part C (the "Securities Ledger") and that they may be exercised and transferred only through the Securities Ledger, within the meaning of Art. 973d para. 1 CO.
> 2. The Securities Ledger consists of (a) the Token contract state on the network named in clause B.1, and (b) the accompanying data listed in clause B.6, linked to the Token by the hash recorded in the Token contract.
> 3. By acquiring a Token, each acquirer accepts this registration agreement and the terms in this Part B as they apply at the time of acquisition.
> 4. The person whose address holds the Token in the Securities Ledger is the creditor of the corresponding Ledger-Based Security towards the Issuer (Art. 973e para. 1 CO).

### B.3 Exercise of rights

1. **Payments and distributions.** The Issuer performs only to the creditor shown in the Securities Ledger at the record time [define record block height or timestamp rule]. Payment is made [on-chain in [settlement asset] to the holding address / off-chain to the bank account notified through the identity registry]. Under Art. 973e para. 2 CO, performance at maturity to the creditor shown discharges the Issuer unless it acted with malice or gross negligence.
2. **Voting and information rights** (shares only). [Describe how holders are identified for general meetings, e.g. a snapshot of the Securities Ledger at a defined block height plus identity registry data.]
3. **Notices.** Notices to holders are published [on the Issuer website / in the Swiss Official Gazette of Commerce where required by law] and recorded as a document reference in the accompanying data.

### B.4 Transfer (Art. 973f para. 1 CO)

1. A transfer takes effect when the transfer transaction is final on the network and recorded in the Token contract state. [Define finality: for example, inclusion of the transaction in a committed block, or a stated number of further blocks. Confirm the network's finality properties in `docs/technology-standards.md` before choosing.]
2. Transfers are allowed only to addresses that meet the eligibility rules in the Token's compliance configuration: [identity registry with verified claims (ERC-3643) / allowlist or RuleEngine rules (CMTAT)], including [investor category, jurisdiction, holding limits].
3. A transfer that the compliance configuration rejects does not take place. No transfer of the right outside the Securities Ledger is effective (Art. 973d para. 1 no. 2 CO).
4. **Network prerequisite.** On QoreChain, an EVM transaction is accepted only if the sending account has a registered ML-DSA-87 key and a live EVM authorization window. The window is opened by a hybrid-signed transaction on the native lane. Holders must complete this step before they can transfer. The Issuer will publish instructions at [URL]. [If the Token requires hybrid-signature holders through the `QoreChainHybridHolderGuard`: transfers to an address without a registered, possession-proven ML-DSA-87 key are rejected. This check is available on the QoreChain testnet only until the precompile is activated on mainnet.]

### B.5 Issuer and agent powers (to be reviewed against Art. 973d para. 2 no. 1 CO)

The Token contracts give the Issuer, or agents it appoints, technical powers. The ledger must give power of disposal to the creditors and not to the obligor. So these powers may be used **only** in the cases listed below, and every use must be recorded on chain with a reason code.

| Power | Contract function (CMTAT / ERC-3643) | Permitted only when |
|---|---|---|
| Freeze an address or part of a balance | `setAddressFrozen`, `freezePartialTokens` | A court or authority orders it, sanctions law requires it, or the holder reports a key compromise. [Complete the list.] |
| Forced transfer | `forcedTransfer` | A court cancellation under Art. 973h CO is followed by reallocation, an enforceable judgment or authority order applies, or [other legally mandated case]. |
| Mint | `mint`, `batchMint` | Issue of new securities under a valid corporate resolution, or reallocation after cancellation. |
| Burn | `burn`, `batchBurn` | Redemption at maturity, buy-back, or cancellation after an Art. 973h CO judgment. |
| Pause | `pause` / `unpause` | Corporate actions, security incidents or a court order, for the shortest time needed. |
| Change compliance rules or the rule engine | `setRuleEngine` (CMTAT), `setCompliance` / modules (ERC-3643) | Only within the eligibility criteria disclosed in the issuer information document, with [notice period] notice to holders unless a court or the law requires otherwise. |

> Drafting note: counsel should decide whether these powers, written into the registration agreement and limited as above, are consistent with Art. 973d para. 2 no. 1 CO. A multi-signature or time-locked admin role can reduce the risk that the obligor holds unrestricted power of disposal.

### B.6 Accompanying data (Art. 973d para. 2 no. 3 CO)

Recorded in the Token contract (CMTAT `terms`, `tokenId` and `information` fields, or ERC-3643 `onchainID` claims) or in documents linked by hash:

- these terms of the Ledger-Based Securities, with version number and SHA-256 hash;
- the registration agreement (Part B.2);
- the description of the functioning of the Securities Ledger (Part D section 3);
- the corporate resolution(s) authorising the issue;
- the list of current agents and their roles (updated on each change).

### B.7 Governing law and jurisdiction

Swiss law. Exclusive jurisdiction: courts of [place of the Issuer's registered office], without prejudice to mandatory venues (for example the court at the bankruptcy venue under Art. 242a para. 3 DEBA).

---

## Part C. Securities ledger requirements checklist (Art. 973d para. 2 CO)

For each requirement, record the evidence the Issuer will rely on. The "Kit mapping" column describes what the kit provides today. The "Open" column lists what the Issuer must still supply.

| No. | Requirement (paraphrase) | Kit mapping | Open / Issuer to supply |
|---|---|---|---|
| 1 | The ledger gives creditors, not the obligor, power of disposal by technological processes | Holders sign transfers with their own keys. Token balances live in the contract state on the QoreChain EVM Engine. | Limit the Issuer and agent powers (Part B.5) and publish their use. Show that agent keys are governed (multi-signature, time lock). Explain the QoreChain prerequisite: a registered ML-DSA-87 key and an EVM authorization window are needed to transfer. A holder who cannot complete them cannot exercise power of disposal. |
| 2 | Integrity secured by adequate technical and organisational measures, e.g. joint management by several independent participants | The network state is replicated by the validator set and agreed by the network's consensus. Contract code is immutable or upgradeable only through declared roles. Native-lane transactions carry a hybrid secp256k1 plus ML-DSA-87 signature. | Number, identity and independence of validators at issuance [to be documented from the public validator set at that time]. The upgrade authority of the chain (on-chain governance) and of the token contract (Issuer roles). Third-party audit reports of the deployed contracts. See `docs/technology-standards.md`. |
| 3 | Content of the rights, functioning of the ledger and the registration agreement recorded in the ledger or linked accompanying data | CMTAT `terms` (document URI and hash) and `information`; ERC-3643 identity and claim references. | Publish the documents in Part B.6, record their hashes on chain, and keep them available for the life of the instrument. |
| 4 | Creditors can view relevant information and entries and check integrity of their own entries without a third party | Public JSON-RPC and REST endpoints. Anyone can run a node. Events give an audit trail (the issuer console reads `Transfer`, freeze and role events from chain). | Self-verification without a third party in practice means running a node or a light client. Document how a holder does this. Note that `eth_getProof` on QoreChain returns IAVL proofs, not Merkle-Patricia proofs, so standard Ethereum proof verifiers do not apply directly. |
| Para. 3 | Obligor ensures the ledger is organised for its purpose and works in line with the registration agreement at all times | Contract tests and deployment scripts in the kit. | Operating procedures, monitoring, incident handling and a contingency plan if the network halts or the contracts must be migrated. State that no metric in this template is a measured availability figure. |

---

## Part D. Issuer information document (Art. 973i CO)

Give this to every acquirer before acquisition. Art. 973i para. 3 CO makes clauses that exclude or limit liability for this information void, so do not include any.

1. **The Issuer.** Name, seat, UID, contact, auditor, [regulatory status, if any].
2. **The Ledger-Based Securities.** Type of right, nominal amount, currency, interest or dividend terms, maturity, ranking, transfer restrictions, eligibility criteria, applicable law, ISIN.
3. **Functioning of the Securities Ledger.**
   - Network: QoreChain [mainnet `qorechain-vladi`, EVM chain ID 9801 / testnet `qorechain-diana`, EVM chain ID 9800]. Token standard: [CMTAT version / ERC-3643 T-REX version]. Contract addresses: [addresses].
   - How a holder gets an address, registers an ML-DSA-87 key, opens an EVM authorization window, and transfers.
   - Who can freeze, force-transfer, mint, burn and pause (Part B.5), and how holders are told when these powers are used.
   - How a holder checks their own entries (Part C, item 4).
4. **Measures protecting functioning and integrity.** Validator set and consensus, chain upgrade governance, contract audit status, key management of the Issuer and agents, incident response contacts. [Every availability or recovery figure: give a measured figure with its source, or write "not measured".]
5. **Risks.** Loss of keys and the cancellation procedure (Part E.3). Network halts or forks. Smart contract defects. Compliance rules that change. Dependence on third-party contracts (CMTAT, ERC-3643) and their licences. The fact that the hybrid holder check is testnet only. The fact that native asset modules described in the kit's proposal do **not** exist on QoreChain.
6. **Liability.** Statement of the Issuer's liability under Art. 973i para. 2 CO.

---

## Part E. Transfer, collateral and cancellation procedures

### E.1 Transfer

See Part B.4. Add the record of each transfer to the Issuer's internal register reconciliation [frequency].

### E.2 Collateral (Art. 973g CO)

Collateral without transfer is possible if it is visible in the ledger and only the collateral taker can dispose on default. Possible implementation: [a pledge registry contract or partial freeze in favour of a named collateral taker, with release only by the collateral taker's key]. Counsel to confirm that the chosen mechanism meets both conditions of Art. 973g para. 1 CO.

### E.3 Cancellation after loss of keys (Art. 973h CO)

1. **Application.** The person entitled applies to the competent court and shows credible evidence of their original power of disposal and of its loss. Art. 982 to 986 CO apply to the procedure.
2. **Simplified cancellation (optional, Art. 973h para. 2 CO).** The parties agree: [number] public call(s) for presentation instead of the statutory number, and a time limit of [period] instead of the statutory time limit. [Statutory numbers and periods under Art. 983 to 984 CO: article to be verified by counsel.]
3. **Technical execution after judgment.** On presentation of the final cancellation judgment, the Issuer (a) freezes the address shown in the judgment, (b) burns the cancelled units or force-transfers them to a cancellation address, and (c) at the applicant's cost, mints or transfers the same number of units to a new address of the applicant that meets the eligibility rules. Each step is recorded on chain with the court reference in the `data` field.

---

## Part F. Insolvency and segregation notes

1. **Insolvency of a holder (Art. 973f para. 2 CO).** Dispositions made before bankruptcy, attachment or a moratorium stay effective if they became irrevocable under the ledger rules and were recorded in the ledger within 24 hours. The registration agreement should define when a transfer is "irrevocable" on QoreChain, for example inclusion in a finalised block.
2. **Insolvency of a custodian (Art. 242a DEBA).** If a custodian holds the Tokens for a client and goes bankrupt, the bankruptcy administration decides on releasing crypto-based assets claimed by a third party. The claim succeeds if the custodian undertook to keep the assets available to the client at all times and the assets are either individually allocated to the client, or held in a pool where the client's share is clear. If the administration rejects the claim, the claimant has 20 days to sue at the bankruptcy venue. The claimant bears the costs and may be asked for an advance. Custody agreements for the Tokens should therefore contain an "available at all times" undertaking and clear allocation records.
3. **Insolvency of the Issuer.** The Ledger-Based Securities represent claims or membership rights against the Issuer. They give no segregation right against the Issuer's estate. Counsel to address ranking.

---

## Part G. Trading venue pointer (FinMIA)

- **DLT securities.** FinMIA Art. 2 let. b^bis defines DLT securities to include ledger-based securities under Art. 973d CO.
- **DLT trading facility.** FinMIA Art. 73a para. 1 defines a DLT trading facility as a commercially operated facility for the multilateral trading of DLT securities that meets at least one of these conditions: (a) it admits participants under Art. 73c para. 1 let. e (persons not supervised under financial market law); (b) it holds DLT securities in central custody under uniform rules and procedures; or (c) it clears and settles transactions in DLT securities under uniform rules and procedures. Para. 2 defines "commercial". Art. 73b to 73f set out further requirements, including admission of participants (Art. 73c) and admission of DLT securities and other assets (Art. 73d).
- **What this means for an issuer.** Issuing a Ledger-Based Security does not in itself require a DLT trading facility licence. Operating multilateral trading of DLT securities may. The kit's contracts and issuer console are not a trading facility. Any secondary trading arrangement needs a separate regulatory analysis.
- Other regimes to check (not covered here): prospectus and key information document duties under the Financial Services Act (FinSA, SR 950.1) [articles to be verified by counsel]; anti-money laundering duties (AMLA, SR 955.0) [articles to be verified by counsel]; the Swiss Financial Market Supervisory Authority (FINMA) practice on token classification.

---

## Part H. Technical mapping to the kit

| Legal element | CMTAT deployment | ERC-3643 (T-REX) deployment | QoreChain-specific |
|---|---|---|---|
| Creditor shown in the ledger | `balanceOf(address)` | `balanceOf(address)` with an identity registered in the `IdentityRegistry` | Address is the holder's EVM account. The same account has a native-lane `qor1...` form. |
| Eligibility for transfer | Rule engine (allowlist, `QoreChainHybridHolderRule` mapped to `QoreChainHybridHolderGuard`) | `ModularCompliance` modules (including `QoreChainHybridHolderModule`) plus identity claims | Hybrid holder check is testnet only until the `pqcKeyStatus` precompile (0x...0A02) is active on mainnet. A contract that relies on it must require `registered` and `possessionProven` to be true. |
| Freeze, partial freeze | `setAddressFrozen`, `freezePartialTokens` | `setAddressFrozen`, `freezePartialTokens` | There is no native per-address freeze on QoreChain. Freeze exists only in the token contract. |
| Forced transfer | `forcedTransfer` | `forcedTransfer` | Agent account needs an EVM authorization window like any sender. |
| Pause | `pause` | `pause` | |
| Accompanying data | `terms` (URI + hash), `information`, `tokenId` | OnchainID claims, token `onchainID` | |
| Audit trail | Contract events | Contract events | Read via public JSON-RPC. The issuer console shows them. |
| Native modules (`x/asset`, `x/compliance`, ...) | Not available | Not available | A proposal only. Not implemented. Requires a chain upgrade that is not scheduled. |

---

## Part I. Open points for counsel

1. Do the Issuer and agent powers in Part B.5 comply with Art. 973d para. 2 no. 1 CO, and which governance controls are needed?
2. Is the QoreChain validator set and governance enough for "joint management by several independent participants" (Art. 973d para. 2 no. 2 CO) at the time of issue?
3. Does the requirement to register an ML-DSA-87 key and open an EVM authorization window affect the holder's power of disposal or the information duty under Art. 973i CO?
4. Wording and number of public calls and time limits for simplified cancellation (Art. 973h para. 2 CO and Art. 982 to 986 CO).
5. Corporate law basis if the rights are shares [article to be verified by counsel].
6. FinSA prospectus or exemption, AMLA status of any intermediary, and tax treatment.
7. What happens to the instrument if QoreChain halts, forks, or the token contract must migrate, and how this is reflected in the registration agreement.

---

## Sources

- Code of Obligations (SR 220), consolidated text on Fedlex: https://www.fedlex.admin.ch/eli/cc/27/317_321_377/en
- Art. 973d to 973i CO, bilingual mirror used to read the text (not official): https://www.droit-bilingue.ch/en-de/2/22/220-973d-1380.html, https://www.droit-bilingue.ch/en-de/2/22/220-973e-1381.html, https://www.droit-bilingue.ch/en-de/2/22/220-973f-1382.html, https://www.droit-bilingue.ch/en-de/2/22/220-973g-1383.html, https://www.droit-bilingue.ch/en-de/2/22/220-973h-1384.html, https://www.droit-bilingue.ch/en-de/2/22/220-973i-1385.html
- DLT Act, AS 2021 33 (Fedlex): https://www.fedlex.admin.ch/eli/oc/2021/33/de
- Debt Enforcement and Bankruptcy Act (SR 281.1), Fedlex: https://www.fedlex.admin.ch/eli/cc/11/529_488_529/en ; Art. 242a, bilingual mirror: https://www.droit-bilingue.ch/de-fr/2/28/281.1-242a-273.html
- Financial Market Infrastructure Act (SR 958.1), Fedlex: https://www.fedlex.admin.ch/eli/cc/2015/853/en ; Art. 2 and 73a to 73c, bilingual mirror: https://www.droit-bilingue.ch/en-de/9/95/958.1-2-5.html, https://www.droit-bilingue.ch/en-de/9/95/958.1-73a-77.html, https://www.droit-bilingue.ch/en-de/9/95/958.1-73c-79.html
- FINMA, licensing as a DLT trading facility: https://www.finma.ch/en/authorisation/fintech/dlt-handelssystem/

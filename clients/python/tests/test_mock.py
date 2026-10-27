# SPDX-License-Identifier: Apache-2.0
import pytest

from qorechain_asset_kit import MockChain, MockChainError, asset, attest, compliance, settlement

ISSUER = "qor1issuer"
AGENT = "qor1agent"
ALICE = "qor1alice"
BOB = "qor1bob"
CAROL = "qor1carol"
KYC = "qor1kycprovider"
BOND = "bond-2030"


def rejects(code, fn, *args, **kwargs):
    with pytest.raises(MockChainError) as info:
        fn(*args, **kwargs)
    assert info.value.code == code, str(info.value)
    return info.value


def make_bond(chain, max_supply="", **flags):
    chain.asset.create_asset(
        issuer=ISSUER, asset_id=BOND, name="Example 2030 Bond", symbol="EB30", decimals=0,
        flags={"freezable": True, "pausable": True, **flags}, max_supply=max_supply,
    )
    chain.asset.set_role(issuer=ISSUER, asset_id=BOND, address=AGENT, role=asset.ROLE_AGENT, granted=True)


def balance(chain, address):
    return chain.asset.holder(asset_id=BOND, address=address).holder.balance


# ---------------------------------------------------------------- issuance

@pytest.fixture
def capped():
    chain = MockChain()
    make_bond(chain, max_supply="1000", supply_cap=True)
    return chain


def test_creates_mints_and_transfers(capped):
    capped.asset.mint(agent=AGENT, asset_id=BOND, to=ALICE, amount="600")
    capped.asset.transfer(from_=ALICE, asset_id=BOND, to=BOB, amount="100")
    assert balance(capped, ALICE) == "500"
    assert balance(capped, BOB) == "100"
    a = capped.asset.asset(asset_id=BOND).asset
    assert a.total_supply == "600"
    assert a.status == asset.ASSET_STATUS_ACTIVE
    assert len(capped.events("qorechain.asset.v1.EventMinted")) == 1


def test_enforces_the_supply_cap(capped):
    capped.asset.mint(agent=AGENT, asset_id=BOND, to=ALICE, amount="1000")
    rejects("ERROR_CODE_SUPPLY_CAP_EXCEEDED", capped.asset.mint, agent=AGENT, asset_id=BOND, to=ALICE, amount="1")


def test_refuses_non_agent_invalid_amount_and_duplicate(capped):
    rejects("ERROR_CODE_UNAUTHORIZED_ROLE", capped.asset.mint, agent=BOB, asset_id=BOND, to=BOB, amount="1")
    rejects("ERROR_CODE_INVALID_AMOUNT", capped.asset.mint, agent=AGENT, asset_id=BOND, to=ALICE, amount="-5")
    rejects("ERROR_CODE_ASSET_EXISTS", capped.asset.create_asset, issuer=ISSUER, asset_id=BOND)


def test_only_relaxes_flags(capped):
    rejects("ERROR_CODE_FLAG_IMMUTABLE", capped.asset.update_flags, issuer=ISSUER, asset_id=BOND,
            flags={"freezable": True, "pausable": True, "supply_cap": False})
    capped.asset.update_flags(issuer=ISSUER, asset_id=BOND, flags={"freezable": True, "pausable": False, "supply_cap": True})
    rejects("ERROR_CODE_FLAG_NOT_ENABLED", capped.asset.pause, agent=AGENT, asset_id=BOND, paused=True)


def test_require_auth():
    c = MockChain()
    c.asset.create_asset(issuer=ISSUER, asset_id="fund-a", flags={"require_auth": True})
    rejects("ERROR_CODE_HOLDER_NOT_AUTHORIZED", c.asset.mint, agent=ISSUER, asset_id="fund-a", to=ALICE, amount="5")
    c.asset.authorize_holder(agent=ISSUER, asset_id="fund-a", holder=ALICE, authorized=True)
    c.asset.mint(agent=ISSUER, asset_id="fund-a", to=ALICE, amount="5")
    rejects("ERROR_CODE_HOLDER_NOT_AUTHORIZED", c.asset.transfer, from_=ALICE, asset_id="fund-a", to=BOB, amount="1")


def test_require_hybrid_signature():
    c = MockChain()
    rejects("ERROR_CODE_HYBRID_SIGNATURE_REQUIRED", c.asset.create_asset, issuer=ISSUER, asset_id="pq-note",
            flags={"require_hybrid_signature": True})
    c.set_hybrid_key(ISSUER, registered=True, possession_proven=True)
    c.asset.create_asset(issuer=ISSUER, asset_id="pq-note", flags={"require_hybrid_signature": True})
    c.set_hybrid_key(ALICE, registered=True, possession_proven=False)
    rejects("ERROR_CODE_HYBRID_SIGNATURE_REQUIRED", c.asset.mint, agent=ISSUER, asset_id="pq-note", to=ALICE, amount="1")
    c.set_hybrid_key(ALICE, registered=True, possession_proven=True)
    c.asset.mint(agent=ISSUER, asset_id="pq-note", to=ALICE, amount="1")


def test_non_transferable_allows_clawback():
    c = MockChain()
    c.asset.create_asset(issuer=ISSUER, asset_id="membership", flags={"non_transferable": True, "freezable": True})
    c.asset.mint(agent=ISSUER, asset_id="membership", to=ALICE, amount="1")
    rejects("ERROR_CODE_NON_TRANSFERABLE", c.asset.transfer, from_=ALICE, asset_id="membership", to=BOB, amount="1")
    c.asset.clawback(agent=ISSUER, asset_id="membership", from_=ALICE, amount="1", reason="membership ended")


# ------------------------------------------- freeze, pause, clawback, forced

@pytest.fixture
def funded():
    chain = MockChain()
    make_bond(chain)
    chain.asset.mint(agent=AGENT, asset_id=BOND, to=ALICE, amount="100")
    return chain


def test_freezes_and_unfreezes(funded):
    funded.asset.freeze(agent=AGENT, asset_id=BOND, holder=ALICE, frozen=True)
    rejects("ERROR_CODE_ADDRESS_FROZEN", funded.asset.transfer, from_=ALICE, asset_id=BOND, to=BOB, amount="1")
    rejects("ERROR_CODE_ADDRESS_FROZEN", funded.asset.mint, agent=AGENT, asset_id=BOND, to=ALICE, amount="1")
    q = funded.asset.can_transfer(asset_id=BOND, from_=ALICE, to=BOB, amount="1")
    assert not q.allowed
    assert q.code == asset.ERROR_CODE_ADDRESS_FROZEN
    funded.asset.freeze(agent=AGENT, asset_id=BOND, holder=ALICE, frozen=False)
    funded.asset.transfer(from_=ALICE, asset_id=BOND, to=BOB, amount="1")


def test_partial_freeze(funded):
    funded.asset.freeze_partial(agent=AGENT, asset_id=BOND, holder=ALICE, frozen_amount="70")
    rejects("ERROR_CODE_INSUFFICIENT_UNFROZEN_BALANCE", funded.asset.transfer, from_=ALICE, asset_id=BOND, to=BOB, amount="31")
    funded.asset.transfer(from_=ALICE, asset_id=BOND, to=BOB, amount="30")


def test_pause_blocks_transfers_not_issuance(funded):
    funded.asset.pause(agent=AGENT, asset_id=BOND, paused=True)
    rejects("ERROR_CODE_ASSET_PAUSED", funded.asset.transfer, from_=ALICE, asset_id=BOND, to=BOB, amount="1")
    funded.asset.mint(agent=AGENT, asset_id=BOND, to=BOB, amount="1")
    funded.asset.pause(agent=AGENT, asset_id=BOND, paused=False)
    funded.asset.transfer(from_=ALICE, asset_id=BOND, to=BOB, amount="1")


def test_clawback_ignores_freeze(funded):
    funded.asset.freeze_partial(agent=AGENT, asset_id=BOND, holder=ALICE, frozen_amount="100")
    funded.asset.freeze(agent=AGENT, asset_id=BOND, holder=ALICE, frozen=True)
    funded.asset.clawback(agent=AGENT, asset_id=BOND, from_=ALICE, amount="40", reason="court order 12/2026")
    h = funded.asset.holder(asset_id=BOND, address=ALICE).holder
    assert h.balance == "60"
    assert h.frozen_amount == "60"
    assert balance(funded, ISSUER) == "40"
    assert funded.events("qorechain.asset.v1.EventClawback")[0].data.reason == "court order 12/2026"


def test_forced_transfer_to_recovery_wallet(funded):
    funded.asset.freeze(agent=AGENT, asset_id=BOND, holder=ALICE, frozen=True)
    funded.asset.force_transfer(agent=AGENT, asset_id=BOND, from_=ALICE, to=CAROL, amount="100", reason="lost key")
    assert balance(funded, CAROL) == "100"
    funded.asset.freeze(agent=AGENT, asset_id=BOND, holder=BOB, frozen=True)
    rejects("ERROR_CODE_ADDRESS_FROZEN", funded.asset.force_transfer, agent=AGENT, asset_id=BOND,
            from_=CAROL, to=BOB, amount="1", reason="x")


def test_issuer_moves_in_two_steps(funded):
    funded.asset.propose_issuer(issuer=ISSUER, asset_id=BOND, new_issuer=CAROL)
    rejects("ERROR_CODE_UNAUTHORIZED_ROLE", funded.asset.accept_issuer, new_issuer=BOB, asset_id=BOND)
    funded.asset.accept_issuer(new_issuer=CAROL, asset_id=BOND)
    assert funded.asset.asset(asset_id=BOND).asset.issuer == CAROL
    roles = funded.asset.roles(asset_id=BOND).roles
    assert next(r for r in roles if r.role == asset.ROLE_ISSUER).address == CAROL


def test_retire(funded):
    funded.asset.retire(issuer=ISSUER, asset_id=BOND)
    rejects("ERROR_CODE_ASSET_RETIRED", funded.asset.transfer, from_=ALICE, asset_id=BOND, to=BOB, amount="1")
    funded.asset.burn(agent=AGENT, asset_id=BOND, from_=ALICE, amount="100")
    assert funded.asset.asset(asset_id=BOND).asset.total_supply == "0"


# ------------------------------------------------- identity and compliance

@pytest.fixture
def kyc():
    chain = MockChain(identity_agents=[KYC])
    make_bond(chain)
    chain.identity.set_claim_issuer(authority="authority", claim_issuer={"address": KYC, "name": "KYC provider", "topics": [1]})
    for iid, addr, country in (("id-alice", ALICE, 756), ("id-bob", BOB, 408)):
        chain.identity.register_identity(agent=KYC, identity_id=iid, address=addr, country=country)
        chain.identity.add_claim(claim_issuer=KYC, identity_id=iid, topic=1, data_hash=bytes(32), valid_until=0)
    chain.compliance.bind_module(issuer=ISSUER, asset_id=BOND, module_id="identity-verified", version=1, params_json='{"topics":[1]}')
    chain.compliance.bind_module(issuer=ISSUER, asset_id=BOND, module_id="country-blocklist", version=1, params_json='{"countries":[408]}')
    return chain


def test_rejects_mint_to_unverified(kyc):
    e = rejects("ERROR_CODE_COMPLIANCE_REJECTED", kyc.asset.mint, agent=AGENT, asset_id=BOND, to=CAROL, amount="1")
    assert "identity-verified" in str(e)


def test_rejects_blocked_country_and_reports_module(kyc):
    kyc.asset.mint(agent=AGENT, asset_id=BOND, to=ALICE, amount="10")
    rejects("ERROR_CODE_COMPLIANCE_REJECTED", kyc.asset.transfer, from_=ALICE, asset_id=BOND, to=BOB, amount="1")
    q = kyc.asset.can_transfer(asset_id=BOND, from_=ALICE, to=BOB, amount="1")
    assert (q.allowed, q.code, q.compliance_module_id) == (False, asset.ERROR_CODE_COMPLIANCE_REJECTED, "country-blocklist")
    check = kyc.compliance.check(asset_id=BOND, from_=ALICE, to=BOB, amount="1")
    assert (check.allowed, check.module_id, check.version) == (False, "country-blocklist", 1)


def test_distrusting_claim_issuer_unverifies(kyc):
    kyc.asset.mint(agent=AGENT, asset_id=BOND, to=ALICE, amount="1")
    kyc.identity.set_claim_issuer(authority="authority", claim_issuer={"address": KYC, "topics": [1]}, remove=True)
    assert not kyc.identity.is_verified(address=ALICE, topics=[1]).verified
    rejects("ERROR_CODE_COMPLIANCE_REJECTED", kyc.asset.mint, agent=AGENT, asset_id=BOND, to=ALICE, amount="1")


def test_disabled_module_fails_closed_until_migration(kyc):
    kyc.asset.mint(agent=AGENT, asset_id=BOND, to=ALICE, amount="10")
    kyc.compliance.register_module(authority="authority", module={
        "module_id": "country-blocklist", "version": 2, "runtime": compliance.MODULE_RUNTIME_NATIVE})
    kyc.compliance.set_module_status(authority="authority", module_id="country-blocklist", version=1,
                                     status=compliance.MODULE_STATUS_DISABLED)
    rejects("ERROR_CODE_COMPLIANCE_REJECTED", kyc.asset.mint, agent=AGENT, asset_id=BOND, to=ALICE, amount="1")
    kyc.compliance.migrate_binding(issuer=ISSUER, asset_id=BOND, module_id="country-blocklist", to_version=2)
    kyc.asset.mint(agent=AGENT, asset_id=BOND, to=ALICE, amount="1")
    rejects("ERROR_CODE_INVALID_PARAMS", kyc.compliance.bind_module, issuer=ISSUER, asset_id=BOND,
            module_id="max-holders", version=1, params_json='{"max":0}')


def test_caps_holders(kyc):
    kyc.compliance.unbind_module(issuer=ISSUER, asset_id=BOND, module_id="country-blocklist")
    kyc.compliance.bind_module(issuer=ISSUER, asset_id=BOND, module_id="max-holders", version=1, params_json='{"max":1}')
    kyc.asset.mint(agent=AGENT, asset_id=BOND, to=ALICE, amount="10")
    rejects("ERROR_CODE_COMPLIANCE_REJECTED", kyc.asset.transfer, from_=ALICE, asset_id=BOND, to=BOB, amount="1")
    kyc.asset.transfer(from_=ALICE, asset_id=BOND, to=BOB, amount="10")


def test_custom_module_logic(kyc):
    kyc.compliance.register_module(authority="authority", module={
        "module_id": "lockup", "version": 1, "runtime": compliance.MODULE_RUNTIME_WASM, "code_ref": "qor1lockupcontract"})
    kyc.define_module_logic(
        "lockup", lambda ctx: "lock-up until day 1" if ctx.from_ and ctx.chain.time < 1_767_225_600 + 86400 else None)
    kyc.compliance.bind_module(issuer=ISSUER, asset_id=BOND, module_id="lockup", version=1, params_json="{}")
    kyc.asset.mint(agent=AGENT, asset_id=BOND, to=ALICE, amount="10")
    kyc.identity.register_identity(agent=KYC, identity_id="id-carol", address=CAROL, country=756)
    kyc.identity.add_claim(claim_issuer=KYC, identity_id="id-carol", topic=1, data_hash=bytes(32), valid_until=0)
    rejects("ERROR_CODE_COMPLIANCE_REJECTED", kyc.asset.transfer, from_=ALICE, asset_id=BOND, to=CAROL, amount="1")
    kyc.advance(10, 86400)
    kyc.asset.transfer(from_=ALICE, asset_id=BOND, to=CAROL, amount="1")


# --------------------------------------------------------------- settlement

def legs(cash):
    return [
        {"from": ALICE, "to": BOB, "denom": f"asset/{BOND}", "amount": "10"},
        {"from": BOB, "to": ALICE, "denom": "uqor", "amount": cash},
    ]


@pytest.fixture
def dvp():
    chain = MockChain()
    make_bond(chain)
    chain.asset.mint(agent=AGENT, asset_id=BOND, to=ALICE, amount="10")
    chain.fund_bank(BOB, "uqor", "1000")
    return chain


def status(chain, iid):
    return chain.settlement.instruction(id=iid).instruction.status


def test_settles_after_bilateral_affirmation(dvp):
    iid = dvp.settlement.create_instruction(creator=ALICE, legs=legs("1000"), deadline=dvp.time + 3600).id
    assert status(dvp, iid) == settlement.INSTRUCTION_STATUS_PENDING
    assert dvp.settlement.affirm(party=BOB, id=iid).executed
    assert balance(dvp, BOB) == "10"
    assert dvp.bank_balance(ALICE, "uqor") == "1000"


def test_failing_cash_leg_moves_no_asset(dvp):
    iid = dvp.settlement.create_instruction(creator=ALICE, legs=legs("1001"), deadline=dvp.time + 3600).id
    assert not dvp.settlement.affirm(party=BOB, id=iid).executed
    ins = dvp.settlement.instruction(id=iid).instruction
    assert ins.status == settlement.INSTRUCTION_STATUS_FAILED
    assert "leg 1" in ins.failure_reason
    assert balance(dvp, ALICE) == "10"
    assert balance(dvp, BOB) == "0"
    assert dvp.bank_balance(BOB, "uqor") == "1000"
    assert dvp.events("qorechain.asset.v1.EventTransferred") == []
    dvp.fund_bank(BOB, "uqor", "1")
    assert dvp.settlement.execute_instruction(signer=BOB, id=iid).status == settlement.INSTRUCTION_STATUS_EXECUTED


def test_frozen_seller_fails_asset_leg(dvp):
    dvp.asset.freeze(agent=AGENT, asset_id=BOND, holder=ALICE, frozen=True)
    iid = dvp.settlement.create_instruction(creator=BOB, legs=legs("1000"), deadline=dvp.time + 3600,
                                            settlement_type=settlement.SETTLEMENT_TYPE_MANUAL).id
    rejects("ERROR_CODE_NOT_FULLY_AFFIRMED", dvp.settlement.execute_instruction, signer=BOB, id=iid)
    dvp.settlement.affirm(party=ALICE, id=iid)
    assert dvp.settlement.execute_instruction(signer=ALICE, id=iid).status == settlement.INSTRUCTION_STATUS_FAILED
    assert dvp.bank_balance(BOB, "uqor") == "1000"
    assert "ERROR_CODE_ADDRESS_FROZEN" in dvp.settlement.instruction(id=iid).instruction.failure_reason


def test_expires_and_refuses_non_parties(dvp):
    iid = dvp.settlement.create_instruction(creator=ALICE, legs=legs("1000"), deadline=dvp.time + 60).id
    rejects("ERROR_CODE_NOT_A_PARTY", dvp.settlement.affirm, party=CAROL, id=iid)
    dvp.advance(100, 61)
    assert status(dvp, iid) == settlement.INSTRUCTION_STATUS_EXPIRED
    rejects("ERROR_CODE_INVALID_STATUS", dvp.settlement.affirm, party=BOB, id=iid)


def test_settles_on_block(dvp):
    iid = dvp.settlement.create_instruction(creator=ALICE, legs=legs("1000"), deadline=dvp.time + 3600,
                                            settlement_type=settlement.SETTLEMENT_TYPE_ON_BLOCK,
                                            settle_height=dvp.height + 5).id
    dvp.settlement.affirm(party=BOB, id=iid)
    assert status(dvp, iid) == settlement.INSTRUCTION_STATUS_AFFIRMED
    dvp.advance(5, 5)
    assert status(dvp, iid) == settlement.INSTRUCTION_STATUS_EXECUTED


# ------------------------------------------------------------- attestations

ADMIN = "qor1fundadmin"
NAV = attest.ATTESTATION_KIND_NAV


@pytest.fixture
def navved():
    chain = MockChain()
    make_bond(chain)
    chain.attest.set_attester(issuer=ISSUER, attester={"asset_id": BOND, "address": ADMIN, "kinds": [NAV], "name": "Fund admin"})
    return chain


def test_fresh_then_stale_gates_transfers(navved):
    assert navved.attest.latest(asset_id=BOND, kind=NAV).freshness == attest.FRESHNESS_MISSING
    navved.attest.submit(attester=ADMIN, asset_id=BOND, kind=NAV, value="101.25", unit="CHF",
                         observed_at=navved.time - 60, valid_for_seconds=86400)
    fresh = navved.attest.latest(asset_id=BOND, kind=NAV)
    assert fresh.freshness == attest.FRESHNESS_FRESH
    assert fresh.attestation.value == "101.25"
    navved.compliance.bind_module(issuer=ISSUER, asset_id=BOND, module_id="attestation-fresh", version=1,
                                  params_json='{"kind":"ATTESTATION_KIND_NAV"}')
    navved.asset.mint(agent=AGENT, asset_id=BOND, to=ALICE, amount="5")
    navved.advance(1000, 86400)
    assert navved.attest.latest(asset_id=BOND, kind=NAV).freshness == attest.FRESHNESS_STALE
    rejects("ERROR_CODE_COMPLIANCE_REJECTED", navved.asset.transfer, from_=ALICE, asset_id=BOND, to=BOB, amount="1")


def test_refuses_bad_attestations(navved):
    t = navved.time
    rejects("ERROR_CODE_NOT_AN_ATTESTER", navved.attest.submit, attester=BOB, asset_id=BOND, kind=NAV, value="1",
            observed_at=t, valid_for_seconds=60)
    rejects("ERROR_CODE_OBSERVATION_IN_FUTURE", navved.attest.submit, attester=ADMIN, asset_id=BOND, kind=NAV,
            value="1", observed_at=t + 1, valid_for_seconds=60)
    navved.attest.submit(attester=ADMIN, asset_id=BOND, kind=NAV, value="1", observed_at=t, valid_for_seconds=60)
    rejects("ERROR_CODE_OLDER_THAN_LATEST", navved.attest.submit, attester=ADMIN, asset_id=BOND, kind=NAV,
            value="1", observed_at=t - 10, valid_for_seconds=60)
    rejects("ERROR_CODE_KIND_NOT_ALLOWED", navved.attest.submit, attester=ADMIN, asset_id=BOND,
            kind=attest.ATTESTATION_KIND_RESERVES, value="1", observed_at=t, valid_for_seconds=60)

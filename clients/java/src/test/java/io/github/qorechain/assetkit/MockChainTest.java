// SPDX-License-Identifier: Apache-2.0
package io.github.qorechain.assetkit;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.protobuf.ByteString;
import io.github.qorechain.assetkit.proto.asset.v1.AssetStatus;
import io.github.qorechain.assetkit.proto.asset.v1.EventClawback;
import io.github.qorechain.assetkit.proto.asset.v1.HolderState;
import io.github.qorechain.assetkit.proto.asset.v1.MsgAcceptIssuer;
import io.github.qorechain.assetkit.proto.asset.v1.MsgAuthorizeHolder;
import io.github.qorechain.assetkit.proto.asset.v1.MsgBurn;
import io.github.qorechain.assetkit.proto.asset.v1.MsgClawback;
import io.github.qorechain.assetkit.proto.asset.v1.MsgCreateAsset;
import io.github.qorechain.assetkit.proto.asset.v1.MsgForceTransfer;
import io.github.qorechain.assetkit.proto.asset.v1.MsgFreeze;
import io.github.qorechain.assetkit.proto.asset.v1.MsgFreezePartial;
import io.github.qorechain.assetkit.proto.asset.v1.MsgMint;
import io.github.qorechain.assetkit.proto.asset.v1.MsgPause;
import io.github.qorechain.assetkit.proto.asset.v1.MsgProposeIssuer;
import io.github.qorechain.assetkit.proto.asset.v1.MsgRetire;
import io.github.qorechain.assetkit.proto.asset.v1.MsgSetRole;
import io.github.qorechain.assetkit.proto.asset.v1.MsgTransfer;
import io.github.qorechain.assetkit.proto.asset.v1.MsgUpdateFlags;
import io.github.qorechain.assetkit.proto.asset.v1.QueryAssetRequest;
import io.github.qorechain.assetkit.proto.asset.v1.QueryCanTransferRequest;
import io.github.qorechain.assetkit.proto.asset.v1.QueryCanTransferResponse;
import io.github.qorechain.assetkit.proto.asset.v1.QueryHolderRequest;
import io.github.qorechain.assetkit.proto.asset.v1.QueryRolesRequest;
import io.github.qorechain.assetkit.proto.asset.v1.Role;
import io.github.qorechain.assetkit.proto.asset.v1.RoleGrant;
import io.github.qorechain.assetkit.proto.asset.v1.RwaFlagsV0;
import io.github.qorechain.assetkit.proto.attest.v1.AttestationKind;
import io.github.qorechain.assetkit.proto.attest.v1.Attester;
import io.github.qorechain.assetkit.proto.attest.v1.Freshness;
import io.github.qorechain.assetkit.proto.attest.v1.MsgSetAttester;
import io.github.qorechain.assetkit.proto.attest.v1.MsgSubmit;
import io.github.qorechain.assetkit.proto.attest.v1.QueryLatestRequest;
import io.github.qorechain.assetkit.proto.attest.v1.QueryLatestResponse;
import io.github.qorechain.assetkit.proto.compliance.v1.ComplianceModule;
import io.github.qorechain.assetkit.proto.compliance.v1.ModuleRuntime;
import io.github.qorechain.assetkit.proto.compliance.v1.ModuleStatus;
import io.github.qorechain.assetkit.proto.compliance.v1.MsgBindModule;
import io.github.qorechain.assetkit.proto.compliance.v1.MsgMigrateBinding;
import io.github.qorechain.assetkit.proto.compliance.v1.MsgRegisterModule;
import io.github.qorechain.assetkit.proto.compliance.v1.MsgSetModuleStatus;
import io.github.qorechain.assetkit.proto.compliance.v1.MsgUnbindModule;
import io.github.qorechain.assetkit.proto.compliance.v1.QueryCheckRequest;
import io.github.qorechain.assetkit.proto.compliance.v1.QueryCheckResponse;
import io.github.qorechain.assetkit.proto.identity.v1.ClaimIssuer;
import io.github.qorechain.assetkit.proto.identity.v1.MsgAddClaim;
import io.github.qorechain.assetkit.proto.identity.v1.MsgRegisterIdentity;
import io.github.qorechain.assetkit.proto.identity.v1.MsgSetClaimIssuer;
import io.github.qorechain.assetkit.proto.identity.v1.QueryIsVerifiedRequest;
import io.github.qorechain.assetkit.proto.settlement.v1.Instruction;
import io.github.qorechain.assetkit.proto.settlement.v1.InstructionStatus;
import io.github.qorechain.assetkit.proto.settlement.v1.Leg;
import io.github.qorechain.assetkit.proto.settlement.v1.MsgAffirm;
import io.github.qorechain.assetkit.proto.settlement.v1.MsgCreateInstruction;
import io.github.qorechain.assetkit.proto.settlement.v1.MsgExecuteInstruction;
import io.github.qorechain.assetkit.proto.settlement.v1.QueryInstructionRequest;
import io.github.qorechain.assetkit.proto.settlement.v1.SettlementType;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

class MockChainTest {
    static final String ISSUER = "qor1issuer";
    static final String AGENT = "qor1agent";
    static final String ALICE = "qor1alice";
    static final String BOB = "qor1bob";
    static final String CAROL = "qor1carol";
    static final String KYC = "qor1kycprovider";
    static final String BOND = "bond-2030";
    static final ByteString HASH = ByteString.copyFrom(new byte[32]);

    static MockChainError rejectsWith(String code, Executable call) {
        MockChainError e = assertThrows(MockChainError.class, call, "expected " + code);
        assertEquals(code, e.code(), e.getMessage());
        return e;
    }

    static void bond(MockChain chain, RwaFlagsV0.Builder flags, String maxSupply) {
        chain.asset().createAsset(MsgCreateAsset.newBuilder()
                .setIssuer(ISSUER).setAssetId(BOND).setName("Example 2030 Bond").setSymbol("EB30").setDecimals(0)
                .setFlags(flags.setFreezable(true).setPausable(true)).setMaxSupply(maxSupply).build());
        chain.asset().setRole(MsgSetRole.newBuilder()
                .setIssuer(ISSUER).setAssetId(BOND).setAddress(AGENT).setRole(Role.ROLE_AGENT).setGranted(true).build());
    }

    static void bond(MockChain chain) {
        bond(chain, RwaFlagsV0.newBuilder(), "");
    }

    static HolderState holder(MockChain chain, String address) {
        return chain.asset().holder(QueryHolderRequest.newBuilder().setAssetId(BOND).setAddress(address).build()).getHolder();
    }

    static String balance(MockChain chain, String address) {
        return holder(chain, address).getBalance();
    }

    static MsgMint mint(String to, String amount) {
        return MsgMint.newBuilder().setAgent(AGENT).setAssetId(BOND).setTo(to).setAmount(amount).build();
    }

    static MsgTransfer transfer(String from, String to, String amount) {
        return MsgTransfer.newBuilder().setFrom(from).setAssetId(BOND).setTo(to).setAmount(amount).build();
    }

    static MsgFreeze freeze(String holder, boolean frozen) {
        return MsgFreeze.newBuilder().setAgent(AGENT).setAssetId(BOND).setHolder(holder).setFrozen(frozen).build();
    }

    static io.github.qorechain.assetkit.proto.asset.v1.Asset asset(MockChain chain) {
        return chain.asset().asset(QueryAssetRequest.newBuilder().setAssetId(BOND).build()).getAsset();
    }

    @Nested
    class Issuance {
        MockChain chain;

        @BeforeEach
        void setUp() {
            chain = new MockChain();
            bond(chain, RwaFlagsV0.newBuilder().setSupplyCap(true), "1000");
        }

        @Test
        void createsMintsAndTransfers() {
            chain.asset().mint(mint(ALICE, "600"));
            chain.asset().transfer(transfer(ALICE, BOB, "100"));
            assertEquals("500", balance(chain, ALICE));
            assertEquals("100", balance(chain, BOB));
            assertEquals("600", asset(chain).getTotalSupply());
            assertEquals(AssetStatus.ASSET_STATUS_ACTIVE, asset(chain).getStatus());
            assertEquals(1, chain.events("qorechain.asset.v1.EventMinted").size());
        }

        @Test
        void enforcesTheSupplyCap() {
            chain.asset().mint(mint(ALICE, "1000"));
            rejectsWith("ERROR_CODE_SUPPLY_CAP_EXCEEDED", () -> chain.asset().mint(mint(ALICE, "1")));
        }

        @Test
        void refusesMintingByANonAgent() {
            rejectsWith("ERROR_CODE_UNAUTHORIZED_ROLE", () -> chain.asset().mint(mint(BOB, "1").toBuilder().setAgent(BOB).build()));
        }

        @Test
        void refusesAnInvalidAmountAndADuplicateAsset() {
            rejectsWith("ERROR_CODE_INVALID_AMOUNT", () -> chain.asset().mint(mint(ALICE, "-5")));
            rejectsWith("ERROR_CODE_ASSET_EXISTS", () -> chain.asset().createAsset(
                    MsgCreateAsset.newBuilder().setIssuer(ISSUER).setAssetId(BOND).build()));
        }

        @Test
        void onlyRelaxesFlags() {
            rejectsWith("ERROR_CODE_FLAG_IMMUTABLE", () -> chain.asset().updateFlags(MsgUpdateFlags.newBuilder()
                    .setIssuer(ISSUER).setAssetId(BOND)
                    .setFlags(RwaFlagsV0.newBuilder().setFreezable(true).setPausable(true).setSupplyCap(false)).build()));
            chain.asset().updateFlags(MsgUpdateFlags.newBuilder().setIssuer(ISSUER).setAssetId(BOND)
                    .setFlags(RwaFlagsV0.newBuilder().setFreezable(true).setPausable(false).setSupplyCap(true)).build());
            rejectsWith("ERROR_CODE_FLAG_NOT_ENABLED", () -> chain.asset().pause(
                    MsgPause.newBuilder().setAgent(AGENT).setAssetId(BOND).setPaused(true).build()));
        }

        @Test
        void requiresAuthorizationWhenRequireAuthIsSet() {
            MockChain c = new MockChain();
            c.asset().createAsset(MsgCreateAsset.newBuilder().setIssuer(ISSUER).setAssetId("fund-a")
                    .setFlags(RwaFlagsV0.newBuilder().setRequireAuth(true)).build());
            MsgMint m = MsgMint.newBuilder().setAgent(ISSUER).setAssetId("fund-a").setTo(ALICE).setAmount("5").build();
            rejectsWith("ERROR_CODE_HOLDER_NOT_AUTHORIZED", () -> c.asset().mint(m));
            c.asset().authorizeHolder(MsgAuthorizeHolder.newBuilder()
                    .setAgent(ISSUER).setAssetId("fund-a").setHolder(ALICE).setAuthorized(true).build());
            c.asset().mint(m);
            rejectsWith("ERROR_CODE_HOLDER_NOT_AUTHORIZED", () -> c.asset().transfer(
                    MsgTransfer.newBuilder().setFrom(ALICE).setAssetId("fund-a").setTo(BOB).setAmount("1").build()));
        }

        @Test
        void requiresAHybridKeyWithProofOfPossession() {
            MockChain c = new MockChain();
            MsgCreateAsset create = MsgCreateAsset.newBuilder().setIssuer(ISSUER).setAssetId("pq-note")
                    .setFlags(RwaFlagsV0.newBuilder().setRequireHybridSignature(true)).build();
            rejectsWith("ERROR_CODE_HYBRID_SIGNATURE_REQUIRED", () -> c.asset().createAsset(create));
            c.setHybridKey(ISSUER, true, true);
            c.asset().createAsset(create);
            c.setHybridKey(ALICE, true, false);
            MsgMint m = MsgMint.newBuilder().setAgent(ISSUER).setAssetId("pq-note").setTo(ALICE).setAmount("1").build();
            rejectsWith("ERROR_CODE_HYBRID_SIGNATURE_REQUIRED", () -> c.asset().mint(m));
            c.setHybridKey(ALICE, true, true);
            c.asset().mint(m);
        }

        @Test
        void blocksHolderTransfersOfANonTransferableAssetButAllowsClawback() {
            MockChain c = new MockChain();
            c.asset().createAsset(MsgCreateAsset.newBuilder().setIssuer(ISSUER).setAssetId("membership")
                    .setFlags(RwaFlagsV0.newBuilder().setNonTransferable(true).setFreezable(true)).build());
            c.asset().mint(MsgMint.newBuilder().setAgent(ISSUER).setAssetId("membership").setTo(ALICE).setAmount("1").build());
            rejectsWith("ERROR_CODE_NON_TRANSFERABLE", () -> c.asset().transfer(
                    MsgTransfer.newBuilder().setFrom(ALICE).setAssetId("membership").setTo(BOB).setAmount("1").build()));
            c.asset().clawback(MsgClawback.newBuilder().setAgent(ISSUER).setAssetId("membership")
                    .setFrom(ALICE).setAmount("1").setReason("membership ended").build());
        }
    }

    @Nested
    class Controls {
        MockChain chain;

        @BeforeEach
        void setUp() {
            chain = new MockChain();
            bond(chain);
            chain.asset().mint(mint(ALICE, "100"));
        }

        @Test
        void freezesAndUnfreezesAnAddress() {
            chain.asset().freeze(freeze(ALICE, true));
            rejectsWith("ERROR_CODE_ADDRESS_FROZEN", () -> chain.asset().transfer(transfer(ALICE, BOB, "1")));
            rejectsWith("ERROR_CODE_ADDRESS_FROZEN", () -> chain.asset().mint(mint(ALICE, "1")));
            QueryCanTransferResponse q = chain.asset().canTransfer(QueryCanTransferRequest.newBuilder()
                    .setAssetId(BOND).setFrom(ALICE).setTo(BOB).setAmount("1").build());
            assertFalse(q.getAllowed());
            assertEquals(io.github.qorechain.assetkit.proto.asset.v1.ErrorCode.ERROR_CODE_ADDRESS_FROZEN, q.getCode());
            chain.asset().freeze(freeze(ALICE, false));
            chain.asset().transfer(transfer(ALICE, BOB, "1"));
        }

        @Test
        void freezesPartOfABalance() {
            chain.asset().freezePartial(MsgFreezePartial.newBuilder()
                    .setAgent(AGENT).setAssetId(BOND).setHolder(ALICE).setFrozenAmount("70").build());
            rejectsWith("ERROR_CODE_INSUFFICIENT_UNFROZEN_BALANCE", () -> chain.asset().transfer(transfer(ALICE, BOB, "31")));
            chain.asset().transfer(transfer(ALICE, BOB, "30"));
        }

        @Test
        void pausesTransfersButNotIssuance() {
            chain.asset().pause(MsgPause.newBuilder().setAgent(AGENT).setAssetId(BOND).setPaused(true).build());
            rejectsWith("ERROR_CODE_ASSET_PAUSED", () -> chain.asset().transfer(transfer(ALICE, BOB, "1")));
            chain.asset().mint(mint(BOB, "1"));
            chain.asset().pause(MsgPause.newBuilder().setAgent(AGENT).setAssetId(BOND).setPaused(false).build());
            chain.asset().transfer(transfer(ALICE, BOB, "1"));
        }

        @Test
        void clawsBackToTheIssuerIgnoringTheFreeze() {
            chain.asset().freezePartial(MsgFreezePartial.newBuilder()
                    .setAgent(AGENT).setAssetId(BOND).setHolder(ALICE).setFrozenAmount("100").build());
            chain.asset().freeze(freeze(ALICE, true));
            chain.asset().clawback(MsgClawback.newBuilder().setAgent(AGENT).setAssetId(BOND)
                    .setFrom(ALICE).setAmount("40").setReason("court order 12/2026").build());
            HolderState h = holder(chain, ALICE);
            assertEquals("60", h.getBalance());
            assertEquals("60", h.getFrozenAmount());
            assertEquals("40", balance(chain, ISSUER));
            EventClawback ev = (EventClawback) chain.events("qorechain.asset.v1.EventClawback").get(0).data();
            assertEquals("court order 12/2026", ev.getReason());
        }

        @Test
        void forceTransfersFromAFrozenAddressToARecoveryWallet() {
            chain.asset().freeze(freeze(ALICE, true));
            chain.asset().forceTransfer(MsgForceTransfer.newBuilder().setAgent(AGENT).setAssetId(BOND)
                    .setFrom(ALICE).setTo(CAROL).setAmount("100").setReason("lost key").build());
            assertEquals("100", balance(chain, CAROL));
            chain.asset().freeze(freeze(BOB, true));
            rejectsWith("ERROR_CODE_ADDRESS_FROZEN", () -> chain.asset().forceTransfer(MsgForceTransfer.newBuilder()
                    .setAgent(AGENT).setAssetId(BOND).setFrom(CAROL).setTo(BOB).setAmount("1").setReason("x").build()));
        }

        @Test
        void movesTheIssuerRoleInTwoSteps() {
            chain.asset().proposeIssuer(MsgProposeIssuer.newBuilder().setIssuer(ISSUER).setAssetId(BOND).setNewIssuer(CAROL).build());
            rejectsWith("ERROR_CODE_UNAUTHORIZED_ROLE", () -> chain.asset().acceptIssuer(
                    MsgAcceptIssuer.newBuilder().setNewIssuer(BOB).setAssetId(BOND).build()));
            chain.asset().acceptIssuer(MsgAcceptIssuer.newBuilder().setNewIssuer(CAROL).setAssetId(BOND).build());
            assertEquals(CAROL, asset(chain).getIssuer());
            List<RoleGrant> roles = chain.asset().roles(QueryRolesRequest.newBuilder().setAssetId(BOND).build()).getRolesList();
            assertEquals(CAROL, roles.stream().filter(r -> r.getRole() == Role.ROLE_ISSUER).findFirst().orElseThrow().getAddress());
        }

        @Test
        void retiresNoTransferBurnStillAllowed() {
            chain.asset().retire(MsgRetire.newBuilder().setIssuer(ISSUER).setAssetId(BOND).build());
            rejectsWith("ERROR_CODE_ASSET_RETIRED", () -> chain.asset().transfer(transfer(ALICE, BOB, "1")));
            chain.asset().burn(MsgBurn.newBuilder().setAgent(AGENT).setAssetId(BOND).setFrom(ALICE).setAmount("100").build());
            assertEquals("0", asset(chain).getTotalSupply());
        }
    }

    @Nested
    class IdentityAndCompliance {
        MockChain chain;

        MsgBindModule bind(String moduleId, int version, String params) {
            return MsgBindModule.newBuilder().setIssuer(ISSUER).setAssetId(BOND).setModuleId(moduleId)
                    .setVersion(version).setParamsJson(params).build();
        }

        void registerVerified(String id, String address, int country) {
            chain.identity().registerIdentity(MsgRegisterIdentity.newBuilder()
                    .setAgent(KYC).setIdentityId(id).setAddress(address).setCountry(country).build());
            chain.identity().addClaim(MsgAddClaim.newBuilder()
                    .setClaimIssuer(KYC).setIdentityId(id).setTopic(1).setDataHash(HASH).setValidUntil(0).build());
        }

        @BeforeEach
        void setUp() {
            chain = new MockChain(new MockChain.Options().identityAgents(List.of(KYC)));
            bond(chain);
            chain.identity().setClaimIssuer(MsgSetClaimIssuer.newBuilder().setAuthority("authority")
                    .setClaimIssuer(ClaimIssuer.newBuilder().setAddress(KYC).setName("KYC provider").addTopics(1)).build());
            registerVerified("id-alice", ALICE, 756);
            registerVerified("id-bob", BOB, 408);
            chain.compliance().bindModule(bind("identity-verified", 1, "{\"topics\":[1]}"));
            chain.compliance().bindModule(bind("country-blocklist", 1, "{\"countries\":[408]}"));
        }

        @Test
        void rejectsAMintToAnUnverifiedAddress() {
            MockChainError e = rejectsWith("ERROR_CODE_COMPLIANCE_REJECTED", () -> chain.asset().mint(mint(CAROL, "1")));
            assertTrue(e.getMessage().contains("identity-verified"));
        }

        @Test
        void rejectsATransferToABlockedCountryAndReportsTheModule() {
            chain.asset().mint(mint(ALICE, "10"));
            rejectsWith("ERROR_CODE_COMPLIANCE_REJECTED", () -> chain.asset().transfer(transfer(ALICE, BOB, "1")));
            QueryCanTransferResponse q = chain.asset().canTransfer(QueryCanTransferRequest.newBuilder()
                    .setAssetId(BOND).setFrom(ALICE).setTo(BOB).setAmount("1").build());
            assertFalse(q.getAllowed());
            assertEquals(io.github.qorechain.assetkit.proto.asset.v1.ErrorCode.ERROR_CODE_COMPLIANCE_REJECTED, q.getCode());
            assertEquals("country-blocklist", q.getComplianceModuleId());
            QueryCheckResponse check = chain.compliance().check(QueryCheckRequest.newBuilder()
                    .setAssetId(BOND).setFrom(ALICE).setTo(BOB).setAmount("1").build());
            assertFalse(check.getAllowed());
            assertEquals("country-blocklist", check.getModuleId());
            assertEquals(1, check.getVersion());
        }

        @Test
        void distrustingTheClaimIssuerUnverifiesTheHolder() {
            chain.asset().mint(mint(ALICE, "1"));
            chain.identity().setClaimIssuer(MsgSetClaimIssuer.newBuilder().setAuthority("authority")
                    .setClaimIssuer(ClaimIssuer.newBuilder().setAddress(KYC).addTopics(1)).setRemove(true).build());
            assertFalse(chain.identity().isVerified(QueryIsVerifiedRequest.newBuilder()
                    .setAddress(ALICE).addTopics(1).build()).getVerified());
            rejectsWith("ERROR_CODE_COMPLIANCE_REJECTED", () -> chain.asset().mint(mint(ALICE, "1")));
        }

        @Test
        void disablingAModuleVersionFailsClosedUntilTheBindingMigrates() {
            chain.asset().mint(mint(ALICE, "10"));
            chain.compliance().registerModule(MsgRegisterModule.newBuilder().setAuthority("authority")
                    .setModule(ComplianceModule.newBuilder().setModuleId("country-blocklist").setVersion(2)
                            .setRuntime(ModuleRuntime.MODULE_RUNTIME_NATIVE)).build());
            chain.compliance().setModuleStatus(MsgSetModuleStatus.newBuilder().setAuthority("authority")
                    .setModuleId("country-blocklist").setVersion(1).setStatus(ModuleStatus.MODULE_STATUS_DISABLED).build());
            rejectsWith("ERROR_CODE_COMPLIANCE_REJECTED", () -> chain.asset().mint(mint(ALICE, "1")));
            chain.compliance().migrateBinding(MsgMigrateBinding.newBuilder().setIssuer(ISSUER).setAssetId(BOND)
                    .setModuleId("country-blocklist").setToVersion(2).build());
            chain.asset().mint(mint(ALICE, "1"));
            rejectsWith("ERROR_CODE_INVALID_PARAMS", () -> chain.compliance().bindModule(bind("max-holders", 1, "{\"max\":0}")));
        }

        @Test
        void capsTheNumberOfHolders() {
            chain.compliance().unbindModule(MsgUnbindModule.newBuilder().setIssuer(ISSUER).setAssetId(BOND)
                    .setModuleId("country-blocklist").build());
            chain.compliance().bindModule(bind("max-holders", 1, "{\"max\":1}"));
            chain.asset().mint(mint(ALICE, "10"));
            rejectsWith("ERROR_CODE_COMPLIANCE_REJECTED", () -> chain.asset().transfer(transfer(ALICE, BOB, "1")));
            chain.asset().transfer(transfer(ALICE, BOB, "10"));
        }

        @Test
        void runsCustomModuleLogicSuppliedByTheApplication() {
            chain.compliance().registerModule(MsgRegisterModule.newBuilder().setAuthority("authority")
                    .setModule(ComplianceModule.newBuilder().setModuleId("lockup").setVersion(1)
                            .setRuntime(ModuleRuntime.MODULE_RUNTIME_WASM).setCodeRef("qor1lockupcontract")).build());
            chain.defineModuleLogic("lockup", ctx -> !ctx.from().isEmpty() && ctx.chain().time() < 1_767_225_600L + 86400
                    ? Optional.of("lock-up until day 1") : Optional.empty());
            chain.compliance().bindModule(bind("lockup", 1, "{}"));
            chain.asset().mint(mint(ALICE, "10"));
            registerVerified("id-carol", CAROL, 756);
            rejectsWith("ERROR_CODE_COMPLIANCE_REJECTED", () -> chain.asset().transfer(transfer(ALICE, CAROL, "1")));
            chain.advance(10, 86400);
            chain.asset().transfer(transfer(ALICE, CAROL, "1"));
        }
    }

    @Nested
    class Settlement {
        MockChain chain;

        List<Leg> legs(String cash) {
            return List.of(
                    Leg.newBuilder().setFrom(ALICE).setTo(BOB).setDenom("asset/" + BOND).setAmount("10").build(),
                    Leg.newBuilder().setFrom(BOB).setTo(ALICE).setDenom("uqor").setAmount(cash).build());
        }

        MsgCreateInstruction.Builder create(String creator, String cash) {
            return MsgCreateInstruction.newBuilder().setCreator(creator).addAllLegs(legs(cash)).setDeadline(chain.time() + 3600);
        }

        Instruction instruction(long id) {
            return chain.settlement().instruction(QueryInstructionRequest.newBuilder().setId(id).build()).getInstruction();
        }

        MsgAffirm affirm(String party, long id) {
            return MsgAffirm.newBuilder().setParty(party).setId(id).build();
        }

        @BeforeEach
        void setUp() {
            chain = new MockChain();
            bond(chain);
            chain.asset().mint(mint(ALICE, "10"));
            chain.fundBank(BOB, "uqor", "1000");
        }

        @Test
        void settlesBothLegsAfterBilateralAffirmation() {
            long id = chain.settlement().createInstruction(create(ALICE, "1000").build()).getId();
            assertEquals(InstructionStatus.INSTRUCTION_STATUS_PENDING, instruction(id).getStatus());
            assertTrue(chain.settlement().affirm(affirm(BOB, id)).getExecuted());
            assertEquals("10", balance(chain, BOB));
            assertEquals("1000", chain.bankBalance(ALICE, "uqor"));
        }

        @Test
        void allOrNothingAFailingCashLegMovesNoAsset() {
            long id = chain.settlement().createInstruction(create(ALICE, "1001").build()).getId();
            assertFalse(chain.settlement().affirm(affirm(BOB, id)).getExecuted());
            Instruction ins = instruction(id);
            assertEquals(InstructionStatus.INSTRUCTION_STATUS_FAILED, ins.getStatus());
            assertTrue(ins.getFailureReason().contains("leg 1"));
            assertEquals("10", balance(chain, ALICE));
            assertEquals("0", balance(chain, BOB));
            assertEquals("1000", chain.bankBalance(BOB, "uqor"));
            assertEquals(0, chain.events("qorechain.asset.v1.EventTransferred").size());
            chain.fundBank(BOB, "uqor", "1");
            assertEquals(InstructionStatus.INSTRUCTION_STATUS_EXECUTED, chain.settlement().executeInstruction(
                    MsgExecuteInstruction.newBuilder().setSigner(BOB).setId(id).build()).getStatus());
        }

        @Test
        void allOrNothingAFrozenSellerFailsTheAssetLeg() {
            chain.asset().freeze(freeze(ALICE, true));
            long id = chain.settlement().createInstruction(create(BOB, "1000")
                    .setSettlementType(SettlementType.SETTLEMENT_TYPE_MANUAL).build()).getId();
            rejectsWith("ERROR_CODE_NOT_FULLY_AFFIRMED", () -> chain.settlement().executeInstruction(
                    MsgExecuteInstruction.newBuilder().setSigner(BOB).setId(id).build()));
            chain.settlement().affirm(affirm(ALICE, id));
            assertEquals(InstructionStatus.INSTRUCTION_STATUS_FAILED, chain.settlement().executeInstruction(
                    MsgExecuteInstruction.newBuilder().setSigner(ALICE).setId(id).build()).getStatus());
            assertEquals("1000", chain.bankBalance(BOB, "uqor"));
            assertTrue(instruction(id).getFailureReason().contains("ERROR_CODE_ADDRESS_FROZEN"));
        }

        @Test
        void expiresAfterTheDeadlineAndRefusesNonParties() {
            long id = chain.settlement().createInstruction(create(ALICE, "1000").setDeadline(chain.time() + 60).build()).getId();
            rejectsWith("ERROR_CODE_NOT_A_PARTY", () -> chain.settlement().affirm(affirm(CAROL, id)));
            chain.advance(100, 61);
            assertEquals(InstructionStatus.INSTRUCTION_STATUS_EXPIRED, instruction(id).getStatus());
            rejectsWith("ERROR_CODE_INVALID_STATUS", () -> chain.settlement().affirm(affirm(BOB, id)));
        }

        @Test
        void settlesOnBlockAtTheSettleHeight() {
            long id = chain.settlement().createInstruction(create(ALICE, "1000")
                    .setSettlementType(SettlementType.SETTLEMENT_TYPE_ON_BLOCK).setSettleHeight(chain.height() + 5).build()).getId();
            chain.settlement().affirm(affirm(BOB, id));
            assertEquals(InstructionStatus.INSTRUCTION_STATUS_AFFIRMED, instruction(id).getStatus());
            chain.advance(5, 5);
            assertEquals(InstructionStatus.INSTRUCTION_STATUS_EXECUTED, instruction(id).getStatus());
        }
    }

    @Nested
    class Attestations {
        static final String ADMIN = "qor1fundadmin";
        static final AttestationKind NAV = AttestationKind.ATTESTATION_KIND_NAV;
        MockChain chain;

        MsgSubmit.Builder submit(String attester, AttestationKind kind, long observedAt, long validFor) {
            return MsgSubmit.newBuilder().setAttester(attester).setAssetId(BOND).setKind(kind).setValue("1")
                    .setObservedAt(observedAt).setValidForSeconds(validFor);
        }

        QueryLatestResponse latest() {
            return chain.attest().latest(QueryLatestRequest.newBuilder().setAssetId(BOND).setKind(NAV).build());
        }

        @BeforeEach
        void setUp() {
            chain = new MockChain();
            bond(chain);
            chain.attest().setAttester(MsgSetAttester.newBuilder().setIssuer(ISSUER).setAttester(
                    Attester.newBuilder().setAssetId(BOND).setAddress(ADMIN).addKinds(NAV).setName("Fund admin")).build());
        }

        @Test
        void isFreshThenStaleAndCanGateTransfers() {
            assertEquals(Freshness.FRESHNESS_MISSING, latest().getFreshness());
            chain.attest().submit(submit(ADMIN, NAV, chain.time() - 60, 86400).setValue("101.25").setUnit("CHF").build());
            QueryLatestResponse fresh = latest();
            assertEquals(Freshness.FRESHNESS_FRESH, fresh.getFreshness());
            assertEquals("101.25", fresh.getAttestation().getValue());

            chain.compliance().bindModule(MsgBindModule.newBuilder().setIssuer(ISSUER).setAssetId(BOND)
                    .setModuleId("attestation-fresh").setVersion(1).setParamsJson("{\"kind\":\"ATTESTATION_KIND_NAV\"}").build());
            chain.asset().mint(mint(ALICE, "5"));
            chain.advance(1000, 86400);
            assertEquals(Freshness.FRESHNESS_STALE, latest().getFreshness());
            rejectsWith("ERROR_CODE_COMPLIANCE_REJECTED", () -> chain.asset().transfer(transfer(ALICE, BOB, "1")));
        }

        @Test
        void refusesUnknownAttestersFutureObservationsAndOlderStatements() {
            long now = chain.time();
            rejectsWith("ERROR_CODE_NOT_AN_ATTESTER", () -> chain.attest().submit(submit(BOB, NAV, now, 60).build()));
            rejectsWith("ERROR_CODE_OBSERVATION_IN_FUTURE", () -> chain.attest().submit(submit(ADMIN, NAV, now + 1, 60).build()));
            chain.attest().submit(submit(ADMIN, NAV, now, 60).build());
            rejectsWith("ERROR_CODE_OLDER_THAN_LATEST", () -> chain.attest().submit(submit(ADMIN, NAV, now - 10, 60).build()));
            rejectsWith("ERROR_CODE_KIND_NOT_ALLOWED", () -> chain.attest().submit(
                    submit(ADMIN, AttestationKind.ATTESTATION_KIND_RESERVES, now, 60).build()));
        }
    }
}

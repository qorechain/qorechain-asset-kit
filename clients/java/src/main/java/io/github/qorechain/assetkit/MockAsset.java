// SPDX-License-Identifier: Apache-2.0
package io.github.qorechain.assetkit;

import static io.github.qorechain.assetkit.MockChain.fail;
import static io.github.qorechain.assetkit.MockChain.parseAmount;

import io.github.qorechain.assetkit.proto.asset.v1.*;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

/** x/asset in {@link MockChain}. */
final class MockAsset implements AssetApi {
    private static final String M = "x/asset";
    private static final Pattern ASSET_ID = Pattern.compile("^[a-z][a-z0-9-]{2,31}$");

    static final class Holder {
        BigInteger balance = BigInteger.ZERO;
        boolean authorized;
        boolean frozen;
        BigInteger frozenAmount = BigInteger.ZERO;

        Holder copy() {
            Holder h = new Holder();
            h.balance = balance;
            h.authorized = authorized;
            h.frozen = frozen;
            h.frozenAmount = frozenAmount;
            return h;
        }
    }

    static final class Rec {
        final Asset.Builder asset;
        /** address -> role number -> granted height. */
        final Map<String, Map<Integer, Long>> roles = new LinkedHashMap<>();
        Map<String, Holder> holders = new LinkedHashMap<>();

        Rec(Asset.Builder asset) {
            this.asset = asset;
        }
    }

    /** A refused check: error code, optional compliance module id, reason. */
    record Refusal(String code, String moduleId, String reason) {
        String message() {
            return moduleId == null ? reason : moduleId + ": " + reason;
        }
    }

    private final MockChain chain;
    final Params params = Params.newBuilder().setCreationFee("0").setMaxAgents(10).setMaxComplianceModules(10).build();
    final Map<String, Rec> assets = new LinkedHashMap<>();

    MockAsset(MockChain chain) {
        this.chain = chain;
    }

    // ------------------------------------------------------------------ helpers

    Rec rec(String assetId) {
        Rec r = assets.get(assetId);
        if (r == null) {
            throw fail(M, "ERROR_CODE_ASSET_NOT_FOUND", "asset " + assetId + " not found");
        }
        return r;
    }

    static RwaFlagsV0 flags(Rec r) {
        return r.asset.getFlags();
    }

    Holder holderOf(Rec r, String address) {
        return r.holders.computeIfAbsent(address, a -> new Holder());
    }

    Holder peekHolder(Rec r, String address) {
        Holder h = r.holders.get(address);
        return h == null ? new Holder() : h;
    }

    boolean hasRole(Rec r, String address, Role role) {
        Map<Integer, Long> m = r.roles.get(address);
        return m != null && m.containsKey(role.getNumber());
    }

    private void requireIssuer(Rec r, String signer) {
        if (!r.asset.getIssuer().equals(signer)) {
            throw fail(M, "ERROR_CODE_UNAUTHORIZED_ROLE", signer + " is not the issuer of " + r.asset.getAssetId());
        }
        requireSignerKey(r, signer);
    }

    private void requireAgent(Rec r, String signer) {
        if (!r.asset.getIssuer().equals(signer) && !hasRole(r, signer, Role.ROLE_AGENT)) {
            throw fail(M, "ERROR_CODE_UNAUTHORIZED_ROLE", signer + " is not an agent of " + r.asset.getAssetId());
        }
        requireSignerKey(r, signer);
    }

    private void requireSignerKey(Rec r, String signer) {
        if (flags(r).getRequireHybridSignature() && !chain.hasHybridKey(signer)) {
            throw fail(M, "ERROR_CODE_HYBRID_SIGNATURE_REQUIRED", signer + " has no registered ML-DSA-87 key with proof of possession");
        }
    }

    private void requireFreezable(Rec r) {
        if (!flags(r).getFreezable()) {
            throw fail(M, "ERROR_CODE_FLAG_NOT_ENABLED", "freezable is not set");
        }
    }

    private static String noKey(String who) {
        return who + " has no registered ML-DSA-87 key with proof of possession";
    }

    /** Checks on a receiving address shared by mint, transfer and forced transfer. */
    Refusal receiverRefusal(Rec r, String to) {
        RwaFlagsV0 f = flags(r);
        Holder h = peekHolder(r, to);
        if (h.frozen) {
            return new Refusal("ERROR_CODE_ADDRESS_FROZEN", null, to + " is frozen");
        }
        if (f.getRequireAuth() && !h.authorized) {
            return new Refusal("ERROR_CODE_HOLDER_NOT_AUTHORIZED", null, to + " is not authorized");
        }
        if (f.getRequireHybridSignature() && !chain.hasHybridKey(to)) {
            return new Refusal("ERROR_CODE_HYBRID_SIGNATURE_REQUIRED", null, noKey(to));
        }
        return null;
    }

    Refusal complianceRefusal(String assetId, String from, String to, BigInteger amount) {
        MockCompliance.Rejection c = chain.compliance.run(assetId, from, to, amount);
        return c == null ? null : new Refusal("ERROR_CODE_COMPLIANCE_REJECTED", c.moduleId(), c.reason());
    }

    /** The ordered checks of docs/proposal.md section 4.1, without the amount parse. */
    Refusal transferRefusal(Rec r, String from, String to, BigInteger amount) {
        RwaFlagsV0 f = flags(r);
        AssetStatus st = r.asset.getStatus();
        if (st == AssetStatus.ASSET_STATUS_RETIRED) {
            return new Refusal("ERROR_CODE_ASSET_RETIRED", null, "asset is retired");
        }
        if (st == AssetStatus.ASSET_STATUS_PAUSED) {
            return new Refusal("ERROR_CODE_ASSET_PAUSED", null, "asset is paused");
        }
        if (f.getNonTransferable()) {
            return new Refusal("ERROR_CODE_NON_TRANSFERABLE", null, "asset is non-transferable");
        }
        Holder hf = peekHolder(r, from);
        Holder ht = peekHolder(r, to);
        if (hf.frozen || ht.frozen) {
            return new Refusal("ERROR_CODE_ADDRESS_FROZEN", null, (hf.frozen ? from : to) + " is frozen");
        }
        if (f.getRequireAuth() && (!hf.authorized || !ht.authorized)) {
            return new Refusal("ERROR_CODE_HOLDER_NOT_AUTHORIZED", null, (!hf.authorized ? from : to) + " is not authorized");
        }
        if (f.getRequireHybridSignature() && (!chain.hasHybridKey(from) || !chain.hasHybridKey(to))) {
            String who = !chain.hasHybridKey(from) ? from : to;
            return new Refusal("ERROR_CODE_HYBRID_SIGNATURE_REQUIRED", null, noKey(who));
        }
        if (hf.balance.compareTo(amount) < 0) {
            return new Refusal("ERROR_CODE_INSUFFICIENT_BALANCE", null, from + " balance is too low");
        }
        if (hf.balance.subtract(hf.frozenAmount).compareTo(amount) < 0) {
            return new Refusal("ERROR_CODE_INSUFFICIENT_UNFROZEN_BALANCE", null, from + " unfrozen balance is too low");
        }
        return complianceRefusal(r.asset.getAssetId(), from, to, amount);
    }

    void move(Rec r, String from, String to, BigInteger amount) {
        Holder hf = holderOf(r, from);
        hf.balance = hf.balance.subtract(amount);
        if (hf.frozenAmount.compareTo(hf.balance) > 0) {
            hf.frozenAmount = hf.balance;
        }
        Holder ht = holderOf(r, to);
        ht.balance = ht.balance.add(amount);
    }

    Runnable snapshotHolders() {
        Map<String, Map<String, Holder>> copy = new LinkedHashMap<>();
        assets.forEach((id, r) -> {
            Map<String, Holder> m = new LinkedHashMap<>();
            r.holders.forEach((a, h) -> m.put(a, h.copy()));
            copy.put(id, m);
        });
        return () -> assets.forEach((id, r) -> r.holders = copy.getOrDefault(id, new LinkedHashMap<>()));
    }

    // ----------------------------------------------------------------- messages

    @Override
    public MsgCreateAssetResponse createAsset(MsgCreateAsset m) {
        if (!ASSET_ID.matcher(m.getAssetId()).matches()) {
            throw fail(M, "ERROR_CODE_INVALID_ASSET_ID", "invalid asset id \"" + m.getAssetId() + "\"");
        }
        if (assets.containsKey(m.getAssetId())) {
            throw fail(M, "ERROR_CODE_ASSET_EXISTS", "asset " + m.getAssetId() + " exists");
        }
        RwaFlagsV0 flags = m.getFlags();
        String maxSupply = "";
        if (flags.getSupplyCap()) {
            maxSupply = parseAmount(M, m.getMaxSupply(), false).toString();
        }
        if (flags.getRequireHybridSignature() && !chain.hasHybridKey(m.getIssuer())) {
            throw fail(M, "ERROR_CODE_HYBRID_SIGNATURE_REQUIRED", noKey(m.getIssuer()));
        }
        Asset.Builder a = Asset.newBuilder()
                .setAssetId(m.getAssetId())
                .setIssuer(m.getIssuer())
                .setName(m.getName())
                .setSymbol(m.getSymbol())
                .setDecimals(m.getDecimals())
                .setFlags(flags)
                .setMaxSupply(maxSupply)
                .setTotalSupply("0")
                .setStatus(AssetStatus.ASSET_STATUS_ACTIVE)
                .setTermsHash(m.getTermsHash())
                .setTermsUri(m.getTermsUri())
                .setCreatedHeight(chain.height);
        Rec r = new Rec(a);
        Map<Integer, Long> roles = new LinkedHashMap<>();
        roles.put(Role.ROLE_ISSUER_VALUE, chain.height);
        r.roles.put(m.getIssuer(), roles);
        assets.put(m.getAssetId(), r);
        chain.emit("qorechain.asset.v1.EventAssetCreated", EventAssetCreated.newBuilder()
                .setAssetId(m.getAssetId()).setIssuer(m.getIssuer()).setFlags(flags).setMaxSupply(maxSupply).build());
        return MsgCreateAssetResponse.newBuilder().setDenom("asset/" + m.getAssetId()).build();
    }

    @Override
    public MsgUpdateFlagsResponse updateFlags(MsgUpdateFlags m) {
        Rec r = rec(m.getAssetId());
        requireIssuer(r, m.getIssuer());
        RwaFlagsV0 cur = flags(r);
        RwaFlagsV0 next = m.getFlags();
        if (cur.getNonTransferable() != next.getNonTransferable()) {
            throw fail(M, "ERROR_CODE_FLAG_IMMUTABLE", "nonTransferable cannot change after creation");
        }
        if (cur.getSupplyCap() != next.getSupplyCap()) {
            throw fail(M, "ERROR_CODE_FLAG_IMMUTABLE", "supplyCap cannot change after creation");
        }
        if (cur.getRequireHybridSignature() != next.getRequireHybridSignature()) {
            throw fail(M, "ERROR_CODE_FLAG_IMMUTABLE", "requireHybridSignature cannot change after creation");
        }
        if (!cur.getRequireAuth() && next.getRequireAuth()) {
            throw fail(M, "ERROR_CODE_FLAG_IMMUTABLE", "requireAuth can only be switched off");
        }
        if (!cur.getFreezable() && next.getFreezable()) {
            throw fail(M, "ERROR_CODE_FLAG_IMMUTABLE", "freezable can only be switched off");
        }
        if (!cur.getPausable() && next.getPausable()) {
            throw fail(M, "ERROR_CODE_FLAG_IMMUTABLE", "pausable can only be switched off");
        }
        r.asset.setFlags(next);
        chain.emit("qorechain.asset.v1.EventFlagsUpdated", EventFlagsUpdated.newBuilder()
                .setAssetId(m.getAssetId()).setFlags(next).build());
        return MsgUpdateFlagsResponse.getDefaultInstance();
    }

    @Override
    public MsgSetRoleResponse setRole(MsgSetRole m) {
        Rec r = rec(m.getAssetId());
        requireIssuer(r, m.getIssuer());
        if (m.getRole() != Role.ROLE_AGENT && m.getRole() != Role.ROLE_AUDITOR) {
            throw fail(M, "ERROR_CODE_UNAUTHORIZED_ROLE", "only ROLE_AGENT and ROLE_AUDITOR can be granted");
        }
        int role = m.getRoleValue();
        if (m.getGranted()) {
            if (m.getRole() == Role.ROLE_AGENT && !hasRole(r, m.getAddress(), Role.ROLE_AGENT)) {
                long agents = r.roles.values().stream().filter(x -> x.containsKey(Role.ROLE_AGENT_VALUE)).count();
                if (agents >= params.getMaxAgents()) {
                    throw fail(M, "ERROR_CODE_TOO_MANY_AGENTS", "too many agents");
                }
            }
            r.roles.computeIfAbsent(m.getAddress(), a -> new LinkedHashMap<>()).putIfAbsent(role, chain.height);
        } else {
            Map<Integer, Long> set = r.roles.get(m.getAddress());
            if (set != null) {
                set.remove(role);
            }
        }
        chain.emit("qorechain.asset.v1.EventRoleChanged", EventRoleChanged.newBuilder()
                .setAssetId(m.getAssetId()).setAddress(m.getAddress()).setRole(m.getRole()).setGranted(m.getGranted()).build());
        return MsgSetRoleResponse.getDefaultInstance();
    }

    @Override
    public MsgProposeIssuerResponse proposeIssuer(MsgProposeIssuer m) {
        Rec r = rec(m.getAssetId());
        requireIssuer(r, m.getIssuer());
        r.asset.setPendingIssuer(m.getNewIssuer());
        chain.emit("qorechain.asset.v1.EventIssuerTransferProposed", EventIssuerTransferProposed.newBuilder()
                .setAssetId(m.getAssetId()).setIssuer(m.getIssuer()).setNewIssuer(m.getNewIssuer()).build());
        return MsgProposeIssuerResponse.getDefaultInstance();
    }

    @Override
    public MsgAcceptIssuerResponse acceptIssuer(MsgAcceptIssuer m) {
        Rec r = rec(m.getAssetId());
        String pending = r.asset.getPendingIssuer();
        if (pending.isEmpty() || !pending.equals(m.getNewIssuer())) {
            throw fail(M, "ERROR_CODE_UNAUTHORIZED_ROLE", m.getNewIssuer() + " is not the pending issuer");
        }
        requireSignerKey(r, m.getNewIssuer());
        String previous = r.asset.getIssuer();
        Map<Integer, Long> old = r.roles.get(previous);
        if (old != null) {
            old.remove(Role.ROLE_ISSUER_VALUE);
        }
        r.roles.computeIfAbsent(m.getNewIssuer(), a -> new LinkedHashMap<>()).put(Role.ROLE_ISSUER_VALUE, chain.height);
        r.asset.setIssuer(m.getNewIssuer()).setPendingIssuer("");
        chain.emit("qorechain.asset.v1.EventIssuerTransferred", EventIssuerTransferred.newBuilder()
                .setAssetId(m.getAssetId()).setPreviousIssuer(previous).setNewIssuer(m.getNewIssuer()).build());
        return MsgAcceptIssuerResponse.getDefaultInstance();
    }

    @Override
    public MsgAuthorizeHolderResponse authorizeHolder(MsgAuthorizeHolder m) {
        Rec r = rec(m.getAssetId());
        requireAgent(r, m.getAgent());
        if (!flags(r).getRequireAuth()) {
            throw fail(M, "ERROR_CODE_FLAG_NOT_ENABLED", "require_auth is not set");
        }
        holderOf(r, m.getHolder()).authorized = m.getAuthorized();
        chain.emit("qorechain.asset.v1.EventHolderAuthorized", EventHolderAuthorized.newBuilder()
                .setAssetId(m.getAssetId()).setHolder(m.getHolder()).setAuthorized(m.getAuthorized()).setAgent(m.getAgent()).build());
        return MsgAuthorizeHolderResponse.getDefaultInstance();
    }

    @Override
    public MsgMintResponse mint(MsgMint m) {
        Rec r = rec(m.getAssetId());
        requireAgent(r, m.getAgent());
        BigInteger amount = parseAmount(M, m.getAmount(), false);
        if (r.asset.getStatus() == AssetStatus.ASSET_STATUS_RETIRED) {
            throw fail(M, "ERROR_CODE_ASSET_RETIRED", "asset is retired");
        }
        Refusal refusal = receiverRefusal(r, m.getTo());
        if (refusal != null) {
            throw fail(M, refusal.code(), refusal.reason());
        }
        BigInteger total = new BigInteger(r.asset.getTotalSupply()).add(amount);
        if (flags(r).getSupplyCap() && total.compareTo(new BigInteger(r.asset.getMaxSupply())) > 0) {
            throw fail(M, "ERROR_CODE_SUPPLY_CAP_EXCEEDED", "supply would exceed " + r.asset.getMaxSupply());
        }
        Refusal c = complianceRefusal(m.getAssetId(), "", m.getTo(), amount);
        if (c != null) {
            throw fail(M, c.code(), c.moduleId() + ": " + c.reason());
        }
        Holder h = holderOf(r, m.getTo());
        h.balance = h.balance.add(amount);
        r.asset.setTotalSupply(total.toString());
        chain.emit("qorechain.asset.v1.EventMinted", EventMinted.newBuilder()
                .setAssetId(m.getAssetId()).setTo(m.getTo()).setAmount(amount.toString()).setAgent(m.getAgent()).build());
        return MsgMintResponse.getDefaultInstance();
    }

    @Override
    public MsgBurnResponse burn(MsgBurn m) {
        Rec r = rec(m.getAssetId());
        requireAgent(r, m.getAgent());
        BigInteger amount = parseAmount(M, m.getAmount(), false);
        Holder h = peekHolder(r, m.getFrom());
        if (h.frozen) {
            throw fail(M, "ERROR_CODE_ADDRESS_FROZEN", m.getFrom() + " is frozen");
        }
        if (h.balance.compareTo(amount) < 0) {
            throw fail(M, "ERROR_CODE_INSUFFICIENT_BALANCE", m.getFrom() + " balance is too low");
        }
        if (h.balance.subtract(h.frozenAmount).compareTo(amount) < 0) {
            throw fail(M, "ERROR_CODE_INSUFFICIENT_UNFROZEN_BALANCE", m.getFrom() + " unfrozen balance is too low");
        }
        Holder hh = holderOf(r, m.getFrom());
        hh.balance = hh.balance.subtract(amount);
        r.asset.setTotalSupply(new BigInteger(r.asset.getTotalSupply()).subtract(amount).toString());
        chain.emit("qorechain.asset.v1.EventBurned", EventBurned.newBuilder()
                .setAssetId(m.getAssetId()).setFrom(m.getFrom()).setAmount(amount.toString()).setAgent(m.getAgent()).build());
        return MsgBurnResponse.getDefaultInstance();
    }

    @Override
    public MsgTransferResponse transfer(MsgTransfer m) {
        BigInteger amount = parseAmount(M, m.getAmount(), false);
        Rec r = rec(m.getAssetId());
        Refusal refusal = transferRefusal(r, m.getFrom(), m.getTo(), amount);
        if (refusal != null) {
            throw fail(M, refusal.code(), refusal.message());
        }
        move(r, m.getFrom(), m.getTo(), amount);
        chain.emit("qorechain.asset.v1.EventTransferred", EventTransferred.newBuilder()
                .setAssetId(m.getAssetId()).setFrom(m.getFrom()).setTo(m.getTo()).setAmount(amount.toString()).build());
        return MsgTransferResponse.getDefaultInstance();
    }

    @Override
    public MsgFreezeResponse freeze(MsgFreeze m) {
        Rec r = rec(m.getAssetId());
        requireAgent(r, m.getAgent());
        requireFreezable(r);
        holderOf(r, m.getHolder()).frozen = m.getFrozen();
        chain.emit("qorechain.asset.v1.EventFrozen", EventFrozen.newBuilder()
                .setAssetId(m.getAssetId()).setHolder(m.getHolder()).setFrozen(m.getFrozen()).setAgent(m.getAgent()).build());
        return MsgFreezeResponse.getDefaultInstance();
    }

    @Override
    public MsgFreezePartialResponse freezePartial(MsgFreezePartial m) {
        Rec r = rec(m.getAssetId());
        requireAgent(r, m.getAgent());
        requireFreezable(r);
        BigInteger amount = parseAmount(M, m.getFrozenAmount(), true);
        if (amount.compareTo(peekHolder(r, m.getHolder()).balance) > 0) {
            throw fail(M, "ERROR_CODE_INSUFFICIENT_BALANCE", "frozen amount exceeds the balance");
        }
        holderOf(r, m.getHolder()).frozenAmount = amount;
        chain.emit("qorechain.asset.v1.EventPartiallyFrozen", EventPartiallyFrozen.newBuilder()
                .setAssetId(m.getAssetId()).setHolder(m.getHolder()).setFrozenAmount(amount.toString()).setAgent(m.getAgent()).build());
        return MsgFreezePartialResponse.getDefaultInstance();
    }

    @Override
    public MsgPauseResponse pause(MsgPause m) {
        Rec r = rec(m.getAssetId());
        requireAgent(r, m.getAgent());
        if (r.asset.getStatus() == AssetStatus.ASSET_STATUS_RETIRED) {
            throw fail(M, "ERROR_CODE_ASSET_RETIRED", "asset is retired");
        }
        if (m.getPaused() && !flags(r).getPausable()) {
            throw fail(M, "ERROR_CODE_FLAG_NOT_ENABLED", "pausable is not set");
        }
        r.asset.setStatus(m.getPaused() ? AssetStatus.ASSET_STATUS_PAUSED : AssetStatus.ASSET_STATUS_ACTIVE);
        chain.emit("qorechain.asset.v1.EventPaused", EventPaused.newBuilder()
                .setAssetId(m.getAssetId()).setPaused(m.getPaused()).setAgent(m.getAgent()).build());
        return MsgPauseResponse.getDefaultInstance();
    }

    @Override
    public MsgClawbackResponse clawback(MsgClawback m) {
        Rec r = rec(m.getAssetId());
        requireAgent(r, m.getAgent());
        requireFreezable(r);
        BigInteger amount = parseAmount(M, m.getAmount(), false);
        if (peekHolder(r, m.getFrom()).balance.compareTo(amount) < 0) {
            throw fail(M, "ERROR_CODE_INSUFFICIENT_BALANCE", m.getFrom() + " balance is too low");
        }
        move(r, m.getFrom(), r.asset.getIssuer(), amount);
        chain.emit("qorechain.asset.v1.EventClawback", EventClawback.newBuilder()
                .setAssetId(m.getAssetId()).setFrom(m.getFrom()).setAmount(amount.toString())
                .setAgent(m.getAgent()).setReason(m.getReason()).build());
        return MsgClawbackResponse.getDefaultInstance();
    }

    @Override
    public MsgForceTransferResponse forceTransfer(MsgForceTransfer m) {
        Rec r = rec(m.getAssetId());
        requireAgent(r, m.getAgent());
        requireFreezable(r);
        BigInteger amount = parseAmount(M, m.getAmount(), false);
        if (r.asset.getStatus() == AssetStatus.ASSET_STATUS_RETIRED) {
            throw fail(M, "ERROR_CODE_ASSET_RETIRED", "asset is retired");
        }
        if (peekHolder(r, m.getFrom()).balance.compareTo(amount) < 0) {
            throw fail(M, "ERROR_CODE_INSUFFICIENT_BALANCE", m.getFrom() + " balance is too low");
        }
        Refusal refusal = receiverRefusal(r, m.getTo());
        if (refusal == null) {
            refusal = complianceRefusal(m.getAssetId(), m.getFrom(), m.getTo(), amount);
        }
        if (refusal != null) {
            throw fail(M, refusal.code(), refusal.message());
        }
        move(r, m.getFrom(), m.getTo(), amount);
        chain.emit("qorechain.asset.v1.EventForcedTransfer", EventForcedTransfer.newBuilder()
                .setAssetId(m.getAssetId()).setFrom(m.getFrom()).setTo(m.getTo()).setAmount(amount.toString())
                .setAgent(m.getAgent()).setReason(m.getReason()).build());
        return MsgForceTransferResponse.getDefaultInstance();
    }

    @Override
    public MsgSetTermsResponse setTerms(MsgSetTerms m) {
        Rec r = rec(m.getAssetId());
        requireIssuer(r, m.getIssuer());
        r.asset.setTermsHash(m.getTermsHash()).setTermsUri(m.getTermsUri());
        chain.emit("qorechain.asset.v1.EventTermsUpdated", EventTermsUpdated.newBuilder()
                .setAssetId(m.getAssetId()).setTermsHash(m.getTermsHash()).setTermsUri(m.getTermsUri()).build());
        return MsgSetTermsResponse.getDefaultInstance();
    }

    @Override
    public MsgRetireResponse retire(MsgRetire m) {
        Rec r = rec(m.getAssetId());
        requireIssuer(r, m.getIssuer());
        r.asset.setStatus(AssetStatus.ASSET_STATUS_RETIRED);
        chain.emit("qorechain.asset.v1.EventRetired", EventRetired.newBuilder().setAssetId(m.getAssetId()).build());
        return MsgRetireResponse.getDefaultInstance();
    }

    // ------------------------------------------------------------------ queries

    @Override
    public QueryParamsResponse params(QueryParamsRequest req) {
        return QueryParamsResponse.newBuilder().setParams(params).build();
    }

    private Asset snapshotAsset(String assetId) {
        Rec r = rec(assetId);
        Asset.Builder b = r.asset.clone().clearComplianceModuleIds();
        for (var binding : chain.compliance.bindingsOf(assetId)) {
            b.addComplianceModuleIds(binding.getModuleId());
        }
        return b.build();
    }

    @Override
    public QueryAssetResponse asset(QueryAssetRequest q) {
        return QueryAssetResponse.newBuilder().setAsset(snapshotAsset(q.getAssetId())).build();
    }

    @Override
    public QueryAssetsResponse assets(QueryAssetsRequest q) {
        QueryAssetsResponse.Builder b = QueryAssetsResponse.newBuilder();
        assets.values().stream()
                .filter(r -> q.getIssuer().isEmpty() || r.asset.getIssuer().equals(q.getIssuer()))
                .map(r -> snapshotAsset(r.asset.getAssetId()))
                .sorted(Comparator.comparing(Asset::getAssetId))
                .forEach(b::addAssets);
        return b.build();
    }

    private static HolderState holderState(String assetId, String address, Holder h) {
        return HolderState.newBuilder()
                .setAssetId(assetId)
                .setAddress(address)
                .setBalance(h.balance.toString())
                .setAuthorized(h.authorized)
                .setFrozen(h.frozen)
                .setFrozenAmount(h.frozenAmount.toString())
                .build();
    }

    @Override
    public QueryHolderResponse holder(QueryHolderRequest q) {
        Rec r = rec(q.getAssetId());
        return QueryHolderResponse.newBuilder()
                .setHolder(holderState(q.getAssetId(), q.getAddress(), peekHolder(r, q.getAddress()))).build();
    }

    @Override
    public QueryHoldersResponse holders(QueryHoldersRequest q) {
        Rec r = rec(q.getAssetId());
        QueryHoldersResponse.Builder b = QueryHoldersResponse.newBuilder();
        r.holders.entrySet().stream()
                .sorted(Map.Entry.comparingByKey())
                .forEach(e -> b.addHolders(holderState(q.getAssetId(), e.getKey(), e.getValue())));
        return b.build();
    }

    @Override
    public QueryRolesResponse roles(QueryRolesRequest q) {
        Rec r = rec(q.getAssetId());
        List<RoleGrant> roles = new ArrayList<>();
        r.roles.forEach((address, set) -> set.forEach((role, height) -> roles.add(RoleGrant.newBuilder()
                .setAssetId(q.getAssetId()).setAddress(address).setRoleValue(role).setGrantedHeight(height).build())));
        roles.sort(Comparator.comparingInt(RoleGrant::getRoleValue).thenComparing(RoleGrant::getAddress));
        return QueryRolesResponse.newBuilder().addAllRoles(roles).build();
    }

    @Override
    public QueryCanTransferResponse canTransfer(QueryCanTransferRequest q) {
        if (!MockChain.isPositiveInteger(q.getAmount())) {
            return no("ERROR_CODE_INVALID_AMOUNT", "amount must be a positive integer", null);
        }
        Rec r = assets.get(q.getAssetId());
        if (r == null) {
            return no("ERROR_CODE_ASSET_NOT_FOUND", "asset " + q.getAssetId() + " not found", null);
        }
        Refusal refusal = transferRefusal(r, q.getFrom(), q.getTo(), new BigInteger(q.getAmount()));
        if (refusal != null) {
            return no(refusal.code(), refusal.reason(), refusal.moduleId());
        }
        return QueryCanTransferResponse.newBuilder().setAllowed(true).build();
    }

    private static QueryCanTransferResponse no(String code, String reason, String moduleId) {
        return QueryCanTransferResponse.newBuilder()
                .setAllowed(false)
                .setCode(ErrorCode.valueOf(code))
                .setComplianceModuleId(moduleId == null ? "" : moduleId)
                .setReason(reason)
                .build();
    }
}

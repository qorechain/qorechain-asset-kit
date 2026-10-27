// SPDX-License-Identifier: Apache-2.0
package io.github.qorechain.assetkit;

import com.google.protobuf.Message;
import io.github.qorechain.assetkit.proto.attest.v1.AttestationKind;
import io.github.qorechain.assetkit.proto.attest.v1.QueryLatestResponse;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.OptionalInt;
import java.util.regex.Pattern;

/**
 * In-memory implementation of the PROPOSED modules, for building and testing
 * applications. It is not QoreChain and proves nothing about how the chain
 * would behave; it implements the rules written in docs/proposal.md. Signer
 * fields are trusted as given: there are no signatures in the mock.
 */
public final class MockChain implements AssetKit {
    /** Constructor options. */
    public static final class Options {
        String authority = "authority";
        List<String> identityAgents = List.of();
        long time = 1_767_225_600L;
        long height = 1;

        /** Address treated as the governance authority. Default "authority". */
        public Options authority(String v) {
            authority = v;
            return this;
        }

        /** Identity agents of x/identity. Default: none (the authority can always act). */
        public Options identityAgents(List<String> v) {
            identityAgents = List.copyOf(v);
            return this;
        }

        /** Initial block time, Unix seconds. Default 1767225600 (2026-01-01T00:00:00Z). */
        public Options time(long v) {
            time = v;
            return this;
        }

        /** Initial height. Default 1. */
        public Options height(long v) {
            height = v;
            return this;
        }
    }

    static final Pattern INTEGER = Pattern.compile("^[0-9]+$");

    final String authority;
    long height;
    long time;
    final List<Event> log = new ArrayList<>();
    private final Map<String, boolean[]> keys = new HashMap<>();
    Map<String, Map<String, BigInteger>> bank = new LinkedHashMap<>();
    final Map<String, ModuleLogic> customLogic = new HashMap<>();

    final MockAsset asset;
    final MockIdentity identity;
    final MockCompliance compliance;
    final MockSettlement settlement;
    final MockAttest attest;

    public MockChain() {
        this(new Options());
    }

    public MockChain(Options options) {
        this.authority = options.authority;
        this.time = options.time;
        this.height = options.height;
        this.asset = new MockAsset(this);
        this.identity = new MockIdentity(this, options.identityAgents);
        this.compliance = new MockCompliance(this);
        this.settlement = new MockSettlement(this);
        this.attest = new MockAttest(this);
    }

    @Override
    public AssetApi asset() {
        return asset;
    }

    @Override
    public IdentityApi identity() {
        return identity;
    }

    @Override
    public ComplianceApi compliance() {
        return compliance;
    }

    @Override
    public SettlementApi settlement() {
        return settlement;
    }

    @Override
    public AttestApi attest() {
        return attest;
    }

    public String authority() {
        return authority;
    }

    public long height() {
        return height;
    }

    /** Block time, Unix seconds. */
    public long time() {
        return time;
    }

    /**
     * Advances the chain by {@code blocks} blocks and {@code seconds} seconds, then
     * runs the end blocker: ON_BLOCK instructions due at the new height settle (or
     * fail if not fully affirmed), then instructions past their deadline expire.
     */
    public void advance(long blocks, long seconds) {
        if (blocks < 0 || seconds < 0) {
            throw new IllegalArgumentException("cannot go back in time");
        }
        height += blocks;
        time += seconds;
        settlement.endBlock();
    }

    /** Sets what pqcKeyStatus would report for an address. */
    public void setHybridKey(String address, boolean registered, boolean possessionProven) {
        keys.put(address, new boolean[] {registered, possessionProven});
    }

    /** True when the address has a registered ML-DSA-87 key with proof of possession. */
    public boolean hasHybridKey(String address) {
        boolean[] k = keys.get(address);
        return k != null && k[0] && k[1];
    }

    /** Credits a bank denom (for example "uqor") to an address: the cash side of DvP tests. */
    public void fundBank(String address, String denom, BigInteger amount) {
        bank.computeIfAbsent(address, a -> new LinkedHashMap<>()).merge(denom, amount, BigInteger::add);
    }

    /** Credits a bank denom, amount as an integer string. */
    public void fundBank(String address, String denom, String amount) {
        fundBank(address, denom, new BigInteger(amount));
    }

    public String bankBalance(String address, String denom) {
        return bankBig(address, denom).toString();
    }

    BigInteger bankBig(String address, String denom) {
        Map<String, BigInteger> m = bank.get(address);
        return m == null ? BigInteger.ZERO : m.getOrDefault(denom, BigInteger.ZERO);
    }

    /** Recorded events, optionally filtered by full type name (null for all). */
    public List<Event> events(String type) {
        List<Event> out = new ArrayList<>();
        for (Event e : log) {
            if (type == null || e.type().equals(type)) {
                out.add(e);
            }
        }
        return out;
    }

    /** All recorded events. */
    public List<Event> events() {
        return events(null);
    }

    /** Supplies the logic of a compliance module registered by governance (for example a WASM module). */
    public void defineModuleLogic(String moduleId, ModuleLogic logic) {
        customLogic.put(moduleId, logic);
    }

    /** Topics, of those asked, for which the address holds no valid claim. */
    public List<Integer> missingTopics(String address, List<Integer> topics) {
        return identity.missingTopics(address, topics);
    }

    /** The identity country of an address, if it has an identity. */
    public OptionalInt countryOf(String address) {
        return identity.countryOf(address);
    }

    /** Freshness of the latest attestation of a kind, at the current block time. */
    public QueryLatestResponse freshness(String assetId, AttestationKind kind) {
        return attest.freshness(assetId, kind);
    }

    void emit(String type, Message data) {
        log.add(new Event(type, height, data));
    }

    static MockChainError fail(String module, String code, String message) {
        return new MockChainError(message, code, module);
    }

    static BigInteger parseAmount(String module, String value, boolean allowZero) {
        String s = value == null ? "" : value;
        if (!INTEGER.matcher(s).matches()) {
            throw fail(module, "ERROR_CODE_INVALID_AMOUNT", "amount \"" + s + "\" is not a non-negative integer");
        }
        BigInteger n = new BigInteger(s);
        if (!allowZero && n.signum() == 0) {
            throw fail(module, "ERROR_CODE_INVALID_AMOUNT", "amount must be greater than zero");
        }
        return n;
    }

    static boolean isPositiveInteger(String s) {
        return s != null && INTEGER.matcher(s).matches() && new BigInteger(s).signum() > 0;
    }

    /** Saves balances and the event log; the returned runnable restores them. */
    Runnable snapshot() {
        Runnable assets = asset.snapshotHolders();
        Map<String, Map<String, BigInteger>> bankCopy = new LinkedHashMap<>();
        bank.forEach((a, m) -> bankCopy.put(a, new LinkedHashMap<>(m)));
        int events = log.size();
        return () -> {
            assets.run();
            bank = bankCopy;
            while (log.size() > events) {
                log.remove(log.size() - 1);
            }
        };
    }
}

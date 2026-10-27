// SPDX-License-Identifier: Apache-2.0
package io.github.qorechain.assetkit;

import static io.github.qorechain.assetkit.MockChain.fail;

import io.github.qorechain.assetkit.proto.attest.v1.AttestationKind;
import io.github.qorechain.assetkit.proto.attest.v1.Freshness;
import io.github.qorechain.assetkit.proto.compliance.v1.*;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.OptionalInt;

/** x/compliance in {@link MockChain}. */
final class MockCompliance implements ComplianceApi {
    private static final String M = "x/compliance";

    /** A refusal by a bound module. */
    record Rejection(String moduleId, int version, String reason) {}

    private static final String[][] BUILTIN = {
        {"identity-verified",
            "{\"type\":\"object\",\"required\":[\"topics\"],\"properties\":{\"topics\":{\"type\":\"array\",\"items\":{\"type\":\"integer\"}}}}",
            "The receiver is verified in x/identity for every listed claim topic."},
        {"country-allowlist",
            "{\"type\":\"object\",\"required\":[\"countries\"],\"properties\":{\"countries\":{\"type\":\"array\",\"items\":{\"type\":\"integer\"}}}}",
            "The receiver's identity country is in the list; no identity is refused."},
        {"country-blocklist",
            "{\"type\":\"object\",\"required\":[\"countries\"],\"properties\":{\"countries\":{\"type\":\"array\",\"items\":{\"type\":\"integer\"}}}}",
            "The receiver's identity country is not in the list; no identity is allowed."},
        {"max-holders",
            "{\"type\":\"object\",\"required\":[\"max\"],\"properties\":{\"max\":{\"type\":\"integer\",\"minimum\":1}}}",
            "The number of addresses with a positive balance never exceeds max."},
        {"max-balance",
            "{\"type\":\"object\",\"required\":[\"max\"],\"properties\":{\"max\":{\"type\":\"string\",\"pattern\":\"^[0-9]+$\"}}}",
            "The receiver's balance after the transfer is at most max."},
        {"attestation-fresh",
            "{\"type\":\"object\",\"required\":[\"kind\"],\"properties\":{\"kind\":{\"type\":\"string\"}}}",
            "The latest attestation of the given kind for the asset is fresh."},
    };

    private final MockChain chain;
    private final Params params = Params.newBuilder().setMaxModuleGas(1_000_000L).build();
    private final Map<String, ComplianceModule.Builder> registry = new LinkedHashMap<>();
    private final Map<String, List<Binding.Builder>> bindingsByAsset = new LinkedHashMap<>();

    MockCompliance(MockChain chain) {
        this.chain = chain;
        for (String[] b : BUILTIN) {
            registry.put(b[0] + "@1", ComplianceModule.newBuilder()
                    .setModuleId(b[0])
                    .setVersion(1)
                    .setRuntime(ModuleRuntime.MODULE_RUNTIME_NATIVE)
                    .setStatus(ModuleStatus.MODULE_STATUS_ACTIVE)
                    .setParamsSchema(b[1])
                    .setDescription(b[2]));
        }
    }

    List<Binding> bindingsOf(String assetId) {
        List<Binding> out = new ArrayList<>();
        for (Binding.Builder b : bindingsByAsset.getOrDefault(assetId, List.of())) {
            out.add(b.build());
        }
        out.sort(Comparator.comparingInt(Binding::getPosition));
        return out;
    }

    private ComplianceModule.Builder moduleVersion(String moduleId, int version) {
        ComplianceModule.Builder mod = registry.get(moduleId + "@" + version);
        if (mod == null) {
            throw fail(M, "ERROR_CODE_MODULE_NOT_FOUND", "module " + moduleId + " v" + version + " not found");
        }
        return mod;
    }

    private void requireAuthority(String signer) {
        if (!signer.equals(chain.authority)) {
            throw fail(M, "ERROR_CODE_UNAUTHORIZED", signer + " is not the governance authority");
        }
    }

    private void requireAssetIssuer(String assetId, String signer) {
        MockAsset.Rec r = chain.asset.assets.get(assetId);
        if (r == null || !r.asset.getIssuer().equals(signer)) {
            throw fail(M, "ERROR_CODE_NOT_ISSUER", signer + " is not the issuer of " + assetId);
        }
    }

    @Override
    public MsgRegisterModuleResponse registerModule(MsgRegisterModule m) {
        requireAuthority(m.getAuthority());
        ComplianceModule.Builder mod = m.getModule().toBuilder();
        if (mod.getModuleId().isEmpty() || mod.getVersion() < 1) {
            throw fail(M, "ERROR_CODE_INVALID_PARAMS", "module id and a version >= 1 are required");
        }
        int latest = 0;
        for (ComplianceModule.Builder x : registry.values()) {
            if (x.getModuleId().equals(mod.getModuleId())) {
                latest = Math.max(latest, x.getVersion());
            }
        }
        if (mod.getVersion() <= latest) {
            throw fail(M, "ERROR_CODE_MODULE_VERSION_EXISTS", "version must be greater than " + latest);
        }
        if (mod.getStatus() == ModuleStatus.MODULE_STATUS_UNSPECIFIED) {
            mod.setStatus(ModuleStatus.MODULE_STATUS_ACTIVE);
        }
        registry.put(mod.getModuleId() + "@" + mod.getVersion(), mod);
        chain.emit("qorechain.compliance.v1.EventModuleRegistered", EventModuleRegistered.newBuilder()
                .setModuleId(mod.getModuleId()).setVersion(mod.getVersion()).setRuntime(mod.getRuntime()).build());
        return MsgRegisterModuleResponse.getDefaultInstance();
    }

    @Override
    public MsgSetModuleStatusResponse setModuleStatus(MsgSetModuleStatus m) {
        requireAuthority(m.getAuthority());
        moduleVersion(m.getModuleId(), m.getVersion()).setStatus(m.getStatus());
        chain.emit("qorechain.compliance.v1.EventModuleStatusChanged", EventModuleStatusChanged.newBuilder()
                .setModuleId(m.getModuleId()).setVersion(m.getVersion()).setStatus(m.getStatus()).build());
        return MsgSetModuleStatusResponse.getDefaultInstance();
    }

    private static boolean isInt(Object o) {
        if (o instanceof Long) {
            return true;
        }
        return o instanceof Double d && d == Math.rint(d) && !d.isInfinite();
    }

    private static long asLong(Object o) {
        return o instanceof Long l ? l : (long) (double) (Double) o;
    }

    private static boolean intList(Map<String, Object> p, String k) {
        if (!(p.get(k) instanceof List<?> l) || l.isEmpty()) {
            return false;
        }
        for (Object x : l) {
            if (!isInt(x) || asLong(x) < 0) {
                return false;
            }
        }
        return true;
    }

    private static List<Long> longs(Object o) {
        List<Long> out = new ArrayList<>();
        for (Object x : (List<?>) o) {
            out.add(asLong(x));
        }
        return out;
    }

    private static AttestationKind kindOf(Object o) {
        if (!(o instanceof String s)) {
            return null;
        }
        try {
            AttestationKind k = AttestationKind.valueOf(s);
            return k == AttestationKind.UNRECOGNIZED || k == AttestationKind.ATTESTATION_KIND_UNSPECIFIED ? null : k;
        } catch (IllegalArgumentException e) {
            return null;
        }
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> parseParams(String moduleId, String json) {
        Object v;
        try {
            v = Json.parse(json.isEmpty() ? "{}" : json);
        } catch (RuntimeException e) {
            throw fail(M, "ERROR_CODE_INVALID_PARAMS", "params_json is not valid JSON");
        }
        if (!(v instanceof Map)) {
            throw fail(M, "ERROR_CODE_INVALID_PARAMS", "params_json must be a JSON object");
        }
        Map<String, Object> p = (Map<String, Object>) v;
        String bad = null;
        switch (moduleId) {
            case "identity-verified" -> {
                if (!intList(p, "topics")) {
                    bad = "topics must be a non-empty list of integers";
                }
            }
            case "country-allowlist", "country-blocklist" -> {
                if (!intList(p, "countries")) {
                    bad = "countries must be a non-empty list of integers";
                }
            }
            case "max-holders" -> {
                if (!isInt(p.get("max")) || asLong(p.get("max")) < 1) {
                    bad = "max must be a positive integer";
                }
            }
            case "max-balance" -> {
                if (!(p.get("max") instanceof String s) || !MockChain.INTEGER.matcher(s).matches()) {
                    bad = "max must be an integer string";
                }
            }
            case "attestation-fresh" -> {
                if (kindOf(p.get("kind")) == null) {
                    bad = "kind must be an AttestationKind name";
                }
            }
            default -> { }
        }
        if (bad != null) {
            throw fail(M, "ERROR_CODE_INVALID_PARAMS", moduleId + ": " + bad);
        }
        return p;
    }

    @Override
    public MsgBindModuleResponse bindModule(MsgBindModule m) {
        requireAssetIssuer(m.getAssetId(), m.getIssuer());
        ComplianceModule.Builder mod = moduleVersion(m.getModuleId(), m.getVersion());
        if (mod.getStatus() == ModuleStatus.MODULE_STATUS_DEPRECATED) {
            throw fail(M, "ERROR_CODE_MODULE_DEPRECATED", "module version is deprecated");
        }
        if (mod.getStatus() == ModuleStatus.MODULE_STATUS_DISABLED) {
            throw fail(M, "ERROR_CODE_MODULE_DISABLED", "module version is disabled");
        }
        parseParams(m.getModuleId(), m.getParamsJson());
        List<Binding.Builder> list = bindingsByAsset.computeIfAbsent(m.getAssetId(), a -> new ArrayList<>());
        for (Binding.Builder b : list) {
            if (b.getModuleId().equals(m.getModuleId())) {
                throw fail(M, "ERROR_CODE_BINDING_EXISTS", m.getModuleId() + " is already bound");
            }
        }
        if (list.size() >= chain.asset.params.getMaxComplianceModules()) {
            throw fail(M, "ERROR_CODE_TOO_MANY_BINDINGS", "too many bindings");
        }
        int position = 0;
        for (Binding.Builder b : list) {
            position = Math.max(position, b.getPosition() + 1);
        }
        list.add(Binding.newBuilder()
                .setAssetId(m.getAssetId())
                .setModuleId(m.getModuleId())
                .setVersion(m.getVersion())
                .setParamsJson(m.getParamsJson().isEmpty() ? "{}" : m.getParamsJson())
                .setPosition(position));
        chain.emit("qorechain.compliance.v1.EventModuleBound", EventModuleBound.newBuilder()
                .setAssetId(m.getAssetId()).setModuleId(m.getModuleId()).setVersion(m.getVersion()).build());
        return MsgBindModuleResponse.getDefaultInstance();
    }

    @Override
    public MsgUnbindModuleResponse unbindModule(MsgUnbindModule m) {
        requireAssetIssuer(m.getAssetId(), m.getIssuer());
        List<Binding.Builder> list = bindingsByAsset.getOrDefault(m.getAssetId(), new ArrayList<>());
        if (!list.removeIf(b -> b.getModuleId().equals(m.getModuleId()))) {
            throw fail(M, "ERROR_CODE_BINDING_NOT_FOUND", m.getModuleId() + " is not bound");
        }
        chain.emit("qorechain.compliance.v1.EventModuleUnbound", EventModuleUnbound.newBuilder()
                .setAssetId(m.getAssetId()).setModuleId(m.getModuleId()).build());
        return MsgUnbindModuleResponse.getDefaultInstance();
    }

    @Override
    public MsgMigrateBindingResponse migrateBinding(MsgMigrateBinding m) {
        requireAssetIssuer(m.getAssetId(), m.getIssuer());
        Binding.Builder b = null;
        for (Binding.Builder x : bindingsByAsset.getOrDefault(m.getAssetId(), List.of())) {
            if (x.getModuleId().equals(m.getModuleId())) {
                b = x;
            }
        }
        if (b == null) {
            throw fail(M, "ERROR_CODE_BINDING_NOT_FOUND", m.getModuleId() + " is not bound");
        }
        ComplianceModule.Builder mod = moduleVersion(m.getModuleId(), m.getToVersion());
        if (mod.getStatus() != ModuleStatus.MODULE_STATUS_ACTIVE) {
            throw fail(M, "ERROR_CODE_MODULE_DEPRECATED", "target version is not active");
        }
        String paramsJson = m.getParamsJson().isEmpty() ? b.getParamsJson() : m.getParamsJson();
        parseParams(m.getModuleId(), paramsJson);
        int from = b.getVersion();
        b.setVersion(m.getToVersion()).setParamsJson(paramsJson);
        chain.emit("qorechain.compliance.v1.EventBindingMigrated", EventBindingMigrated.newBuilder()
                .setAssetId(m.getAssetId()).setModuleId(m.getModuleId()).setFromVersion(from).setToVersion(m.getToVersion()).build());
        return MsgMigrateBindingResponse.getDefaultInstance();
    }

    @Override
    public QueryParamsResponse params(QueryParamsRequest req) {
        return QueryParamsResponse.newBuilder().setParams(params).build();
    }

    @Override
    public QueryModulesResponse modules(QueryModulesRequest q) {
        QueryModulesResponse.Builder b = QueryModulesResponse.newBuilder();
        registry.values().stream()
                .filter(x -> q.getModuleId().isEmpty() || x.getModuleId().equals(q.getModuleId()))
                .map(ComplianceModule.Builder::build)
                .sorted(Comparator.comparing(ComplianceModule::getModuleId).thenComparingInt(ComplianceModule::getVersion))
                .forEach(b::addModules);
        return b.build();
    }

    @Override
    public QueryModuleResponse module(QueryModuleRequest q) {
        return QueryModuleResponse.newBuilder().setModule(moduleVersion(q.getModuleId(), q.getVersion()).build()).build();
    }

    @Override
    public QueryBindingsResponse bindings(QueryBindingsRequest q) {
        return QueryBindingsResponse.newBuilder().addAllBindings(bindingsOf(q.getAssetId())).build();
    }

    private ModuleLogic builtinLogic(String moduleId) {
        switch (moduleId) {
            case "identity-verified":
                return ctx -> {
                    List<Integer> topics = new ArrayList<>();
                    for (Long t : longs(ctx.params().get("topics"))) {
                        topics.add(t.intValue());
                    }
                    List<Integer> missing = ctx.chain().missingTopics(ctx.to(), topics);
                    if (missing.isEmpty()) {
                        return Optional.empty();
                    }
                    List<String> s = new ArrayList<>();
                    missing.forEach(x -> s.add(String.valueOf(x)));
                    return Optional.of(ctx.to() + " is not verified for topics " + String.join(",", s));
                };
            case "country-allowlist":
                return ctx -> {
                    OptionalInt c = ctx.chain().countryOf(ctx.to());
                    if (c.isEmpty()) {
                        return Optional.of(ctx.to() + " has no identity");
                    }
                    return longs(ctx.params().get("countries")).contains((long) c.getAsInt())
                            ? Optional.empty() : Optional.of("country " + c.getAsInt() + " is not allowed");
                };
            case "country-blocklist":
                return ctx -> {
                    OptionalInt c = ctx.chain().countryOf(ctx.to());
                    return c.isPresent() && longs(ctx.params().get("countries")).contains((long) c.getAsInt())
                            ? Optional.of("country " + c.getAsInt() + " is blocked") : Optional.empty();
                };
            case "max-holders":
                return ctx -> {
                    MockAsset a = chain.asset;
                    MockAsset.Rec r = a.assets.get(ctx.assetId());
                    long count = r.holders.values().stream().filter(h -> h.balance.signum() > 0).count();
                    int joins = a.peekHolder(r, ctx.to()).balance.signum() == 0 && ctx.amount().signum() > 0 ? 1 : 0;
                    int leaves = !ctx.from().isEmpty() && !ctx.from().equals(ctx.to())
                            && a.peekHolder(r, ctx.from()).balance.equals(ctx.amount()) ? 1 : 0;
                    long max = asLong(ctx.params().get("max"));
                    return count + joins - leaves > max ? Optional.of("more than " + max + " holders") : Optional.empty();
                };
            case "max-balance":
                return ctx -> {
                    MockAsset a = chain.asset;
                    MockAsset.Rec r = a.assets.get(ctx.assetId());
                    String max = (String) ctx.params().get("max");
                    return a.peekHolder(r, ctx.to()).balance.add(ctx.amount()).compareTo(new BigInteger(max)) > 0
                            ? Optional.of("balance of " + ctx.to() + " would exceed " + max) : Optional.empty();
                };
            case "attestation-fresh":
                return ctx -> {
                    String name = (String) ctx.params().get("kind");
                    Freshness f = ctx.chain().freshness(ctx.assetId(), AttestationKind.valueOf(name)).getFreshness();
                    return f == Freshness.FRESHNESS_FRESH ? Optional.empty()
                            : Optional.of("latest " + name + " attestation is " + f.name());
                };
            default:
                return null;
        }
    }

    @SuppressWarnings("unchecked")
    Rejection run(String assetId, String from, String to, BigInteger amount) {
        for (Binding b : bindingsOf(assetId)) {
            ComplianceModule.Builder mod = registry.get(b.getModuleId() + "@" + b.getVersion());
            if (mod == null || mod.getStatus() == ModuleStatus.MODULE_STATUS_DISABLED) {
                return new Rejection(b.getModuleId(), b.getVersion(), "module version is disabled");
            }
            ModuleLogic logic = chain.customLogic.get(b.getModuleId());
            if (logic == null) {
                logic = builtinLogic(b.getModuleId());
            }
            if (logic == null) {
                return new Rejection(b.getModuleId(), b.getVersion(), "no logic for this module in MockChain");
            }
            Map<String, Object> p = (Map<String, Object>) Json.parse(b.getParamsJson());
            Optional<String> reason = logic.check(new ModuleLogic.Context(chain, assetId, from, to, amount, p));
            if (reason.isPresent()) {
                return new Rejection(b.getModuleId(), b.getVersion(), reason.get());
            }
        }
        return null;
    }

    @Override
    public QueryCheckResponse check(QueryCheckRequest q) {
        BigInteger amount = MockChain.INTEGER.matcher(q.getAmount()).matches() ? new BigInteger(q.getAmount()) : BigInteger.ZERO;
        Rejection c = run(q.getAssetId(), q.getFrom(), q.getTo(), amount);
        if (c == null) {
            return QueryCheckResponse.newBuilder().setAllowed(true).build();
        }
        return QueryCheckResponse.newBuilder()
                .setAllowed(false).setModuleId(c.moduleId()).setVersion(c.version()).setReason(c.reason()).build();
    }
}

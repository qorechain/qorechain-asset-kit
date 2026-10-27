// SPDX-License-Identifier: Apache-2.0
package io.github.qorechain.assetkit;

import static io.github.qorechain.assetkit.MockChain.fail;

import io.github.qorechain.assetkit.proto.asset.v1.Role;
import io.github.qorechain.assetkit.proto.attest.v1.*;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** x/attest in {@link MockChain}. */
final class MockAttest implements AttestApi {
    private static final String M = "x/attest";
    private static final Comparator<Attestation.Builder> NEWEST_FIRST =
            Comparator.comparingLong(Attestation.Builder::getObservedAt).reversed()
                    .thenComparing(Comparator.comparingLong(Attestation.Builder::getId).reversed());

    private final MockChain chain;
    private final Params params = Params.newBuilder()
            .setMaxObservationLagSeconds(7L * 86400)
            .setMaxValiditySeconds(400L * 86400)
            .build();
    private final Map<String, Map<String, Attester>> attesters = new LinkedHashMap<>();
    private final List<Attestation.Builder> attestations = new ArrayList<>();
    private long nextId = 1;

    MockAttest(MockChain chain) {
        this.chain = chain;
    }

    @Override
    public MsgSetAttesterResponse setAttester(MsgSetAttester m) {
        Attester at = m.getAttester();
        MockAsset.Rec r = chain.asset.assets.get(at.getAssetId());
        if (r == null || !r.asset.getIssuer().equals(m.getIssuer())) {
            throw fail(M, "ERROR_CODE_NOT_ISSUER", m.getIssuer() + " is not the issuer of " + at.getAssetId());
        }
        Map<String, Attester> map = attesters.computeIfAbsent(at.getAssetId(), a -> new LinkedHashMap<>());
        if (m.getRemove()) {
            map.remove(at.getAddress());
        } else {
            map.put(at.getAddress(), at);
        }
        chain.emit("qorechain.attest.v1.EventAttesterChanged", EventAttesterChanged.newBuilder()
                .setAssetId(at.getAssetId()).setAddress(at.getAddress()).addAllKinds(at.getKindsList())
                .setRemoved(m.getRemove()).build());
        return MsgSetAttesterResponse.getDefaultInstance();
    }

    private Attestation.Builder latestOf(String assetId, AttestationKind kind) {
        return attestations.stream()
                .filter(a -> a.getAssetId().equals(assetId) && a.getKind() == kind && !a.getRevoked())
                .sorted(NEWEST_FIRST)
                .findFirst()
                .orElse(null);
    }

    @Override
    public MsgSubmitResponse submit(MsgSubmit m) {
        Attester at = attesters.getOrDefault(m.getAssetId(), Map.of()).get(m.getAttester());
        if (at == null) {
            throw fail(M, "ERROR_CODE_NOT_AN_ATTESTER", m.getAttester() + " is not an attester of " + m.getAssetId());
        }
        if (!at.getKindsList().contains(m.getKind())) {
            throw fail(M, "ERROR_CODE_KIND_NOT_ALLOWED", m.getKind().name() + " not allowed");
        }
        if (m.getKind() == AttestationKind.ATTESTATION_KIND_AUDIT_REPORT) {
            MockAsset.Rec r = chain.asset.assets.get(m.getAssetId());
            if (r == null || !chain.asset.hasRole(r, m.getAttester(), Role.ROLE_AUDITOR)) {
                throw fail(M, "ERROR_CODE_KIND_NOT_ALLOWED", "AUDIT_REPORT requires the auditor role");
            }
        }
        long observed = m.getObservedAt();
        long validFor = m.getValidForSeconds();
        if (observed > chain.time) {
            throw fail(M, "ERROR_CODE_OBSERVATION_IN_FUTURE", "observed_at is in the future");
        }
        if (chain.time - observed > params.getMaxObservationLagSeconds()) {
            throw fail(M, "ERROR_CODE_OBSERVATION_TOO_OLD", "observed_at is too old");
        }
        if (validFor <= 0 || validFor > params.getMaxValiditySeconds()) {
            throw fail(M, "ERROR_CODE_VALIDITY_TOO_LONG", "valid_for_seconds is out of range");
        }
        Attestation.Builder latest = latestOf(m.getAssetId(), m.getKind());
        if (latest != null && observed < latest.getObservedAt()) {
            throw fail(M, "ERROR_CODE_OLDER_THAN_LATEST", "older than the latest attestation");
        }
        long id = nextId++;
        attestations.add(Attestation.newBuilder()
                .setId(id)
                .setAssetId(m.getAssetId())
                .setKind(m.getKind())
                .setAttester(m.getAttester())
                .setValue(m.getValue())
                .setUnit(m.getUnit())
                .setReportHash(m.getReportHash())
                .setReportUri(m.getReportUri())
                .setObservedAt(observed)
                .setValidForSeconds(validFor)
                .setAcceptedAt(chain.time)
                .setRevoked(false));
        chain.emit("qorechain.attest.v1.EventAttestationSubmitted", EventAttestationSubmitted.newBuilder()
                .setId(id).setAssetId(m.getAssetId()).setKind(m.getKind()).setAttester(m.getAttester())
                .setValue(m.getValue()).setObservedAt(observed).setValidForSeconds(validFor).build());
        return MsgSubmitResponse.newBuilder().setId(id).build();
    }

    @Override
    public MsgRevokeResponse revoke(MsgRevoke m) {
        Attestation.Builder a = attestations.stream().filter(x -> x.getId() == m.getId()).findFirst().orElse(null);
        if (a == null) {
            throw fail(M, "ERROR_CODE_ATTESTATION_NOT_FOUND", "attestation " + m.getId() + " not found");
        }
        MockAsset.Rec r = chain.asset.assets.get(a.getAssetId());
        boolean issuer = r != null && r.asset.getIssuer().equals(m.getSigner());
        if (!m.getSigner().equals(a.getAttester()) && !issuer) {
            throw fail(M, "ERROR_CODE_NOT_AN_ATTESTER", m.getSigner() + " may not revoke");
        }
        a.setRevoked(true);
        chain.emit("qorechain.attest.v1.EventAttestationRevoked", EventAttestationRevoked.newBuilder()
                .setId(m.getId()).setSigner(m.getSigner()).setReason(m.getReason()).build());
        return MsgRevokeResponse.getDefaultInstance();
    }

    QueryLatestResponse freshness(String assetId, AttestationKind kind) {
        Attestation.Builder a = latestOf(assetId, kind);
        if (a == null) {
            return QueryLatestResponse.newBuilder().setFreshness(Freshness.FRESHNESS_MISSING).build();
        }
        long staleAt = a.getObservedAt() + a.getValidForSeconds();
        return QueryLatestResponse.newBuilder()
                .setAttestation(a.build())
                .setFreshness(chain.time < staleAt ? Freshness.FRESHNESS_FRESH : Freshness.FRESHNESS_STALE)
                .setStaleAt(staleAt)
                .build();
    }

    @Override
    public QueryParamsResponse params(QueryParamsRequest req) {
        return QueryParamsResponse.newBuilder().setParams(params).build();
    }

    @Override
    public QueryLatestResponse latest(QueryLatestRequest q) {
        return freshness(q.getAssetId(), q.getKind());
    }

    @Override
    public QueryHistoryResponse history(QueryHistoryRequest q) {
        QueryHistoryResponse.Builder b = QueryHistoryResponse.newBuilder();
        attestations.stream()
                .filter(a -> a.getAssetId().equals(q.getAssetId()) && a.getKind() == q.getKind())
                .sorted(NEWEST_FIRST)
                .limit(q.getLimit() > 0 ? q.getLimit() : Long.MAX_VALUE)
                .forEach(a -> b.addAttestations(a.build()));
        return b.build();
    }

    @Override
    public QueryAttestersResponse attesters(QueryAttestersRequest q) {
        QueryAttestersResponse.Builder b = QueryAttestersResponse.newBuilder();
        attesters.getOrDefault(q.getAssetId(), Map.of()).values().stream()
                .sorted(Comparator.comparing(Attester::getAddress))
                .forEach(b::addAttesters);
        return b.build();
    }
}

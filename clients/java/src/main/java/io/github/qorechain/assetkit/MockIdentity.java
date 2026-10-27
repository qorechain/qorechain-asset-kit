// SPDX-License-Identifier: Apache-2.0
package io.github.qorechain.assetkit;

import static io.github.qorechain.assetkit.MockChain.fail;

import io.github.qorechain.assetkit.proto.identity.v1.*;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.OptionalInt;

/** x/identity in {@link MockChain}. */
final class MockIdentity implements IdentityApi {
    private static final String M = "x/identity";

    private final MockChain chain;
    private final Params params;
    private final Map<String, Identity.Builder> identities = new LinkedHashMap<>();
    private final Map<String, String> identityOf = new LinkedHashMap<>();
    private final Map<String, ClaimIssuer> claimIssuers = new LinkedHashMap<>();

    MockIdentity(MockChain chain, List<String> agents) {
        this.chain = chain;
        this.params = Params.newBuilder().addAllIdentityAgents(agents).build();
    }

    private void requireIdentityAgent(String signer) {
        if (!signer.equals(chain.authority) && !params.getIdentityAgentsList().contains(signer)) {
            throw fail(M, "ERROR_CODE_NOT_IDENTITY_AGENT", signer + " is not an identity agent");
        }
    }

    private Identity.Builder ident(String id) {
        Identity.Builder x = identities.get(id);
        if (x == null) {
            throw fail(M, "ERROR_CODE_IDENTITY_NOT_FOUND", "identity " + id + " not found");
        }
        return x;
    }

    @Override
    public MsgRegisterIdentityResponse registerIdentity(MsgRegisterIdentity m) {
        requireIdentityAgent(m.getAgent());
        if (identities.containsKey(m.getIdentityId())) {
            throw fail(M, "ERROR_CODE_IDENTITY_EXISTS", "identity " + m.getIdentityId() + " exists");
        }
        if (identityOf.containsKey(m.getAddress())) {
            throw fail(M, "ERROR_CODE_ADDRESS_ALREADY_BOUND", m.getAddress() + " is already bound");
        }
        identities.put(m.getIdentityId(), Identity.newBuilder()
                .setIdentityId(m.getIdentityId())
                .addAddresses(m.getAddress())
                .setCountry(m.getCountry())
                .setRegisteredBy(m.getAgent()));
        identityOf.put(m.getAddress(), m.getIdentityId());
        chain.emit("qorechain.identity.v1.EventIdentityRegistered", EventIdentityRegistered.newBuilder()
                .setIdentityId(m.getIdentityId()).setAddress(m.getAddress()).setCountry(m.getCountry()).setAgent(m.getAgent()).build());
        return MsgRegisterIdentityResponse.getDefaultInstance();
    }

    @Override
    public MsgUpdateCountryResponse updateCountry(MsgUpdateCountry m) {
        requireIdentityAgent(m.getAgent());
        ident(m.getIdentityId()).setCountry(m.getCountry());
        chain.emit("qorechain.identity.v1.EventCountryUpdated", EventCountryUpdated.newBuilder()
                .setIdentityId(m.getIdentityId()).setCountry(m.getCountry()).build());
        return MsgUpdateCountryResponse.getDefaultInstance();
    }

    @Override
    public MsgBindAddressResponse bindAddress(MsgBindAddress m) {
        requireIdentityAgent(m.getAgent());
        Identity.Builder x = ident(m.getIdentityId());
        if (identityOf.containsKey(m.getAddress())) {
            throw fail(M, "ERROR_CODE_ADDRESS_ALREADY_BOUND", m.getAddress() + " is already bound");
        }
        x.addAddresses(m.getAddress());
        identityOf.put(m.getAddress(), m.getIdentityId());
        chain.emit("qorechain.identity.v1.EventAddressBound", EventAddressBound.newBuilder()
                .setIdentityId(m.getIdentityId()).setAddress(m.getAddress()).setBound(true).build());
        return MsgBindAddressResponse.getDefaultInstance();
    }

    @Override
    public MsgUnbindAddressResponse unbindAddress(MsgUnbindAddress m) {
        requireIdentityAgent(m.getAgent());
        Identity.Builder x = ident(m.getIdentityId());
        if (!m.getIdentityId().equals(identityOf.get(m.getAddress()))) {
            throw fail(M, "ERROR_CODE_IDENTITY_NOT_FOUND", m.getAddress() + " is not bound to " + m.getIdentityId());
        }
        List<String> rest = new ArrayList<>(x.getAddressesList());
        rest.remove(m.getAddress());
        x.clearAddresses().addAllAddresses(rest);
        identityOf.remove(m.getAddress());
        chain.emit("qorechain.identity.v1.EventAddressBound", EventAddressBound.newBuilder()
                .setIdentityId(m.getIdentityId()).setAddress(m.getAddress()).setBound(false).build());
        return MsgUnbindAddressResponse.getDefaultInstance();
    }

    @Override
    public MsgAddClaimResponse addClaim(MsgAddClaim m) {
        ClaimIssuer issuer = claimIssuers.get(m.getClaimIssuer());
        if (issuer == null) {
            throw fail(M, "ERROR_CODE_CLAIM_ISSUER_NOT_TRUSTED", m.getClaimIssuer() + " is not a trusted claim issuer");
        }
        if (!issuer.getTopicsList().contains(m.getTopic())) {
            throw fail(M, "ERROR_CODE_CLAIM_TOPIC_NOT_ALLOWED", "topic " + m.getTopic() + " not allowed");
        }
        Identity.Builder x = ident(m.getIdentityId());
        List<Claim> claims = new ArrayList<>();
        for (Claim c : x.getClaimsList()) {
            if (!(c.getTopic() == m.getTopic() && c.getIssuer().equals(m.getClaimIssuer()))) {
                claims.add(c);
            }
        }
        claims.add(Claim.newBuilder()
                .setTopic(m.getTopic())
                .setIssuer(m.getClaimIssuer())
                .setDataHash(m.getDataHash())
                .setValidUntil(m.getValidUntil())
                .setRevoked(false)
                .build());
        x.clearClaims().addAllClaims(claims);
        chain.emit("qorechain.identity.v1.EventClaimAdded", EventClaimAdded.newBuilder()
                .setIdentityId(m.getIdentityId()).setTopic(m.getTopic()).setClaimIssuer(m.getClaimIssuer())
                .setValidUntil(m.getValidUntil()).build());
        return MsgAddClaimResponse.getDefaultInstance();
    }

    @Override
    public MsgRevokeClaimResponse revokeClaim(MsgRevokeClaim m) {
        Identity.Builder x = ident(m.getIdentityId());
        int idx = -1;
        for (int i = 0; i < x.getClaimsCount(); i++) {
            Claim c = x.getClaims(i);
            if (c.getTopic() == m.getTopic() && c.getIssuer().equals(m.getClaimIssuer()) && !c.getRevoked()) {
                idx = i;
                break;
            }
        }
        if (idx < 0) {
            throw fail(M, "ERROR_CODE_CLAIM_NOT_FOUND", "no claim for topic " + m.getTopic() + " from " + m.getClaimIssuer());
        }
        x.setClaims(idx, x.getClaims(idx).toBuilder().setRevoked(true).build());
        chain.emit("qorechain.identity.v1.EventClaimRevoked", EventClaimRevoked.newBuilder()
                .setIdentityId(m.getIdentityId()).setTopic(m.getTopic()).setClaimIssuer(m.getClaimIssuer()).build());
        return MsgRevokeClaimResponse.getDefaultInstance();
    }

    @Override
    public MsgRemoveIdentityResponse removeIdentity(MsgRemoveIdentity m) {
        requireIdentityAgent(m.getAgent());
        Identity.Builder x = ident(m.getIdentityId());
        for (String a : x.getAddressesList()) {
            identityOf.remove(a);
        }
        identities.remove(m.getIdentityId());
        chain.emit("qorechain.identity.v1.EventIdentityRemoved", EventIdentityRemoved.newBuilder()
                .setIdentityId(m.getIdentityId()).build());
        return MsgRemoveIdentityResponse.getDefaultInstance();
    }

    @Override
    public MsgSetClaimIssuerResponse setClaimIssuer(MsgSetClaimIssuer m) {
        if (!m.getAuthority().equals(chain.authority)) {
            throw fail(M, "ERROR_CODE_UNAUTHORIZED", m.getAuthority() + " is not the governance authority");
        }
        ClaimIssuer ci = m.getClaimIssuer();
        if (m.getRemove()) {
            claimIssuers.remove(ci.getAddress());
        } else {
            claimIssuers.put(ci.getAddress(), ci);
        }
        chain.emit("qorechain.identity.v1.EventClaimIssuerChanged", EventClaimIssuerChanged.newBuilder()
                .setAddress(ci.getAddress()).addAllTopics(ci.getTopicsList()).setRemoved(m.getRemove()).build());
        return MsgSetClaimIssuerResponse.getDefaultInstance();
    }

    @Override
    public QueryParamsResponse params(QueryParamsRequest req) {
        return QueryParamsResponse.newBuilder().setParams(params).build();
    }

    @Override
    public QueryIdentityResponse identity(QueryIdentityRequest q) {
        return QueryIdentityResponse.newBuilder().setIdentity(ident(q.getIdentityId()).build()).build();
    }

    @Override
    public QueryIdentityByAddressResponse identityByAddress(QueryIdentityByAddressRequest q) {
        String id = identityOf.get(q.getAddress());
        if (id == null) {
            throw fail(M, "ERROR_CODE_IDENTITY_NOT_FOUND", q.getAddress() + " has no identity");
        }
        return QueryIdentityByAddressResponse.newBuilder().setIdentity(ident(id).build()).build();
    }

    @Override
    public QueryClaimIssuersResponse claimIssuers(QueryClaimIssuersRequest req) {
        QueryClaimIssuersResponse.Builder b = QueryClaimIssuersResponse.newBuilder();
        claimIssuers.values().stream().sorted(Comparator.comparing(ClaimIssuer::getAddress)).forEach(b::addClaimIssuers);
        return b.build();
    }

    List<Integer> missingTopics(String address, List<Integer> topics) {
        String id = identityOf.get(address);
        Identity.Builder x = id == null ? null : identities.get(id);
        List<Integer> missing = new ArrayList<>();
        for (Integer topic : topics) {
            boolean ok = false;
            if (x != null) {
                for (Claim c : x.getClaimsList()) {
                    ClaimIssuer ci = claimIssuers.get(c.getIssuer());
                    boolean trusted = ci != null && ci.getTopicsList().contains(topic);
                    boolean live = c.getValidUntil() == 0 || c.getValidUntil() > chain.time;
                    if (c.getTopic() == topic && !c.getRevoked() && trusted && live) {
                        ok = true;
                        break;
                    }
                }
            }
            if (!ok) {
                missing.add(topic);
            }
        }
        return missing;
    }

    OptionalInt countryOf(String address) {
        String id = identityOf.get(address);
        Identity.Builder x = id == null ? null : identities.get(id);
        return x == null ? OptionalInt.empty() : OptionalInt.of(x.getCountry());
    }

    @Override
    public QueryIsVerifiedResponse isVerified(QueryIsVerifiedRequest q) {
        List<Integer> missing = missingTopics(q.getAddress(), q.getTopicsList());
        boolean bound = identityOf.containsKey(q.getAddress());
        return QueryIsVerifiedResponse.newBuilder()
                .setVerified(bound && missing.isEmpty())
                .addAllMissingTopics(missing)
                .build();
    }
}

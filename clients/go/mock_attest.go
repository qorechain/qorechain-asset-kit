// SPDX-License-Identifier: Apache-2.0

package assetkit

import (
	"context"
	"sort"

	"google.golang.org/protobuf/proto"

	assetv1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/asset/v1"
	attestv1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/attest/v1"
)

func (c *MockChain) setAttester(m *attestv1.MsgSetAttester) (*attestv1.MsgSetAttesterResponse, error) {
	at := &attestv1.Attester{}
	if m.Attester != nil {
		at = proto.Clone(m.Attester).(*attestv1.Attester)
	}
	r, ok := c.assets[at.AssetId]
	if !ok || r.asset.Issuer != m.Issuer {
		return nil, fail(ModuleAttest, "ERROR_CODE_NOT_ISSUER", "%s is not the issuer of %s", m.Issuer, at.AssetId)
	}
	set := c.attesters[at.AssetId]
	if set == nil {
		set = map[string]*attestv1.Attester{}
		c.attesters[at.AssetId] = set
	}
	if m.Remove {
		delete(set, at.Address)
	} else {
		set[at.Address] = at
	}
	c.emit("qorechain.attest.v1.EventAttesterChanged", &attestv1.EventAttesterChanged{
		AssetId: at.AssetId, Address: at.Address, Kinds: append([]attestv1.AttestationKind(nil), at.Kinds...), Removed: m.Remove,
	})
	return &attestv1.MsgSetAttesterResponse{}, nil
}

// newestFirst orders attestations by observation time, then id, descending.
func newestFirst(list []*attestv1.Attestation) {
	sort.SliceStable(list, func(i, j int) bool {
		if list[i].ObservedAt != list[j].ObservedAt {
			return list[i].ObservedAt > list[j].ObservedAt
		}
		return list[i].Id > list[j].Id
	})
}

func (c *MockChain) latestOf(assetID string, kind attestv1.AttestationKind) *attestv1.Attestation {
	var list []*attestv1.Attestation
	for _, a := range c.attestations {
		if a.AssetId == assetID && a.Kind == kind && !a.Revoked {
			list = append(list, a)
		}
	}
	if len(list) == 0 {
		return nil
	}
	newestFirst(list)
	return list[0]
}

func (c *MockChain) submitAttestation(m *attestv1.MsgSubmit) (*attestv1.MsgSubmitResponse, error) {
	at, ok := c.attesters[m.AssetId][m.Attester]
	if !ok {
		return nil, fail(ModuleAttest, "ERROR_CODE_NOT_AN_ATTESTER", "%s is not an attester of %s", m.Attester, m.AssetId)
	}
	if !contains(at.Kinds, m.Kind) {
		return nil, fail(ModuleAttest, "ERROR_CODE_KIND_NOT_ALLOWED", "%s not allowed", m.Kind)
	}
	if m.Kind == attestv1.AttestationKind_ATTESTATION_KIND_AUDIT_REPORT {
		r, ok := c.assets[m.AssetId]
		if !ok || !hasRole(r, m.Attester, assetv1.Role_ROLE_AUDITOR) {
			return nil, fail(ModuleAttest, "ERROR_CODE_KIND_NOT_ALLOWED", "AUDIT_REPORT requires the auditor role")
		}
	}
	if m.ObservedAt > c.time {
		return nil, fail(ModuleAttest, "ERROR_CODE_OBSERVATION_IN_FUTURE", "observed_at is in the future")
	}
	if c.time-m.ObservedAt > c.attestParams.MaxObservationLagSeconds {
		return nil, fail(ModuleAttest, "ERROR_CODE_OBSERVATION_TOO_OLD", "observed_at is too old")
	}
	if m.ValidForSeconds <= 0 || m.ValidForSeconds > c.attestParams.MaxValiditySeconds {
		return nil, fail(ModuleAttest, "ERROR_CODE_VALIDITY_TOO_LONG", "valid_for_seconds is out of range")
	}
	if latest := c.latestOf(m.AssetId, m.Kind); latest != nil && m.ObservedAt < latest.ObservedAt {
		return nil, fail(ModuleAttest, "ERROR_CODE_OLDER_THAN_LATEST", "older than the latest attestation")
	}
	id := c.nextAttestationID
	c.nextAttestationID++
	c.attestations = append(c.attestations, &attestv1.Attestation{
		Id: id, AssetId: m.AssetId, Kind: m.Kind, Attester: m.Attester, Value: m.Value, Unit: m.Unit,
		ReportHash: append([]byte(nil), m.ReportHash...), ReportUri: m.ReportUri, ObservedAt: m.ObservedAt,
		ValidForSeconds: m.ValidForSeconds, AcceptedAt: c.time,
	})
	c.emit("qorechain.attest.v1.EventAttestationSubmitted", &attestv1.EventAttestationSubmitted{
		Id: id, AssetId: m.AssetId, Kind: m.Kind, Attester: m.Attester, Value: m.Value,
		ObservedAt: m.ObservedAt, ValidForSeconds: m.ValidForSeconds,
	})
	return &attestv1.MsgSubmitResponse{Id: id}, nil
}

func (c *MockChain) revokeAttestation(m *attestv1.MsgRevoke) (*attestv1.MsgRevokeResponse, error) {
	var a *attestv1.Attestation
	for _, x := range c.attestations {
		if x.Id == m.Id {
			a = x
		}
	}
	if a == nil {
		return nil, fail(ModuleAttest, "ERROR_CODE_ATTESTATION_NOT_FOUND", "attestation %d not found", m.Id)
	}
	issuer := ""
	if r, ok := c.assets[a.AssetId]; ok {
		issuer = r.asset.Issuer
	}
	if m.Signer != a.Attester && m.Signer != issuer {
		return nil, fail(ModuleAttest, "ERROR_CODE_NOT_AN_ATTESTER", "%s may not revoke", m.Signer)
	}
	a.Revoked = true
	c.emit("qorechain.attest.v1.EventAttestationRevoked", &attestv1.EventAttestationRevoked{Id: m.Id, Signer: m.Signer, Reason: m.Reason})
	return &attestv1.MsgRevokeResponse{}, nil
}

// Freshness returns the latest attestation of a kind and its freshness at the
// current block time.
func (c *MockChain) Freshness(assetID string, kind attestv1.AttestationKind) *attestv1.QueryLatestResponse {
	a := c.latestOf(assetID, kind)
	if a == nil {
		return &attestv1.QueryLatestResponse{Freshness: attestv1.Freshness_FRESHNESS_MISSING}
	}
	staleAt := a.ObservedAt + a.ValidForSeconds
	f := attestv1.Freshness_FRESHNESS_STALE
	if c.time < staleAt {
		f = attestv1.Freshness_FRESHNESS_FRESH
	}
	return &attestv1.QueryLatestResponse{Attestation: proto.Clone(a).(*attestv1.Attestation), Freshness: f, StaleAt: staleAt}
}

// mockAttest adapts MockChain to AttestAPI.
type mockAttest struct{ c *MockChain }

func (t mockAttest) SetAttester(_ context.Context, m *attestv1.MsgSetAttester) (*attestv1.MsgSetAttesterResponse, error) {
	return t.c.setAttester(orEmpty(m))
}

func (t mockAttest) Submit(_ context.Context, m *attestv1.MsgSubmit) (*attestv1.MsgSubmitResponse, error) {
	return t.c.submitAttestation(orEmpty(m))
}

func (t mockAttest) Revoke(_ context.Context, m *attestv1.MsgRevoke) (*attestv1.MsgRevokeResponse, error) {
	return t.c.revokeAttestation(orEmpty(m))
}

func (t mockAttest) Params(context.Context, *attestv1.QueryParamsRequest) (*attestv1.QueryParamsResponse, error) {
	return &attestv1.QueryParamsResponse{Params: proto.Clone(t.c.attestParams).(*attestv1.Params)}, nil
}

func (t mockAttest) Latest(_ context.Context, q *attestv1.QueryLatestRequest) (*attestv1.QueryLatestResponse, error) {
	q = orEmpty(q)
	return t.c.Freshness(q.AssetId, q.Kind), nil
}

func (t mockAttest) History(_ context.Context, q *attestv1.QueryHistoryRequest) (*attestv1.QueryHistoryResponse, error) {
	q = orEmpty(q)
	var list []*attestv1.Attestation
	for _, a := range t.c.attestations {
		if a.AssetId == q.AssetId && a.Kind == q.Kind {
			list = append(list, proto.Clone(a).(*attestv1.Attestation))
		}
	}
	newestFirst(list)
	if q.Limit > 0 && int(q.Limit) < len(list) {
		list = list[:q.Limit]
	}
	return &attestv1.QueryHistoryResponse{Attestations: list}, nil
}

func (t mockAttest) Attesters(_ context.Context, q *attestv1.QueryAttestersRequest) (*attestv1.QueryAttestersResponse, error) {
	set := t.c.attesters[orEmpty(q).AssetId]
	out := &attestv1.QueryAttestersResponse{}
	for _, a := range sortedKeys(set) {
		out.Attesters = append(out.Attesters, proto.Clone(set[a]).(*attestv1.Attester))
	}
	return out, nil
}

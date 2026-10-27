// SPDX-License-Identifier: Apache-2.0

package assetkit

import (
	"context"

	"google.golang.org/protobuf/proto"

	identityv1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/identity/v1"
)

func (c *MockChain) requireIdentityAgent(signer string) error {
	if signer != c.authority && !contains(c.identityParams.IdentityAgents, signer) {
		return fail(ModuleIdentity, "ERROR_CODE_NOT_IDENTITY_AGENT", "%s is not an identity agent", signer)
	}
	return nil
}

func (c *MockChain) ident(id string) (*identityv1.Identity, error) {
	x, ok := c.identities[id]
	if !ok {
		return nil, fail(ModuleIdentity, "ERROR_CODE_IDENTITY_NOT_FOUND", "identity %s not found", id)
	}
	return x, nil
}

func (c *MockChain) registerIdentity(m *identityv1.MsgRegisterIdentity) (*identityv1.MsgRegisterIdentityResponse, error) {
	if err := c.requireIdentityAgent(m.Agent); err != nil {
		return nil, err
	}
	if _, ok := c.identities[m.IdentityId]; ok {
		return nil, fail(ModuleIdentity, "ERROR_CODE_IDENTITY_EXISTS", "identity %s exists", m.IdentityId)
	}
	if _, ok := c.identityOf[m.Address]; ok {
		return nil, fail(ModuleIdentity, "ERROR_CODE_ADDRESS_ALREADY_BOUND", "%s is already bound", m.Address)
	}
	c.identities[m.IdentityId] = &identityv1.Identity{
		IdentityId: m.IdentityId, Addresses: []string{m.Address}, Country: m.Country, RegisteredBy: m.Agent,
	}
	c.identityOf[m.Address] = m.IdentityId
	c.emit("qorechain.identity.v1.EventIdentityRegistered", &identityv1.EventIdentityRegistered{
		IdentityId: m.IdentityId, Address: m.Address, Country: m.Country, Agent: m.Agent,
	})
	return &identityv1.MsgRegisterIdentityResponse{}, nil
}

func (c *MockChain) updateCountry(m *identityv1.MsgUpdateCountry) (*identityv1.MsgUpdateCountryResponse, error) {
	if err := c.requireIdentityAgent(m.Agent); err != nil {
		return nil, err
	}
	x, err := c.ident(m.IdentityId)
	if err != nil {
		return nil, err
	}
	x.Country = m.Country
	c.emit("qorechain.identity.v1.EventCountryUpdated", &identityv1.EventCountryUpdated{IdentityId: m.IdentityId, Country: m.Country})
	return &identityv1.MsgUpdateCountryResponse{}, nil
}

func (c *MockChain) bindAddress(m *identityv1.MsgBindAddress) (*identityv1.MsgBindAddressResponse, error) {
	if err := c.requireIdentityAgent(m.Agent); err != nil {
		return nil, err
	}
	x, err := c.ident(m.IdentityId)
	if err != nil {
		return nil, err
	}
	if _, ok := c.identityOf[m.Address]; ok {
		return nil, fail(ModuleIdentity, "ERROR_CODE_ADDRESS_ALREADY_BOUND", "%s is already bound", m.Address)
	}
	x.Addresses = append(x.Addresses, m.Address)
	c.identityOf[m.Address] = m.IdentityId
	c.emit("qorechain.identity.v1.EventAddressBound", &identityv1.EventAddressBound{IdentityId: m.IdentityId, Address: m.Address, Bound: true})
	return &identityv1.MsgBindAddressResponse{}, nil
}

func (c *MockChain) unbindAddress(m *identityv1.MsgUnbindAddress) (*identityv1.MsgUnbindAddressResponse, error) {
	if err := c.requireIdentityAgent(m.Agent); err != nil {
		return nil, err
	}
	x, err := c.ident(m.IdentityId)
	if err != nil {
		return nil, err
	}
	if c.identityOf[m.Address] != m.IdentityId {
		return nil, fail(ModuleIdentity, "ERROR_CODE_IDENTITY_NOT_FOUND", "%s is not bound to %s", m.Address, m.IdentityId)
	}
	kept := x.Addresses[:0]
	for _, a := range x.Addresses {
		if a != m.Address {
			kept = append(kept, a)
		}
	}
	x.Addresses = kept
	delete(c.identityOf, m.Address)
	c.emit("qorechain.identity.v1.EventAddressBound", &identityv1.EventAddressBound{IdentityId: m.IdentityId, Address: m.Address, Bound: false})
	return &identityv1.MsgUnbindAddressResponse{}, nil
}

func (c *MockChain) addClaim(m *identityv1.MsgAddClaim) (*identityv1.MsgAddClaimResponse, error) {
	issuer, ok := c.claimIssuers[m.ClaimIssuer]
	if !ok {
		return nil, fail(ModuleIdentity, "ERROR_CODE_CLAIM_ISSUER_NOT_TRUSTED", "%s is not a trusted claim issuer", m.ClaimIssuer)
	}
	if !contains(issuer.Topics, m.Topic) {
		return nil, fail(ModuleIdentity, "ERROR_CODE_CLAIM_TOPIC_NOT_ALLOWED", "topic %d not allowed", m.Topic)
	}
	x, err := c.ident(m.IdentityId)
	if err != nil {
		return nil, err
	}
	kept := x.Claims[:0]
	for _, cl := range x.Claims {
		if !(cl.Topic == m.Topic && cl.Issuer == m.ClaimIssuer) {
			kept = append(kept, cl)
		}
	}
	x.Claims = append(kept, &identityv1.Claim{
		Topic: m.Topic, Issuer: m.ClaimIssuer, DataHash: append([]byte(nil), m.DataHash...), ValidUntil: m.ValidUntil,
	})
	c.emit("qorechain.identity.v1.EventClaimAdded", &identityv1.EventClaimAdded{
		IdentityId: m.IdentityId, Topic: m.Topic, ClaimIssuer: m.ClaimIssuer, ValidUntil: m.ValidUntil,
	})
	return &identityv1.MsgAddClaimResponse{}, nil
}

func (c *MockChain) revokeClaim(m *identityv1.MsgRevokeClaim) (*identityv1.MsgRevokeClaimResponse, error) {
	x, err := c.ident(m.IdentityId)
	if err != nil {
		return nil, err
	}
	for _, cl := range x.Claims {
		if cl.Topic == m.Topic && cl.Issuer == m.ClaimIssuer && !cl.Revoked {
			cl.Revoked = true
			c.emit("qorechain.identity.v1.EventClaimRevoked", &identityv1.EventClaimRevoked{
				IdentityId: m.IdentityId, Topic: m.Topic, ClaimIssuer: m.ClaimIssuer,
			})
			return &identityv1.MsgRevokeClaimResponse{}, nil
		}
	}
	return nil, fail(ModuleIdentity, "ERROR_CODE_CLAIM_NOT_FOUND", "no claim for topic %d from %s", m.Topic, m.ClaimIssuer)
}

func (c *MockChain) removeIdentity(m *identityv1.MsgRemoveIdentity) (*identityv1.MsgRemoveIdentityResponse, error) {
	if err := c.requireIdentityAgent(m.Agent); err != nil {
		return nil, err
	}
	x, err := c.ident(m.IdentityId)
	if err != nil {
		return nil, err
	}
	for _, a := range x.Addresses {
		delete(c.identityOf, a)
	}
	delete(c.identities, m.IdentityId)
	c.emit("qorechain.identity.v1.EventIdentityRemoved", &identityv1.EventIdentityRemoved{IdentityId: m.IdentityId})
	return &identityv1.MsgRemoveIdentityResponse{}, nil
}

func (c *MockChain) setClaimIssuer(m *identityv1.MsgSetClaimIssuer) (*identityv1.MsgSetClaimIssuerResponse, error) {
	if m.Authority != c.authority {
		return nil, fail(ModuleIdentity, "ERROR_CODE_UNAUTHORIZED", "%s is not the governance authority", m.Authority)
	}
	ci := &identityv1.ClaimIssuer{}
	if m.ClaimIssuer != nil {
		ci = proto.Clone(m.ClaimIssuer).(*identityv1.ClaimIssuer)
	}
	if m.Remove {
		delete(c.claimIssuers, ci.Address)
	} else {
		c.claimIssuers[ci.Address] = ci
	}
	c.emit("qorechain.identity.v1.EventClaimIssuerChanged", &identityv1.EventClaimIssuerChanged{
		Address: ci.Address, Topics: append([]uint32(nil), ci.Topics...), Removed: m.Remove,
	})
	return &identityv1.MsgSetClaimIssuerResponse{}, nil
}

// MissingTopics returns the topics, of those asked, for which the address
// holds no valid claim (unrevoked, unexpired, from an issuer trusted for it).
func (c *MockChain) MissingTopics(address string, topics []uint32) []uint32 {
	var x *identityv1.Identity
	if id, ok := c.identityOf[address]; ok {
		x = c.identities[id]
	}
	var missing []uint32
	for _, topic := range topics {
		found := false
		if x != nil {
			for _, cl := range x.Claims {
				issuer, trusted := c.claimIssuers[cl.Issuer]
				trusted = trusted && contains(issuer.Topics, topic)
				live := cl.ValidUntil == 0 || cl.ValidUntil > c.time
				if cl.Topic == topic && !cl.Revoked && trusted && live {
					found = true
					break
				}
			}
		}
		if !found {
			missing = append(missing, topic)
		}
	}
	return missing
}

// CountryOf returns the identity country of an address and whether it has one.
func (c *MockChain) CountryOf(address string) (uint32, bool) {
	id, ok := c.identityOf[address]
	if !ok {
		return 0, false
	}
	x, ok := c.identities[id]
	if !ok {
		return 0, false
	}
	return x.Country, true
}

// mockIdentity adapts MockChain to IdentityAPI.
type mockIdentity struct{ c *MockChain }

func (i mockIdentity) RegisterIdentity(_ context.Context, m *identityv1.MsgRegisterIdentity) (*identityv1.MsgRegisterIdentityResponse, error) {
	return i.c.registerIdentity(orEmpty(m))
}

func (i mockIdentity) UpdateCountry(_ context.Context, m *identityv1.MsgUpdateCountry) (*identityv1.MsgUpdateCountryResponse, error) {
	return i.c.updateCountry(orEmpty(m))
}

func (i mockIdentity) BindAddress(_ context.Context, m *identityv1.MsgBindAddress) (*identityv1.MsgBindAddressResponse, error) {
	return i.c.bindAddress(orEmpty(m))
}

func (i mockIdentity) UnbindAddress(_ context.Context, m *identityv1.MsgUnbindAddress) (*identityv1.MsgUnbindAddressResponse, error) {
	return i.c.unbindAddress(orEmpty(m))
}

func (i mockIdentity) AddClaim(_ context.Context, m *identityv1.MsgAddClaim) (*identityv1.MsgAddClaimResponse, error) {
	return i.c.addClaim(orEmpty(m))
}

func (i mockIdentity) RevokeClaim(_ context.Context, m *identityv1.MsgRevokeClaim) (*identityv1.MsgRevokeClaimResponse, error) {
	return i.c.revokeClaim(orEmpty(m))
}

func (i mockIdentity) RemoveIdentity(_ context.Context, m *identityv1.MsgRemoveIdentity) (*identityv1.MsgRemoveIdentityResponse, error) {
	return i.c.removeIdentity(orEmpty(m))
}

func (i mockIdentity) SetClaimIssuer(_ context.Context, m *identityv1.MsgSetClaimIssuer) (*identityv1.MsgSetClaimIssuerResponse, error) {
	return i.c.setClaimIssuer(orEmpty(m))
}

func (i mockIdentity) Params(context.Context, *identityv1.QueryParamsRequest) (*identityv1.QueryParamsResponse, error) {
	return &identityv1.QueryParamsResponse{Params: proto.Clone(i.c.identityParams).(*identityv1.Params)}, nil
}

func (i mockIdentity) Identity(_ context.Context, q *identityv1.QueryIdentityRequest) (*identityv1.QueryIdentityResponse, error) {
	x, err := i.c.ident(orEmpty(q).IdentityId)
	if err != nil {
		return nil, err
	}
	return &identityv1.QueryIdentityResponse{Identity: proto.Clone(x).(*identityv1.Identity)}, nil
}

func (i mockIdentity) IdentityByAddress(_ context.Context, q *identityv1.QueryIdentityByAddressRequest) (*identityv1.QueryIdentityByAddressResponse, error) {
	q = orEmpty(q)
	id, ok := i.c.identityOf[q.Address]
	if !ok {
		return nil, fail(ModuleIdentity, "ERROR_CODE_IDENTITY_NOT_FOUND", "%s has no identity", q.Address)
	}
	x, err := i.c.ident(id)
	if err != nil {
		return nil, err
	}
	return &identityv1.QueryIdentityByAddressResponse{Identity: proto.Clone(x).(*identityv1.Identity)}, nil
}

func (i mockIdentity) ClaimIssuers(context.Context, *identityv1.QueryClaimIssuersRequest) (*identityv1.QueryClaimIssuersResponse, error) {
	out := &identityv1.QueryClaimIssuersResponse{}
	for _, a := range sortedKeys(i.c.claimIssuers) {
		out.ClaimIssuers = append(out.ClaimIssuers, proto.Clone(i.c.claimIssuers[a]).(*identityv1.ClaimIssuer))
	}
	return out, nil
}

func (i mockIdentity) IsVerified(_ context.Context, q *identityv1.QueryIsVerifiedRequest) (*identityv1.QueryIsVerifiedResponse, error) {
	q = orEmpty(q)
	missing := i.c.MissingTopics(q.Address, q.Topics)
	_, bound := i.c.identityOf[q.Address]
	return &identityv1.QueryIsVerifiedResponse{Verified: bound && len(missing) == 0, MissingTopics: missing}, nil
}

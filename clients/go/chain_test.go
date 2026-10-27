// SPDX-License-Identifier: Apache-2.0

package assetkit_test

import (
	"context"
	"errors"
	"strings"
	"testing"

	assetkit "github.com/qorechain/qorechain-asset-kit/clients/go"
	assetv1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/asset/v1"
	attestv1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/attest/v1"
	compliancev1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/compliance/v1"
	identityv1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/identity/v1"
	settlementv1 "github.com/qorechain/qorechain-asset-kit/clients/go/gen/qorechain/settlement/v1"
)

func TestChainClientReturnsChainUpgradeRequired(t *testing.T) {
	ctx := context.Background()
	var kit assetkit.AssetKit = assetkit.NewChainClient(assetkit.ChainClientOptions{RESTURL: "https://api-testnet.qore.host"})

	_, err := kit.Asset().CreateAsset(ctx, &assetv1.MsgCreateAsset{Issuer: "qor1issuer", AssetId: "bond-2030"})
	var cur *assetkit.ChainUpgradeRequired
	if !errors.As(err, &cur) {
		t.Fatalf("want *ChainUpgradeRequired, got %v", err)
	}
	if cur.Module != "x/asset" || cur.Code() != "CHAIN_UPGRADE_REQUIRED" || !strings.Contains(err.Error(), "not scheduled") {
		t.Fatalf("unexpected error %#v: %v", cur, err)
	}

	cases := []struct {
		module string
		call   func() error
	}{
		{"x/asset", func() error { _, e := kit.Asset().Asset(ctx, &assetv1.QueryAssetRequest{AssetId: "x"}); return e }},
		{"x/identity", func() error {
			_, e := kit.Identity().IsVerified(ctx, &identityv1.QueryIsVerifiedRequest{Address: "qor1a", Topics: []uint32{1}})
			return e
		}},
		{"x/compliance", func() error {
			_, e := kit.Compliance().Check(ctx, &compliancev1.QueryCheckRequest{AssetId: "x"})
			return e
		}},
		{"x/settlement", func() error {
			_, e := kit.Settlement().Affirm(ctx, &settlementv1.MsgAffirm{Party: "qor1a", Id: 1})
			return e
		}},
		{"x/attest", func() error { _, e := kit.Attest().Latest(ctx, &attestv1.QueryLatestRequest{AssetId: "x"}); return e }},
	}
	for _, c := range cases {
		var e *assetkit.ChainUpgradeRequired
		if err := c.call(); !errors.As(err, &e) || e.Module != c.module {
			t.Errorf("%s: want ChainUpgradeRequired, got %v", c.module, err)
		}
	}
}

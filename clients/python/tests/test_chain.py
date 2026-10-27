# SPDX-License-Identifier: Apache-2.0
import pytest

from qorechain_asset_kit import ChainClient, ChainUpgradeRequired, asset

chain = ChainClient(rest_url="https://api-testnet.qore.host")


def test_create_asset_raises_chain_upgrade_required():
    with pytest.raises(ChainUpgradeRequired) as info:
        chain.asset.create_asset(asset.MsgCreateAsset(issuer="qor1issuer", asset_id="bond-2030"))
    assert info.value.module == "x/asset"
    assert info.value.code == "CHAIN_UPGRADE_REQUIRED"
    assert "not scheduled" in str(info.value)


@pytest.mark.parametrize(
    "call, module",
    [
        (lambda: chain.asset.asset(asset_id="x"), "x/asset"),
        (lambda: chain.identity.is_verified(address="qor1a", topics=[1]), "x/identity"),
        (lambda: chain.compliance.check(asset_id="x"), "x/compliance"),
        (lambda: chain.settlement.affirm(party="qor1a", id=1), "x/settlement"),
        (lambda: chain.attest.latest(asset_id="x"), "x/attest"),
    ],
)
def test_every_module_names_itself(call, module):
    with pytest.raises(ChainUpgradeRequired) as info:
        call()
    assert info.value.module == module


def test_unknown_method_is_an_attribute_error():
    with pytest.raises(AttributeError):
        chain.asset.no_such_method()

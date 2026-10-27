<!-- SPDX-License-Identifier: Apache-2.0 -->

# qorechain-asset-kit (Python)

Python client for the **proposed** QoreChain regulated-asset modules: `x/asset`, `x/identity`, `x/compliance`, `x/settlement` and `x/attest`.

> These modules are a proposal. They do not exist on QoreChain, on mainnet or on the testnet, and no chain upgrade that would add them is scheduled. What works on QoreChain today is the set of EVM contracts in [`contracts/`](https://github.com/qorechain/qorechain-asset-kit/tree/main/contracts).

- `ChainClient` raises `ChainUpgradeRequired` (with `.module`, for example `"x/asset"`, and `.code == "CHAIN_UPGRADE_REQUIRED"`) on every call. It makes no network request.
- `MockChain` implements the proposed rules of [docs/proposal.md](https://github.com/qorechain/qorechain-asset-kit/blob/main/docs/proposal.md) in memory, so that applications can be built and tested now. Refusals raise `MockChainError` with the proposed error code name (for example `ERROR_CODE_ADDRESS_FROZEN`).
- Types generated from [`proto/`](https://github.com/qorechain/qorechain-asset-kit/tree/main/proto) are in `qorechain_asset_kit.asset`, `.identity`, `.compliance`, `.settlement` and `.attest`.

Python 3.10 or later.

```python
from qorechain_asset_kit import MockChain, MockChainError, asset

chain = MockChain()
chain.asset.create_asset(issuer="qor1issuer", asset_id="bond-2030", flags={"freezable": True})
chain.asset.mint(agent="qor1issuer", asset_id="bond-2030", to="qor1alice", amount="100")
chain.asset.freeze(agent="qor1issuer", asset_id="bond-2030", holder="qor1alice", frozen=True)
try:
    chain.asset.transfer(from_="qor1alice", asset_id="bond-2030", to="qor1bob", amount="1")
except MockChainError as e:
    print(e.code)  # ERROR_CODE_ADDRESS_FROZEN
```

Methods take either the generated message, a dict, or keyword arguments. The proto field `from` is a Python keyword: pass it as `from_` (or inside a dict as `"from"`).

Mock helpers: `set_hybrid_key`, `has_hybrid_key`, `fund_bank`, `bank_balance`, `advance(blocks, seconds)`, `height`, `time`, `events(type=None)`, `define_module_logic(module_id, fn)`.

## Development

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt && pip install -e .
pytest
scripts/gen.sh   # regenerate the protobuf code (protoc 36.2)
```

Licence: Apache-2.0. Copyright 2026 QoreChain Association.

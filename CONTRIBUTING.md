# Contributing to the QoreChain Asset Kit

Thanks for your interest. Issues, pull requests and discussion are welcome.

## Layout

| Path | Contents |
|---|---|
| `proto` | proposed module interfaces (not on chain) |
| `clients/ts`, `clients/python`, `clients/go`, `clients/java` | clients generated from `proto`, plus `ChainClient` and `MockChain` |
| `contracts` | Foundry project: EVM adapters, tests and deployment scripts |
| `packages/issuer-console` | React app over the EVM adapters |
| `docs`, `legal` | documentation and legal templates |

## Build and test

```bash
buf lint                                                        # proto
pnpm install && pnpm -r build && pnpm -r typecheck && pnpm -r test   # TypeScript client and console
(cd clients/python && pip install -r requirements-dev.txt && pip install -e . && pytest)
(cd clients/go && gofmt -l . && go vet ./... && go test ./...)
(cd clients/java && mvn -B test)
(cd contracts && forge fmt --check && forge build && forge test)
```

## Changing a proposed interface

The `.proto` files are the source of truth. Change them, keep the `PROPOSAL` notice at the top of every file, regenerate the code of every client (`pnpm gen` in `clients/ts`, `scripts/gen.sh` in the other clients), update `docs/proposal.md`, and make every `MockChain` follow the new rule in the same pull request, with tests.

## Dependencies

Pin exact versions. A new third-party version must be at least 14 days old (`pnpm-workspace.yaml` enforces this for npm packages). Do not copy GPL or MPL source into this repository; add it as a dependency and list it in `NOTICE`.

## Pull requests

- Keep changes focused; add tests for behaviour changes.
- Every source file starts with an SPDX licence identifier.
- Do not describe anything as available on QoreChain mainnet unless it is.

## Code of Conduct

By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).

## Security

Do not open public issues for vulnerabilities; see [SECURITY.md](SECURITY.md).

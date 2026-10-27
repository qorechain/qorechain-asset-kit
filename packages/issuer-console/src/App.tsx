// SPDX-License-Identifier: Apache-2.0
import { useCallback, useState } from "react";
import type { Address } from "viem";
import { Connect } from "./components/Connect";
import { CreateToken } from "./components/CreateToken";
import { TokenPanel } from "./components/TokenPanel";
import { Wordmark } from "./components/Wordmark";
import type { Connection } from "./lib/clients";
import { DOCS_EVM_ADAPTERS, networkStatus } from "./lib/network";

export function App() {
  const [connection, setConnection] = useState<Connection>();
  const [created, setCreated] = useState<Address>();
  const onConnect = useCallback((c?: Connection) => setConnection(c), []);
  const status = networkStatus(connection?.chainId);

  return (
    <main>
      <header>
        <Wordmark />
        <span className="title">Issuer console</span>
      </header>

      {status === "mainnet" && (
        <div className="banner danger" role="alert">
          You are on QoreChain mainnet (chain 9801). The hybrid-holder guard is testnet only: the pqcKeyStatus
          precompile (0x0A02) is not active on mainnet, so the guard fails closed and a token using it cannot move
          between ordinary holders. Creating a token is disabled here.
        </div>
      )}
      {status === "other" && (
        <div className="banner">Chain {connection?.chainId} is not a QoreChain network. Switch to the QoreChain Testnet (9800).</div>
      )}

      <div className="banner info">
        <strong>Before any transaction:</strong> on QoreChain every EVM transaction needs the sender's registered
        ML-DSA-87 key and an open EVM authorization window, opened on the native lane by a hybrid-signed
        MsgOpenEVMWindow (with no allowed targets for deployments). This console does not open windows. See{" "}
        <a href={DOCS_EVM_ADAPTERS} target="_blank" rel="noreferrer noopener">
          docs/evm-adapters.md
        </a>
        .
      </div>

      <Connect connection={connection} onConnect={onConnect} />
      <CreateToken connection={connection} onCreated={setCreated} />
      <TokenPanel connection={connection} initialAddress={created} />

      <footer className="muted small">
        No backend: the console talks only to your wallet. Apache-2.0, QoreChain Association.
      </footer>
    </main>
  );
}

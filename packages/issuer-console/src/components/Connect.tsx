// SPDX-License-Identifier: Apache-2.0
import { useEffect, useState } from "react";
import type { Address } from "viem";
import { discoverProviders, safeIcon, type Eip6963ProviderDetail } from "../lib/eip6963";
import { ADD_TESTNET_PARAMS, networkStatus } from "../lib/network";
import { clientsFor, errorMessage, type Connection } from "../lib/clients";

export function Connect({ connection, onConnect }: { connection?: Connection; onConnect: (c?: Connection) => void }) {
  const [providers, setProviders] = useState<Eip6963ProviderDetail[]>([]);
  const [error, setError] = useState<string>();

  useEffect(() => discoverProviders(window, setProviders), []);

  useEffect(() => {
    const p = connection?.provider;
    if (!p?.on) return;
    const reconnect = async () => {
      try {
        const [account] = (await p.request({ method: "eth_accounts" })) as Address[];
        if (!account) return onConnect(undefined);
        const chainId = Number(await p.request({ method: "eth_chainId" }));
        onConnect({ provider: p, account, chainId, ...clientsFor(p, account) });
      } catch (e) {
        setError(errorMessage(e));
      }
    };
    p.on("chainChanged", reconnect);
    p.on("accountsChanged", reconnect);
    return () => {
      p.removeListener?.("chainChanged", reconnect);
      p.removeListener?.("accountsChanged", reconnect);
    };
  }, [connection?.provider, onConnect]);

  async function connect(d: Eip6963ProviderDetail) {
    setError(undefined);
    try {
      const [account] = (await d.provider.request({ method: "eth_requestAccounts" })) as Address[];
      const chainId = Number(await d.provider.request({ method: "eth_chainId" }));
      onConnect({ provider: d.provider, account: account!, chainId, ...clientsFor(d.provider, account!) });
    } catch (e) {
      setError(errorMessage(e));
    }
  }

  async function addTestnet() {
    if (!connection) return;
    setError(undefined);
    try {
      await connection.provider.request({ method: "wallet_addEthereumChain", params: [ADD_TESTNET_PARAMS] });
    } catch (e) {
      setError(errorMessage(e));
    }
  }

  const status = networkStatus(connection?.chainId);
  return (
    <section className="card">
      <h2>Wallet</h2>
      {connection ? (
        <div className="row">
          <span className="mono">{connection.account}</span>
          <span className={`pill ${status}`}>chain {connection.chainId}</span>
          {status !== "testnet" && <button onClick={addTestnet}>Add or switch to QoreChain Testnet</button>}
          <button className="secondary" onClick={() => onConnect(undefined)}>
            Disconnect
          </button>
        </div>
      ) : providers.length === 0 ? (
        <p className="muted">
          No wallet announced itself through EIP-6963. Install or unlock a wallet that supports EIP-6963 and reload.
        </p>
      ) : (
        <div className="row">
          {providers.map((d) => (
            <button key={d.info.uuid} onClick={() => connect(d)}>
              {safeIcon(d.info.icon) && <img src={safeIcon(d.info.icon)} alt="" width={18} height={18} />}
              {d.info.name}
            </button>
          ))}
        </div>
      )}
      <p className="muted small">
        Works with any wallet that announces itself through EIP-6963 and can sign EVM transactions on the QoreChain
        Testnet.
      </p>
      {error && <p className="error">{error}</p>}
    </section>
  );
}

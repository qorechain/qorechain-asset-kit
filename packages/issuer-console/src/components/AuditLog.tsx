// SPDX-License-Identifier: Apache-2.0
import { useState } from "react";
import { formatUnits, type Address } from "viem";
import { tokenAbi } from "../lib/abis";
import { decodeAuditLogs, newestFirst, type AuditEntry, type RawLog } from "../lib/events";
import { candidateHolders, positiveHolders, type Holder } from "../lib/holders";
import { planRanges } from "../lib/ranges";
import { errorMessage, type Connection } from "../lib/clients";
import { addressUrl, txUrl } from "../lib/network";
import type { TokenInfo } from "./TokenPanel";

export function AuditLog({ connection, token }: { connection: Connection; token: TokenInfo }) {
  const [fromBlock, setFromBlock] = useState("0");
  const [chunk, setChunk] = useState("10000");
  const [progress, setProgress] = useState<string>();
  const [entries, setEntries] = useState<AuditEntry[]>([]);
  const [holders, setHolders] = useState<Holder[]>([]);
  const [error, setError] = useState<string>();
  const [busy, setBusy] = useState(false);

  async function scan() {
    setBusy(true);
    setError(undefined);
    setEntries([]);
    setHolders([]);
    try {
      const latest = await connection.public.getBlockNumber();
      const ranges = planRanges(BigInt(fromBlock || "0"), latest, BigInt(chunk || "10000"));
      const addresses = [token.address, token.identityRegistry, token.guard].filter(Boolean) as Address[];
      const logs: RawLog[] = [];
      for (const [i, r] of ranges.entries()) {
        setProgress(`blocks ${r.fromBlock} to ${r.toBlock} (${i + 1} of ${ranges.length})`);
        logs.push(...((await connection.public.getLogs({ address: addresses, fromBlock: r.fromBlock, toBlock: r.toBlock })) as RawLog[]));
      }
      const decoded = decodeAuditLogs(logs);
      setEntries(newestFirst(decoded));
      setProgress(`confirming balances`);
      const confirmed = new Map<string, bigint>();
      for (const h of candidateHolders(decoded, token.address)) {
        const balance = await connection.public.readContract({ address: token.address, abi: tokenAbi, functionName: "balanceOf", args: [h as Address] });
        confirmed.set(h, balance);
      }
      setHolders(positiveHolders(confirmed));
      setProgress(`scanned blocks ${fromBlock} to ${latest}: ${decoded.length} events`);
    } catch (e) {
      setError(errorMessage(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="card">
      <h2>Holders and audit log</h2>
      <p className="muted small">
        Read from chain events of the token{token.identityRegistry ? ", its identity registry" : ""}
        {token.guard ? " and its guard" : ""}. Start at or before the deployment block for a complete holder list;
        every balance shown is confirmed with balanceOf.
      </p>
      <div className="row">
        <label>
          From block
          <input value={fromBlock} onChange={(e) => setFromBlock(e.target.value.replace(/\D/g, ""))} />
        </label>
        <label>
          Blocks per request
          <input value={chunk} onChange={(e) => setChunk(e.target.value.replace(/\D/g, ""))} />
        </label>
        <button disabled={busy} onClick={scan}>
          {busy ? "Scanning..." : "Scan"}
        </button>
      </div>
      {progress && <p className="muted small">{progress}</p>}
      {error && <p className="error">{error}</p>}
      {holders.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Holder</th>
              <th className="num">Balance</th>
            </tr>
          </thead>
          <tbody>
            {holders.map((h) => (
              <tr key={h.address}>
                <td>
                  <a className="mono" href={addressUrl(h.address)} target="_blank" rel="noreferrer noopener">
                    {h.address}
                  </a>
                </td>
                <td className="num">{formatUnits(h.balance, token.decimals)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {entries.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Block</th>
              <th>Event</th>
              <th>Details</th>
              <th>Transaction</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((e) => (
              <tr key={`${e.txHash}-${e.logIndex}`}>
                <td>{e.blockNumber.toString()}</td>
                <td>{e.name}</td>
                <td>{e.summary}</td>
                <td>
                  <a className="mono" href={txUrl(e.txHash)} target="_blank" rel="noreferrer noopener">
                    {e.txHash.slice(0, 10)}...
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}

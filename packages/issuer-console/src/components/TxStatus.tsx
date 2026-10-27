// SPDX-License-Identifier: Apache-2.0
import { useState } from "react";
import type { Hex } from "viem";
import { errorMessage, type Connection } from "../lib/clients";
import { txUrl } from "../lib/network";

export interface TxState {
  label?: string;
  hash?: Hex;
  status?: "pending" | "done" | "failed";
  error?: string;
}

/** Runs a write, waits for the receipt and keeps its state for display. */
export function useTx(connection: Connection | undefined) {
  const [state, setState] = useState<TxState>({});
  async function run(label: string, send: () => Promise<Hex>): Promise<boolean> {
    if (!connection) return false;
    setState({ label, status: "pending" });
    try {
      const hash = await send();
      setState({ label, hash, status: "pending" });
      const receipt = await connection.public.waitForTransactionReceipt({ hash });
      const ok = receipt.status === "success";
      setState({ label, hash, status: ok ? "done" : "failed", error: ok ? undefined : "reverted" });
      return ok;
    } catch (e) {
      setState((s) => ({ ...s, label, status: "failed", error: errorMessage(e) }));
      return false;
    }
  }
  return { state, run };
}

export function TxStatus({ state }: { state: TxState }) {
  if (!state.status) return null;
  return (
    <p className={state.status === "failed" ? "error" : "muted"}>
      {state.label}: {state.status}
      {state.hash && (
        <>
          {" "}
          <a href={txUrl(state.hash)} target="_blank" rel="noreferrer noopener" className="mono">
            {state.hash.slice(0, 10)}...
          </a>
        </>
      )}
      {state.error && <> ({state.error})</>}
    </p>
  );
}

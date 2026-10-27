// SPDX-License-Identifier: Apache-2.0
import type { AuditEntry } from "./events";

const ZERO = /^0x0{40}$/i;

/**
 * Net balances implied by the Transfer events of one token, oldest first. Only complete if the scan
 * started at or before the token's deployment block; the console confirms each with balanceOf.
 */
export function balancesFromTransfers(entries: readonly AuditEntry[], token: string): Map<string, bigint> {
  const balances = new Map<string, bigint>();
  const ordered = [...entries].sort((x, y) =>
    x.blockNumber === y.blockNumber ? x.logIndex - y.logIndex : x.blockNumber < y.blockNumber ? -1 : 1,
  );
  for (const e of ordered) {
    if (e.name !== "Transfer" || e.emitter.toLowerCase() !== token.toLowerCase()) continue;
    const from = String(e.args.from).toLowerCase();
    const to = String(e.args.to).toLowerCase();
    const value = e.args.value as bigint;
    if (!ZERO.test(from)) balances.set(from, (balances.get(from) ?? 0n) - value);
    if (!ZERO.test(to)) balances.set(to, (balances.get(to) ?? 0n) + value);
  }
  return balances;
}

/** Addresses ever seen in a Transfer of the token, the candidates to confirm with balanceOf. */
export function candidateHolders(entries: readonly AuditEntry[], token: string): string[] {
  return [...balancesFromTransfers(entries, token).keys()].sort();
}

export interface Holder {
  address: string;
  balance: bigint;
}

/** Holders with a positive balance, largest first, ties by address. */
export function positiveHolders(balances: Map<string, bigint>): Holder[] {
  return [...balances.entries()]
    .filter(([, b]) => b > 0n)
    .map(([address, balance]) => ({ address, balance }))
    .sort((x, y) => (x.balance === y.balance ? (x.address < y.address ? -1 : 1) : x.balance > y.balance ? -1 : 1));
}

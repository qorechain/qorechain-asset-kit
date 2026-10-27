// SPDX-License-Identifier: Apache-2.0
import { decodeEventLog, type Hex } from "viem";
import { auditEventsAbi } from "./abis";

/** The fields of an RPC log the console needs. */
export interface RawLog {
  address: string;
  topics: readonly Hex[];
  data: Hex;
  blockNumber: bigint | null;
  logIndex: number | null;
  transactionHash: Hex | null;
}

export interface AuditEntry {
  blockNumber: bigint;
  logIndex: number;
  txHash: string;
  /** Contract that emitted the event (token, identity registry or guard). */
  emitter: string;
  name: string;
  args: Record<string, unknown>;
  summary: string;
}

function short(a: unknown): string {
  const s = String(a);
  return /^0x[0-9a-fA-F]{40}$/.test(s) ? `${s.slice(0, 8)}...${s.slice(-4)}` : s;
}

function describe(name: string, a: Record<string, unknown>): string {
  switch (name) {
    case "Transfer":
      if (/^0x0{40}$/i.test(String(a.from))) return `mint ${a.value} to ${short(a.to)}`;
      if (/^0x0{40}$/i.test(String(a.to))) return `burn ${a.value} from ${short(a.from)}`;
      return `transfer ${a.value} from ${short(a.from)} to ${short(a.to)}`;
    case "AddressFrozen":
      return `${a.isFrozen ? "freeze" : "unfreeze"} ${short(a.account)}`;
    case "TokensFrozen":
      return `freeze ${a.amount} of ${short(a.account)}`;
    case "TokensUnfrozen":
      return `unfreeze ${a.amount} of ${short(a.account)}`;
    case "Paused":
      return `pause by ${short(a.account)}`;
    case "Unpaused":
      return `unpause by ${short(a.account)}`;
    case "Mint":
      return `mint ${a.value} to ${short(a.account)} by ${short(a.minter)}`;
    case "Burn":
      return `burn ${a.value} from ${short(a.account)} by ${short(a.burner)}`;
    case "RecoverySuccess":
      return `recovery from ${short(a.lostWallet)} to ${short(a.newWallet)}`;
    case "IdentityRegistered":
      return `identity ${short(a.identity)} registered for ${short(a.investor)}`;
    case "IdentityRemoved":
      return `identity ${short(a.identity)} removed for ${short(a.investor)}`;
    case "ExemptionSet":
      return `${a.exempt ? "exempt" : "un-exempt"} ${short(a.account)} (${a.reason})`;
    default:
      return name;
  }
}

/** Decodes the logs the audit log knows; other logs are skipped. */
export function decodeAuditLogs(logs: readonly RawLog[]): AuditEntry[] {
  const out: AuditEntry[] = [];
  for (const log of logs) {
    if (log.topics.length === 0) continue;
    try {
      const decoded = decodeEventLog({
        abi: auditEventsAbi,
        topics: log.topics as [Hex, ...Hex[]],
        data: log.data,
        strict: true,
      });
      const args = (decoded.args ?? {}) as Record<string, unknown>;
      out.push({
        blockNumber: log.blockNumber ?? 0n,
        logIndex: log.logIndex ?? 0,
        txHash: log.transactionHash ?? "",
        emitter: log.address,
        name: decoded.eventName,
        args,
        summary: describe(decoded.eventName, args),
      });
    } catch {
      // Not an audit event (for example an Approval or a role change): ignored.
    }
  }
  return out;
}

/** Newest first: by block, then by log index. */
export function newestFirst(entries: readonly AuditEntry[]): AuditEntry[] {
  return [...entries].sort((x, y) =>
    x.blockNumber === y.blockNumber ? y.logIndex - x.logIndex : x.blockNumber > y.blockNumber ? -1 : 1,
  );
}

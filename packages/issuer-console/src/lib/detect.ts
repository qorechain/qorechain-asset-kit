// SPDX-License-Identifier: Apache-2.0

export type TokenKind = "erc3643" | "cmtat" | "unknown";

/** Results of read-only probes on a token address; undefined means the call reverted. */
export interface TokenProbe {
  identityRegistry?: string;
  ruleEngine?: string;
}

/**
 * ERC-3643 (T-REX) tokens expose identityRegistry(); CMTAT v3 tokens with a rule engine expose
 * ruleEngine(). A contract that answers both is treated as ERC-3643, whose compliance is the stronger
 * contract on transfers.
 */
export function detectTokenKind(probe: TokenProbe): TokenKind {
  if (probe.identityRegistry && /^0x[0-9a-fA-F]{40}$/.test(probe.identityRegistry)) return "erc3643";
  if (probe.ruleEngine !== undefined && /^0x[0-9a-fA-F]{40}$/.test(probe.ruleEngine)) return "cmtat";
  return "unknown";
}

export function isZeroAddress(a: string | undefined): boolean {
  return !a || /^0x0{40}$/i.test(a);
}

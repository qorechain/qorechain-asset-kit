// SPDX-License-Identifier: Apache-2.0

export interface BlockRange {
  fromBlock: bigint;
  toBlock: bigint;
}

/** Splits [from, to] into inclusive chunks of at most `chunk` blocks, oldest first. */
export function planRanges(from: bigint, to: bigint, chunk: bigint): BlockRange[] {
  if (chunk <= 0n) throw new RangeError("chunk must be positive");
  if (from < 0n || to < from) return [];
  const out: BlockRange[] = [];
  for (let start = from; start <= to; start += chunk) {
    const end = start + chunk - 1n < to ? start + chunk - 1n : to;
    out.push({ fromBlock: start, toBlock: end });
  }
  return out;
}

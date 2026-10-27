// SPDX-License-Identifier: Apache-2.0
import { describe, expect, it } from "vitest";
import { encodeAbiParameters, encodeEventTopics, parseAbi, type Hex } from "viem";
import { auditEventsAbi } from "./abis";
import { decodeAuditLogs, newestFirst, type RawLog } from "./events";
import { balancesFromTransfers, candidateHolders, positiveHolders } from "./holders";
import { planRanges } from "./ranges";
import { detectTokenKind, isZeroAddress } from "./detect";
import { canCreateToken, networkStatus } from "./network";
import { mergeAnnouncement, safeIcon, type Eip6963ProviderDetail } from "./eip6963";

const TOKEN = "0x00000000000000000000000000000000000000aa";
const REGISTRY = "0x00000000000000000000000000000000000000bb";
const ZERO = "0x0000000000000000000000000000000000000000";
const A = "0x1111111111111111111111111111111111111111";
const B = "0x2222222222222222222222222222222222222222";
const C = "0x3333333333333333333333333333333333333333";

let index = 0;
function log(address: string, block: bigint, topics: Hex[], data: Hex = "0x"): RawLog {
  return { address, topics, data, blockNumber: block, logIndex: index++, transactionHash: `0x${"ab".repeat(32)}` };
}

function transfer(block: bigint, from: string, to: string, value: bigint): RawLog {
  const topics = encodeEventTopics({ abi: auditEventsAbi, eventName: "Transfer", args: { from: from as Hex, to: to as Hex } });
  return log(TOKEN, block, topics as Hex[], encodeAbiParameters([{ type: "uint256" }], [value]));
}

describe("audit log decoding", () => {
  it("decodes both AddressFrozen layouts and skips unknown events", () => {
    const trex = parseAbi(["event AddressFrozen(address indexed a, bool indexed f, address indexed o)"]);
    const cmtat = parseAbi(["event AddressFrozen(address indexed a, bool indexed f, address indexed e, bytes d)"]);
    const approval = parseAbi(["event Approval(address indexed owner, address indexed spender, uint256 value)"]);
    const logs: RawLog[] = [
      log(TOKEN, 5n, encodeEventTopics({ abi: trex, eventName: "AddressFrozen", args: { a: A, f: true, o: B } }) as Hex[]),
      log(
        TOKEN,
        6n,
        encodeEventTopics({ abi: cmtat, eventName: "AddressFrozen", args: { a: A, f: false, e: B } }) as Hex[],
        encodeAbiParameters([{ type: "bytes" }], ["0x"]),
      ),
      log(
        TOKEN,
        7n,
        encodeEventTopics({ abi: approval, eventName: "Approval", args: { owner: A, spender: B } }) as Hex[],
        encodeAbiParameters([{ type: "uint256" }], [1n]),
      ),
    ];
    const entries = decodeAuditLogs(logs);
    expect(entries.map((e) => e.summary)).toEqual([`freeze 0x111111...1111`, `unfreeze 0x111111...1111`]);
  });

  it("decodes identity and exemption events and sorts newest first", () => {
    const reg = encodeEventTopics({ abi: auditEventsAbi, eventName: "IdentityRegistered", args: { investor: A, identity: C } });
    const ex = encodeEventTopics({ abi: auditEventsAbi, eventName: "ExemptionSet", args: { account: C } });
    const entries = newestFirst(
      decodeAuditLogs([
        log(REGISTRY, 10n, reg as Hex[]),
        log(TOKEN, 12n, ex as Hex[], encodeAbiParameters([{ type: "bool" }, { type: "string" }], [true, "vault contract"])),
        transfer(12n, ZERO, A, 5n),
      ]),
    );
    expect(entries.map((e) => e.name)).toEqual(["Transfer", "ExemptionSet", "IdentityRegistered"]);
    expect(entries[0]!.summary).toBe("mint 5 to 0x111111...1111");
    expect(entries[1]!.summary).toContain("vault contract");
  });
});

describe("holders", () => {
  it("nets transfers and keeps positive balances only", () => {
    const entries = decodeAuditLogs([
      transfer(1n, ZERO, A, 100n),
      transfer(2n, A, B, 40n),
      transfer(3n, B, C, 40n),
      transfer(4n, A, ZERO, 10n),
    ]);
    const balances = balancesFromTransfers(entries, TOKEN);
    expect(positiveHolders(balances)).toEqual([
      { address: A, balance: 50n },
      { address: C, balance: 40n },
    ]);
    expect(candidateHolders(entries, TOKEN)).toEqual([A, B, C]);
    expect(balancesFromTransfers(entries, REGISTRY).size).toBe(0);
  });
});

describe("ranges", () => {
  it("plans inclusive chunks", () => {
    expect(planRanges(0n, 25n, 10n)).toEqual([
      { fromBlock: 0n, toBlock: 9n },
      { fromBlock: 10n, toBlock: 19n },
      { fromBlock: 20n, toBlock: 25n },
    ]);
    expect(planRanges(5n, 5n, 10_000n)).toEqual([{ fromBlock: 5n, toBlock: 5n }]);
    expect(planRanges(10n, 5n, 10n)).toEqual([]);
    expect(() => planRanges(0n, 1n, 0n)).toThrow();
  });
});

describe("token kind and network", () => {
  it("detects ERC-3643 and CMTAT", () => {
    expect(detectTokenKind({ identityRegistry: REGISTRY })).toBe("erc3643");
    expect(detectTokenKind({ ruleEngine: ZERO })).toBe("cmtat");
    expect(detectTokenKind({})).toBe("unknown");
    expect(isZeroAddress(ZERO)).toBe(true);
  });

  it("allows token creation on the testnet only", () => {
    expect(networkStatus(9800)).toBe("testnet");
    expect(networkStatus(9801)).toBe("mainnet");
    expect(canCreateToken(9801)).toBe(false);
    expect(canCreateToken(9800)).toBe(true);
    expect(canCreateToken(undefined)).toBe(false);
  });
});

describe("EIP-6963", () => {
  const provider = { request: async () => null };
  const detail = (uuid: string, name: string): Eip6963ProviderDetail => ({ info: { uuid, name, icon: "", rdns: "x" }, provider });

  it("merges announcements by uuid", () => {
    let list = mergeAnnouncement([], detail("1", "Wallet A"));
    list = mergeAnnouncement(list, detail("2", "Wallet B"));
    list = mergeAnnouncement(list, detail("1", "Wallet A v2"));
    expect(list.map((d) => d.info.name)).toEqual(["Wallet A v2", "Wallet B"]);
    expect(mergeAnnouncement(list, { info: { uuid: "", name: "", icon: "", rdns: "" }, provider })).toBe(list);
  });

  it("renders only data: icons", () => {
    expect(safeIcon("data:image/svg+xml;base64,AAAA")).toBeDefined();
    expect(safeIcon("https://example.org/icon.png")).toBeUndefined();
  });
});

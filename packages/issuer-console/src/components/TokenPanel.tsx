// SPDX-License-Identifier: Apache-2.0
import { useEffect, useState } from "react";
import { formatUnits, isAddress, parseUnits, type Address } from "viem";
import { cmtatAbi, erc3643Abi, guardAbi, identityRegistryAbi, ruleAbi, tokenAbi } from "../lib/abis";
import { detectTokenKind, isZeroAddress, type TokenKind } from "../lib/detect";
import { errorMessage, type Connection } from "../lib/clients";
import { addressUrl } from "../lib/network";
import { TxStatus, useTx } from "./TxStatus";
import { AuditLog } from "./AuditLog";

export interface TokenInfo {
  address: Address;
  kind: TokenKind;
  name: string;
  symbol: string;
  decimals: number;
  totalSupply: bigint;
  paused: boolean;
  version?: string;
  identityRegistry?: Address;
  ruleEngine?: Address;
  guard?: Address;
}

async function tryRead<T>(p: Promise<T>): Promise<T | undefined> {
  try {
    return await p;
  } catch {
    return undefined;
  }
}

export async function loadToken(c: Connection, address: Address): Promise<TokenInfo> {
  const read = <T,>(abi: readonly unknown[], functionName: string, args: unknown[] = []) =>
    c.public.readContract({ address, abi: abi as never, functionName: functionName as never, args: args as never }) as Promise<T>;
  const [identityRegistry, ruleEngine] = await Promise.all([
    tryRead(read<Address>(erc3643Abi, "identityRegistry")),
    tryRead(read<Address>(cmtatAbi, "ruleEngine")),
  ]);
  const kind = detectTokenKind({ identityRegistry, ruleEngine });
  const [name, symbol, decimals, totalSupply, paused, version] = await Promise.all([
    read<string>(tokenAbi, "name"),
    read<string>(tokenAbi, "symbol"),
    read<number>(tokenAbi, "decimals"),
    read<bigint>(tokenAbi, "totalSupply"),
    tryRead(read<boolean>(tokenAbi, "paused")),
    tryRead(read<string>(cmtatAbi, "version")),
  ]);
  let guard: Address | undefined;
  if (kind === "cmtat" && ruleEngine && !isZeroAddress(ruleEngine)) {
    guard = await tryRead(
      c.public.readContract({ address: ruleEngine, abi: ruleAbi, functionName: "guard" }) as Promise<Address>,
    );
  }
  return {
    address,
    kind,
    name,
    symbol,
    decimals: Number(decimals),
    totalSupply,
    paused: paused ?? false,
    version,
    identityRegistry: kind === "erc3643" ? identityRegistry : undefined,
    ruleEngine: kind === "cmtat" ? ruleEngine : undefined,
    guard,
  };
}

export function TokenPanel({ connection, initialAddress }: { connection?: Connection; initialAddress?: Address }) {
  const [input, setInput] = useState<string>(initialAddress ?? "");
  const [token, setToken] = useState<TokenInfo>();
  const [error, setError] = useState<string>();

  async function open(address: string) {
    setError(undefined);
    setToken(undefined);
    if (!connection) return setError("Connect a wallet first.");
    if (!isAddress(address)) return setError("Not an address.");
    try {
      setToken(await loadToken(connection, address));
    } catch (e) {
      setError(`Could not read a token at this address: ${errorMessage(e)}`);
    }
  }

  useEffect(() => {
    if (initialAddress) {
      setInput(initialAddress);
      void open(initialAddress);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialAddress, connection?.chainId]);

  return (
    <>
      <section className="card">
        <h2>Open a token</h2>
        <div className="row">
          <input className="grow mono" placeholder="0x... (CMTAT or ERC-3643 token)" value={input} onChange={(e) => setInput(e.target.value)} />
          <button disabled={!connection} onClick={() => open(input)}>
            Open
          </button>
        </div>
        {error && <p className="error">{error}</p>}
        {token && (
          <dl className="facts">
            <dt>Standard</dt>
            <dd>{token.kind === "erc3643" ? "ERC-3643 (T-REX)" : token.kind === "cmtat" ? "CMTAT" : "unknown"}{token.version ? ` ${token.version}` : ""}</dd>
            <dt>Name</dt>
            <dd>
              {token.name} ({token.symbol})
            </dd>
            <dt>Decimals</dt>
            <dd>{token.decimals}</dd>
            <dt>Total supply</dt>
            <dd>{formatUnits(token.totalSupply, token.decimals)}</dd>
            <dt>Paused</dt>
            <dd>{token.paused ? "yes" : "no"}</dd>
            {token.identityRegistry && (
              <>
                <dt>Identity registry</dt>
                <dd className="mono">{token.identityRegistry}</dd>
              </>
            )}
            {token.ruleEngine && (
              <>
                <dt>Rule engine</dt>
                <dd className="mono">{token.ruleEngine}</dd>
              </>
            )}
            {token.guard && (
              <>
                <dt>Hybrid-holder guard</dt>
                <dd>
                  <a className="mono" href={addressUrl(token.guard)} target="_blank" rel="noreferrer noopener">
                    {token.guard}
                  </a>
                </dd>
              </>
            )}
          </dl>
        )}
      </section>
      {token && connection && (
        <>
          <Actions connection={connection} token={token} onChanged={() => open(token.address)} />
          {token.kind === "erc3643" && token.identityRegistry && <Identity connection={connection} registry={token.identityRegistry} />}
          {token.guard && <GuardPanel connection={connection} guard={token.guard} />}
          <AuditLog connection={connection} token={token} />
        </>
      )}
    </>
  );
}

function Actions({ connection, token, onChanged }: { connection: Connection; token: TokenInfo; onChanged: () => void }) {
  const { state, run } = useTx(connection);
  const [account, setAccount] = useState("");
  const [to, setTo] = useState("");
  const [amount, setAmount] = useState("");

  const write = (label: string, functionName: string, args: unknown[]) =>
    run(label, () =>
      connection.wallet.writeContract({
        address: token.address,
        abi: tokenAbi,
        functionName: functionName as never,
        args: args as never,
        account: connection.account,
        chain: null,
      }),
    ).then((ok) => ok && onChanged());

  const value = () => parseUnits(amount || "0", token.decimals);
  const valid = isAddress(account);

  return (
    <section className="card">
      <h2>Agent actions</h2>
      <p className="muted small">The connected account needs the matching role (CMTAT) or the agent role (ERC-3643).</p>
      <div className="grid">
        <label>
          Account
          <input className="mono" value={account} onChange={(e) => setAccount(e.target.value)} placeholder="0x..." />
        </label>
        <label>
          Amount
          <input value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="0" />
        </label>
        <label>
          Receiver (forced transfer)
          <input className="mono" value={to} onChange={(e) => setTo(e.target.value)} placeholder="0x..." />
        </label>
      </div>
      <div className="row">
        <button disabled={!valid} onClick={() => write("Mint", "mint", [account, value()])}>Mint</button>
        <button disabled={!valid} onClick={() => write("Burn", "burn", [account, value()])}>Burn</button>
        <button disabled={!valid} onClick={() => write("Freeze", "setAddressFrozen", [account, true])}>Freeze</button>
        <button disabled={!valid} onClick={() => write("Unfreeze", "setAddressFrozen", [account, false])}>Unfreeze</button>
        <button disabled={!valid || !isAddress(to)} onClick={() => write("Forced transfer", "forcedTransfer", [account, to, value()])}>
          Forced transfer
        </button>
        <button className="secondary" onClick={() => write(token.paused ? "Unpause" : "Pause", token.paused ? "unpause" : "pause", [])}>
          {token.paused ? "Unpause" : "Pause"}
        </button>
      </div>
      <TxStatus state={state} />
    </section>
  );
}

function Identity({ connection, registry }: { connection: Connection; registry: Address }) {
  const { state, run } = useTx(connection);
  const [wallet, setWallet] = useState("");
  const [onchainId, setOnchainId] = useState("");
  const [country, setCountry] = useState("756");
  const [lookup, setLookup] = useState<string>();

  const write = (label: string, functionName: "registerIdentity" | "deleteIdentity", args: unknown[]) =>
    run(label, () =>
      connection.wallet.writeContract({
        address: registry,
        abi: identityRegistryAbi,
        functionName,
        args: args as never,
        account: connection.account,
        chain: null,
      }),
    );

  async function check() {
    if (!isAddress(wallet)) return;
    try {
      const verified = await connection.public.readContract({ address: registry, abi: identityRegistryAbi, functionName: "isVerified", args: [wallet] });
      setLookup(verified ? "verified" : "not verified");
    } catch (e) {
      setLookup(errorMessage(e));
    }
  }

  return (
    <section className="card">
      <h2>Identity registry (ERC-3643)</h2>
      <div className="grid">
        <label>
          Wallet
          <input className="mono" value={wallet} onChange={(e) => setWallet(e.target.value)} placeholder="0x..." />
        </label>
        <label>
          ONCHAINID
          <input className="mono" value={onchainId} onChange={(e) => setOnchainId(e.target.value)} placeholder="0x..." />
        </label>
        <label>
          Country (ISO 3166-1 numeric)
          <input value={country} onChange={(e) => setCountry(e.target.value)} />
        </label>
      </div>
      <div className="row">
        <button disabled={!isAddress(wallet) || !isAddress(onchainId)} onClick={() => write("Register identity", "registerIdentity", [wallet, onchainId, Number(country)])}>
          Register
        </button>
        <button disabled={!isAddress(wallet)} onClick={() => write("Delete identity", "deleteIdentity", [wallet])}>
          Delete
        </button>
        <button className="secondary" disabled={!isAddress(wallet)} onClick={check}>
          Is verified?
        </button>
        {lookup && <span className="pill">{lookup}</span>}
      </div>
      <TxStatus state={state} />
    </section>
  );
}

function GuardPanel({ connection, guard }: { connection: Connection; guard: Address }) {
  const { state, run } = useTx(connection);
  const [account, setAccount] = useState("");
  const [reason, setReason] = useState("vault contract");
  const [status, setStatus] = useState<string>();

  async function check() {
    if (!isAddress(account)) return;
    try {
      const [responded, registered, algorithmId, proven] = await connection.public.readContract({
        address: guard,
        abi: guardAbi,
        functionName: "keyStatus",
        args: [account],
      });
      const [eligible, exempt] = await Promise.all([
        connection.public.readContract({ address: guard, abi: guardAbi, functionName: "isHybridHolder", args: [account] }),
        connection.public.readContract({ address: guard, abi: guardAbi, functionName: "exempt", args: [account] }),
      ]);
      setStatus(
        !responded
          ? `precompile not active on this network: ${exempt ? "exempt" : "ineligible (fails closed)"}`
          : `registered ${registered}, algorithm ${algorithmId}, possession proven ${proven}, exempt ${exempt}: ${eligible ? "eligible" : "not eligible"}`,
      );
    } catch (e) {
      setStatus(errorMessage(e));
    }
  }

  const setExempt = (value: boolean) =>
    run(value ? "Exempt" : "Remove exemption", () =>
      connection.wallet.writeContract({
        address: guard,
        abi: guardAbi,
        functionName: "setExempt",
        args: [account as Address, value, reason],
        account: connection.account,
        chain: null,
      }),
    );

  return (
    <section className="card">
      <h2>Hybrid-holder guard</h2>
      <p className="muted small">
        A holder is eligible with a registered ML-DSA-87 key and proof of possession, read from the pqcKeyStatus
        precompile (0x0A02, testnet only). Contracts that must hold the token (vaults, escrows) can be exempted by the
        guard owner.
      </p>
      <div className="grid">
        <label>
          Account
          <input className="mono" value={account} onChange={(e) => setAccount(e.target.value)} placeholder="0x..." />
        </label>
        <label>
          Exemption reason
          <input value={reason} onChange={(e) => setReason(e.target.value)} />
        </label>
      </div>
      <div className="row">
        <button className="secondary" disabled={!isAddress(account)} onClick={check}>
          Key status
        </button>
        <button disabled={!isAddress(account)} onClick={() => setExempt(true)}>
          Exempt
        </button>
        <button disabled={!isAddress(account)} onClick={() => setExempt(false)}>
          Remove exemption
        </button>
      </div>
      {status && <p className="muted">{status}</p>}
      <TxStatus state={state} />
    </section>
  );
}

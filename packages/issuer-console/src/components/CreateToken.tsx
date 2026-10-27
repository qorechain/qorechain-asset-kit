// SPDX-License-Identifier: Apache-2.0
import { useState } from "react";
import { zeroAddress, zeroHash, type Abi, type Address, type Hex } from "viem";
import guardArtifact from "../artifacts/QoreChainHybridHolderGuard.json";
import ruleArtifact from "../artifacts/QoreChainHybridHolderRule.json";
import cmtatArtifact from "../artifacts/CMTATStandalone.json";
import { errorMessage, type Connection } from "../lib/clients";
import { addressUrl, canCreateToken } from "../lib/network";

interface Step {
  label: string;
  address?: Address;
  error?: string;
}

/** Deploys guard, rule and CMTAT token with the constructor arguments of contracts/script/DeployCmtat.s.sol. */
export function CreateToken({ connection, onCreated }: { connection?: Connection; onCreated: (token: Address) => void }) {
  const [form, setForm] = useState({
    name: "Example Ledger-Based Note",
    symbol: "ELBN",
    tokenId: "CH0000000000",
    termsUri: "https://example.org/terms.pdf",
    admin: "",
  });
  const [steps, setSteps] = useState<Step[]>([]);
  const [busy, setBusy] = useState(false);
  const enabled = !!connection && canCreateToken(connection.chainId) && !busy;

  async function deploy(label: string, abi: unknown, bytecode: string, args: unknown[]): Promise<Address> {
    const c = connection!;
    setSteps((s) => [...s, { label }]);
    const hash = await c.wallet.deployContract({
      abi: abi as Abi,
      bytecode: bytecode as Hex,
      args,
      account: c.account,
      chain: null,
    });
    const receipt = await c.public.waitForTransactionReceipt({ hash });
    if (receipt.status !== "success" || !receipt.contractAddress) throw new Error(`${label}: deployment reverted`);
    const address = receipt.contractAddress;
    setSteps((s) => s.map((x, i) => (i === s.length - 1 ? { ...x, address } : x)));
    return address;
  }

  async function create() {
    if (!connection) return;
    const admin = (form.admin || connection.account) as Address;
    setBusy(true);
    setSteps([]);
    try {
      const guard = await deploy("Hybrid-holder guard", guardArtifact.abi, guardArtifact.bytecode, [admin]);
      const rule = await deploy("CMTAT rule", ruleArtifact.abi, ruleArtifact.bytecode, [guard]);
      const token = await deploy("CMTAT token", cmtatArtifact.abi, cmtatArtifact.bytecode, [
        zeroAddress,
        admin,
        { name: form.name, symbol: form.symbol, decimalsIrrevocable: 0 },
        {
          tokenId: form.tokenId,
          terms: { name: "Terms", uri: form.termsUri, documentHash: zeroHash },
          information: "Issued with qorechain-asset-kit (CMTAT v3.2.0)",
        },
        { ruleEngine: rule },
      ]);
      onCreated(token);
    } catch (e) {
      setSteps((s) => [...s, { label: "Stopped", error: errorMessage(e) }]);
    } finally {
      setBusy(false);
    }
  }

  const field = (key: keyof typeof form, label: string, placeholder?: string) => (
    <label>
      {label}
      <input value={form[key]} placeholder={placeholder} onChange={(e) => setForm({ ...form, [key]: e.target.value })} />
    </label>
  );

  return (
    <section className="card">
      <h2>Create a CMTAT token</h2>
      <p className="muted small">
        Three deployments: the hybrid-holder guard, the CMTAT rule mapped to it, and a CMTAT v3.2.0 token (0 decimals,
        no proxy, no forwarder). ERC-3643 tokens are deployed with the Foundry script in contracts/script/erc3643 and
        opened below.
      </p>
      <div className="grid">
        {field("name", "Name")}
        {field("symbol", "Symbol")}
        {field("tokenId", "Identifier (ISIN or other)")}
        {field("termsUri", "Terms URI")}
        {field("admin", "Admin (default: connected account)", connection?.account)}
      </div>
      <button disabled={!enabled} onClick={create}>
        {busy ? "Deploying..." : "Create token"}
      </button>
      {connection && !canCreateToken(connection.chainId) && (
        <p className="muted small">Token creation is available on the QoreChain Testnet (chain 9800) only.</p>
      )}
      <ol>
        {steps.map((s, i) => (
          <li key={i} className={s.error ? "error" : undefined}>
            {s.label}
            {s.address && (
              <>
                {": "}
                <a href={addressUrl(s.address)} target="_blank" rel="noreferrer noopener" className="mono">
                  {s.address}
                </a>
              </>
            )}
            {s.error && <>: {s.error}</>}
            {!s.address && !s.error && busy && i === steps.length - 1 && " (waiting for the wallet and the block)"}
          </li>
        ))}
      </ol>
    </section>
  );
}

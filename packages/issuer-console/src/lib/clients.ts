// SPDX-License-Identifier: Apache-2.0
import { createPublicClient, createWalletClient, custom, type Address, type PublicClient, type WalletClient } from "viem";
import type { Eip1193Provider } from "./eip6963";

export interface Connection {
  provider: Eip1193Provider;
  account: Address;
  chainId: number;
  wallet: WalletClient;
  /** Reads go through the connected wallet's provider, so they follow the wallet's network. */
  public: PublicClient;
}

export function clientsFor(provider: Eip1193Provider, account: Address): Pick<Connection, "wallet" | "public"> {
  const transport = custom(provider);
  return {
    wallet: createWalletClient({ account, transport }),
    public: createPublicClient({ transport }) as PublicClient,
  };
}

export function errorMessage(e: unknown): string {
  const x = e as { shortMessage?: string; message?: string };
  return x?.shortMessage ?? x?.message ?? String(e);
}

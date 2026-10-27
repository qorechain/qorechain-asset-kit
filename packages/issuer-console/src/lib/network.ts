// SPDX-License-Identifier: Apache-2.0
import { defineChain } from "viem";

export const TESTNET_CHAIN_ID = 9800;
export const MAINNET_CHAIN_ID = 9801;
export const EXPLORER_URL = "https://explore.qore.network";
export const DOCS_EVM_ADAPTERS = "https://github.com/qorechain/qorechain-asset-kit/blob/main/docs/evm-adapters.md";

/** The QoreChain testnet (qorechain-diana), the only network the console deploys to. */
export const qorechainTestnet = defineChain({
  id: TESTNET_CHAIN_ID,
  name: "QoreChain Testnet",
  nativeCurrency: { name: "QOR", symbol: "QOR", decimals: 18 },
  rpcUrls: { default: { http: ["https://evm-testnet.qore.host"] } },
  blockExplorers: { default: { name: "QoreChain Explorer", url: EXPLORER_URL } },
  testnet: true,
});

/** Parameters for wallet_addEthereumChain (EIP-3085). */
export const ADD_TESTNET_PARAMS = {
  chainId: "0x2648",
  chainName: "QoreChain Testnet",
  nativeCurrency: { name: "QOR", symbol: "QOR", decimals: 18 },
  rpcUrls: ["https://evm-testnet.qore.host"],
  blockExplorerUrls: [EXPLORER_URL],
} as const;

export type NetworkStatus = "testnet" | "mainnet" | "other" | "disconnected";

export function networkStatus(chainId: number | undefined): NetworkStatus {
  if (chainId === undefined) return "disconnected";
  if (chainId === TESTNET_CHAIN_ID) return "testnet";
  if (chainId === MAINNET_CHAIN_ID) return "mainnet";
  return "other";
}

/** Creating a token deploys the hybrid-holder guard, which works only where 0x0A02 is active. */
export function canCreateToken(chainId: number | undefined): boolean {
  return networkStatus(chainId) === "testnet";
}

export function txUrl(hash: string): string {
  return `${EXPLORER_URL}/tx/${hash}`;
}

export function addressUrl(address: string): string {
  return `${EXPLORER_URL}/address/${address}`;
}

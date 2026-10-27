// SPDX-License-Identifier: Apache-2.0
import { parseAbi } from "viem";

/** Read and agent functions common to CMTAT v3 and ERC-3643 (T-REX v4) tokens. */
export const tokenAbi = parseAbi([
  "function name() view returns (string)",
  "function symbol() view returns (string)",
  "function decimals() view returns (uint8)",
  "function totalSupply() view returns (uint256)",
  "function balanceOf(address) view returns (uint256)",
  "function paused() view returns (bool)",
  "function isFrozen(address) view returns (bool)",
  "function pause()",
  "function unpause()",
  "function mint(address to, uint256 amount)",
  "function burn(address from, uint256 amount)",
  "function setAddressFrozen(address account, bool freeze)",
  "function forcedTransfer(address from, address to, uint256 amount) returns (bool)",
]);

/** ERC-3643 specifics. */
export const erc3643Abi = parseAbi([
  "function identityRegistry() view returns (address)",
  "function compliance() view returns (address)",
  "function version() view returns (string)",
]);

/** CMTAT specifics. */
export const cmtatAbi = parseAbi([
  "function ruleEngine() view returns (address)",
  "function version() view returns (string)",
]);

/** ERC-3643 identity registry. */
export const identityRegistryAbi = parseAbi([
  "function registerIdentity(address userAddress, address identity, uint16 country)",
  "function deleteIdentity(address userAddress)",
  "function isVerified(address userAddress) view returns (bool)",
  "function identity(address userAddress) view returns (address)",
  "function investorCountry(address userAddress) view returns (uint16)",
]);

/** QoreChainHybridHolderRule (only what the console reads). */
export const ruleAbi = parseAbi(["function guard() view returns (address)"]);

/** QoreChainHybridHolderGuard. */
export const guardAbi = parseAbi([
  "function owner() view returns (address)",
  "function exempt(address) view returns (bool)",
  "function precompileActive() view returns (bool)",
  "function isHybridHolder(address) view returns (bool)",
  "function keyStatus(address) view returns (bool responded, bool registered, uint8 algorithmId, bool possessionProven)",
  "function setExempt(address account, bool value, string reason)",
]);

/**
 * Events of the audit log. AddressFrozen and TokensFrozen/TokensUnfrozen exist in two layouts (T-REX and
 * CMTAT); they have different signatures, so their topics differ and both decode.
 */
export const auditEventsAbi = parseAbi([
  "event Transfer(address indexed from, address indexed to, uint256 value)",
  "event AddressFrozen(address indexed account, bool indexed isFrozen, address indexed agent)",
  "event AddressFrozen(address indexed account, bool indexed isFrozen, address indexed enforcer, bytes data)",
  "event TokensFrozen(address indexed account, uint256 amount)",
  "event TokensFrozen(address indexed account, uint256 amount, bytes data)",
  "event TokensUnfrozen(address indexed account, uint256 amount)",
  "event TokensUnfrozen(address indexed account, uint256 amount, bytes data)",
  "event Paused(address account)",
  "event Unpaused(address account)",
  "event Mint(address indexed minter, address indexed account, uint256 value, bytes data)",
  "event Burn(address indexed burner, address indexed account, uint256 value, bytes data)",
  "event RecoverySuccess(address indexed lostWallet, address indexed newWallet, address indexed investorOnchainId)",
  "event IdentityRegistered(address indexed investor, address indexed identity)",
  "event IdentityRemoved(address indexed investor, address indexed identity)",
  "event ExemptionSet(address indexed account, bool exempt, string reason)",
]);

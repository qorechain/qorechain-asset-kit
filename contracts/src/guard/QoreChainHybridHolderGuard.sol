// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.28;

import {Ownable, Ownable2Step} from "@openzeppelin/contracts/access/Ownable2Step.sol";
import {IQorePqcKeyStatus} from "../interfaces/IQorePqcKeyStatus.sol";
import {IHolderEligibility} from "../interfaces/IHolderEligibility.sol";

/// @title QoreChainHybridHolderGuard
/// @notice Says whether an address has a registered ML-DSA-87 key with proof of possession on QoreChain,
/// by reading the `pqcKeyStatus` precompile (0x0A02). It is the EVM counterpart of the proposed
/// `require_hybrid_signature` flag and is used by the CMTAT rule, the ERC-3643 compliance module and the
/// vaults in this repository.
///
/// TESTNET ONLY until the precompile is active on mainnet. On a network where 0x0A02 is not active
/// the call returns empty data and the guard FAILS CLOSED: every non-exempt address is ineligible.
///
/// Contracts (vaults, escrows, settlement contracts) cannot hold an ML-DSA-87 key; the owner can exempt
/// them explicitly. Every exemption change is an event.
contract QoreChainHybridHolderGuard is Ownable2Step, IHolderEligibility {
    /// @notice Address of the pqcKeyStatus precompile.
    address public constant PQC_KEY_STATUS = address(0x0A02);

    /// @notice Gas forwarded to the precompile (it charges a flat 2,500).
    uint256 public constant PRECOMPILE_GAS = 50_000;

    /// @notice The only key algorithm accepted: 1 = ML-DSA-87.
    uint8 public constant ML_DSA_87 = 1;

    /// @notice Upper bound on the returned public key (an ML-DSA-87 key is 2,592 bytes).
    uint256 public constant MAX_PUBKEY_LENGTH = 4096;

    /// @notice Addresses treated as eligible without a key (contracts that hold the asset by design).
    mapping(address account => bool) public exempt;

    event ExemptionSet(address indexed account, bool exempt, string reason);

    error HybridKeyRequired(address account);

    constructor(address initialOwner) Ownable(initialOwner) {}

    /// @notice Exempts or un-exempts an address, with a reason recorded in the event.
    function setExempt(address account, bool value, string calldata reason) external onlyOwner {
        exempt[account] = value;
        emit ExemptionSet(account, value, reason);
    }

    /// @notice Raw status of an address. `responded` is false when the precompile is not active on this
    /// network or returned data in an unexpected format.
    function keyStatus(address account)
        public
        view
        returns (bool responded, bool registered, uint8 algorithmId, bool possessionProven)
    {
        (bool ok, bytes memory ret) =
            PQC_KEY_STATUS.staticcall{gas: PRECOMPILE_GAS}(abi.encodeCall(IQorePqcKeyStatus.pqcKeyStatus, (account)));
        if (!ok) return (false, false, 0, false);
        return decodeKeyStatus(ret);
    }

    /// @notice Strict decoder of a pqcKeyStatus answer. Anything that is not exactly the expected ABI
    /// layout returns `valid == false`, which callers treat as "no key" (fail closed).
    /// Layout: bool registered | uint8 algorithmId | offset of pubkey (0x80) | bool possessionProven |
    /// pubkey length | pubkey bytes, padded to 32.
    function decodeKeyStatus(bytes memory ret)
        public
        pure
        returns (bool valid, bool registered, uint8 algorithmId, bool possessionProven)
    {
        if (ret.length < 160) return (false, false, 0, false);
        (uint256 w0, uint256 w1, uint256 offset, uint256 w3, uint256 keyLength) =
            abi.decode(ret, (uint256, uint256, uint256, uint256, uint256));
        if (w0 > 1 || w1 > type(uint8).max || offset != 0x80 || w3 > 1) return (false, false, 0, false);
        if (keyLength > MAX_PUBKEY_LENGTH) return (false, false, 0, false);
        if (ret.length < 160 + ((keyLength + 31) / 32) * 32) return (false, false, 0, false);
        return (true, w0 == 1, uint8(w1), w3 == 1);
    }

    /// @notice True when the precompile answers on this network.
    function precompileActive() external view returns (bool active) {
        (active,,,) = keyStatus(address(0));
    }

    /// @notice True when `account` is exempt, or has a registered ML-DSA-87 key (algorithm id 1) with
    /// proof of possession.
    function isHybridHolder(address account) public view returns (bool) {
        if (exempt[account]) return true;
        (bool responded, bool registered, uint8 algorithmId, bool possessionProven) = keyStatus(account);
        return responded && registered && algorithmId == ML_DSA_87 && possessionProven;
    }

    /// @inheritdoc IHolderEligibility
    function isEligible(address account) external view returns (bool) {
        return isHybridHolder(account);
    }

    /// @notice Reverts with `HybridKeyRequired` unless `account` is a hybrid holder.
    function requireHybridHolder(address account) external view {
        if (!isHybridHolder(account)) revert HybridKeyRequired(account);
    }
}

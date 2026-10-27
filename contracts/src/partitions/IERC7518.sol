// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.28;

import {IERC1155} from "@openzeppelin/contracts/token/ERC1155/IERC1155.sol";

/// @title IERC7518 (interface sketch, no implementation)
/// @notice Core interface of ERC-7518 "Dynamic Compliant Interop Security Token": an ERC-1155 token whose
/// token ids are partitions (classes, tranches, lock-up buckets) of one security, with per-partition
/// transfer restrictions, locks, forced transfers, address freezing and payouts.
///
/// Status: ERC-7518 is in Review and its optional extensions are still changing. No maintained
/// reference implementation was selected; this repository ships the interface only, transcribed from the
/// ERC text (two signatures that are not valid Solidity in the
/// ERC, `payout` and `batchPayout`, are declared `external` with plain parameters). With
/// `safeTransferFrom` redeclared here, `type(IERC7518).interfaceId` is 0x5a264a5d, the identifier the ERC
/// specifies. See docs/evm-adapters.md for how partitions map onto the CMTAT and ERC-3643 adapters.
interface IERC7518 is IERC1155 {
    event TokensLocked(address indexed account, uint256 indexed id, uint256 amount, uint256 releaseTime);
    event TokenUnlocked(address indexed account, uint256 indexed id);
    event TokensForceTransferred(address indexed from, address indexed to, uint256 indexed id, uint256 amount);
    event AddressFrozen(address indexed account, bytes data);
    event AddressUnfrozen(address indexed account, bytes data);
    event TransferRestricted(uint256 indexed id);
    event TransferRestrictionRemoved(uint256 indexed id);
    event PayoutDelivered(address indexed from, address indexed to, uint256 amount);

    /// @notice Balance of partition `id` that is neither locked nor otherwise restricted.
    function transferableBalance(address account, uint256 id) external view returns (uint256);

    /// @notice Balance of partition `id` locked until a release time.
    function lockedBalanceOf(address account, uint256 id) external view returns (uint256);

    /// @notice Stops all transfers of partition `id`.
    function restrictTransfer(uint256 id) external returns (bool);

    /// @notice Lifts the restriction set by `restrictTransfer`.
    function removeRestriction(uint256 id) external returns (bool);

    /// @notice ERC-1155 transfer that MUST call `canTransfer` first.
    function safeTransferFrom(address from, address to, uint256 id, uint256 value, bytes calldata data)
        external
        override;

    /// @notice Whether a transfer of `amount` of partition `id` would succeed.
    function canTransfer(address from, address to, uint256 id, uint256 amount, bytes calldata data)
        external
        view
        returns (bool status);

    function lockTokens(address account, uint256 id, uint256 amount, uint256 releaseTime) external returns (bool);

    function unlockToken(address account, uint256 id) external;

    function forceTransfer(address from, address to, uint256 id, uint256 amount, bytes memory data)
        external
        returns (bool);

    function freezeAddress(address account, bytes calldata data) external returns (bool);

    function unFreeze(address account, bytes memory data) external returns (bool);

    function payout(address to, uint256 amount) external returns (bool);

    function batchPayout(address[] calldata to, uint256[] calldata amount) external returns (bool);
}

// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.28;

/// @title IHolderEligibility
/// @notice A policy that says whether an address may hold a restricted asset or vault share.
interface IHolderEligibility {
    function isEligible(address account) external view returns (bool);
}

// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.28;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {ERC4626} from "@openzeppelin/contracts/token/ERC20/extensions/ERC4626.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {IHolderEligibility} from "../interfaces/IHolderEligibility.sol";

/// @title QoreChainRwaVault
/// @notice ERC-4626 vault over a restricted asset (for example a CMTAT or ERC-3643 token), built on the
/// OpenZeppelin implementation. Vault shares are restricted too: every address that RECEIVES shares (by
/// deposit, mint or transfer) must pass `eligibility` (for example {QoreChainHybridHolderGuard}, or a policy
/// that reads the token's identity registry). Without that, shares would be an unrestricted wrapper around
/// a restricted asset. Sending and redeeming are not checked: a holder who lost eligibility can still
/// redeem, and can still transfer to an eligible receiver.
///
/// The vault itself must be allowed to hold the underlying asset: whitelist it in the token's compliance
/// (ERC-3643 identity registry, CMTAT rule) and exempt it in the guard.
contract QoreChainRwaVault is ERC4626 {
    IHolderEligibility public immutable eligibility;

    error QoreChainRwaVault_NotEligible(address account);

    constructor(IERC20 asset_, string memory name_, string memory symbol_, IHolderEligibility eligibility_)
        ERC20(name_, symbol_)
        ERC4626(asset_)
    {
        eligibility = eligibility_;
    }

    /// @dev Checks the receiving side of every share movement; burns (redemptions) are never refused.
    function _update(address from, address to, uint256 value) internal virtual override {
        if (to != address(0) && !eligibility.isEligible(to)) revert QoreChainRwaVault_NotEligible(to);
        super._update(from, to, value);
    }

    /// @dev Zero for a receiver that cannot hold shares.
    function maxDeposit(address receiver) public view virtual override returns (uint256) {
        return eligibility.isEligible(receiver) ? super.maxDeposit(receiver) : 0;
    }

    /// @dev Zero for a receiver that cannot hold shares.
    function maxMint(address receiver) public view virtual override returns (uint256) {
        return eligibility.isEligible(receiver) ? super.maxMint(receiver) : 0;
    }
}

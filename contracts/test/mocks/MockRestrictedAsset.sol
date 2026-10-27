// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.28;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";

/// @notice Plain ERC-20 standing in for a restricted asset in the vault tests.
contract MockRestrictedAsset is ERC20 {
    constructor() ERC20("Example Fund Unit", "EFU") {}

    function mint(address to, uint256 amount) external {
        _mint(to, amount);
    }

    /// @dev Stands in for an agent's clawback or forced transfer out of an address.
    function seize(address from, uint256 amount) external {
        _burn(from, amount);
    }
}

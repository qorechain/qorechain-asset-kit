// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.28;

/// @title IERC3643ComplianceModule
/// @notice The functions a modular compliance contract of the ERC-3643 reference implementation (T-REX v4)
/// calls on a compliance module. Declared here, independently, so that this Apache-2.0 repository does not
/// import the GPL-3.0 reference sources; the selectors are the ones the reference implementation uses.
interface IERC3643ComplianceModule {
    event ComplianceBound(address indexed compliance);
    event ComplianceUnbound(address indexed compliance);

    function bindCompliance(address compliance) external;
    function unbindCompliance(address compliance) external;
    function moduleTransferAction(address from, address to, uint256 value) external;
    function moduleMintAction(address to, uint256 value) external;
    function moduleBurnAction(address from, uint256 value) external;
    function moduleCheck(address from, address to, uint256 value, address compliance) external view returns (bool);
    function isComplianceBound(address compliance) external view returns (bool);
    function canComplianceBind(address compliance) external view returns (bool);
    function isPlugAndPlay() external pure returns (bool);
    function name() external pure returns (string memory);
}

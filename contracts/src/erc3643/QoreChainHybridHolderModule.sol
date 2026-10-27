// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.28;

import {IERC3643ComplianceModule} from "./IERC3643ComplianceModule.sol";
import {QoreChainHybridHolderGuard} from "../guard/QoreChainHybridHolderGuard.sol";

/// @title QoreChainHybridHolderModule
/// @notice ERC-3643 (T-REX v4) modular-compliance module mapped to {QoreChainHybridHolderGuard}: a transfer
/// or mint is allowed only if the sender (unless minting) and the receiver have a registered ML-DSA-87 key
/// with proof of possession, or are exempt in the guard. Plug and play: no per-compliance configuration.
///
/// TESTNET ONLY until the pqcKeyStatus precompile is active on mainnet: on mainnet the guard fails closed.
contract QoreChainHybridHolderModule is IERC3643ComplianceModule {
    QoreChainHybridHolderGuard public immutable guard;

    mapping(address compliance => bool) private _bound;

    error OnlyComplianceCanBind();
    error ComplianceAlreadyBound();
    error ComplianceNotBound();

    constructor(QoreChainHybridHolderGuard guard_) {
        guard = guard_;
    }

    function bindCompliance(address compliance) external override {
        if (msg.sender != compliance) revert OnlyComplianceCanBind();
        if (_bound[compliance]) revert ComplianceAlreadyBound();
        _bound[compliance] = true;
        emit ComplianceBound(compliance);
    }

    function unbindCompliance(address compliance) external override {
        if (msg.sender != compliance) revert OnlyComplianceCanBind();
        if (!_bound[compliance]) revert ComplianceNotBound();
        _bound[compliance] = false;
        emit ComplianceUnbound(compliance);
    }

    function moduleTransferAction(address, address, uint256) external view override {
        if (!_bound[msg.sender]) revert ComplianceNotBound();
    }

    function moduleMintAction(address, uint256) external view override {
        if (!_bound[msg.sender]) revert ComplianceNotBound();
    }

    function moduleBurnAction(address, uint256) external view override {
        if (!_bound[msg.sender]) revert ComplianceNotBound();
    }

    function moduleCheck(address from, address to, uint256, address) external view override returns (bool) {
        if (from != address(0) && !guard.isHybridHolder(from)) return false;
        if (to != address(0) && !guard.isHybridHolder(to)) return false;
        return true;
    }

    function isComplianceBound(address compliance) external view override returns (bool) {
        return _bound[compliance];
    }

    function canComplianceBind(address) external pure override returns (bool) {
        return true;
    }

    function isPlugAndPlay() external pure override returns (bool) {
        return true;
    }

    function name() external pure override returns (string memory) {
        return "QoreChainHybridHolderModule";
    }
}

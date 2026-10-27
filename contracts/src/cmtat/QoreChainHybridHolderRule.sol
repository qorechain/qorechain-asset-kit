// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.28;

import {IERC165} from "@openzeppelin/contracts/utils/introspection/IERC165.sol";
import {IRuleEngineERC1404} from "CMTAT/interfaces/engine/IRuleEngine.sol";
import {RuleEngineInterfaceId} from "CMTAT/library/RuleEngineInterfaceId.sol";
import {ERC1404ExtendInterfaceId} from "CMTAT/library/ERC1404ExtendInterfaceId.sol";
import {QoreChainHybridHolderGuard} from "../guard/QoreChainHybridHolderGuard.sol";

/// @title QoreChainHybridHolderRule
/// @notice A CMTAT transfer rule mapped to {QoreChainHybridHolderGuard}: every sender, receiver and
/// spender of a transfer must have a registered ML-DSA-87 key with proof of possession (or be exempt in
/// the guard). Mint (from = 0) checks only the receiver. Burns (to = 0) are never refused by this rule:
/// the check is about who may receive the asset, so a holder who lost eligibility can still be redeemed.
///
/// It can be used two ways:
/// - directly as the `ruleEngine` of a CMTAT token (it implements CMTAT's `IRuleEngineERC1404`);
/// - as one rule inside a CMTA RuleEngine (it also implements `canReturnTransferRestrictionCode`
///   and advertises both RuleEngine rule interface ids, 0x2497d6cb and 0xb1a69752).
///
/// TESTNET ONLY until the pqcKeyStatus precompile is active on mainnet: on mainnet the guard fails
/// closed and every transfer between non-exempt addresses is refused.
contract QoreChainHybridHolderRule is IRuleEngineERC1404 {
    /// @notice The sender has no registered ML-DSA-87 key with proof of possession.
    uint8 public constant CODE_FROM_NOT_HYBRID = 60;
    /// @notice The receiver has no registered ML-DSA-87 key with proof of possession.
    uint8 public constant CODE_TO_NOT_HYBRID = 61;
    /// @notice The spender has no registered ML-DSA-87 key with proof of possession.
    uint8 public constant CODE_SPENDER_NOT_HYBRID = 62;
    /// @notice ERC-1404 "no restriction".
    uint8 public constant TRANSFER_OK = 0;

    /// @notice ERC-165 id of a rule usable by the CMTA RuleEngine, as advertised by RuleEngine v3 release
    /// candidates up to rc6 (`RuleInterfaceId`).
    bytes4 public constant RULE_INTERFACE_ID = 0x2497d6cb;
    /// @notice ERC-165 id of a rule in the current CMTA RuleEngine development line.
    bytes4 public constant RULE_INTERFACE_ID_CURRENT = 0xb1a69752;

    QoreChainHybridHolderGuard public immutable guard;

    error QoreChainHybridHolderRule_TransferRejected(uint8 code);

    constructor(QoreChainHybridHolderGuard guard_) {
        guard = guard_;
    }

    function detectTransferRestriction(address from, address to, uint256) public view override returns (uint8) {
        if (to == address(0)) return TRANSFER_OK; // burn
        if (from != address(0) && !guard.isHybridHolder(from)) return CODE_FROM_NOT_HYBRID;
        if (!guard.isHybridHolder(to)) return CODE_TO_NOT_HYBRID;
        return TRANSFER_OK;
    }

    function detectTransferRestrictionFrom(address spender, address from, address to, uint256 value)
        public
        view
        override
        returns (uint8)
    {
        if (to == address(0)) return TRANSFER_OK; // burn
        if (spender != address(0) && spender != from && !guard.isHybridHolder(spender)) {
            return CODE_SPENDER_NOT_HYBRID;
        }
        return detectTransferRestriction(from, to, value);
    }

    function canReturnTransferRestrictionCode(uint8 restrictionCode) external pure returns (bool) {
        return restrictionCode == CODE_FROM_NOT_HYBRID || restrictionCode == CODE_TO_NOT_HYBRID
            || restrictionCode == CODE_SPENDER_NOT_HYBRID;
    }

    function messageForTransferRestriction(uint8 restrictionCode) external pure override returns (string memory) {
        if (restrictionCode == TRANSFER_OK) return "No restriction";
        if (restrictionCode == CODE_FROM_NOT_HYBRID) {
            return "Sender has no registered ML-DSA-87 key with proof of possession";
        }
        if (restrictionCode == CODE_TO_NOT_HYBRID) {
            return "Receiver has no registered ML-DSA-87 key with proof of possession";
        }
        if (restrictionCode == CODE_SPENDER_NOT_HYBRID) {
            return "Spender has no registered ML-DSA-87 key with proof of possession";
        }
        return "Unknown restriction code";
    }

    function canTransfer(address from, address to, uint256 value) external view override returns (bool) {
        return detectTransferRestriction(from, to, value) == TRANSFER_OK;
    }

    function canTransferFrom(address spender, address from, address to, uint256 value)
        external
        view
        override
        returns (bool)
    {
        return detectTransferRestrictionFrom(spender, from, to, value) == TRANSFER_OK;
    }

    /// @dev Stateless: re-checks and reverts if the transfer is not allowed.
    function transferred(address from, address to, uint256 value) external view override {
        uint8 code = detectTransferRestriction(from, to, value);
        if (code != TRANSFER_OK) revert QoreChainHybridHolderRule_TransferRejected(code);
    }

    /// @dev Stateless: re-checks and reverts if the transfer is not allowed.
    function transferred(address spender, address from, address to, uint256 value) external view override {
        uint8 code = detectTransferRestrictionFrom(spender, from, to, value);
        if (code != TRANSFER_OK) revert QoreChainHybridHolderRule_TransferRejected(code);
    }

    function supportsInterface(bytes4 interfaceId) external pure override returns (bool) {
        return interfaceId == type(IERC165).interfaceId || interfaceId == RuleEngineInterfaceId.RULE_ENGINE_INTERFACE_ID
            || interfaceId == ERC1404ExtendInterfaceId.ERC1404EXTEND_INTERFACE_ID || interfaceId == RULE_INTERFACE_ID
            || interfaceId == RULE_INTERFACE_ID_CURRENT;
    }
}

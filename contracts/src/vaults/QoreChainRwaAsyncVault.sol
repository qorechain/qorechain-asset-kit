// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.28;

import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";
import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {ERC4626} from "@openzeppelin/contracts/token/ERC20/extensions/ERC4626.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {Math} from "@openzeppelin/contracts/utils/math/Math.sol";
import {IHolderEligibility} from "../interfaces/IHolderEligibility.sol";

/// @title QoreChainRwaAsyncVault
/// @notice ERC-7540 vault with asynchronous deposits and redemptions over a restricted asset, built on the
/// OpenZeppelin ERC-4626 implementation. Typical use: a fund whose subscriptions and redemptions are
/// processed in batches by an operator (FULFILLER_ROLE). The price used at fulfilment is the vault's own
/// share price (its asset balance, less reserved assets, per share); there is no external NAV input.
///
/// Flow: requestDeposit locks assets (Pending); the fulfiller prices them (Claimable, shares held in
/// escrow by the vault); the controller claims with deposit or mint. requestRedeem locks shares; the
/// fulfiller prices them (Claimable, assets reserved); the controller claims with redeem or withdraw.
/// Requests are aggregated per controller (requestId 0). Pending requests cannot be cancelled in this
/// version.
///
/// Shares are restricted by `eligibility` on the receiving side only, as in {QoreChainRwaVault}; moving
/// shares into the vault (redemption requests) and redeeming are always allowed.
///
/// Recovery: if an agent of the underlying token moves or burns assets out of the vault (forced transfer,
/// clawback), the balance can fall below the reserved assets. `totalAssets` then reads zero instead of
/// reverting, and claims that need the missing assets fail until the issuer restores the balance (for
/// example by minting or force-transferring the same amount back to the vault).
contract QoreChainRwaAsyncVault is ERC4626, AccessControl {
    using SafeERC20 for IERC20;

    bytes32 public constant FULFILLER_ROLE = keccak256("FULFILLER_ROLE");
    uint256 internal constant REQUEST_ID = 0;

    IHolderEligibility public immutable eligibility;

    mapping(address controller => mapping(address operator => bool)) public isOperator;

    mapping(address controller => uint256) internal _pendingDepositAssets;
    mapping(address controller => uint256) internal _claimableDepositAssets;
    mapping(address controller => uint256) internal _claimableDepositShares;
    mapping(address controller => uint256) internal _pendingRedeemShares;
    mapping(address controller => uint256) internal _claimableRedeemAssets;
    mapping(address controller => uint256) internal _claimableRedeemShares;

    /// @dev Assets held by the vault that do not belong to share holders: pending deposits and
    /// claimable redemptions.
    uint256 internal _reservedAssets;

    event DepositRequest(
        address indexed controller, address indexed owner, uint256 indexed requestId, address sender, uint256 assets
    );
    event RedeemRequest(
        address indexed controller, address indexed owner, uint256 indexed requestId, address sender, uint256 shares
    );
    event OperatorSet(address indexed controller, address indexed operator, bool approved);
    event DepositFulfilled(address indexed controller, uint256 assets, uint256 shares);
    event RedeemFulfilled(address indexed controller, uint256 shares, uint256 assets);

    error QoreChainRwaAsyncVault_NotEligible(address account);
    error QoreChainRwaAsyncVault_NotAuthorized();
    error QoreChainRwaAsyncVault_ZeroAmount();
    error QoreChainRwaAsyncVault_ExceedsRequest();
    error QoreChainRwaAsyncVault_ExceedsClaimable();
    error QoreChainRwaAsyncVault_AsyncPreviewUnsupported();
    error QoreChainRwaAsyncVault_ZeroAdmin();
    error QoreChainRwaAsyncVault_ZeroShares();

    constructor(
        IERC20 asset_,
        string memory name_,
        string memory symbol_,
        IHolderEligibility eligibility_,
        address admin
    ) ERC20(name_, symbol_) ERC4626(asset_) {
        if (admin == address(0)) revert QoreChainRwaAsyncVault_ZeroAdmin();
        eligibility = eligibility_;
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(FULFILLER_ROLE, admin);
    }

    // ------------------------------------------------------------------ operators

    function setOperator(address operator, bool approved) external returns (bool) {
        isOperator[msg.sender][operator] = approved;
        emit OperatorSet(msg.sender, operator, approved);
        return true;
    }

    function _requireControllerOrOperator(address controller) internal view {
        if (msg.sender != controller && !isOperator[controller][msg.sender]) {
            revert QoreChainRwaAsyncVault_NotAuthorized();
        }
    }

    // ------------------------------------------------------------------ ERC-7575

    function share() external view returns (address) {
        return address(this);
    }

    // ------------------------------------------------------------------ deposits

    function requestDeposit(uint256 assets, address controller, address owner) external returns (uint256) {
        if (assets == 0) revert QoreChainRwaAsyncVault_ZeroAmount();
        if (owner != msg.sender && !isOperator[owner][msg.sender]) revert QoreChainRwaAsyncVault_NotAuthorized();
        if (!eligibility.isEligible(controller)) revert QoreChainRwaAsyncVault_NotEligible(controller);
        IERC20(asset()).safeTransferFrom(owner, address(this), assets);
        _pendingDepositAssets[controller] += assets;
        _reservedAssets += assets;
        emit DepositRequest(controller, owner, REQUEST_ID, msg.sender, assets);
        return REQUEST_ID;
    }

    function pendingDepositRequest(uint256, address controller) external view returns (uint256) {
        return _pendingDepositAssets[controller];
    }

    function claimableDepositRequest(uint256, address controller) external view returns (uint256) {
        return _claimableDepositAssets[controller];
    }

    /// @notice Prices `assets` of `controller`'s pending deposit at the current share price.
    function fulfillDeposit(address controller, uint256 assets)
        external
        onlyRole(FULFILLER_ROLE)
        returns (uint256 shares)
    {
        if (assets == 0) revert QoreChainRwaAsyncVault_ZeroAmount();
        if (assets > _pendingDepositAssets[controller]) revert QoreChainRwaAsyncVault_ExceedsRequest();
        shares = _convertToShares(assets, Math.Rounding.Floor);
        if (shares == 0) revert QoreChainRwaAsyncVault_ZeroShares();
        _pendingDepositAssets[controller] -= assets;
        _reservedAssets -= assets;
        _claimableDepositAssets[controller] += assets;
        _claimableDepositShares[controller] += shares;
        _mint(address(this), shares);
        emit DepositFulfilled(controller, assets, shares);
    }

    function deposit(uint256 assets, address receiver, address controller) public returns (uint256 shares) {
        _requireControllerOrOperator(controller);
        uint256 claimableAssets = _claimableDepositAssets[controller];
        if (assets == 0) revert QoreChainRwaAsyncVault_ZeroAmount();
        if (assets > claimableAssets) revert QoreChainRwaAsyncVault_ExceedsClaimable();
        shares = Math.mulDiv(assets, _claimableDepositShares[controller], claimableAssets, Math.Rounding.Floor);
        _claimableDepositAssets[controller] = claimableAssets - assets;
        _claimableDepositShares[controller] -= shares;
        _transfer(address(this), receiver, shares);
        emit Deposit(controller, receiver, assets, shares);
    }

    function deposit(uint256 assets, address receiver) public override returns (uint256) {
        return deposit(assets, receiver, msg.sender);
    }

    function mint(uint256 shares, address receiver, address controller) public returns (uint256 assets) {
        _requireControllerOrOperator(controller);
        uint256 claimableShares = _claimableDepositShares[controller];
        if (shares == 0) revert QoreChainRwaAsyncVault_ZeroAmount();
        if (shares > claimableShares) revert QoreChainRwaAsyncVault_ExceedsClaimable();
        assets = Math.mulDiv(shares, _claimableDepositAssets[controller], claimableShares, Math.Rounding.Ceil);
        _claimableDepositShares[controller] = claimableShares - shares;
        _claimableDepositAssets[controller] -= assets;
        _transfer(address(this), receiver, shares);
        emit Deposit(controller, receiver, assets, shares);
    }

    function mint(uint256 shares, address receiver) public override returns (uint256) {
        return mint(shares, receiver, msg.sender);
    }

    // ------------------------------------------------------------------ redemptions

    function requestRedeem(uint256 shares, address controller, address owner) external returns (uint256) {
        if (shares == 0) revert QoreChainRwaAsyncVault_ZeroAmount();
        if (owner != msg.sender && !isOperator[owner][msg.sender]) _spendAllowance(owner, msg.sender, shares);
        _transfer(owner, address(this), shares);
        _pendingRedeemShares[controller] += shares;
        emit RedeemRequest(controller, owner, REQUEST_ID, msg.sender, shares);
        return REQUEST_ID;
    }

    function pendingRedeemRequest(uint256, address controller) external view returns (uint256) {
        return _pendingRedeemShares[controller];
    }

    function claimableRedeemRequest(uint256, address controller) external view returns (uint256) {
        return _claimableRedeemShares[controller];
    }

    /// @notice Prices `shares` of `controller`'s pending redemption at the current share price.
    function fulfillRedeem(address controller, uint256 shares)
        external
        onlyRole(FULFILLER_ROLE)
        returns (uint256 assets)
    {
        if (shares == 0) revert QoreChainRwaAsyncVault_ZeroAmount();
        if (shares > _pendingRedeemShares[controller]) revert QoreChainRwaAsyncVault_ExceedsRequest();
        assets = _convertToAssets(shares, Math.Rounding.Floor);
        _pendingRedeemShares[controller] -= shares;
        _claimableRedeemShares[controller] += shares;
        _claimableRedeemAssets[controller] += assets;
        _reservedAssets += assets;
        _burn(address(this), shares);
        emit RedeemFulfilled(controller, shares, assets);
    }

    function redeem(uint256 shares, address receiver, address controller) public override returns (uint256 assets) {
        _requireControllerOrOperator(controller);
        uint256 claimableShares = _claimableRedeemShares[controller];
        if (shares == 0) revert QoreChainRwaAsyncVault_ZeroAmount();
        if (shares > claimableShares) revert QoreChainRwaAsyncVault_ExceedsClaimable();
        assets = Math.mulDiv(shares, _claimableRedeemAssets[controller], claimableShares, Math.Rounding.Floor);
        _claimableRedeemShares[controller] = claimableShares - shares;
        _claimableRedeemAssets[controller] -= assets;
        _reservedAssets -= assets;
        IERC20(asset()).safeTransfer(receiver, assets);
        emit Withdraw(msg.sender, receiver, controller, assets, shares);
    }

    function withdraw(uint256 assets, address receiver, address controller) public override returns (uint256 shares) {
        _requireControllerOrOperator(controller);
        uint256 claimableAssets = _claimableRedeemAssets[controller];
        if (assets == 0) revert QoreChainRwaAsyncVault_ZeroAmount();
        if (assets > claimableAssets) revert QoreChainRwaAsyncVault_ExceedsClaimable();
        shares = Math.mulDiv(assets, _claimableRedeemShares[controller], claimableAssets, Math.Rounding.Ceil);
        _claimableRedeemAssets[controller] = claimableAssets - assets;
        _claimableRedeemShares[controller] -= shares;
        _reservedAssets -= assets;
        IERC20(asset()).safeTransfer(receiver, assets);
        emit Withdraw(msg.sender, receiver, controller, assets, shares);
    }

    // ------------------------------------------------------------------ ERC-4626 views

    /// @notice Assets that back the outstanding shares (excludes pending deposits and claimable redemptions).
    /// Saturates at zero if assets were moved out of the vault by the token's agent (see the recovery note).
    function totalAssets() public view override returns (uint256) {
        uint256 balance = IERC20(asset()).balanceOf(address(this));
        return balance > _reservedAssets ? balance - _reservedAssets : 0;
    }

    /// @dev Claimable assets, or zero when the controller cannot receive shares.
    function maxDeposit(address controller) public view override returns (uint256) {
        return eligibility.isEligible(controller) ? _claimableDepositAssets[controller] : 0;
    }

    /// @dev Claimable shares, or zero when the controller cannot receive shares.
    function maxMint(address controller) public view override returns (uint256) {
        return eligibility.isEligible(controller) ? _claimableDepositShares[controller] : 0;
    }

    function maxRedeem(address controller) public view override returns (uint256) {
        return _claimableRedeemShares[controller];
    }

    function maxWithdraw(address controller) public view override returns (uint256) {
        return _claimableRedeemAssets[controller];
    }

    /// @dev ERC-7540: previews MUST revert for asynchronous flows.
    function previewDeposit(uint256) public pure override returns (uint256) {
        revert QoreChainRwaAsyncVault_AsyncPreviewUnsupported();
    }

    function previewMint(uint256) public pure override returns (uint256) {
        revert QoreChainRwaAsyncVault_AsyncPreviewUnsupported();
    }

    function previewRedeem(uint256) public pure override returns (uint256) {
        revert QoreChainRwaAsyncVault_AsyncPreviewUnsupported();
    }

    function previewWithdraw(uint256) public pure override returns (uint256) {
        revert QoreChainRwaAsyncVault_AsyncPreviewUnsupported();
    }

    // ------------------------------------------------------------------ restrictions and ERC-165

    /// @dev Checks the receiving side only. Shares may always move into the vault (redemption requests) and
    /// be burned (redemptions), so a holder who lost eligibility can still redeem.
    function _update(address from, address to, uint256 value) internal virtual override {
        if (to != address(0) && to != address(this) && !eligibility.isEligible(to)) {
            revert QoreChainRwaAsyncVault_NotEligible(to);
        }
        super._update(from, to, value);
    }

    function supportsInterface(bytes4 interfaceId) public view override returns (bool) {
        return interfaceId == 0xe3bc4e65 // ERC-7540 operator methods
            || interfaceId == 0x2f0a18c5 // ERC-7575
            || interfaceId == 0xce3bbe50 // ERC-7540 asynchronous deposit
            || interfaceId == 0x620ee8e4 // ERC-7540 asynchronous redemption
            || super.supportsInterface(interfaceId);
    }
}

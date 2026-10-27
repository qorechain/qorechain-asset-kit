// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.28;

import {Test} from "forge-std/Test.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {ERC4626} from "@openzeppelin/contracts/token/ERC20/extensions/ERC4626.sol";
import {QoreChainHybridHolderGuard} from "../src/guard/QoreChainHybridHolderGuard.sol";
import {QoreChainRwaVault} from "../src/vaults/QoreChainRwaVault.sol";
import {QoreChainRwaAsyncVault} from "../src/vaults/QoreChainRwaAsyncVault.sol";
import {MockPqcKeyStatus, PqcPrecompile} from "./mocks/MockPqcKeyStatus.sol";
import {MockRestrictedAsset} from "./mocks/MockRestrictedAsset.sol";

contract VaultTest is Test {
    MockPqcKeyStatus pqc;
    QoreChainHybridHolderGuard guard;
    MockRestrictedAsset asset;
    address admin = makeAddr("admin");
    address alice = makeAddr("alice");
    address bob = makeAddr("bob");
    address mallory = makeAddr("mallory");

    function setUp() public {
        pqc = PqcPrecompile.install(vm);
        guard = new QoreChainHybridHolderGuard(admin);
        asset = new MockRestrictedAsset();
        pqc.set(alice, true, true);
        pqc.set(bob, true, true);
        asset.mint(alice, 1_000e18);
    }

    function test_Erc4626SharesAreRestricted() public {
        QoreChainRwaVault vault = new QoreChainRwaVault(IERC20(address(asset)), "Fund shares", "vEFU", guard);
        vm.startPrank(alice);
        asset.approve(address(vault), 101e18);
        vault.deposit(100e18, alice);
        assertEq(vault.balanceOf(alice), vault.convertToShares(100e18));
        assertTrue(vault.transfer(bob, 1e18));
        vm.expectRevert(abi.encodeWithSelector(QoreChainRwaVault.QoreChainRwaVault_NotEligible.selector, mallory));
        assertFalse(vault.transfer(mallory, 1e18));
        vm.expectRevert(abi.encodeWithSelector(ERC4626.ERC4626ExceededMaxDeposit.selector, mallory, 1e18, 0));
        vault.deposit(1e18, mallory);
        vault.redeem(vault.balanceOf(alice), alice, alice);
        vm.stopPrank();
    }

    function _asyncVault() internal returns (QoreChainRwaAsyncVault vault) {
        vault = new QoreChainRwaAsyncVault(IERC20(address(asset)), "Fund shares", "aEFU", guard, admin);
    }

    function test_Erc7540AsyncDepositAndRedeem() public {
        QoreChainRwaAsyncVault vault = _asyncVault();
        vm.startPrank(alice);
        asset.approve(address(vault), 100e18);
        vault.requestDeposit(100e18, alice, alice);
        vm.stopPrank();
        assertEq(vault.pendingDepositRequest(0, alice), 100e18);
        assertEq(vault.totalAssets(), 0, "pending deposits do not back shares");

        vm.prank(admin);
        uint256 shares = vault.fulfillDeposit(alice, 100e18);
        assertEq(vault.pendingDepositRequest(0, alice), 0);
        assertEq(vault.claimableDepositRequest(0, alice), 100e18);
        assertEq(vault.maxMint(alice), shares);

        vm.prank(alice);
        vault.deposit(100e18, alice, alice);
        assertEq(vault.balanceOf(alice), shares);
        assertEq(vault.totalAssets(), 100e18);

        // Gains accrue to holders: the vault's asset balance rises by 10%.
        asset.mint(address(vault), 10e18);

        vm.prank(alice);
        vault.requestRedeem(shares, alice, alice);
        assertEq(vault.pendingRedeemRequest(0, alice), shares);
        vm.prank(admin);
        uint256 assetsOut = vault.fulfillRedeem(alice, shares);
        assertApproxEqAbs(assetsOut, 110e18, 1e6);
        assertEq(vault.maxWithdraw(alice), assetsOut);

        uint256 before = asset.balanceOf(alice);
        vm.prank(alice);
        vault.redeem(shares, alice, alice);
        assertEq(asset.balanceOf(alice) - before, assetsOut);
    }

    function test_Erc7540OperatorAndRestrictions() public {
        QoreChainRwaAsyncVault vault = _asyncVault();
        vm.prank(alice);
        asset.approve(address(vault), 50e18);

        vm.prank(bob);
        vm.expectRevert(QoreChainRwaAsyncVault.QoreChainRwaAsyncVault_NotAuthorized.selector);
        vault.requestDeposit(50e18, alice, alice);

        vm.prank(alice);
        vault.setOperator(bob, true);
        assertTrue(vault.isOperator(alice, bob));
        vm.prank(bob);
        vault.requestDeposit(50e18, alice, alice);

        vm.prank(alice);
        vm.expectRevert(
            abi.encodeWithSelector(QoreChainRwaAsyncVault.QoreChainRwaAsyncVault_NotEligible.selector, mallory)
        );
        vault.requestDeposit(1, mallory, alice);

        vm.prank(admin);
        vault.fulfillDeposit(alice, 50e18);
        vm.prank(bob);
        vm.expectRevert(
            abi.encodeWithSelector(QoreChainRwaAsyncVault.QoreChainRwaAsyncVault_NotEligible.selector, mallory)
        );
        vault.deposit(50e18, mallory, alice);

        vm.prank(mallory);
        vm.expectRevert(QoreChainRwaAsyncVault.QoreChainRwaAsyncVault_NotAuthorized.selector);
        vault.deposit(50e18, mallory, alice);
    }

    function test_Erc7540PreviewsRevertAndInterfaces() public {
        QoreChainRwaAsyncVault vault = _asyncVault();
        vm.expectRevert(QoreChainRwaAsyncVault.QoreChainRwaAsyncVault_AsyncPreviewUnsupported.selector);
        vault.previewDeposit(1);
        vm.expectRevert(QoreChainRwaAsyncVault.QoreChainRwaAsyncVault_AsyncPreviewUnsupported.selector);
        vault.previewRedeem(1);
        assertTrue(vault.supportsInterface(0xe3bc4e65));
        assertTrue(vault.supportsInterface(0x2f0a18c5));
        assertTrue(vault.supportsInterface(0xce3bbe50));
        assertTrue(vault.supportsInterface(0x620ee8e4));
        assertEq(vault.share(), address(vault));
    }

    function test_Erc7540OnlyFulfillerPrices() public {
        QoreChainRwaAsyncVault vault = _asyncVault();
        vm.startPrank(alice);
        asset.approve(address(vault), 10e18);
        vault.requestDeposit(10e18, alice, alice);
        vm.expectRevert();
        vault.fulfillDeposit(alice, 10e18);
        vm.stopPrank();
        vm.prank(admin);
        vm.expectRevert(QoreChainRwaAsyncVault.QoreChainRwaAsyncVault_ExceedsRequest.selector);
        vault.fulfillDeposit(alice, 11e18);
    }

    function test_Erc4626IneligibleOwnerCanStillRedeem() public {
        QoreChainRwaVault vault = new QoreChainRwaVault(IERC20(address(asset)), "Fund shares", "vEFU", guard);
        vm.startPrank(alice);
        asset.approve(address(vault), 10e18);
        vault.deposit(10e18, alice);
        vm.stopPrank();
        pqc.set(alice, false, false); // alice loses eligibility
        assertEq(vault.maxDeposit(alice), 0);
        assertEq(vault.maxMint(alice), 0);
        assertEq(vault.maxRedeem(alice), vault.balanceOf(alice));
        uint256 held = vault.balanceOf(alice);
        vm.prank(alice);
        vault.redeem(held, alice, alice);
        assertEq(vault.balanceOf(alice), 0);
    }

    function test_Erc7540TotalAssetsSaturatesAfterSeizure() public {
        QoreChainRwaAsyncVault vault = _asyncVault();
        vm.startPrank(alice);
        asset.approve(address(vault), 100e18);
        vault.requestDeposit(100e18, alice, alice);
        vm.stopPrank();
        // An agent of the underlying token moves assets out of the vault while they are reserved.
        asset.seize(address(vault), 60e18);
        assertEq(vault.totalAssets(), 0, "saturates instead of reverting");
        // Recovery: the issuer restores the balance.
        asset.mint(address(vault), 60e18);
        assertEq(vault.totalAssets(), 0);
        vm.prank(admin);
        vault.fulfillDeposit(alice, 100e18);
        assertEq(vault.totalAssets(), 100e18);
    }

    function test_Erc7540RejectsZeroSharesAndZeroAdmin() public {
        vm.expectRevert(QoreChainRwaAsyncVault.QoreChainRwaAsyncVault_ZeroAdmin.selector);
        new QoreChainRwaAsyncVault(IERC20(address(asset)), "x", "x", guard, address(0));

        QoreChainRwaAsyncVault vault = _asyncVault();
        vm.startPrank(alice);
        asset.approve(address(vault), 2e18);
        vault.requestDeposit(1e18, alice, alice);
        vm.stopPrank();
        vm.prank(admin);
        vault.fulfillDeposit(alice, 1e18);
        vm.prank(alice);
        vault.deposit(1e18, alice, alice);
        // A large donation makes one wei of assets worth less than one share.
        asset.mint(address(vault), 1_000_000e18);
        vm.prank(alice);
        vault.requestDeposit(1, alice, alice);
        vm.prank(admin);
        vm.expectRevert(QoreChainRwaAsyncVault.QoreChainRwaAsyncVault_ZeroShares.selector);
        vault.fulfillDeposit(alice, 1);
    }

    function test_Erc7540IneligibleControllerCanRedeemButNotClaimShares() public {
        QoreChainRwaAsyncVault vault = _asyncVault();
        vm.startPrank(alice);
        asset.approve(address(vault), 20e18);
        vault.requestDeposit(20e18, alice, alice);
        vm.stopPrank();
        vm.prank(admin);
        uint256 shares = vault.fulfillDeposit(alice, 20e18);
        vm.prank(alice);
        vault.deposit(10e18, alice, alice);

        pqc.set(alice, false, false);
        assertEq(vault.maxDeposit(alice), 0, "cannot receive the remaining claimable shares");
        assertEq(vault.maxMint(alice), 0);
        vm.prank(alice);
        vm.expectRevert(
            abi.encodeWithSelector(QoreChainRwaAsyncVault.QoreChainRwaAsyncVault_NotEligible.selector, alice)
        );
        vault.deposit(10e18, alice, alice);

        uint256 held = vault.balanceOf(alice);
        assertGt(held, 0);
        assertLe(held, shares);
        vm.prank(alice);
        vault.requestRedeem(held, alice, alice);
        vm.prank(admin);
        vault.fulfillRedeem(alice, held);
        assertEq(vault.maxRedeem(alice), held);
        vm.prank(alice);
        vault.redeem(held, alice, alice);
    }
}

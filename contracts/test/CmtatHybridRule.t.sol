// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.28;

import {Test} from "forge-std/Test.sol";
import {DeployCmtat} from "../script/DeployCmtat.s.sol";
import {QoreChainHybridHolderRule} from "../src/cmtat/QoreChainHybridHolderRule.sol";
import {MockPqcKeyStatus, PqcPrecompile} from "./mocks/MockPqcKeyStatus.sol";

contract CmtatHybridRuleTest is Test {
    DeployCmtat.Deployment d;
    MockPqcKeyStatus pqc;
    address admin = makeAddr("admin");
    address alice = makeAddr("alice");
    address bob = makeAddr("bob");
    address carol = makeAddr("carol");

    function setUp() public {
        pqc = PqcPrecompile.install(vm);
        d = new DeployCmtat().deploy(admin, "Example Note", "EXN", "CH0000000000", "https://example.org/terms.pdf");
        pqc.set(alice, true, true);
        pqc.set(bob, true, true);
        pqc.set(carol, true, false); // key registered, possession not proven
    }

    function test_MintAndTransferBetweenHybridHolders() public {
        vm.prank(admin);
        d.token.mint(alice, 100);
        vm.prank(alice);
        d.token.transfer(bob, 40);
        assertEq(d.token.balanceOf(bob), 40);
        assertEq(d.token.decimals(), 0);
    }

    function test_RejectsReceiverWithoutProofOfPossession() public {
        vm.prank(admin);
        d.token.mint(alice, 100);
        assertEq(d.rule.detectTransferRestriction(alice, carol, 1), d.rule.CODE_TO_NOT_HYBRID());
        assertFalse(d.token.canTransfer(alice, carol, 1));
        vm.prank(alice);
        vm.expectRevert();
        d.token.transfer(carol, 1);
        vm.prank(admin);
        vm.expectRevert();
        d.token.mint(carol, 1);
    }

    function test_FailsClosedWithoutPrecompile() public {
        vm.prank(admin);
        d.token.mint(alice, 10);
        vm.etch(address(0x0A02), "");
        assertFalse(d.token.canTransfer(alice, bob, 1), "mainnet today: no transfer between non-exempt holders");
    }

    function test_CmtatControlsStillApply() public {
        vm.startPrank(admin);
        d.token.mint(alice, 100);
        d.token.setAddressFrozen(alice, true);
        vm.stopPrank();
        vm.prank(alice);
        vm.expectRevert();
        d.token.transfer(bob, 1);

        vm.startPrank(admin);
        d.token.setAddressFrozen(alice, false);
        d.token.pause();
        vm.stopPrank();
        vm.prank(alice);
        vm.expectRevert();
        d.token.transfer(bob, 1);
    }

    function test_SpenderMustBeHybridHolder() public view {
        assertEq(d.rule.detectTransferRestrictionFrom(carol, alice, bob, 1), d.rule.CODE_SPENDER_NOT_HYBRID());
        assertEq(d.rule.detectTransferRestrictionFrom(alice, alice, bob, 1), 0);
    }

    function test_RuleInterfaceAndMessages() public view {
        QoreChainHybridHolderRule rule = d.rule;
        assertTrue(rule.supportsInterface(0x2497d6cb), "CMTA RuleEngine rule id (rc6)");
        assertTrue(rule.supportsInterface(0xb1a69752), "CMTA RuleEngine rule id (current)");
        assertTrue(rule.supportsInterface(0x20c49ce7), "CMTAT rule engine id");
        assertTrue(rule.supportsInterface(0x01ffc9a7), "ERC-165");
        assertTrue(rule.canReturnTransferRestrictionCode(61));
        assertFalse(rule.canReturnTransferRestrictionCode(1));
        assertEq(rule.messageForTransferRestriction(0), "No restriction");
    }

    function test_BurnFromHolderWhoLostEligibility() public {
        vm.prank(admin);
        d.token.mint(alice, 10);
        pqc.set(alice, false, false);
        assertEq(d.rule.detectTransferRestriction(alice, address(0), 10), 0, "burns are never refused");
        vm.prank(admin);
        d.token.burn(alice, 10);
        assertEq(d.token.balanceOf(alice), 0);
        vm.prank(admin);
        vm.expectRevert();
        d.token.mint(alice, 1); // receiving stays fail-closed
    }
}

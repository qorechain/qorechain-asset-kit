// SPDX-License-Identifier: GPL-3.0-or-later
// Compiles together with the GPL-3.0 ERC-3643 reference implementation; see
// script/erc3643/TrexSuiteDeployer.sol.
pragma solidity 0.8.17;

import {Test} from "forge-std/Test.sol";
import {IIdentity} from "@onchain-id/solidity/contracts/interface/IIdentity.sol";
import {TrexSuiteDeployer} from "../../script/erc3643/TrexSuiteDeployer.sol";

interface IMockPqc {
    function set(address account, bool registered, bool possessionProven) external;
}

interface IGuard {
    function setExempt(address account, bool value, string calldata reason) external;
}

contract TrexIntegrationTest is Test, TrexSuiteDeployer {
    Infra infra;
    Suite s;
    IMockPqc pqc = IMockPqc(address(0x0A02));
    address owner = makeAddr("owner");
    address agent = makeAddr("agent");
    address alice = makeAddr("alice");
    address bob = makeAddr("bob");

    function setUp() public {
        vm.etch(address(0x0A02), vm.getDeployedCode("MockPqcKeyStatus.sol:MockPqcKeyStatus"));
        vm.startPrank(owner);
        infra = deployInfra(owner);
        s = deploySuite(infra, owner, agent, "bond", "Example 2030 Bond", "EB30");
        address aliceId = infra.idFactory.createIdentity(alice, "alice");
        address bobId = infra.idFactory.createIdentity(bob, "bob");
        vm.stopPrank();

        vm.startPrank(agent);
        s.identityRegistry.registerIdentity(alice, IIdentity(aliceId), 756);
        s.identityRegistry.registerIdentity(bob, IIdentity(bobId), 756);
        s.token.unpause();
        vm.stopPrank();
        pqc.set(alice, true, true);
    }

    function test_ModuleIsBound() public view {
        assertTrue(s.compliance.isModuleBound(s.module));
    }

    function test_MintRequiresHybridHolder() public {
        vm.prank(agent);
        s.token.mint(alice, 100);
        assertEq(s.token.balanceOf(alice), 100);
        vm.prank(agent);
        vm.expectRevert("Compliance not followed");
        s.token.mint(bob, 1);
    }

    function test_TransferRequiresHybridReceiver() public {
        vm.prank(agent);
        s.token.mint(alice, 100);

        vm.prank(alice);
        vm.expectRevert("Transfer not possible");
        s.token.transfer(bob, 1);

        pqc.set(bob, true, false);
        vm.prank(alice);
        vm.expectRevert("Transfer not possible");
        s.token.transfer(bob, 1);

        pqc.set(bob, true, true);
        vm.prank(alice);
        s.token.transfer(bob, 1);
        assertEq(s.token.balanceOf(bob), 1);
    }

    function test_ReferenceControlsStillApply() public {
        pqc.set(bob, true, true);
        vm.startPrank(agent);
        s.token.mint(alice, 100);
        s.token.setAddressFrozen(alice, true);
        vm.stopPrank();
        vm.prank(alice);
        vm.expectRevert("wallet is frozen");
        s.token.transfer(bob, 1);

        vm.prank(agent);
        s.token.setAddressFrozen(alice, false);
        vm.prank(agent);
        s.token.forcedTransfer(alice, bob, 10);
        assertEq(s.token.balanceOf(bob), 10);
    }

    function test_FailsClosedWithoutPrecompile() public {
        vm.etch(address(0x0A02), "");
        vm.prank(agent);
        vm.expectRevert("Compliance not followed");
        s.token.mint(alice, 1);
    }

    function test_GuardExemptionForAContractHolder() public {
        address escrow = makeAddr("escrow-contract");
        address escrowId;
        vm.prank(owner);
        escrowId = infra.idFactory.createIdentity(escrow, "escrow");
        vm.prank(agent);
        s.identityRegistry.registerIdentity(escrow, IIdentity(escrowId), 756);
        vm.prank(owner);
        IGuard(s.guard).setExempt(escrow, true, "settlement escrow");
        vm.prank(agent);
        s.token.mint(escrow, 5);
        assertEq(s.token.balanceOf(escrow), 5);
    }
}

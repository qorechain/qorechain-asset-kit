// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.28;

import {Test} from "forge-std/Test.sol";
import {QoreChainHybridHolderGuard} from "../src/guard/QoreChainHybridHolderGuard.sol";
import {QoreChainHybridHolderModule} from "../src/erc3643/QoreChainHybridHolderModule.sol";
import {MockPqcKeyStatus, PqcPrecompile} from "./mocks/MockPqcKeyStatus.sol";

/// Unit test of the module against the calls a modular compliance makes. The end-to-end test with the
/// ERC-3643 reference implementation is test/erc3643/TrexIntegration.t.sol (GPL-3.0).
contract Erc3643ModuleTest is Test {
    QoreChainHybridHolderGuard guard;
    QoreChainHybridHolderModule module;
    MockPqcKeyStatus pqc;
    address compliance = makeAddr("compliance");
    address alice = makeAddr("alice");
    address bob = makeAddr("bob");

    function setUp() public {
        pqc = PqcPrecompile.install(vm);
        guard = new QoreChainHybridHolderGuard(address(this));
        module = new QoreChainHybridHolderModule(guard);
        pqc.set(alice, true, true);
    }

    function test_BindingIsByTheComplianceItself() public {
        vm.expectRevert(QoreChainHybridHolderModule.OnlyComplianceCanBind.selector);
        module.bindCompliance(compliance);
        vm.prank(compliance);
        module.bindCompliance(compliance);
        assertTrue(module.isComplianceBound(compliance));
        assertTrue(module.isPlugAndPlay());
        assertEq(module.name(), "QoreChainHybridHolderModule");
        vm.prank(compliance);
        module.moduleTransferAction(alice, bob, 1);
        vm.expectRevert(QoreChainHybridHolderModule.ComplianceNotBound.selector);
        module.moduleMintAction(alice, 1);
    }

    function test_ModuleCheck() public {
        assertTrue(module.moduleCheck(address(0), alice, 1, compliance), "mint to a hybrid holder");
        assertFalse(module.moduleCheck(address(0), bob, 1, compliance), "mint to an address without a key");
        assertFalse(module.moduleCheck(alice, bob, 1, compliance));
        pqc.set(bob, true, false);
        assertFalse(module.moduleCheck(alice, bob, 1, compliance), "key without proof of possession");
        pqc.set(bob, true, true);
        assertTrue(module.moduleCheck(alice, bob, 1, compliance));
        vm.etch(address(0x0A02), "");
        assertFalse(module.moduleCheck(alice, bob, 1, compliance), "fails closed without the precompile");
    }
}

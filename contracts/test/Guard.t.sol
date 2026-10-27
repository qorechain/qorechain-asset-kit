// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.28;

import {Test} from "forge-std/Test.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {QoreChainHybridHolderGuard} from "../src/guard/QoreChainHybridHolderGuard.sol";
import {MockPqcKeyStatus, PqcPrecompile} from "./mocks/MockPqcKeyStatus.sol";

contract GuardTest is Test {
    QoreChainHybridHolderGuard guard;
    address owner = makeAddr("owner");
    address alice = makeAddr("alice");
    address bob = makeAddr("bob");

    function setUp() public {
        guard = new QoreChainHybridHolderGuard(owner);
    }

    function test_FailsClosedWhenPrecompileIsInactive() public view {
        // Mainnet today: 0x0A02 has no code and returns empty data.
        assertFalse(guard.precompileActive());
        assertFalse(guard.isHybridHolder(alice));
        (bool responded,,,) = guard.keyStatus(alice);
        assertFalse(responded);
    }

    function test_RequiresRegisteredAndPossessionProven() public {
        MockPqcKeyStatus pqc = PqcPrecompile.install(vm);
        assertTrue(guard.precompileActive());
        assertFalse(guard.isHybridHolder(alice));

        pqc.set(alice, true, false);
        assertFalse(guard.isHybridHolder(alice), "a key without proof of possession is not enough");

        pqc.set(alice, true, true);
        assertTrue(guard.isHybridHolder(alice));
        assertTrue(guard.isEligible(alice));
        (bool responded, bool registered, uint8 algorithmId, bool proven) = guard.keyStatus(alice);
        assertTrue(responded && registered && proven);
        assertEq(algorithmId, 1);
    }

    function test_FailsClosedOnLegacyLayout() public {
        MockPqcKeyStatus pqc = PqcPrecompile.install(vm);
        pqc.set(alice, true, true);
        pqc.setLegacyLayout(true);
        assertFalse(guard.isHybridHolder(alice), "no possessionProven field means not proven");
        pqc.set(bob, false, false);
        assertFalse(guard.isHybridHolder(bob));
    }

    function test_RequiresMlDsa87AlgorithmId() public {
        MockPqcKeyStatus pqc = PqcPrecompile.install(vm);
        pqc.set(alice, true, true);
        assertTrue(guard.isHybridHolder(alice));
        pqc.setAlgorithm(alice, 2);
        assertFalse(guard.isHybridHolder(alice), "only algorithm id 1 (ML-DSA-87) is accepted");
    }

    function test_FailsClosedOnMalformedAnswer() public {
        MockPqcKeyStatus pqc = PqcPrecompile.install(vm);
        pqc.set(alice, true, true);
        pqc.setMalformed(true);
        (bool responded,,,) = guard.keyStatus(alice);
        assertFalse(responded);
        assertFalse(guard.isHybridHolder(alice));
    }

    function test_DecoderRejectsBadLayouts() public view {
        bytes memory good = abi.encode(true, uint8(1), new bytes(2592), true);
        (bool valid, bool registered, uint8 alg, bool proven) = guard.decodeKeyStatus(good);
        assertTrue(valid && registered && alg == 1 && proven);

        bytes memory truncated = new bytes(200);
        for (uint256 i = 0; i < 200; i++) {
            truncated[i] = good[i];
        }
        (valid,,,) = guard.decodeKeyStatus(truncated);
        assertFalse(valid, "length word larger than the data");

        bytes memory badBool = abi.encode(uint256(2), uint8(1), new bytes(0), true);
        (valid,,,) = guard.decodeKeyStatus(badBool);
        assertFalse(valid, "bool word out of range");

        (valid,,,) = guard.decodeKeyStatus(abi.encode(true, uint8(1), new bytes(5000), true));
        assertFalse(valid, "key longer than the bound");
    }

    function test_RequireHybridHolderReverts() public {
        PqcPrecompile.install(vm);
        vm.expectRevert(abi.encodeWithSelector(QoreChainHybridHolderGuard.HybridKeyRequired.selector, alice));
        guard.requireHybridHolder(alice);
    }

    function test_ExemptionsAreOwnerOnlyAndLogged() public {
        vm.expectRevert(abi.encodeWithSelector(Ownable.OwnableUnauthorizedAccount.selector, alice));
        vm.prank(alice);
        guard.setExempt(alice, true, "self");

        vm.expectEmit(address(guard));
        emit QoreChainHybridHolderGuard.ExemptionSet(bob, true, "vault contract");
        vm.prank(owner);
        guard.setExempt(bob, true, "vault contract");
        assertTrue(guard.isHybridHolder(bob));
    }
}

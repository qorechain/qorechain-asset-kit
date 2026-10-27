// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.28;

import {Test} from "forge-std/Test.sol";
import {IERC7518} from "../src/partitions/IERC7518.sol";

contract Erc7518InterfaceTest is Test {
    function test_InterfaceIdMatchesTheErc() public pure {
        assertEq(type(IERC7518).interfaceId, bytes4(0x5a264a5d));
    }
}

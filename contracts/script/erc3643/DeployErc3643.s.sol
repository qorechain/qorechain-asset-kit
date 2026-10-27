// SPDX-License-Identifier: GPL-3.0-or-later
// Compiles together with the GPL-3.0 ERC-3643 reference implementation; see TrexSuiteDeployer.sol.
pragma solidity 0.8.17;

import {console2} from "forge-std/Script.sol";
import {TrexSuiteDeployer} from "./TrexSuiteDeployer.sol";

/// @notice Deploys the ERC-3643 reference implementation and an example token with the
/// QoreChainHybridHolderModule bound to its compliance.
///
/// Dry run (no funds spent; `forge build` first so the guard and module artifacts exist):
///   forge script script/erc3643/DeployErc3643.s.sol --rpc-url qorechain_testnet --sender <deployer>
/// Broadcasting needs a registered ML-DSA-87 key and an open EVM authorization window with no
/// allowed_targets; see script/QoreChainTestnet.sol. Environment (optional): TREX_AGENT, TREX_SALT.
contract DeployErc3643 is TrexSuiteDeployer {
    function run() external returns (Infra memory infra, Suite memory suite) {
        require(block.chainid != 9801, "QoreChain mainnet: the hybrid-holder guard is testnet only");
        address owner = msg.sender;
        address agent = vm.envOr("TREX_AGENT", owner);
        string memory salt = vm.envOr("TREX_SALT", string("example-bond-2030"));
        vm.startBroadcast();
        infra = deployInfra(owner);
        suite = deploySuite(infra, owner, agent, salt, "Example 2030 Bond", "EB30");
        vm.stopBroadcast();
        console2.log("TREXFactory", address(infra.factory));
        console2.log("token", address(suite.token));
        console2.log("identity registry", address(suite.identityRegistry));
        console2.log("modular compliance", address(suite.compliance));
        console2.log("hybrid holder guard", suite.guard);
        console2.log("hybrid holder module", suite.module);
    }
}

// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.28;

import {Script, console2} from "forge-std/Script.sol";

/// @notice Shared checks for the deployment scripts. Every script in this folder is meant to be run as a
/// DRY RUN first (no --broadcast). Broadcasting on QoreChain needs two things that happen on the native
/// lane, outside Foundry:
///
/// 1. The deployer account has a registered ML-DSA-87 key (MsgRegisterPQCKeyV2 with proof of possession).
/// 2. The deployer has an open EVM authorization window, opened by a hybrid-signed native-lane transaction
///    (/qorechain.pqc.v1.MsgOpenEVMWindow) whose max_value covers the value plus the maximum fee
///    (gas limit x max fee per gas) of every transaction the script sends, whose max_txs covers their count,
///    and whose allowed_targets is EMPTY (a window with allowed_targets refuses contract creation).
///    Opening the window advances the account sequence, which is also the EVM nonce: open it first, then
///    run the script. The QoreChain SDK messages `pqc.openEvmWindow` and the `fetchEvmWindow` query
///    (TypeScript) or `qorsdk.msg.pqc.open_evm_window` (Python) build and read it.
///
/// Simulation (eth_call, gas estimation) needs no window, so a dry run against the testnet RPC works from
/// any address.
abstract contract QoreChainTestnet is Script {
    uint256 internal constant TESTNET_CHAIN_ID = 9800;
    uint256 internal constant MAINNET_CHAIN_ID = 9801;
    address internal constant PQC_KEY_STATUS = address(0x0A02);

    /// @dev Prints the network, whether the pqcKeyStatus precompile answers on the REAL node (read with
    /// eth_call through vm.rpc, because a local fork does not run QoreChain precompiles), and the
    /// deployer's key status. Refuses mainnet: the guard is testnet only.
    function preflight(address deployer) internal {
        require(block.chainid != MAINNET_CHAIN_ID, "QoreChain mainnet: the hybrid-holder guard is testnet only");
        console2.log("chain id", block.chainid);
        if (block.chainid != TESTNET_CHAIN_ID) {
            console2.log("not the QoreChain testnet: skipping the precompile check");
            return;
        }
        string memory params = string.concat(
            '[{"to":"0x0000000000000000000000000000000000000a02","data":"',
            vm.toString(abi.encodeWithSignature("pqcKeyStatus(address)", deployer)),
            '"},"latest"]'
        );
        bytes memory ret = vm.rpc("eth_call", params);
        if (ret.length < 160) {
            console2.log("pqcKeyStatus precompile: NOT active on this node");
            return;
        }
        (bool registered,,, bool possessionProven) = abi.decode(ret, (bool, uint8, bytes, bool));
        console2.log("pqcKeyStatus precompile: active");
        console2.log("deployer key registered", registered);
        console2.log("deployer possession proven", possessionProven);
        if (!registered) {
            console2.log("Broadcasting would fail: register an ML-DSA-87 key and open an EVM window first.");
        } else {
            console2.log("Before --broadcast: open an EVM authorization window (see script/QoreChainTestnet.sol).");
        }
    }
}

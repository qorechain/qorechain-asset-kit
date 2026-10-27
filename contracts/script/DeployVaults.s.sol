// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.28;

import {console2} from "forge-std/Script.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {QoreChainHybridHolderGuard} from "../src/guard/QoreChainHybridHolderGuard.sol";
import {QoreChainRwaVault} from "../src/vaults/QoreChainRwaVault.sol";
import {QoreChainRwaAsyncVault} from "../src/vaults/QoreChainRwaAsyncVault.sol";
import {DeployCmtat} from "./DeployCmtat.s.sol";

/// @notice Deploys an ERC-4626 vault and an ERC-7540 vault over a restricted asset, both gated by a
/// {QoreChainHybridHolderGuard}, and exempts the two vault contracts in that guard.
///
/// With VAULT_ASSET and VAULT_GUARD set, it uses them (the broadcaster must own the guard). Without them,
/// it first deploys the example CMTAT token and its guard (see DeployCmtat.s.sol).
///
/// Dry run (no funds spent):
///   forge script script/DeployVaults.s.sol --rpc-url qorechain_testnet --sender <deployer>
contract DeployVaults is DeployCmtat {
    function run() external override returns (Deployment memory d) {
        address admin = msg.sender;
        preflight(msg.sender);
        address assetAddr = vm.envOr("VAULT_ASSET", address(0));
        address guardAddr = vm.envOr("VAULT_GUARD", address(0));
        vm.startBroadcast();
        if (assetAddr == address(0) || guardAddr == address(0)) {
            d = deploy(admin, "Example Fund Unit", "EFU", "CH0000000001", "https://example.org/fund-terms.pdf");
            assetAddr = address(d.token);
            guardAddr = address(d.guard);
        }
        QoreChainHybridHolderGuard guard = QoreChainHybridHolderGuard(guardAddr);
        QoreChainRwaVault vault = new QoreChainRwaVault(IERC20(assetAddr), "Example Fund Shares", "sEFU", guard);
        QoreChainRwaAsyncVault asyncVault =
            new QoreChainRwaAsyncVault(IERC20(assetAddr), "Example Fund Async Shares", "aEFU", guard, admin);
        guard.setExempt(address(vault), true, "ERC-4626 vault contract");
        guard.setExempt(address(asyncVault), true, "ERC-7540 vault contract");
        vm.stopBroadcast();
        console2.log("asset", assetAddr);
        console2.log("guard", guardAddr);
        console2.log("erc4626 vault", address(vault));
        console2.log("erc7540 vault", address(asyncVault));
    }
}

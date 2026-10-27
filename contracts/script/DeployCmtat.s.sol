// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.28;

import {console2} from "forge-std/Script.sol";
import {CMTATStandalone} from "CMTAT/deployment/CMTATStandalone.sol";
import {ICMTATConstructor} from "CMTAT/interfaces/technical/ICMTATConstructor.sol";
import {IERC1643CMTAT} from "CMTAT/interfaces/tokenization/draft-IERC1643CMTAT.sol";
import {IRuleEngine} from "CMTAT/interfaces/engine/IRuleEngine.sol";
import {QoreChainHybridHolderGuard} from "../src/guard/QoreChainHybridHolderGuard.sol";
import {QoreChainHybridHolderRule} from "../src/cmtat/QoreChainHybridHolderRule.sol";
import {QoreChainTestnet} from "./QoreChainTestnet.sol";

/// @notice Deploys a CMTAT v3 token (standalone, no proxy, no forwarder) whose rule engine is the
/// {QoreChainHybridHolderRule}, itself mapped to a new {QoreChainHybridHolderGuard}.
///
/// Dry run (no funds spent):
///   forge script script/DeployCmtat.s.sol --rpc-url qorechain_testnet --sender <deployer>
/// Environment (optional): CMTAT_ADMIN, CMTAT_NAME, CMTAT_SYMBOL, CMTAT_TOKEN_ID, CMTAT_TERMS_URI.
contract DeployCmtat is QoreChainTestnet {
    struct Deployment {
        QoreChainHybridHolderGuard guard;
        QoreChainHybridHolderRule rule;
        CMTATStandalone token;
    }

    function run() external virtual returns (Deployment memory d) {
        address admin = vm.envOr("CMTAT_ADMIN", msg.sender);
        preflight(msg.sender);
        vm.startBroadcast();
        d = deploy(
            admin,
            vm.envOr("CMTAT_NAME", string("Example Ledger-Based Note")),
            vm.envOr("CMTAT_SYMBOL", string("ELBN")),
            vm.envOr("CMTAT_TOKEN_ID", string("CH0000000000")),
            vm.envOr("CMTAT_TERMS_URI", string("https://example.org/terms.pdf"))
        );
        vm.stopBroadcast();
        console2.log("guard", address(d.guard));
        console2.log("rule", address(d.rule));
        console2.log("token", address(d.token));
    }

    function deploy(
        address admin,
        string memory name,
        string memory symbol,
        string memory tokenId,
        string memory termsUri
    ) public returns (Deployment memory d) {
        d.guard = new QoreChainHybridHolderGuard(admin);
        d.rule = new QoreChainHybridHolderRule(d.guard);
        d.token = new CMTATStandalone(
            address(0),
            admin,
            ICMTATConstructor.ERC20Attributes({name: name, symbol: symbol, decimalsIrrevocable: 0}),
            ICMTATConstructor.ExtraInformationAttributes({
                tokenId: tokenId,
                terms: IERC1643CMTAT.DocumentInfo({name: "Terms", uri: termsUri, documentHash: bytes32(0)}),
                information: "Issued with qorechain-asset-kit (CMTAT v3.2.0)"
            }),
            ICMTATConstructor.Engine({ruleEngine: IRuleEngine(address(d.rule))})
        );
    }
}

// SPDX-License-Identifier: GPL-3.0-or-later
// This file compiles together with the ERC-3643 reference implementation (T-REX v4.1.6) and ONCHAINID,
// both GPL-3.0, and is therefore GPL-3.0-or-later itself (LICENSES/GPL-3.0.txt). The rest of this
// repository is Apache-2.0.
pragma solidity 0.8.17;

import {Script} from "forge-std/Script.sol";
import {Token} from "T-REX/token/Token.sol";
import {ClaimTopicsRegistry} from "T-REX/registry/implementation/ClaimTopicsRegistry.sol";
import {IdentityRegistry} from "T-REX/registry/implementation/IdentityRegistry.sol";
import {IdentityRegistryStorage} from "T-REX/registry/implementation/IdentityRegistryStorage.sol";
import {TrustedIssuersRegistry} from "T-REX/registry/implementation/TrustedIssuersRegistry.sol";
import {ModularCompliance} from "T-REX/compliance/modular/ModularCompliance.sol";
import {TREXImplementationAuthority} from "T-REX/proxy/authority/TREXImplementationAuthority.sol";
import {ITREXImplementationAuthority} from "T-REX/proxy/authority/ITREXImplementationAuthority.sol";
import {TREXFactory} from "T-REX/factory/TREXFactory.sol";
import {ITREXFactory} from "T-REX/factory/ITREXFactory.sol";
import {Identity} from "@onchain-id/solidity/contracts/Identity.sol";
import {ImplementationAuthority} from "@onchain-id/solidity/contracts/proxy/ImplementationAuthority.sol";
import {IdFactory} from "@onchain-id/solidity/contracts/factory/IdFactory.sol";

/// @notice Deploys the ERC-3643 reference implementation (T-REX v4.1.6, used unmodified as a dependency)
/// and one token suite whose modular compliance has the QoreChainHybridHolderModule bound.
/// The guard and the module are Apache-2.0 contracts compiled with solc 0.8.28; they are deployed from
/// their build artifacts (vm.deployCode), not imported.
abstract contract TrexSuiteDeployer is Script {
    struct Infra {
        TREXImplementationAuthority implementationAuthority;
        IdFactory idFactory;
        TREXFactory factory;
    }

    struct Suite {
        Token token;
        IdentityRegistry identityRegistry;
        ModularCompliance compliance;
        address guard;
        address module;
    }

    /// @dev Deploys the shared infrastructure. The caller (msg.sender of the calls, the broadcaster in a
    /// script) becomes the owner of the authorities and factories.
    function deployInfra(address owner) internal returns (Infra memory infra) {
        ITREXImplementationAuthority.TREXContracts memory impls = ITREXImplementationAuthority.TREXContracts({
            tokenImplementation: address(new Token()),
            ctrImplementation: address(new ClaimTopicsRegistry()),
            irImplementation: address(new IdentityRegistry()),
            irsImplementation: address(new IdentityRegistryStorage()),
            tirImplementation: address(new TrustedIssuersRegistry()),
            mcImplementation: address(new ModularCompliance())
        });
        infra.implementationAuthority = new TREXImplementationAuthority(true, address(0), address(0));
        infra.implementationAuthority
            .addAndUseTREXVersion(ITREXImplementationAuthority.Version({major: 4, minor: 1, patch: 6}), impls);
        Identity identityImplementation = new Identity(owner, true);
        ImplementationAuthority identityAuthority = new ImplementationAuthority(address(identityImplementation));
        infra.idFactory = new IdFactory(address(identityAuthority));
        infra.factory = new TREXFactory(address(infra.implementationAuthority), address(infra.idFactory));
        infra.idFactory.addTokenFactory(address(infra.factory));
    }

    /// @dev Deploys the guard and the module from their artifacts, then a token suite with the module bound.
    /// No claim topics are required: an address is verified once its identity is registered. Add claim
    /// topics and trusted issuers for production use.
    function deploySuite(
        Infra memory infra,
        address owner,
        address agent,
        string memory salt,
        string memory name,
        string memory symbol
    ) internal returns (Suite memory s) {
        s.guard = deployCode("QoreChainHybridHolderGuard.sol:QoreChainHybridHolderGuard", abi.encode(owner));
        s.module = deployCode("QoreChainHybridHolderModule.sol:QoreChainHybridHolderModule", abi.encode(s.guard));

        address[] memory agents = new address[](1);
        agents[0] = agent;
        address[] memory modules = new address[](1);
        modules[0] = s.module;
        infra.factory
            .deployTREXSuite(
                salt,
                ITREXFactory.TokenDetails({
                    owner: owner,
                    name: name,
                    symbol: symbol,
                    decimals: 0,
                    irs: address(0),
                    ONCHAINID: address(0),
                    irAgents: agents,
                    tokenAgents: agents,
                    complianceModules: modules,
                    complianceSettings: new bytes[](0)
                }),
                ITREXFactory.ClaimDetails({
                    claimTopics: new uint256[](0), issuers: new address[](0), issuerClaims: new uint256[][](0)
                })
            );
        s.token = Token(infra.factory.getToken(salt));
        s.identityRegistry = IdentityRegistry(address(s.token.identityRegistry()));
        s.compliance = ModularCompliance(address(s.token.compliance()));
    }
}

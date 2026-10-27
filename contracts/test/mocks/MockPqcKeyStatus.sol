// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.28;

import {Vm} from "forge-std/Vm.sol";

/// @notice Test double of the QoreChain pqcKeyStatus precompile, etched at 0x0A02.
contract MockPqcKeyStatus {
    struct Status {
        bool registered;
        bool possessionProven;
        uint8 algorithmId;
    }

    mapping(address => Status) internal _status;
    /// @dev When true, answers in the three-field layout of older chain versions.
    bool public legacyLayout;

    function set(address account, bool registered, bool possessionProven) external {
        _status[account] = Status(registered, possessionProven, registered ? 1 : 0);
    }

    function setLegacyLayout(bool value) external {
        legacyLayout = value;
    }

    /// @dev When true, answers with a wrong offset for the dynamic `pubkey`.
    bool public malformed;

    function setMalformed(bool value) external {
        malformed = value;
    }

    function setAlgorithm(address account, uint8 algorithmId) external {
        _status[account].algorithmId = algorithmId;
    }

    fallback(bytes calldata data) external returns (bytes memory) {
        address account = abi.decode(data[4:], (address));
        Status memory s = _status[account];
        // The real precompile charges a flat 2,500 gas; the key is built in memory to stay cheap.
        bytes memory pubkey = s.registered ? new bytes(2592) : bytes("");
        if (legacyLayout) return abi.encode(s.registered, s.algorithmId, pubkey);
        bytes memory out = abi.encode(s.registered, s.algorithmId, pubkey, s.possessionProven);
        if (malformed) {
            assembly {
                mstore(add(out, 0x60), 0xa0) // offset word of `pubkey`
            }
        }
        return out;
    }
}

library PqcPrecompile {
    address internal constant ADDRESS = address(0x0A02);

    /// @notice Installs the mock at 0x0A02 and returns a handle to configure it.
    function install(Vm vm) internal returns (MockPqcKeyStatus) {
        MockPqcKeyStatus impl = new MockPqcKeyStatus();
        vm.etch(ADDRESS, address(impl).code);
        return MockPqcKeyStatus(payable(ADDRESS));
    }
}

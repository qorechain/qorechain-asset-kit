// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.28;

/// @title IQorePqcKeyStatus
/// @notice The QoreChain `pqcKeyStatus` precompile at address 0x0A02.
/// @dev Active on the QoreChain testnet only. On mainnet the address is not an active precompile
/// and a call returns empty data; mainnet activation is a governance decision that has not been taken.
/// `possessionProven` is encoded after the dynamic `pubkey`, so an older three-field decoder keeps working.
/// A contract that relies on the returned key MUST require `possessionProven == true`.
interface IQorePqcKeyStatus {
    function pqcKeyStatus(address account)
        external
        view
        returns (bool registered, uint8 algorithmId, bytes memory pubkey, bool possessionProven);
}

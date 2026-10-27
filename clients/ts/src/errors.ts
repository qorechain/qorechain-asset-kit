// SPDX-License-Identifier: Apache-2.0

/** The five proposed modules. None of them exists on QoreChain. */
export type ModuleName = "x/asset" | "x/identity" | "x/compliance" | "x/settlement" | "x/attest";

/** Base class of every error thrown by this package. */
export class AssetKitError extends Error {
  constructor(
    message: string,
    /** Stable machine-readable code. */
    readonly code: string,
    /** Module the error belongs to. */
    readonly module: ModuleName,
  ) {
    super(message);
    this.name = new.target.name;
  }
}

/**
 * Thrown by every call of {@link ChainClient}: the module is a proposal, is not
 * part of QoreChain, and needs a chain upgrade that is not scheduled.
 */
export class ChainUpgradeRequired extends AssetKitError {
  constructor(module: ModuleName) {
    super(
      `${module} is a proposal and does not exist on QoreChain; it requires a chain upgrade that is not scheduled. ` +
        "Use MockChain to build and test, or the EVM adapters (contracts/) for what works on QoreChain today.",
      "CHAIN_UPGRADE_REQUIRED",
      module,
    );
  }
}

/**
 * A message refused by {@link MockChain}. `code` is the name of the value in the
 * module's proposed `ErrorCode` enum, for example `ERROR_CODE_ADDRESS_FROZEN`.
 */
export class MockChainError extends AssetKitError {}

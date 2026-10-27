// SPDX-License-Identifier: Apache-2.0
//
// Copies the ABI and creation bytecode of the contracts the console deploys from the Foundry build
// (contracts/out, run `forge build` in contracts/ first) into src/artifacts. Only `abi` and `bytecode`
// are kept: no metadata, no source paths.

import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const out = join(here, "..", "..", "..", "contracts", "out");
const dest = join(here, "..", "src", "artifacts");

const CONTRACTS = [
  ["QoreChainHybridHolderGuard.sol", "QoreChainHybridHolderGuard"],
  ["QoreChainHybridHolderRule.sol", "QoreChainHybridHolderRule"],
  ["CMTATStandalone.sol", "CMTATStandalone"],
];

mkdirSync(dest, { recursive: true });
for (const [file, name] of CONTRACTS) {
  const artifact = JSON.parse(readFileSync(join(out, file, `${name}.json`), "utf8"));
  const bytecode = artifact.bytecode?.object;
  if (typeof bytecode !== "string" || !bytecode.startsWith("0x") || bytecode.length < 4) {
    throw new Error(`${name}: no creation bytecode in the artifact`);
  }
  if (artifact.bytecode.linkReferences && Object.keys(artifact.bytecode.linkReferences).length > 0) {
    throw new Error(`${name}: needs library linking, which the console does not support`);
  }
  const slim = { contractName: name, abi: artifact.abi, bytecode };
  writeFileSync(join(dest, `${name}.json`), `${JSON.stringify(slim, null, 2)}\n`);
  console.log(`${name}: ${(bytecode.length - 2) / 2} bytes`);
}

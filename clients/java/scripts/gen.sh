#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Regenerates the Java sources from the proposed protos in ../../proto.
# Needs protoc 36.x (the gencode must match the protobuf-java 4.36.x runtime).
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf src/main/java/io/github/qorechain/assetkit/proto
protoc --java_out=src/main/java -I ../../proto $(cd ../../proto && find qorechain -name '*.proto' | sort)
OUT=src/main/java/io/github/qorechain/assetkit/proto PATTERN='*.java'

# Generated files carry the licence of the protos they come from.
find "$OUT" -name "$PATTERN" -print0 | while IFS= read -r -d "" f; do
  head -5 "$f" | grep -q "SPDX-License-Identifier" || { printf "%s\n" "// SPDX-License-Identifier: Apache-2.0" | cat - "$f" > "$f.tmp" && mv "$f.tmp" "$f"; }
done

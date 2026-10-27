#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Regenerates src/gen from the proposed protos in ../../proto with ts-proto (pinned in package.json).
# Needs protoc 36.x on PATH.
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf src/gen/qorechain
protoc --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=src/gen \
  --ts_proto_opt=esModuleInterop=true,forceLong=string,outputServices=false,useExactTypes=false,importSuffix=.js,snakeToCamel=true,exportCommonSymbols=false \
  -I ../../proto $(cd ../../proto && find qorechain -name '*.proto' | sort)
OUT=src/gen/qorechain PATTERN='*.ts'
# Generated files carry the licence of the protos they come from.
find "$OUT" -name "$PATTERN" -print0 | while IFS= read -r -d "" f; do
  head -5 "$f" | grep -q "SPDX-License-Identifier" || { printf "%s\n" "// SPDX-License-Identifier: Apache-2.0" | cat - "$f" > "$f.tmp" && mv "$f.tmp" "$f"; }
done

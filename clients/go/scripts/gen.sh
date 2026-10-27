#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
#
# Regenerates gen/ from the proposed protos in ../../proto.
# Requires protoc and protoc-gen-go v1.36.12 on PATH:
#   go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.36.12
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf gen
protoc --go_out=. --go_opt=module=github.com/qorechain/qorechain-asset-kit/clients/go \
  -I ../../proto $(find ../../proto -name '*.proto' | sort)
OUT=gen PATTERN='*.pb.go'

# Generated files carry the licence of the protos they come from.
find "$OUT" -name "$PATTERN" -print0 | while IFS= read -r -d "" f; do
  head -5 "$f" | grep -q "SPDX-License-Identifier" || { printf "%s\n" "// SPDX-License-Identifier: Apache-2.0" | cat - "$f" > "$f.tmp" && mv "$f.tmp" "$f"; }
done

#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
#
# Regenerates src/qorechain_asset_kit/gen from ../../proto with protoc.
# The generated imports are rewritten so that everything lives inside the
# qorechain_asset_kit package (no top-level "qorechain" package is created).
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
proto="$here/../../proto"
out="$here/src/qorechain_asset_kit/gen"
rm -rf "$out"
mkdir -p "$out"
(cd "$proto" && protoc -I . --python_out="$out" --pyi_out="$out" $(find qorechain -name '*.proto' | sort))
find "$out" -type d -exec sh -c 'printf "# SPDX-License-Identifier: Apache-2.0\n" > "$1/__init__.py"' _ {} \;
find "$out" -name '*_pb2.py*' | while read -r f; do
  sed -i.bak -e 's/^from qorechain\./from qorechain_asset_kit.gen.qorechain./' "$f"
  rm -f "$f.bak"
  { printf '# SPDX-License-Identifier: Apache-2.0\n'; cat "$f"; } > "$f.tmp" && mv "$f.tmp" "$f"
done

#!/usr/bin/env bash

# Script to copy the SearXNG code into our _vendor directory.

set -euo pipefail

REV="${1:?provide 'CURRENT' or 'HEAD' or a SearXNG commit hash}"
BRANCH="master"

echo "Vendoring SearXNG $REV..."
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC_DIR="$ROOT/src/simplexng"
VENDOR_DIR="$SRC_DIR/_vendor"
# Record the exact commit and REV information for provenance
VERSION_FILE="$SRC_DIR/searxng_version.txt"


if [ "$REV" = "CURRENT" ]; then
   REV=$(cat $VERSION_FILE)
   echo "Using current version: $REV from $VERSION_FILE"
fi

set -x

tmpdir="./tmp"
rm -rf "$tmpdir"
mkdir -p "$tmpdir"

git clone --depth 1 --branch "$BRANCH" https://github.com/searxng/searxng.git "$tmpdir"

if [ "$REV" != "HEAD" ]; then
    git -C "$tmpdir" fetch --depth 1 origin "$REV"
    git -C "$tmpdir" checkout --quiet "$REV"
fi

set +x

# Get the actual commit hash
COMMIT_HASH="$(git -C "$tmpdir" rev-parse HEAD)"

echo "Resolved to commit: $COMMIT_HASH"

# Generate version_frozen.py to avoid git-related errors in vendored code
echo "Generating version_frozen.py..."
(cd "$tmpdir" && uv run python -m searx.version freeze)

set -x

# Remove old vendor copy
rm -rf "$VENDOR_DIR"
mkdir -p "$VENDOR_DIR"
touch "$VENDOR_DIR/__init__.py"

# Copy only the Python package + licences
rsync -a --delete \
      --exclude 'tests' \
      --exclude 'utils' \
      --exclude '.git' \
      "$tmpdir/searx" "$VENDOR_DIR/"

cp "$tmpdir/LICENSE" "$VENDOR_DIR/SEARXNG_LICENSE"

set +x

# Also copy AGPL requirements notice
cat > "$VENDOR_DIR/LICENSE_NOTICE" << EOF
This directory contains code from SearXNG (https://github.com/searxng/searxng)
which is licensed under the GNU Affero General Public License v3.0 or later.
As this code is included in this package, the entire package is subject to
the AGPL-3.0-or-later license terms. See SEARXNG_LICENSE for full text.
EOF


echo "$COMMIT_HASH" > "$VERSION_FILE"

echo
echo "✔ Done. Vendored commit $COMMIT_HASH"
echo "Version info written: $VERSION_FILE"
echo "Commit the changes and build as usual."
#!/usr/bin/env bash
# Install the wasmtime runtime (Linux / macOS / WSL).
# Installs to ~/.wasmtime/bin/wasmtime — doesn't require sudo or root.
#
# Run once, then use `bin/dvid3 encode ...` or `bin/dvid3 decode ...`.

set -e

if command -v wasmtime >/dev/null 2>&1; then
    echo "wasmtime already installed: $(command -v wasmtime)"
    wasmtime --version
    exit 0
fi

echo "Installing wasmtime to \$HOME/.wasmtime/bin ..."
curl -sSL https://wasmtime.dev/install.sh | bash

# Refresh PATH so we can verify in this shell.
if [[ -x "${HOME}/.wasmtime/bin/wasmtime" ]]; then
    echo ""
    echo "Installed:"
    "${HOME}/.wasmtime/bin/wasmtime" --version
    echo ""
    echo "To add wasmtime to your PATH permanently, add this to ~/.bashrc or ~/.zshrc:"
    echo "    export PATH=\"\$HOME/.wasmtime/bin:\$PATH\""
else
    echo "warning: wasmtime install script ran but the binary is not at the expected location." >&2
    echo "Try running:  curl -sSL https://wasmtime.dev/install.sh | bash" >&2
    exit 1
fi

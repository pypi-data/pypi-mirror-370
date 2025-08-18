#!/bin/bash
# Exit on non-zero returns from commands.
set -e
cd "$(dirname "${BASH_SOURCE[0]}")"
uv tool run ruff@0.11.13 check . --fix
uv tool run ruff@0.11.13 format .

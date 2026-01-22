#!/bin/bash
# Run the Rietman Familie Bingo app from the project root
# Make this file executable with: chmod +x run.command
# Double-click in Finder or run from Xcode via an External Build System or Run Script.

set -euo pipefail

# Go to the directory of this script (project root)
cd "$(dirname "$0")"

# If you use a virtual environment, uncomment and adjust the next line:
# source .venv/bin/activate

# If streamlit isn't on PATH, set an absolute path to your venv or python:
# /absolute/path/to/.venv/bin/streamlit run bingo.py
# or
# /usr/bin/env python3 -m streamlit run bingo.py

# Default: use streamlit on PATH
exec /usr/bin/env streamlit run bingo.py

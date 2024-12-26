#!/bin/bash

# Detect the directory the script is in
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")

# Use absolute paths for the input UI files and output Python files
poetry run pyuic5 "$SCRIPT_DIR/watermark_window.ui" > "$SCRIPT_DIR/watermark_window_ui.py"
poetry run pyuic5 "$SCRIPT_DIR/watermark_progress.ui" > "$SCRIPT_DIR/watermark_progress_ui.py"

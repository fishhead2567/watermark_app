#!/bin/bash

# Figure out where the code lives
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")

# make a directory into which pyinstaller should install files

mkdir -p build

poetry run pyinstaller -F $SCRIPT_DIR/watermark_gui.py --specpath build
poetry run pyinstaller -F $SCRIPT_DIR/watermark_cli.py --specpath build

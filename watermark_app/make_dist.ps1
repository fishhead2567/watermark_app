# Figure out where the code lives
$SCRIPT_DIR=Split-Path -Parent -Path $MyInvocation.MyCommand.Definition

# make a directory into which pyinstaller should install files
New-Item -ItemType Directory -Force -path build

poetry run pyinstaller -F $SCRIPT_DIR\watermark_gui.py --specpath build
poetry run pyinstaller -F $SCRIPT_DIR\watermark_cli.py --specpath build

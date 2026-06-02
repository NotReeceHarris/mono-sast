"""Runtime configuration shared across all tool modules."""

import os
import sys

# Falls back to /target, the conventional mount point inside the Docker image.
TARGET_DIR = os.environ.get("TARGET_DIR", "/target")

# Parse o= and f= from argv.
#   o=<dir>          directory to write output files into (default: current working dir)
#   f=<fmt,...>      comma-separated list of output formats: sarif, html (default: sarif)
OUTPUT_DIR = "."
OUTPUT_FORMATS = {"sarif"}

for _arg in sys.argv[1:]:
    if _arg.startswith("o="):
        OUTPUT_DIR = _arg[2:].strip() or "."
    elif _arg.startswith("f="):
        _fmts = {f.strip() for f in _arg[2:].split(",") if f.strip()}
        if _fmts:
            OUTPUT_FORMATS = _fmts
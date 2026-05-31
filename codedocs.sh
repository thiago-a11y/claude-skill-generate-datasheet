#!/bin/bash
# CodeDocs — run from anywhere
# Usage: codedocs /path/to/project [--name "Product Name" --target react --erp TOTVS]
CODEDOCS_HOME="/Users/thiagoxavier/claude-skill-generate-datasheet"
PYTHONPATH="$CODEDOCS_HOME" python3 -m codedocs "$@"

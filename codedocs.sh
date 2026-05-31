#!/bin/bash
# CodeDocs — run from anywhere
# Usage: codedocs /path/to/project [--migration --target react+fastapi --erp SAP TOTVS]
CODEDOCS_HOME="/Users/thiagoxavier/claude-skill-generate-datasheet"
cd "$CODEDOCS_HOME" && python3 -m codedocs "$@"

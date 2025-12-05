#!/usr/bin/env python3
"""
Generates an index-wrapper.js that loads .env file before user's function.
This ensures custom environment variables are available at runtime.
"""

import sys
from pathlib import Path

WRAPPER_PATH = Path("index-wrapper.js")
USER_INDEX_PATH = Path("index.js")

WRAPPER_TEMPLATE = """// Auto-generated wrapper to load .env file
require('dotenv').config();

// Load user's function
const userFunction = require('./index-original.js');

// Export the handler
exports.handler = userFunction.handler;
"""

def main():
    """
    Create a wrapper that loads dotenv before the user's function.
    Renames user's index.js to index-original.js and creates new index.js wrapper.
    """
    
    # Check if .env file exists
    env_exists = Path(".env").exists()
    
    if not env_exists:
        print("No .env file found, skipping wrapper generation")
        sys.exit(0)
    
    # Check if user's index.js exists
    if not USER_INDEX_PATH.exists():
        print("ERROR: index.js not found", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Rename user's index.js to index-original.js
        USER_INDEX_PATH.rename("index-original.js")
        print("✓ Renamed index.js to index-original.js")
        
        # Create wrapper as new index.js
        USER_INDEX_PATH.write_text(WRAPPER_TEMPLATE, encoding="utf-8")
        print("✓ Created index.js wrapper with dotenv loader")
        
    except Exception as exc:
        print(f"ERROR: Failed to create wrapper: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

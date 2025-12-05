#!/usr/bin/env python3

import json
import sys
from pathlib import Path

PACKAGE_PATH = Path("package.json")

DEFAULT_NAME = "user-function"
DEFAULT_VERSION = "0.0.1"
DEFAULT_MAIN = "index.js"

FUNCTIONS_FRAMEWORK_VERSION = "^3.0.0"
EXPRESS_VERSION = "^4.18.2"

START_SCRIPT = f"functions-framework --target=handler --port=${{PORT:-8080}} --host=0.0.0.0"

def main():
    """
    Load or create package.json, ensure @google-cloud/functions-framework dependency,
    ensure start script for Cloud Functions Framework, and write back to file.
    
    Process:
      1. Load existing package.json or create default skeleton
      2. Add @google-cloud/functions-framework to dependencies
      3. Add start script to invoke functions-framework CLI
      4. Write updated package.json back to disk
    """
    # Try to load existing package.json; if invalid or missing, use defaults
    if PACKAGE_PATH.exists():
        try:
            content = PACKAGE_PATH.read_text(encoding="utf-8")
            data = json.loads(content)
            print("✓ Loaded existing package.json")
        except json.JSONDecodeError as exc:
            print(f"⚠ Invalid JSON in package.json: {exc}")
            print("  Creating new default skeleton...")
            data = _create_default_package_json()
        except Exception as exc:
            print(f"✗ Error reading package.json: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        print("✓ package.json not found; creating default skeleton")
        data = _create_default_package_json()

    # Ensure dependencies object exists and add Functions Framework
    if "dependencies" not in data:
        data["dependencies"] = {}
    data["dependencies"]["@google-cloud/functions-framework"] = FUNCTIONS_FRAMEWORK_VERSION
    data["dependencies"]["express"] = EXPRESS_VERSION
    print(f"✓ Added @google-cloud/functions-framework@{FUNCTIONS_FRAMEWORK_VERSION}")
    print(f"✓ Added express@{EXPRESS_VERSION}")

    # Ensure scripts object exists and add start script
    if "scripts" not in data:
        data["scripts"] = {}
    data["scripts"]["start"] = START_SCRIPT
    print(f"✓ Added start script: {START_SCRIPT}")

    # Write back to file with pretty formatting
    try:
        PACKAGE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"✅ Successfully patched package.json")
    except Exception as exc:
        print(f"✗ Error writing package.json: {exc}", file=sys.stderr)
        sys.exit(1)


def _create_default_package_json() -> dict:
    """Create a minimal valid package.json skeleton."""
    return {
        "name": DEFAULT_NAME,
        "version": DEFAULT_VERSION,
        "main": DEFAULT_MAIN,
    }


if __name__ == "__main__":
    main()

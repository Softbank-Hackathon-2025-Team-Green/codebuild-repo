#!/usr/bin/env python3

import json
import sys
from pathlib import Path

PACKAGE_PATH = Path("package.json")
STEP = "[patch_package_json]"

DEFAULT_NAME = "user-function"
DEFAULT_VERSION = "0.0.1"
DEFAULT_MAIN = "index.js"

FUNCTIONS_FRAMEWORK_VERSION = "^3.0.0"
DOTENV_VERSION = "^16.0.0"

START_SCRIPT = f"functions-framework --target=handler --port=${{PORT:-8080}} --host=0.0.0.0"

def log_info(msg):
    print(f"{STEP} INFO: {msg}", file=sys.stderr)
    
def log_warn(msg):
    print(f"{STEP} WARN: {msg}", file=sys.stderr)

def log_error(msg):
    print(f"{STEP} ERROR: {msg}", file=sys.stderr)

def main():
    """
    Load or create package.json, ensure dependencies and start script exist.
    """

    # 1. Load or Create package.json
    if PACKAGE_PATH.exists():
        try:
            content = PACKAGE_PATH.read_text(encoding="utf-8")
            data = json.loads(content)
            log_info("Loaded existing package.json")
        except json.JSONDecodeError as exc:
            log_warn(f"Invalid JSON in package.json: {exc}")
            log_info("Creating new default skeleton...")
            data = _create_default_package_json()
        except Exception as exc:
            log_error(f"Error reading package.json: {exc}")
            sys.exit(1)
    else:
        log_info("package.json not found; creating default skeleton")
        data = _create_default_package_json()

        
    # 2. Ensure Dependencies
    if "dependencies" not in data:
        data["dependencies"] = {}

    # Always overwrite/ensure these specific versions required for the platform
    data["dependencies"]["@google-cloud/functions-framework"] = FUNCTIONS_FRAMEWORK_VERSION
    data["dependencies"]["dotenv"] = DOTENV_VERSION
    
    log_info(f"Ensured dependency: @google-cloud/functions-framework@{FUNCTIONS_FRAMEWORK_VERSION}")
    log_info(f"Ensured dependency: dotenv@{DOTENV_VERSION}")


    # 3. Ensure Start Script
    if "scripts" not in data:
        data["scripts"] = {}

    data["scripts"]["start"] = START_SCRIPT
    log_info(f"Ensured start script: {START_SCRIPT}")


    # 4. Write back to file
    try:
        PACKAGE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
        log_info("Successfully patched package.json")
    except Exception as exc:
        log_error(f"Error writing package.json: {exc}")
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

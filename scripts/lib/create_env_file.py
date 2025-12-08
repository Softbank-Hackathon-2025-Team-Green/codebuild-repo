#!/usr/bin/env python3

import json
import os
import sys
from pathlib import Path

ENV_FILE_PATH = Path(".env")
STEP = "[create_env_file]"

def log_info(msg):
    print(f"{STEP} INFO: {msg}", file=sys.stderr)

def log_warn(msg):
    print(f"{STEP} WARN: {msg}", file=sys.stderr)

def log_error(msg):
    print(f"{STEP} ERROR: {msg}", file=sys.stderr)

def main():
    """
    Parse CUSTOM_ENV environment variable and create a .env file
    for runtime environment variables in the container.
    
    Expected format: [{"key": "NAME", "value": "val"}, ...]
    
    Process:
      1. Read CUSTOM_ENV from environment variable
      2. Parse JSON array
      3. Write KEY=VALUE pairs to .env file
    
    Exit codes:
      0: Success (includes empty/no custom env)
      1: JSON validation or parsing error
    """
    custom_env = os.environ.get("CUSTOM_ENV", "")
    
    # Handle empty or missing CUSTOM_ENV
    if not custom_env or custom_env == "[]":
        log_info("No custom environment variables provided, creating empty .env file")
        ENV_FILE_PATH.write_text("", encoding="utf-8")
        log_info("Created empty .env file")
        sys.exit(0)
    
    try:
        # Parse JSON
        data = json.loads(custom_env)
        
        # Validate it's an array
        if not isinstance(data, list):
            log_error(f"CUSTOM_ENV must be a JSON array, got {type(data).__name__}")
            log_error(f"Expected format: [{{\"key\": \"NAME\", \"value\": \"val\"}}, ...]")
            sys.exit(1)
        
        # Build .env file content
        env_lines = []
        for item in data:
            if not isinstance(item, dict):
                log_warn(f"Skipping invalid item (not a dict): {item}")
                continue
            
            key = item.get("key")
            value = item.get("value")
            
            if not key or value is None:
                log_warn(f"Skipping item missing 'key' or 'value': {item}")
                continue
            
            # Validate key is a valid environment variable name
            if not key.replace("_", "").isalnum():
                log_warn(f"Skipping invalid environment variable name: {key}")
                continue
            
            # Escape special characters in value
            escaped_value = str(value).replace("\\", "\\\\").replace("\n", "\\n").replace("\"", "\\\"")
            
            # Handle values with spaces or special chars
            if " " in str(value) or any(c in str(value) for c in ['$', '!', '"', "'"]):
                env_lines.append(f'{key}="{escaped_value}"')
            else:
                env_lines.append(f"{key}={value}")
        
        if not env_lines:
            log_info("No valid environment variables found")
            sys.exit(0)
        
        # Write to .env file
        ENV_FILE_PATH.write_text("\n".join(env_lines) + "\n", encoding="utf-8")
        log_info(f"Created .env file with {len(env_lines)} variable(s)")
        
        # Display contents for debugging
        # print("Contents:")
        # for line in env_lines:
        #     print(f"  {line}")
        
    except json.JSONDecodeError as exc:
        log_error(f"CUSTOM_ENV is not valid JSON format: {exc}")
        log_error(f"  Parse error: {exc}")
        log_error(f"  Received: {custom_env}")
        sys.exit(1)
    except Exception as exc:
        log_error(f"Unexpected error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()

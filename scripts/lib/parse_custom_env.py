#!/usr/bin/env python3

import json
import os
import sys

STEP = "[parse_custom_env]"

def log_info(msg):
    print(f"{STEP} INFO: {msg}", file=sys.stderr)
    
def log_warn(msg):
    print(f"{STEP} WARN: {msg}", file=sys.stderr)

def log_error(msg):
    print(f"{STEP} ERROR: {msg}", file=sys.stderr)

def main():
    """
    Parse CUSTOM_ENV environment variable (JSON string) and output
    pack build --env flags for each key-value pair.
    
    Expected format: [{"key": "NAME", "value": "val"}, ...]
    
    Process:
      1. Read CUSTOM_ENV from environment variable
      2. Validate JSON format
      3. Convert to space-separated --env flags for pack build
      4. Print flags to stdout for shell capture
    
    Exit codes:
      0: Success (includes empty/no custom env)
      1: JSON validation or parsing error
    """

    custom_env = os.environ.get("CUSTOM_ENV", "")
    
    # Handle empty or missing CUSTOM_ENV
    if not custom_env or custom_env == "[]":
        log_info("No custom environment variables provided (CUSTOM_ENV is empty)")
        sys.exit(0)
    
    try:
        # Parse JSON
        data = json.loads(custom_env)
        
        # Validate it's an array
        if not isinstance(data, list):
            log_error(f"CUSTOM_ENV must be a JSON array, got {type(data).__name__}")
            log_error("Expected format: [{\"key\": \"NAME\", \"value\": \"val\"}, ...]")
            sys.exit(1)
        
        # Convert array to key-value pairs
        env_vars = {}
        for item in data:
            if not isinstance(item, dict):
                log_warn(f"Skipping invalid item in CUSTOM_ENV array: {item}")
                continue
            
            key = item.get("key")
            value = item.get("value")
            
            if not key or value is None:
                log_warn(f"Skipping item missing 'key' or 'value': {item}")
                continue
            
            env_vars[key] = value
        
        # Build pack --env flags
        flags = []
        for key, value in env_vars.items():
            # Validate key is a valid environment variable name
            if not key.replace("_", "").isalnum():
                log_warn(f"Skipping invalid environment variable name: {key}")
                continue
            
            # Escape values that contain spaces or special characters
            if " " in str(value) or '"' in str(value):
                escaped_value = str(value).replace('"', '\\"')
                flags.append(f'--env {key}="{escaped_value}"')
            else:
                flags.append(f"--env {key}={value}")
        
        if not flags:
            log_info("No valid environment variables found in CUSTOM_ENV")
            sys.exit(0)
        
        # Output space-separated flags
        print(" ".join(flags))
        log_info(f"Parsed {len(flags)} custom environment variable(s)")
        
    except json.JSONDecodeError as exc:
        log_error("CUSTOM_ENV is not valid JSON format")
        log_error(f"Parse error: {exc}")
        log_error(f"Received: {custom_env}")
        sys.exit(1)
    except Exception as exc:
        log_error(f"Unexpected error parsing CUSTOM_ENV: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

import json
import os
import sys

def main():
    """
    Parse CUSTOM_ENV environment variable (JSON string) and output
    pack build --env flags for each key-value pair.
    
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
    if not custom_env or custom_env == "{}":
        print("No custom environment variables provided (CUSTOM_ENV is empty or {})")
        sys.exit(0)
    
    try:
        # Parse JSON
        env_vars = json.loads(custom_env)
        
        # Validate it's a dictionary
        if not isinstance(env_vars, dict):
            print(f"ERROR: CUSTOM_ENV must be a JSON object/dictionary, got {type(env_vars).__name__}", file=sys.stderr)
            sys.exit(1)
        
        # Build pack --env flags
        flags = []
        for key, value in env_vars.items():
            # Validate key is a valid environment variable name
            if not key.replace("_", "").isalnum():
                print(f"WARNING: Skipping invalid environment variable name: {key}", file=sys.stderr)
                continue
            
            # Escape values that contain spaces or special characters
            if " " in str(value) or '"' in str(value):
                escaped_value = str(value).replace('"', '\\"')
                flags.append(f'--env {key}="{escaped_value}"')
            else:
                flags.append(f"--env {key}={value}")
        
        if not flags:
            print("No valid environment variables found in CUSTOM_ENV")
            sys.exit(0)
        
        # Output space-separated flags
        print(" ".join(flags))
        print(f"✓ Parsed {len(flags)} custom environment variable(s)", file=sys.stderr)
        
    except json.JSONDecodeError as exc:
        print(f"ERROR: CUSTOM_ENV is not valid JSON format", file=sys.stderr)
        print(f"  Parse error: {exc}", file=sys.stderr)
        print(f"  Received: {custom_env}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"ERROR: Unexpected error parsing CUSTOM_ENV: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

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

// Store original console.log
const originalLog = console.log;
let currentHeaderId = null;

// Override console.log to prepend x-header-id
console.log = function(...args) {
  if (currentHeaderId) {
    originalLog(`[${currentHeaderId}]`, ...args);
  } else {
    originalLog(...args);
  }
};

// Load user's function
const userFunction = require('./index-original.js');

// Wrap the handler to capture request header
exports.handler = async (req, res) => {
  // Get x-header-id from request headers
  currentHeaderId = req.get('x-header-id') || req.headers['x-header-id'] || null;
  
  try {
    // Call the user's handler
    const result = await userFunction.handler(req, res);
    return result;
  } catch (error) {
    // Log error with x-header-id prefix
    console.log('Runtime error:', error.message);
    
    // Send error response if not already sent
    if (!res.headersSent) {
      res.status(500).json({
        error: 'Internal Server Error',
        message: error.message
      });
    }
  } finally {
    // Reset header ID after request
    currentHeaderId = null;
  }
};
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

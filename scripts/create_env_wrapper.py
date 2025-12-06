#!/usr/bin/env python3
"""
Generates an index.js wrapper that:
1. Loads .env file (if exists)
2. Injects Trace ID logging (JSON format)
3. Safely calls user's original function
"""

import sys
import shutil
from pathlib import Path

# 파일 경로 상수 정의
WRAPPER_PATH = Path("index.js")
ORIGINAL_PATH = Path("index-original.js")

WRAPPER_TEMPLATE = """// ===== Whaleray PaaS Runtime Wrapper =====
const fs = require('fs');

// 1. Load .env file safely (Only if it exists)
if (fs.existsSync('.env')) {
    require('dotenv').config();
}

// 2. Load User's Original Code
// We renamed the user's index.js to index-original.js during build
let userModule;
try {
    userModule = require('./index-original.js');
} catch (e) {
    console.error(JSON.stringify({
        level: 'FATAL',
        event: 'module_load_error',
        error: 'Failed to load user code (index-original.js)',
        details: e.message
    }));
    process.exit(1);
}

// 3. Normalize User Handler
// Supports: module.exports = func, exports.handler = func, export default func
const userHandler = typeof userModule === 'function' 
    ? userModule 
    : (userModule.handler || userModule.default || userModule);

if (typeof userHandler !== 'function') {
    console.error(JSON.stringify({
        level: 'FATAL',
        event: 'handler_error',
        error: 'No valid handler function found in index.js. Make sure to export a function.'
    }));
    process.exit(1);
}

// 4. Main Wrapper Handler
exports.handler = async (req, res) => {
    // Extract Trace ID (Case-insensitive)
    const traceId = req.headers['x-request-id'] || req.headers['X-Request-Id'] || 'unknown';
    const startTime = Date.now();

    // [Log] Request Start
    console.log(JSON.stringify({
        level: 'INFO',
        trace_id: traceId,
        event: 'request_start',
        method: req.method,
        path: req.url,
        timestamp: new Date().toISOString()
    }));

    try {
        // Execute User Handler
        // Wrap in Promise.resolve to handle both Async and Sync functions
        const result = await Promise.resolve(userHandler(req, res));
        
        // [Log] Request Complete (Only if no error thrown)
        const duration = Date.now() - startTime;
        console.log(JSON.stringify({
            level: 'INFO',
            trace_id: traceId,
            event: 'request_complete',
            duration_ms: duration,
            timestamp: new Date().toISOString()
        }));

        return result;

    } catch (error) {
        // [Log] Error
        const duration = Date.now() - startTime;
        console.log(JSON.stringify({
            level: 'ERROR',
            trace_id: traceId,
            event: 'request_error',
            error: error.message,
            stack: error.stack,
            duration_ms: duration,
            timestamp: new Date().toISOString()
        }));

        // Error Response Handling
        // If the user code hasn't sent a response yet, we send a 500.
        if (res && !res.headersSent) {
            res.status(500).send('Internal Server Error');
        }
        
        // Re-throw is important for the runtime to know it failed
        throw error;
    }
};
"""

def main():
    """
    Renames user's index.js to index-original.js and creates a new index.js wrapper.
    """
    
    # 1. Check if user's index.js exists
    if not WRAPPER_PATH.exists():
        print(f"ERROR: {WRAPPER_PATH} not found in current directory.", file=sys.stderr)
        sys.exit(1)
    
    # 2. Rename user's index.js -> index-original.js
    # Using shutil.move is safer than rename for cross-filesystem operations, though strictly rename is fine here.
    try:
        # If build is retried, index-original might already exist. 
        # We should not overwrite it with the wrapper if index.js is already the wrapper.
        # But assuming clean build env (CodeBuild), simple rename is okay.
        
        shutil.move(str(WRAPPER_PATH), str(ORIGINAL_PATH))
        print(f"✓ Renamed {WRAPPER_PATH} to {ORIGINAL_PATH}")
        
    except Exception as exc:
        print(f"ERROR: Failed to rename user code: {exc}", file=sys.stderr)
        sys.exit(1)

    # 3. Create the new wrapper index.js
    try:
        WRAPPER_PATH.write_text(WRAPPER_TEMPLATE, encoding="utf-8")
        print(f"✓ Created new {WRAPPER_PATH} with Trace Logging and Env support")
        
    except Exception as exc:
        print(f"ERROR: Failed to create wrapper file: {exc}", file=sys.stderr)
        # Try to rollback
        if ORIGINAL_PATH.exists():
            shutil.move(str(ORIGINAL_PATH), str(WRAPPER_PATH))
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Startup script for the LLM News Thread Web UI
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from webui.app import app

if __name__ == '__main__':
    print("Starting LLM News Thread Web UI...")
    print("Access the web interface at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

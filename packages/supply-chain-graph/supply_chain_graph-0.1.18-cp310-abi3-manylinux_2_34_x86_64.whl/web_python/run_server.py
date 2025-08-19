#!/usr/bin/env python3
"""
Startup script for the Supply Chain Planning FastAPI web service.
"""

import sys
import os
from pathlib import Path

# Add the supply module to the path if needed
current_dir = Path(__file__).parent
supply_dir = current_dir.parent
sys.path.insert(0, str(supply_dir))

from network_api import start_server

def main():
    """Main entry point for the web service."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Supply Chain Planning FastAPI Web Service")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to (default: 8000)")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")
    
    args = parser.parse_args()
    
    print(f"Starting Supply Chain Planning API on {args.host}:{args.port}")
    print(f"Documentation available at: http://{args.host}:{args.port}/docs")
    
    start_server(
        host=args.host,
        port=args.port,
        reload=not args.no_reload
    )

if __name__ == "__main__":
    main() 
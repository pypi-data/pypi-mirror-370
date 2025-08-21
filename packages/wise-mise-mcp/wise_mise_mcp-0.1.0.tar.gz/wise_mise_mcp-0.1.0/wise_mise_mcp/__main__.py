#!/usr/bin/env python3
"""
Main entry point for the Wise Mise MCP Server
"""

def main():
    """Main entry point for the CLI script."""
    from wise_mise_mcp.server import main as server_main
    server_main()

if __name__ == "__main__":
    main()

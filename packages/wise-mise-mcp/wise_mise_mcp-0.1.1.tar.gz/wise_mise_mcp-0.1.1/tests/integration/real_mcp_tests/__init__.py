"""
Real MCP Client Integration Tests

This module contains integration tests that verify the wise-mise-mcp server
works correctly with real MCP client libraries and follows MCP protocol
specifications.

Tests include:
- Protocol handshake and initialization
- Tool discovery and execution
- Error handling and edge cases
- Performance and stability
- Protocol compliance validation
"""

__all__ = [
    "TestRealMCPClientIntegration",
    "TestMCPProtocolCompliance", 
    "TestMCPServerStability",
]
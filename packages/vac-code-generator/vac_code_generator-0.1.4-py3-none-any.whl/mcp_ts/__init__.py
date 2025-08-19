"""
MCP TypeScript 服务器包

提供基于FastMCP框架的TypeScript服务器实现。

版本: 0.1.3
"""

from .server import MCPTSServer

__version__ = '0.1.3'
__all__ = [
    'MCPTSServer',
    '__version__'
]
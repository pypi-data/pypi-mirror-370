"""
Zapr WhatsApp MCP Server

A Model Context Protocol server for WhatsApp messaging via zapr.link
"""

__version__ = "1.0.0"
__author__ = "Zapr.link"
__email__ = "support@zapr.link"

from .server import ZaprMCPServer

__all__ = ["ZaprMCPServer"]
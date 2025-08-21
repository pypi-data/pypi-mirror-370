"""
Video Compressor MCP Server

A comprehensive MCP server for video compression and optimization including:
- Bitrate adjustment for file size control
- Resolution scaling and aspect ratio management
- Frame rate optimization
- Codec conversion and format optimization
- Quality settings and compression profiles
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .main import main

__all__ = ["main"]
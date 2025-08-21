"""
Video Content Extractor MCP Server

A comprehensive MCP server for video content extraction including:
- Audio extraction from video files
- Video trimming and segmentation
- Frame extraction at specified intervals
- Scene detection and analysis
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .main import main

__all__ = ["main"]
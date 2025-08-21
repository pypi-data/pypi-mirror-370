"""
Audio File Processor MCP Server

A comprehensive MCP server for audio file processing including:
- Audio format conversion (MP3, WAV, FLAC, AAC, etc.)
- Audio quality adjustment and optimization
- Volume normalization and enhancement
- Audio trimming and concatenation
- Metadata editing and extraction
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .main import main

__all__ = ["main"]
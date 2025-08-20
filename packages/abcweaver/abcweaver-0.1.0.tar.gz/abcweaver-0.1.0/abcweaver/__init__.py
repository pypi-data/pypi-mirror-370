"""
🎼 ABCWeaver - ABC ↔ MusicXML Transformation Engine

A powerful Python package for bidirectional transformation between ABC notation 
and MusicXML format, enhanced with Redis stream processing capabilities.

Part of the G.Music Assembly ecosystem.
"""

__version__ = "0.1.0"
__author__ = "G.Music Assembly"
__email__ = "assembly@gmusic.com"

from .core.abc_parser import ABCParser
from .core.musicxml_handler import MusicXMLHandler
from .core.converter import Converter
from .core.validator import Validator

__all__ = [
    "ABCParser",
    "MusicXMLHandler", 
    "Converter",
    "Validator",
]
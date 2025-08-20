"""
📡 Caelus Exception Classes

Custom exceptions for specific error handling.
"""


class CaelusError(Exception):
    """Base exception for all Caelus operations"""
    pass


class ABCParseError(CaelusError):
    """Raised when ABC notation parsing fails"""
    pass


class MusicXMLError(CaelusError):
    """Raised when MusicXML processing fails"""
    pass


class StreamError(CaelusError):
    """Raised when Redis stream operations fail"""
    pass


class ValidationError(CaelusError):
    """Raised when file validation fails"""
    pass


class ConversionError(CaelusError):
    """Raised when format conversion fails"""
    pass
"""
UnrealOn Driver exceptions
"""


class ParserError(Exception):
    """Base exception for parser errors"""
    pass


class BrowserError(ParserError):
    """Browser-related errors"""
    pass


class HTMLCleaningError(ParserError):
    """HTML cleaning errors"""
    pass


class ConfigurationError(ParserError):
    """Configuration errors"""
    pass


class ConnectionError(ParserError):
    """Connection errors"""
    pass

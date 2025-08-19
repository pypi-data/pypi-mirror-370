"""Custom exceptions for Word MCP operations."""


class WordMCPError(Exception):
    """Base exception for Word MCP operations."""
    pass


class ValidationError(WordMCPError):
    """Raised when validation fails."""
    pass


class DocumentError(WordMCPError):
    """Raised when document operations fail."""
    pass


class SearchReplaceError(WordMCPError):
    """Raised when search and replace operations fail."""
    pass


class FileError(WordMCPError):
    """Raised when file operations fail."""
    pass
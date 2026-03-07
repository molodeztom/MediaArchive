"""Custom exception classes for Media Archive Manager."""


class MediaArchiveError(Exception):
    """Base exception for Media Archive Manager application.
    
    All custom exceptions inherit from this class.
    """

    pass


class ValidationError(MediaArchiveError):
    """Raised when input validation fails.
    
    Used when user input does not meet validation requirements
    (e.g., empty name, invalid date, unknown media type).
    """

    pass


class DatabaseError(MediaArchiveError):
    """Raised when database operation fails.
    
    Used when SQLite operations encounter errors
    (e.g., connection failure, constraint violation, query error).
    """

    pass


class NotFoundError(MediaArchiveError):
    """Raised when requested resource is not found.
    
    Used when trying to retrieve a media or location that doesn't exist.
    """

    pass

"""StorageLocation model for Media Archive Manager."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class StorageLocation:
    """Represents a physical storage location for media.
    
    Attributes:
        id: Unique identifier (None for new records).
        box: Container name (e.g., "CD Register A").
        place: Physical location (optional, e.g., "office cabinet").
        detail: Additional detail (e.g., "slot 4").
        created_at: Timestamp when record was created.
        updated_at: Timestamp when record was last updated.
    """

    box: str
    place: Optional[str] = None
    detail: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validate and normalize data after initialization."""
        # Trim whitespace from string fields
        self.box = self.box.strip() if self.box else ""
        self.place = self.place.strip() if self.place else ""
        if self.detail:
            self.detail = self.detail.strip()

    def __str__(self) -> str:
        """Return string representation of storage location.
        
        Returns:
            Formatted string showing box and place.
        """
        if self.detail:
            return f"{self.box} - {self.place} ({self.detail})"
        return f"{self.box} - {self.place}"

    def __repr__(self) -> str:
        """Return detailed string representation.
        
        Returns:
            Detailed representation for debugging.
        """
        return (
            f"StorageLocation(id={self.id}, box={self.box!r}, "
            f"place={self.place!r}, detail={self.detail!r})"
        )

    def is_new(self) -> bool:
        """Check if this is a new record (not yet saved).
        
        Returns:
            True if id is None, False otherwise.
        """
        return self.id is None

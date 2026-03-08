"""Media model for Media Archive Manager."""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Media:
    """Represents a physical media item.
    
    Attributes:
        name: Media name/title (required).
        media_type: Type of media (optional, defaults to "Unknown").
        type: Content category (Archive, Program, Backup, Game, etc.).
        content_description: Description of contents.
        remarks: Additional notes.
        creation_date: When media was created.
        valid_until_date: Expiration date (if applicable).
        company: Company/publisher name.
        license_code: License key or activation code.
        location_id: Reference to storage location.
        id: Unique identifier (None for new records).
        created_at: ISO 8601 timestamp when record was created.
        updated_at: ISO 8601 timestamp when record was last updated.
    """

    name: str
    media_type: Optional[str] = None
    type: Optional[str] = None
    content_description: Optional[str] = None
    remarks: Optional[str] = None
    creation_date: Optional[date] = None
    valid_until_date: Optional[date] = None
    company: Optional[str] = None
    license_code: Optional[str] = None
    location_id: Optional[int] = None
    id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate and normalize data after initialization."""
        # Trim whitespace from string fields
        self.name = self.name.strip() if self.name else ""
        self.media_type = self.media_type.strip() if self.media_type else "Unknown"
        if self.type:
            self.type = self.type.strip()
        if self.content_description:
            self.content_description = self.content_description.strip()
        if self.remarks:
            self.remarks = self.remarks.strip()
        if self.company:
            self.company = self.company.strip()
        if self.license_code:
            self.license_code = self.license_code.strip()

    def __str__(self) -> str:
        """Return string representation of media.
        
        Returns:
            Formatted string showing name and type.
        """
        return f"{self.name} ({self.media_type})"

    def __repr__(self) -> str:
        """Return detailed string representation.
        
        Returns:
            Detailed representation for debugging.
        """
        return (
            f"Media(id={self.id}, name={self.name!r}, "
            f"media_type={self.media_type!r}, location_id={self.location_id})"
        )

    def is_new(self) -> bool:
        """Check if this is a new record (not yet saved).
        
        Returns:
            True if id is None, False otherwise.
        """
        return self.id is None

    def is_expired(self) -> bool:
        """Check if media has expired.
        
        Returns:
            True if valid_until_date is set and in the past, False otherwise.
        """
        if self.valid_until_date is None:
            return False
        return self.valid_until_date < date.today()

    def has_location(self) -> bool:
        """Check if media has a storage location assigned.
        
        Returns:
            True if location_id is set, False otherwise.
        """
        return self.location_id is not None

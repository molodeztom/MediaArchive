"""Enumeration types for Media Archive Manager."""

from enum import Enum


class MediaType(str, Enum):
    """Enumeration of supported media types.
    
    Inherits from str for easy database storage and comparison.
    """

    M_DISK = "M-Disk"
    DVD = "DVD"
    CD = "CD"
    BLU_RAY = "Blu-ray"
    USB_DRIVE = "USB Drive"
    EXTERNAL_HDD = "External HDD"
    BACKUP_TAPE = "Backup Tape"
    OTHER = "Other"
    UNKNOWN = "Unknown"

    @classmethod
    def get_all_values(cls) -> list[str]:
        """Get all media type values as strings.
        
        Returns:
            List of all media type values.
        """
        return [member.value for member in cls]

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Check if a value is a valid media type.
        
        Args:
            value: The value to check.
        
        Returns:
            True if value is a valid media type, False otherwise.
        """
        return value in cls.get_all_values()

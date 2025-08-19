"""Source file format type definitions for preprocessing in Switch conversion."""
from enum import Enum


class SourceFormat(str, Enum):
    """Source file format types for preprocessing

    This enum defines the supported source file formats and their preprocessing behavior:
    - SQL: SQL files that require comment removal and whitespace normalization
    - GENERIC: Generic text files that require no preprocessing
    """
    SQL = "sql"
    GENERIC = "generic"

    @classmethod
    def get_supported_formats(cls) -> list[str]:
        """Get list of supported source format values

        Returns:
            List of supported source format names
        """
        return [format_type.value for format_type in cls]

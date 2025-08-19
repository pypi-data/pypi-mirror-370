"""Target output type definitions for Switch conversion."""
from enum import Enum


class TargetType(str, Enum):
    """Target output types for Switch conversion
    
    This enum defines the supported output formats for the conversion process.
    Each type determines the processing flow and output format.
    """
    NOTEBOOK = "notebook"
    FILE = "file"

    @classmethod
    def get_supported_types(cls) -> list[str]:
        """Get list of supported target type values
        
        Returns:
            List of supported target type names
        """
        return [target_type.value for target_type in cls]

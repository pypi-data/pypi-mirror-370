"""Base error classes for Morpheus migration errors."""

from abc import ABC, abstractmethod
from typing import Any


class MigrationError(ABC):
    """Base class for migration errors with embedded resolutions."""

    def __init__(self, migration_id: str, original_error: str):
        self.migration_id = migration_id
        self.original_error = original_error

    @abstractmethod
    def matches(self, error_str: str) -> bool:
        """Check if this error type matches the given error string."""
        pass

    @abstractmethod
    def get_enhanced_message(self) -> str:
        """Generate enhanced error message with resolution guidance."""
        pass

    @classmethod
    @abstractmethod
    def get_pattern_info(cls) -> dict[str, Any]:
        """Get pattern information for testing and documentation."""
        pass

"""Specific migration error implementations with embedded resolutions."""

from typing import Any

from .base import MigrationError


class SchemaDataMixingError(MigrationError):
    """Error for mixing schema changes with data operations in the same transaction."""

    def matches(self, error_str: str) -> bool:
        return "ForbiddenDueToTransactionType" in error_str and (
            "Schema modification after executing Write query" in error_str
            or "Write query after executing Schema modification" in error_str
        )

    def get_enhanced_message(self) -> str:
        # Determine which operation came first to provide specific guidance
        if "Schema modification after executing Write query" in self.original_error:
            order_guidance = (
                "   1. First migration: Data operations only (CREATE, UPDATE, DELETE)\n"
                "   2. Second migration: Schema changes only (constraints, indexes, depends on first migration)"
            )
        else:  # "Write query after executing Schema modification"
            order_guidance = (
                "   1. First migration: Schema changes only (constraints, indexes)\n"
                "   2. Second migration: Data operations only (CREATE, UPDATE, DELETE, depends on first migration)"
            )

        return (
            f"Migration {self.migration_id} failed: Cannot mix schema changes (constraints, indexes) "
            f"with data operations (CREATE, UPDATE, DELETE) in the same transaction.\n\n"
            f"💡 Solution: Split this migration into two separate migrations:\n"
            f"{order_guidance}\n\n"
            f"ℹ️  Note: The order above matches your current migration structure. You can also reorganize\n"
            f"   the operations within a single migration (schema first, then data) if that makes more sense.\n\n"
            f"Original error: {self.original_error}"
        )

    @classmethod
    def get_pattern_info(cls) -> dict[str, Any]:
        return {
            "name": "Schema/Data Mixing Error",
            "patterns": [
                "ForbiddenDueToTransactionType",
                "Schema modification after executing Write query",
                "Write query after executing Schema modification",
            ],
            "description": "Neo4j prohibits mixing schema changes with data operations in the same transaction",
            "solution": "Split into separate migrations or reorganize operation order",
        }


class TransactionClosedError(MigrationError):
    """Error for premature transaction closure."""

    def matches(self, error_str: str) -> bool:
        return (
            "Transaction closed" in error_str
            or "transaction has been closed" in error_str.lower()
        )

    def get_enhanced_message(self) -> str:
        return (
            f"Migration {self.migration_id} failed: Transaction was closed unexpectedly.\n\n"
            f"💡 Common causes and solutions:\n"
            f"   1. Manual tx.commit() or tx.rollback() calls - Remove these, the executor manages transactions\n"
            f"   2. Connection timeout - Check database connection settings\n"
            f"   3. Database server issues - Verify Neo4j is running and accessible\n\n"
            f"⚠️  Most likely: Remove any tx.commit() or tx.rollback() calls from your migration code.\n"
            f"   The migration executor automatically commits successful migrations.\n\n"
            f"Original error: {self.original_error}"
        )

    @classmethod
    def get_pattern_info(cls) -> dict[str, Any]:
        return {
            "name": "Transaction Closed Error",
            "patterns": ["Transaction closed", "transaction has been closed"],
            "description": "Transaction was closed before migration completed",
            "solution": "Remove manual tx.commit()/tx.rollback() calls or check connection",
        }


class ConnectionTimeoutError(MigrationError):
    """Error for database connection timeouts."""

    def matches(self, error_str: str) -> bool:
        return any(
            pattern in error_str.lower()
            for pattern in [
                "connection timeout",
                "timeout expired",
                "read timeout",
                "connection lost",
                "connection refused",
                "connection reset",
            ]
        )

    def get_enhanced_message(self) -> str:
        return (
            f"Migration {self.migration_id} failed: Database connection issue detected.\n\n"
            f"💡 Possible solutions:\n"
            f"   1. Check Neo4j server status - Ensure Neo4j is running and accessible\n"
            f"   2. Verify connection settings - Check URI, username, password in config\n"
            f"   3. Increase timeout values - For large migrations, consider longer timeouts\n"
            f"   4. Network issues - Check firewall, VPN, or network connectivity\n"
            f"   5. Split large migrations - Break down into smaller, faster operations\n\n"
            f"🔧 Quick checks:\n"
            f"   • Can you connect to Neo4j browser at same URI?\n"
            f"   • Are there any network restrictions?\n"
            f"   • Is the migration particularly large or slow?\n\n"
            f"Original error: {self.original_error}"
        )

    @classmethod
    def get_pattern_info(cls) -> dict[str, Any]:
        return {
            "name": "Connection Timeout Error",
            "patterns": [
                "connection timeout",
                "timeout expired",
                "read timeout",
                "connection lost",
                "connection refused",
                "connection reset",
            ],
            "description": "Database connection failed or timed out",
            "solution": "Check connection settings, Neo4j status, and network connectivity",
        }


# Registry of all error types
ERROR_TYPES: list[type[MigrationError]] = [
    SchemaDataMixingError,
    TransactionClosedError,
    ConnectionTimeoutError,
]


def error_resolver(migration_id: str, original_error: Exception) -> str:
    """
    Resolve error to enhanced message with guidance.

    Args:
        migration_id: ID of the migration that failed
        original_error: The original exception that occurred

    Returns:
        Enhanced error message with resolution guidance
    """
    error_str = str(original_error)

    # Try each error type to find a match
    for error_type in ERROR_TYPES:
        error_instance = error_type(migration_id, error_str)
        if error_instance.matches(error_str):
            return error_instance.get_enhanced_message()

    # Default fallback message
    return f"Migration {migration_id} failed: {error_str}"


def get_all_error_patterns() -> dict[str, dict[str, Any]]:
    """Get all registered error patterns for documentation/testing."""
    return {
        error_type.__name__: error_type.get_pattern_info() for error_type in ERROR_TYPES
    }

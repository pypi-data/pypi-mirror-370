import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner
from rich.console import Console

from morpheus.cli.commands.upgrade import upgrade_command
from morpheus.config.config import Config, DatabaseConfig, ExecutionConfig
from morpheus.models.migration import Migration


class TestUpgradeCommand:
    """Test suite for upgrade command with failfast functionality."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock config for testing."""
        config = Config()
        config.database = DatabaseConfig(
            uri="bolt://localhost:7687",
            username="neo4j",
            password="password",
            database="test_db",
        )
        config.execution = ExecutionConfig(max_parallel=4, parallel=True)
        config.migrations = Mock()
        config.migrations.directory = Path("migrations/versions")
        return config

    @pytest.fixture
    def mock_console(self):
        """Create a mock console for testing."""
        return Mock(spec=Console)

    @pytest.fixture
    def sample_migrations(self):
        """Create sample migrations for testing dependencies."""
        migrations = []

        # Migration A - no dependencies
        content_a = '''"""Migration A"""
dependencies = []
tags = []
priority = 1

def upgrade(tx):
    tx.run("CREATE (n:TestA {name: 'A'})")

def downgrade(tx):
    tx.run("MATCH (n:TestA) DELETE n")
'''
        with tempfile.NamedTemporaryFile(
            mode="w", suffix="_migration_a.py", delete=False
        ) as f:
            f.write(content_a)
            migration_a = Migration.from_file(Path(f.name))
            migration_a.id = "20250101_000001_migration_a"
            migrations.append(migration_a)

        # Migration B - depends on A
        content_b = '''"""Migration B"""
dependencies = ["20250101_000001_migration_a"]
tags = []
priority = 1

def upgrade(tx):
    tx.run("CREATE (n:TestB {name: 'B'})")

def downgrade(tx):
    tx.run("MATCH (n:TestB) DELETE n")
'''
        with tempfile.NamedTemporaryFile(
            mode="w", suffix="_migration_b.py", delete=False
        ) as f:
            f.write(content_b)
            migration_b = Migration.from_file(Path(f.name))
            migration_b.id = "20250101_000002_migration_b"
            migration_b.dependencies = ["20250101_000001_migration_a"]
            migrations.append(migration_b)

        # Migration C - depends on B (transitive dependency on A)
        content_c = '''"""Migration C"""
dependencies = ["20250101_000002_migration_b"]
tags = []
priority = 1

def upgrade(tx):
    tx.run("CREATE (n:TestC {name: 'C'})")

def downgrade(tx):
    tx.run("MATCH (n:TestC) DELETE n")
'''
        with tempfile.NamedTemporaryFile(
            mode="w", suffix="_migration_c.py", delete=False
        ) as f:
            f.write(content_c)
            migration_c = Migration.from_file(Path(f.name))
            migration_c.id = "20250101_000003_migration_c"
            migration_c.dependencies = ["20250101_000002_migration_b"]
            migrations.append(migration_c)

        return migrations

    @patch("morpheus.cli.commands.upgrade.resolve_migrations_dir")
    @patch("morpheus.cli.commands.upgrade.load_migrations")
    @patch("morpheus.cli.commands.upgrade.MigrationExecutor")
    @patch("morpheus.cli.commands.upgrade.DAGResolver")
    def test_failfast_enabled_stops_on_first_failure(
        self,
        mock_dag_resolver,
        mock_executor_class,
        mock_load_migrations,
        mock_resolve_dir,
        mock_config,
        mock_console,
        sample_migrations,
    ):
        """Test that failfast=True stops execution on first batch failure."""
        # Arrange
        mock_migrations_dir = Mock(spec=Path)
        mock_migrations_dir.exists.return_value = True
        mock_resolve_dir.return_value = mock_migrations_dir
        mock_load_migrations.return_value = sample_migrations

        mock_executor = Mock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor
        mock_executor.get_applied_migrations.return_value = []

        # Simulate first migration failing
        mock_executor.execute_sequential.return_value = {
            "20250101_000001_migration_a": (False, "Migration failed")
        }

        mock_resolver = Mock()
        mock_dag_resolver.return_value = mock_resolver
        mock_dag = Mock()
        mock_resolver.build_dag.return_value = mock_dag
        mock_resolver.validate_dag.return_value = []
        mock_resolver.check_conflicts.return_value = []
        mock_resolver.get_execution_order.return_value = [
            ["20250101_000001_migration_a"],
            ["20250101_000002_migration_b"],
            ["20250101_000003_migration_c"],
        ]

        runner = CliRunner()

        # Act
        result = runner.invoke(
            upgrade_command,
            ["--failfast", "--yes"],
            obj={"config": mock_config, "console": mock_console},
        )

        # Assert
        assert result.exit_code == 1
        # Should only execute first batch when failfast is enabled
        assert mock_executor.execute_sequential.call_count == 1
        mock_console.print.assert_any_call(
            "[red]Stopping execution due to failfast flag[/red]"
        )

    @patch("morpheus.cli.commands.upgrade.resolve_migrations_dir")
    @patch("morpheus.cli.commands.upgrade.load_migrations")
    @patch("morpheus.cli.commands.upgrade.MigrationExecutor")
    @patch("morpheus.cli.commands.upgrade.DAGResolver")
    def test_failfast_disabled_skips_dependent_migrations(
        self,
        mock_dag_resolver,
        mock_executor_class,
        mock_load_migrations,
        mock_resolve_dir,
        mock_config,
        mock_console,
        sample_migrations,
    ):
        """Test that failfast=False skips migrations that depend on failed ones."""
        # Arrange
        mock_migrations_dir = Mock(spec=Path)
        mock_migrations_dir.exists.return_value = True
        mock_resolve_dir.return_value = mock_migrations_dir
        mock_load_migrations.return_value = sample_migrations

        mock_executor = Mock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor
        mock_executor.get_applied_migrations.return_value = []

        # Simulate first migration failing, second succeeds (independent), third skipped
        mock_executor.execute_sequential.side_effect = [
            {
                "20250101_000001_migration_a": (False, "Migration failed")
            },  # First batch fails
            # Second and third batches should be skipped or filtered
        ]

        mock_resolver = Mock()
        mock_dag_resolver.return_value = mock_resolver
        mock_dag = Mock()
        mock_resolver.build_dag.return_value = mock_dag
        mock_resolver.validate_dag.return_value = []
        mock_resolver.check_conflicts.return_value = []
        mock_resolver.get_execution_order.return_value = [
            ["20250101_000001_migration_a"],
            ["20250101_000002_migration_b"],
            ["20250101_000003_migration_c"],
        ]

        # Mock DAG ancestors for dependency checking
        with patch("morpheus.cli.commands.upgrade.nx") as mock_nx:
            mock_nx.ancestors.side_effect = lambda dag, node_id: {
                "20250101_000002_migration_b": {"20250101_000001_migration_a"},
                "20250101_000003_migration_c": {
                    "20250101_000001_migration_a",
                    "20250101_000002_migration_b",
                },
            }.get(node_id, set())

            runner = CliRunner()

            # Act
            result = runner.invoke(
                upgrade_command,
                ["--no-failfast", "--yes"],
                obj={"config": mock_config, "console": mock_console},
            )

        # Assert
        assert result.exit_code == 1
        # Should execute first batch, then skip dependent migrations
        mock_console.print.assert_any_call(
            "[yellow]Skipping migrations due to failed dependencies: 20250101_000002_migration_b[/yellow]"
        )
        mock_console.print.assert_any_call(
            "[yellow]Skipping migrations due to failed dependencies: 20250101_000003_migration_c[/yellow]"
        )

    @patch("morpheus.cli.commands.upgrade.resolve_migrations_dir")
    @patch("morpheus.cli.commands.upgrade.load_migrations")
    @patch("morpheus.cli.commands.upgrade.MigrationExecutor")
    @patch("morpheus.cli.commands.upgrade.DAGResolver")
    def test_ci_mode_always_fails_fast(
        self,
        mock_dag_resolver,
        mock_executor_class,
        mock_load_migrations,
        mock_resolve_dir,
        mock_config,
        mock_console,
        sample_migrations,
    ):
        """Test that CI mode always fails fast regardless of failfast flag."""
        # Arrange
        mock_migrations_dir = Mock(spec=Path)
        mock_migrations_dir.exists.return_value = True
        mock_resolve_dir.return_value = mock_migrations_dir
        mock_load_migrations.return_value = sample_migrations

        mock_executor = Mock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor
        mock_executor.get_applied_migrations.return_value = []

        # Simulate first migration failing
        mock_executor.execute_sequential.return_value = {
            "20250101_000001_migration_a": (False, "Migration failed")
        }

        mock_resolver = Mock()
        mock_dag_resolver.return_value = mock_resolver
        mock_dag = Mock()
        mock_resolver.build_dag.return_value = mock_dag
        mock_resolver.validate_dag.return_value = []
        mock_resolver.check_conflicts.return_value = []
        mock_resolver.get_execution_order.return_value = [
            ["20250101_000001_migration_a"],
            ["20250101_000002_migration_b"],
        ]

        runner = CliRunner()

        # Act
        result = runner.invoke(
            upgrade_command,
            ["--ci", "--no-failfast", "--yes"],
            obj={"config": mock_config, "console": mock_console},
        )

        # Assert
        assert result.exit_code == 1
        # Should only execute first batch even with --no-failfast because CI mode fails fast
        assert mock_executor.execute_sequential.call_count == 1
        mock_console.print.assert_any_call(
            "[red]CI: Stopping execution due to failures[/red]"
        )

    @patch("morpheus.cli.commands.upgrade.resolve_migrations_dir")
    @patch("morpheus.cli.commands.upgrade.load_migrations")
    @patch("morpheus.cli.commands.upgrade.MigrationExecutor")
    @patch("morpheus.cli.commands.upgrade.DAGResolver")
    def test_dynamic_dependency_skipping_during_execution(
        self,
        mock_dag_resolver,
        mock_executor_class,
        mock_load_migrations,
        mock_resolve_dir,
        mock_config,
        mock_console,
        sample_migrations,
    ):
        """Test that dependencies are dynamically skipped when migrations fail during execution."""
        # Arrange
        mock_migrations_dir = Mock(spec=Path)
        mock_migrations_dir.exists.return_value = True
        mock_resolve_dir.return_value = mock_migrations_dir
        mock_load_migrations.return_value = sample_migrations

        mock_executor = Mock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor
        mock_executor.get_applied_migrations.return_value = []

        # Mock the _mark_migration_as_skipped method
        mock_executor._mark_migration_as_skipped = Mock()

        # Simulate first migration succeeding, second failing, third should be skipped
        mock_executor.execute_sequential.side_effect = [
            {"20250101_000001_migration_a": (True, None)},  # First batch succeeds
            {
                "20250101_000002_migration_b": (False, "Migration B failed")
            },  # Second batch fails
            # Third batch should be skipped dynamically
        ]

        mock_resolver = Mock()
        mock_dag_resolver.return_value = mock_resolver
        mock_dag = Mock()
        mock_resolver.build_dag.return_value = mock_dag
        mock_resolver.validate_dag.return_value = []
        mock_resolver.check_conflicts.return_value = []
        mock_resolver.get_execution_order.return_value = [
            ["20250101_000001_migration_a"],
            ["20250101_000002_migration_b"],
            ["20250101_000003_migration_c"],
        ]

        # Mock DAG ancestors for dependency checking during execution
        with patch("morpheus.cli.commands.upgrade.nx") as mock_nx:
            mock_nx.ancestors.side_effect = lambda dag, node_id: {
                "20250101_000002_migration_b": {"20250101_000001_migration_a"},
                "20250101_000003_migration_c": {
                    "20250101_000001_migration_a",
                    "20250101_000002_migration_b",
                },
            }.get(node_id, set())

            runner = CliRunner()

            # Act
            result = runner.invoke(
                upgrade_command,
                ["--no-failfast", "--yes"],
                obj={"config": mock_config, "console": mock_console},
            )

        # Assert
        assert result.exit_code == 1

        # Should execute first two batches
        assert mock_executor.execute_sequential.call_count == 2

        # Should mark dependent migration as skipped (may be called multiple times due to dynamic handling)
        assert mock_executor._mark_migration_as_skipped.call_count >= 1
        # Check that migration C was marked as skipped
        call_migrations = [
            call[0][0].id
            for call in mock_executor._mark_migration_as_skipped.call_args_list
        ]
        assert "20250101_000003_migration_c" in call_migrations

        # Should print about marking dependent migrations as skipped
        mock_console.print.assert_any_call(
            "[yellow]Marking 1 dependent migrations as skipped due to failures in this batch[/yellow]"
        )

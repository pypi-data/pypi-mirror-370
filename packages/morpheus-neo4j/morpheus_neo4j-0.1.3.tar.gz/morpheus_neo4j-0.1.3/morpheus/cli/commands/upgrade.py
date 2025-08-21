from pathlib import Path

import click
import networkx as nx

from morpheus.cli.utils import resolve_migrations_dir
from morpheus.core.dag_resolver import DAGResolver
from morpheus.core.executor import MigrationExecutor
from morpheus.models.migration import Migration


@click.command()
@click.option("--target", help="Target migration ID to upgrade to")
@click.option(
    "--parallel/--no-parallel", default=None, help="Enable/disable parallel execution"
)
@click.option("--dry-run", is_flag=True, help="Show execution plan without applying")
@click.option(
    "--ci", is_flag=True, help="Enable CI mode with detailed exit status messages"
)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
@click.option(
    "--failfast/--no-failfast",
    default=False,
    help="Stop execution when any migration fails (default: False)",
)
@click.pass_context
def upgrade_command(ctx, target, parallel, dry_run, ci, yes, failfast):
    """Apply pending migrations."""
    config = ctx.obj["config"]
    console = ctx.obj["console"]

    # Override parallel setting if specified
    if parallel is not None:
        config.execution.parallel = parallel

    # Load migrations
    migrations_dir = resolve_migrations_dir(config)
    if not migrations_dir.exists():
        console.print(
            f"[red]Migrations directory does not exist: {migrations_dir}[/red]"
        )
        console.print(
            "Run [cyan]morpheus init[/cyan] first to initialize the migration system"
        )
        ctx.exit(1)

    try:
        migrations = load_migrations(migrations_dir)
        if not migrations:
            console.print("[yellow]No migrations found[/yellow]")
            return

        # Get applied migrations from Neo4j
        applied_migration_ids = set()
        try:
            with MigrationExecutor(config, console) as executor:
                applied_migration_ids = set(executor.get_applied_migrations())
        except Exception as e:
            console.print(f"[yellow]Warning: Could not connect to Neo4j: {e}[/yellow]")
            console.print(
                "[yellow]Proceeding without checking applied migrations[/yellow]"
            )

        # Filter to pending migrations
        pending_migrations = [
            m for m in migrations if m.id not in applied_migration_ids
        ]

        if target:
            # Filter to migrations needed to reach target
            pending_migrations = filter_migrations_to_target(
                migrations, target, applied_migration_ids
            )

        if not pending_migrations:
            console.print("[green]All migrations are up to date[/green]")
            return

        # Build DAG and validate
        resolver = DAGResolver()
        dag = resolver.build_dag(
            migrations
        )  # Use all migrations for dependency resolution

        validation_errors = resolver.validate_dag(dag)
        if validation_errors:
            console.print("[red]DAG validation failed:[/red]")
            for error in validation_errors:
                console.print(f"  [red]• {error}[/red]")
            ctx.exit(1)

        # Check for conflicts
        conflict_errors = resolver.check_conflicts(pending_migrations)
        if conflict_errors:
            console.print("[red]Migration conflicts detected:[/red]")
            for error in conflict_errors:
                console.print(f"  [red]• {error}[/red]")
            ctx.exit(1)

        # Get execution plan
        # Create a subgraph of the full DAG with only pending migrations

        pending_ids = {m.id for m in pending_migrations}
        pending_dag = dag.subgraph(pending_ids).copy()
        execution_batches = resolver.get_execution_order(pending_dag)

        # Show execution plan
        show_execution_plan(console, execution_batches, config.execution.parallel)

        if dry_run:
            console.print(
                "\n[cyan]Dry run complete - no migrations were applied[/cyan]"
            )
            return

        # Confirm execution
        if not yes and not click.confirm("\nProceed with migration?", default=True):
            console.print("[yellow]Migration cancelled[/yellow]")
            return

        # Execute migrations
        with MigrationExecutor(config, console) as executor:
            total_success = True
            all_failed_migrations = set()
            remaining_batches = list(enumerate(execution_batches, 1))

            while remaining_batches:
                batch_num, batch = remaining_batches.pop(0)

                # Filter out migrations that depend on failed migrations (dynamic filtering)
                if not failfast and all_failed_migrations:
                    filtered_batch = []
                    skipped_migrations = []

                    for migration_id in batch:
                        # Check if this migration has any transitive dependency on failed migrations
                        # Use the DAG to find all ancestors (transitive dependencies)
                        ancestors = set(nx.ancestors(dag, migration_id))
                        depends_on_failed = bool(
                            ancestors.intersection(all_failed_migrations)
                        )

                        if depends_on_failed:
                            skipped_migrations.append(migration_id)
                            all_failed_migrations.add(
                                migration_id
                            )  # Mark as failed due to dependency

                            # Mark the migration as skipped in the executor
                            migration = next(
                                m for m in pending_migrations if m.id == migration_id
                            )
                            executor._mark_migration_as_skipped(
                                migration, "Skipped due to failed dependency"
                            )
                        else:
                            filtered_batch.append(migration_id)

                    if skipped_migrations:
                        console.print(
                            f"[yellow]Skipping migrations due to failed dependencies: {', '.join(skipped_migrations)}[/yellow]"
                        )

                    batch = filtered_batch

                if not batch:
                    console.print(
                        f"[yellow]Batch {batch_num}: No migrations to execute (all skipped)[/yellow]"
                    )
                    continue

                batch_migrations = [m for m in pending_migrations if m.id in batch]

                console.print(f"\n[bold]Executing batch {batch_num}[/bold]")

                if config.execution.parallel and len(batch_migrations) > 1:
                    results = executor.execute_parallel(batch_migrations)
                else:
                    results = executor.execute_sequential(batch_migrations)

                # Check results and handle failures dynamically
                batch_failed = False
                failed_migrations = []
                newly_failed = set()

                for migration_id, (success, _error) in results.items():
                    if not success:
                        # Error already printed by executor, just track failure
                        batch_failed = True
                        total_success = False
                        failed_migrations.append(migration_id)
                        all_failed_migrations.add(migration_id)
                        newly_failed.add(migration_id)

                if batch_failed:
                    if ci:
                        console.print(
                            f"[red]CI: Batch {batch_num} failed. Failed migrations: {', '.join(failed_migrations)}[/red]"
                        )
                    elif failfast:
                        console.print(
                            f"[red]Batch {batch_num} failed. Failed migrations: {', '.join(failed_migrations)}[/red]"
                        )

                    # Break execution if failfast is enabled or in CI mode (CI mode always fails fast)
                    if failfast or ci:
                        if ci:
                            console.print(
                                "[red]CI: Stopping execution due to failures[/red]"
                            )
                        elif failfast:
                            console.print(
                                "[red]Stopping execution due to failfast flag[/red]"
                            )
                        break
                    else:
                        # When not failing fast, immediately identify and mark dependent migrations as skipped
                        if newly_failed:
                            dependent_migrations = set()
                            all_remaining_migrations = {
                                mid
                                for _, remaining_batch in remaining_batches
                                for mid in remaining_batch
                            }

                            for migration_id in all_remaining_migrations:
                                # Only check migrations that aren't already marked as failed/skipped
                                if migration_id not in all_failed_migrations:
                                    ancestors = set(nx.ancestors(dag, migration_id))
                                    if ancestors.intersection(newly_failed):
                                        dependent_migrations.add(migration_id)

                            if dependent_migrations:
                                console.print(
                                    f"[yellow]Marking {len(dependent_migrations)} dependent migrations as skipped due to failures in this batch[/yellow]"
                                )
                                for dep_migration_id in dependent_migrations:
                                    all_failed_migrations.add(dep_migration_id)
                                    # Mark the migration as skipped
                                    migration = next(
                                        m
                                        for m in pending_migrations
                                        if m.id == dep_migration_id
                                    )
                                    executor._mark_migration_as_skipped(
                                        migration,
                                        f"Skipped due to failed dependency: {', '.join(newly_failed)}",
                                    )

            if total_success:
                console.print(
                    f"\n[bold green]Successfully applied {len(pending_migrations)} migrations[/bold green]"
                )
                if ci:
                    console.print(
                        "[green]CI: Migration process completed successfully[/green]"
                    )
            else:
                if ci:
                    console.print(
                        "[red]CI: Migration process failed - see errors above[/red]"
                    )
                ctx.exit(1)

    except Exception as e:
        if ci:
            console.print(
                f"[red]CI: Migration command failed with exception: {e}[/red]"
            )
        ctx.exit(1)


def load_migrations(migrations_dir: Path) -> list[Migration]:
    """Load all migration files from directory."""
    migrations = []

    for file_path in migrations_dir.glob("*.py"):
        if file_path.name.startswith("__"):
            continue

        try:
            migration = Migration.from_file(file_path)
            migrations.append(migration)
        except Exception:
            # Skip invalid migration files
            continue

    return sorted(migrations, key=lambda m: m.id)


def filter_migrations_to_target(
    migrations: list[Migration], target_id: str, applied_ids: set
) -> list[Migration]:
    """Filter migrations to only those needed to reach target."""
    # Find target migration
    target_migration = None
    for m in migrations:
        if m.id == target_id:
            target_migration = m
            break

    if not target_migration:
        raise ValueError(f"Target migration not found: {target_id}")

    # Build DAG to find dependencies
    resolver = DAGResolver()
    dag = resolver.build_dag(migrations)

    # Get all dependencies of target (including target itself)
    required_ids = set(nx.ancestors(dag, target_id))
    required_ids.add(target_id)

    # Filter to pending migrations only
    pending_required = [
        m for m in migrations if m.id in required_ids and m.id not in applied_ids
    ]

    return pending_required


def show_execution_plan(
    console, execution_batches: list[list[str]], parallel_enabled: bool
):
    """Display the execution plan."""
    console.print("\n[bold]Execution Plan:[/bold]")

    if not execution_batches:
        console.print("  [yellow]No migrations to execute[/yellow]")
        return

    total_migrations = sum(len(batch) for batch in execution_batches)
    console.print(f"  Total migrations: {total_migrations}")
    console.print(
        f"  Parallel execution: {'enabled' if parallel_enabled else 'disabled'}"
    )
    console.print()

    for batch_num, batch in enumerate(execution_batches, 1):
        if len(batch) == 1:
            console.print(f"  Batch {batch_num}: {batch[0]}")
        else:
            console.print(f"  Batch {batch_num} (parallel):")
            for migration_id in batch:
                console.print(f"    • {migration_id}")
        console.print()

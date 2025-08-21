"""Enhanced CLI display utilities for pydevelop-docs."""

import logging
import sys
from datetime import datetime
from typing import Any, Dict, List

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table


class EnhancedDisplay:
    """Enhanced display manager for CLI output with comprehensive logging."""

    def __init__(self, quiet: bool = False, debug: bool = False, dry_run: bool = False):
        self.quiet = quiet
        self.debug_enabled = debug
        self.dry_run = dry_run
        self.console = Console()
        self.operations_log = []
        self.timing_log = []

        # Set up logging
        self._setup_logging()

        # Track performance
        self.start_time = datetime.now()

    def _setup_logging(self):
        """Set up rich logging with appropriate levels."""
        logging.basicConfig(
            level=logging.DEBUG if self.debug_enabled else logging.INFO,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(console=self.console, show_path=self.debug_enabled)],
        )
        self.logger = logging.getLogger("pydevelop_docs")

        if self.debug_enabled:
            self.logger.debug("🐛 Debug mode enabled")
        if self.dry_run:
            self.logger.info("🧪 Dry-run mode enabled - no changes will be made")

    def log_operation(self, operation: str, details: str = "", success: bool = True):
        """Log an operation for later review."""
        timestamp = datetime.now()
        self.operations_log.append(
            {
                "timestamp": timestamp,
                "operation": operation,
                "details": details,
                "success": success,
                "dry_run": self.dry_run,
            }
        )

        if self.debug_enabled:
            status = "✅" if success else "❌"
            prefix = "[DRY-RUN] " if self.dry_run else ""
            self.logger.debug(f"{status} {prefix}{operation}: {details}")

    def log_timing(self, operation: str, duration_ms: float):
        """Log timing information for performance analysis."""
        self.timing_log.append(
            {
                "operation": operation,
                "duration_ms": duration_ms,
                "timestamp": datetime.now(),
            }
        )

        if self.debug_enabled:
            self.logger.debug(f"⏱️  {operation}: {duration_ms:.2f}ms")

    def show_analysis(self, analysis: Dict[str, Any]) -> None:
        """Display detailed project analysis."""
        if self.quiet:
            return

        click.echo(f"🔍 Analyzing project at {analysis.get('path', 'unknown')}...")
        click.echo(f"📦 Project: {analysis['name']} ({analysis['type']})")
        click.echo(f"🔧 Package Manager: {analysis['package_manager']}")
        click.echo()

        # Show package detection
        if analysis["type"] == "monorepo":
            self._show_package_details(analysis)
            click.echo()

        # Show central hub status
        self._show_central_hub(analysis["central_hub"])
        click.echo()

        # Show dependency issues
        self._show_dependency_analysis(analysis["dependencies"])

    def _show_package_details(self, analysis: Dict[str, Any]) -> None:
        """Display detailed package analysis."""
        click.echo("📋 Detected Packages:")

        for pkg_name in analysis["packages"]:
            details = analysis["package_details"][pkg_name]

            # Status indicators
            src_status = "✅" if details["src_exists"] else "❌"
            docs_status = self._get_docs_status(details)
            config_status = "✅" if details["pyproject_exists"] else "❌"

            # Shared config indicator
            shared_indicator = (
                " (shared)" if details["uses_shared_config"] else " (embedded)"
            )

            click.echo(
                f"   {self._get_package_status(details)} {pkg_name:<15} │ "
                f"src: {src_status} │ docs: {docs_status} │ "
                f"pyproject.toml: {config_status}{shared_indicator}"
            )

    def _get_package_status(self, details: Dict[str, Any]) -> str:
        """Get overall package status indicator."""
        if (
            details["src_exists"]
            and details["docs_exists"]
            and details["conf_py_exists"]
            and details["uses_shared_config"]
        ):
            return "✅"
        elif details["src_exists"] and details["docs_exists"]:
            return "⚠️ "
        else:
            return "❌"

    def _get_docs_status(self, details: Dict[str, Any]) -> str:
        """Get detailed docs status."""
        if not details["docs_exists"]:
            return "❌"
        elif not details["conf_py_exists"]:
            return "⚠️ (no conf.py)"
        elif not details["changelog_exists"]:
            return "⚠️ (no changelog)"
        elif not details["uses_shared_config"]:
            return "⚠️ (embedded config)"
        else:
            return "✅"

    def _show_central_hub(self, hub_info: Dict[str, Any]) -> None:
        """Display central hub status."""
        status = "✅ exists" if hub_info["exists"] else "❌ missing"
        collections = (
            " (collections: ✅)"
            if hub_info.get("collections_configured")
            else " (collections: ❌)"
        )

        click.echo(
            f"🏗️  Central Hub: /docs ({status}{collections if hub_info['exists'] else ''})"
        )

    def _show_dependency_analysis(self, deps: Dict[str, Any]) -> None:
        """Display dependency analysis results."""
        if deps["valid"]:
            click.echo("✅ Dependencies: All valid")
        else:
            click.echo("⚠️  Dependency Issues Found:")
            for issue in deps["issues"]:
                click.echo(f"      - {issue}")

            if not self.quiet:
                click.echo()
                click.echo("🔧 Auto-fixes available:")
                for i, issue in enumerate(deps["issues"], 1):
                    if "Duplicate dependency" in issue:
                        click.echo(f"   [{i}] Remove duplicate entry")
                    elif "TOML parse error" in issue:
                        click.echo(f"   [{i}] Fix TOML syntax")

    def show_processing(self, packages: List[str]) -> None:
        """Display package processing status."""
        if self.quiet:
            return

        click.echo("📦 Processing Packages:")
        for pkg in packages:
            click.echo(
                f"   🔨 {pkg:<15} │ conf.py: ... │ changelog.rst: ... │ index.rst: ..."
            )

    def update_package_status(self, pkg_name: str, status: Dict[str, str]) -> None:
        """Update package processing status."""
        if self.quiet:
            return

        conf_status = status.get("conf_py", "...")
        changelog_status = status.get("changelog", "...")
        index_status = status.get("index", "...")

        # Use ANSI escape codes to update the line
        click.echo(
            f"\r   🔨 {pkg_name:<15} │ conf.py: {conf_status} │ "
            f"changelog.rst: {changelog_status} │ index.rst: {index_status}",
            nl=False,
        )

    def show_summary(self, summary: Dict[str, Any]) -> None:
        """Display final summary."""
        if self.quiet:
            return

        click.echo("\n✅ Documentation initialized successfully!")
        click.echo()
        click.echo("📊 Summary:")
        click.echo(f"   - {summary.get('packages_configured', 0)} packages configured")
        click.echo(
            f"   - {summary.get('packages_created', 0)} packages had docs created"
        )
        click.echo(
            f"   - {summary.get('packages_updated', 0)} packages had docs updated"
        )
        click.echo(f"   - {summary.get('central_hub_status', 'unknown')} central hub")
        click.echo(
            f"   - {summary.get('conflicts_resolved', 0)} dependency conflicts resolved"
        )

        click.echo()
        click.echo("📚 Next steps:")
        click.echo("   1. poetry lock && poetry install --with docs")
        click.echo("   2. poetry run pydevelop-docs build-all --clean")
        click.echo("   3. open docs/build/html/index.html")

    def show_fixes_prompt(self, fixes: List[str]) -> bool:
        """Show available fixes and prompt for confirmation."""
        if self.quiet:
            return True

        if not fixes:
            return True

        click.echo("🔧 Auto-fixes available:")
        for i, fix in enumerate(fixes, 1):
            click.echo(f"   [{i}] {fix}")

        return click.confirm("\nApply fixes?", default=True)

    def debug(self, message: str) -> None:
        """Show debug message if debug mode is enabled."""
        if self.debug_enabled:
            click.echo(f"🐛 DEBUG: {message}", err=True)

    def error(self, message: str) -> None:
        """Show error message."""
        click.echo(f"❌ ERROR: {message}", err=True)

    def success(self, message: str) -> None:
        """Show success message."""
        if not self.quiet:
            click.echo(f"✅ {message}")

    def warning(self, message: str) -> None:
        """Show warning message."""
        if not self.quiet:
            click.echo(f"⚠️  {message}")

    def show_operations_summary(self) -> None:
        """Show summary of all operations performed."""
        if self.quiet or not self.operations_log:
            return

        total_time = (datetime.now() - self.start_time).total_seconds()
        successful_ops = len([op for op in self.operations_log if op["success"]])
        failed_ops = len([op for op in self.operations_log if not op["success"]])
        dry_run_ops = len([op for op in self.operations_log if op["dry_run"]])

        table = Table(
            title="📊 Operations Summary", show_header=True, header_style="bold magenta"
        )
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total Duration", f"{total_time:.2f}s")
        table.add_row("Total Operations", str(len(self.operations_log)))
        table.add_row("Successful", str(successful_ops))
        table.add_row("Failed", str(failed_ops))
        if dry_run_ops > 0:
            table.add_row("Dry-Run Operations", str(dry_run_ops))

        self.console.print(table)

        if self.debug_enabled and self.timing_log:
            self._show_performance_breakdown()

    def _show_performance_breakdown(self) -> None:
        """Show detailed performance breakdown."""
        if not self.timing_log:
            return

        timing_table = Table(title="⏱️  Performance Breakdown", show_header=True)
        timing_table.add_column("Operation", style="cyan")
        timing_table.add_column("Duration", style="green")
        timing_table.add_column("% of Total", style="yellow")

        total_time = sum(log["duration_ms"] for log in self.timing_log)

        for log in sorted(
            self.timing_log, key=lambda x: x["duration_ms"], reverse=True
        ):
            percentage = (
                (log["duration_ms"] / total_time * 100) if total_time > 0 else 0
            )
            timing_table.add_row(
                log["operation"], f"{log['duration_ms']:.2f}ms", f"{percentage:.1f}%"
            )

        self.console.print(timing_table)

    def show_detailed_analysis(self, analysis: Dict[str, Any]) -> None:
        """Show comprehensive project analysis with debugging info."""
        self.show_analysis(analysis)

        if self.debug_enabled:
            self.logger.debug("🔍 Detailed Analysis:")

            # Show package structure details
            for pkg_name, details in analysis.get("package_details", {}).items():
                self.logger.debug(f"📦 {pkg_name}:")
                for key, value in details.items():
                    status = "✅" if value else "❌"
                    self.logger.debug(f"   {key}: {status}")

            # Show configuration details
            config_info = analysis.get("central_hub", {})
            self.logger.debug(f"🏗️  Central Hub Config: {config_info}")

            # Show dependency analysis
            deps_info = analysis.get("dependencies", {})
            self.logger.debug(f"📋 Dependencies: {deps_info}")

    def show_mock_operations(self, operations: List[Dict[str, Any]]) -> None:
        """Show what operations would be performed in dry-run mode."""
        if self.quiet:
            return

        click.echo("\n🧪 Dry-Run Mode - Operations that would be performed:\n")

        for i, op in enumerate(operations, 1):
            operation_type = op.get("type", "unknown")
            description = op.get("description", "No description")
            target = op.get("target", "")

            click.echo(f"  [{i}] {operation_type.upper()}: {description}")
            if target:
                click.echo(f"      Target: {target}")

            if "details" in op:
                for detail in op["details"]:
                    click.echo(f"      - {detail}")

        click.echo(f"\nTotal operations: {len(operations)}")
        click.echo("Note: No actual changes will be made in dry-run mode.\n")

    def prompt_for_continuation(self, message: str, default: bool = True) -> bool:
        """Prompt user for continuation with dry-run awareness."""
        if self.dry_run:
            click.echo(f"🧪 DRY-RUN: Would prompt: {message}")
            return True
        if self.quiet:
            return default
        return click.confirm(message, default=default)

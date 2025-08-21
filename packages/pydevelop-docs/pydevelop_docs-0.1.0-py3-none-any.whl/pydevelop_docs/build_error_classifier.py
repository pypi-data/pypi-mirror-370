"""Build error classification and intelligent logging for documentation builds.

This module provides smart error classification and actionable error reporting
for Sphinx documentation builds, making it easier to identify and fix issues.
"""

import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import click


class ErrorSeverity(Enum):
    """Error severity levels for build issues."""

    CRITICAL = "critical"  # Build-breaking errors
    WARNING = "warning"  # Non-breaking but should fix
    INFO = "info"  # Informational messages
    IGNORE = "ignore"  # Can be safely ignored


@dataclass
class BuildError:
    """Represents a classified build error with context."""

    severity: ErrorSeverity
    category: str
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    suggestion: Optional[str] = None
    raw_error: Optional[str] = None


class BuildErrorClassifier:
    """Classifies and processes Sphinx build errors intelligently."""

    # Critical error patterns that break builds
    CRITICAL_PATTERNS = [
        # Import and module errors
        (r"ImportError: cannot import name '(\w+)'", "import_error"),
        (r"ModuleNotFoundError: No module named '([\w\.]+)'", "module_not_found"),
        (r"NameError: name '(\w+)' is not defined", "undefined_name"),
        (
            r"PydanticUndefinedAnnotation: name '(\w+)' is not defined",
            "pydantic_forward_ref",
        ),
        (r"SyntaxError: (.+)", "syntax_error"),
        (r"TypeError: (.+)", "type_error"),
        (r"circular import", "circular_import"),
        # Extension errors
        (r"Extension error \(([\w\.]+)\)", "extension_error"),
        (r"sphinx\.errors\.ExtensionError: (.+)", "sphinx_extension_error"),
        # Build failures
        (r"build finished with (\d+) errors", "build_failed"),
        (r"Exception occurred:", "exception"),
    ]

    # Warning patterns that don't break builds but should be fixed
    WARNING_PATTERNS = [
        # Grid/layout warnings
        (
            r"WARNING: The parent of a 'grid-item' should be a 'grid-row'",
            "grid_structure",
        ),
        # Docstring formatting
        (r"WARNING: Explicit markup ends without a blank line", "docstring_markup"),
        (r"WARNING: Block quote ends without a blank line", "docstring_block_quote"),
        (r"WARNING: Definition list ends without a blank line", "docstring_definition"),
        (r"WARNING: Unexpected indentation", "docstring_indentation"),
        (r"ERROR: Unexpected indentation", "docstring_indentation_error"),
        # Duplicate definitions
        (r"WARNING: duplicate object description of ([\w\.]+)", "duplicate_object"),
        # Missing references
        (r"WARNING: undefined label: ([\w\-]+)", "undefined_reference"),
        (r"WARNING: document isn't included in any toctree", "orphan_document"),
    ]

    # Info patterns for progress tracking
    INFO_PATTERNS = [
        (r"reading sources\.\.\. \[\s*(\d+)%\]", "reading_progress"),
        (r"building \[(\w+)\]: (.+)", "building_stage"),
        (r"copying static files\.\.\.", "copying_files"),
        (r"dumping object inventory\.\.\.", "dumping_inventory"),
        (r"build succeeded", "build_success"),
    ]

    # Patterns to completely ignore
    IGNORE_PATTERNS = [
        r"WARNING: while setting up the extension",
        r"Loaded Extensions",
        r"Versions",
        r"Platform:",
        r"Python version:",
        r"Sphinx version:",
        r"Last Messages",
    ]

    def __init__(self, package_name: str = ""):
        """Initialize the error classifier.

        Args:
            package_name: Name of the package being built
        """
        self.package_name = package_name
        self.errors: List[BuildError] = []
        self.error_counts = {
            ErrorSeverity.CRITICAL: 0,
            ErrorSeverity.WARNING: 0,
            ErrorSeverity.INFO: 0,
            ErrorSeverity.IGNORE: 0,
        }

    def classify_line(self, line: str) -> Optional[BuildError]:
        """Classify a single line of build output.

        Args:
            line: Line of output to classify

        Returns:
            BuildError if line matches a pattern, None otherwise
        """
        # Check if line should be ignored
        for pattern in self.IGNORE_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                return None

        # Check critical errors
        for pattern, category in self.CRITICAL_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return self._create_error(ErrorSeverity.CRITICAL, category, line, match)

        # Check warnings
        for pattern, category in self.WARNING_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return self._create_error(ErrorSeverity.WARNING, category, line, match)

        # Check info patterns
        for pattern, category in self.INFO_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return self._create_error(ErrorSeverity.INFO, category, line, match)

        return None

    def _create_error(
        self, severity: ErrorSeverity, category: str, line: str, match: re.Match
    ) -> BuildError:
        """Create a BuildError with context and suggestions.

        Args:
            severity: Error severity level
            category: Error category
            line: Original error line
            match: Regex match object

        Returns:
            BuildError with populated fields
        """
        # Extract file path and line number if present
        file_path, line_number = self._extract_location(line)

        # Generate user-friendly message
        message = self._generate_message(category, match, line)

        # Generate fix suggestion
        suggestion = self._generate_suggestion(category, match, file_path)

        error = BuildError(
            severity=severity,
            category=category,
            message=message,
            file_path=file_path,
            line_number=line_number,
            suggestion=suggestion,
            raw_error=line.strip(),
        )

        self.errors.append(error)
        self.error_counts[severity] += 1

        return error

    def _extract_location(self, line: str) -> Tuple[Optional[str], Optional[int]]:
        """Extract file path and line number from error line.

        Args:
            line: Error line to parse

        Returns:
            Tuple of (file_path, line_number)
        """
        # Pattern 1: /path/to/file.py:123:
        match = re.search(r"(/[^:]+\.(?:py|rst)):(\d+):", line)
        if match:
            return match.group(1), int(match.group(2))

        # Pattern 2: (in document `/path/to/file.rst`)
        match = re.search(r"\(in document `([^`]+)`\)", line)
        if match:
            return match.group(1), None

        # Pattern 3: File "/path/to/file.py", line 123
        match = re.search(r'File "([^"]+)", line (\d+)', line)
        if match:
            return match.group(1), int(match.group(2))

        return None, None

    def _generate_message(self, category: str, match: re.Match, line: str) -> str:
        """Generate a user-friendly error message.

        Args:
            category: Error category
            match: Regex match object
            line: Original error line

        Returns:
            User-friendly message
        """
        # Safely get match groups
        group1 = (
            match.group(1)
            if match and match.lastindex and match.lastindex >= 1
            else None
        )

        messages = {
            "import_error": (
                f"Cannot import '{group1}'" if group1 else "Import error detected"
            ),
            "module_not_found": (
                f"Module '{group1}' not found" if group1 else "Module not found"
            ),
            "undefined_name": (
                f"Name '{group1}' is not defined" if group1 else "Undefined name error"
            ),
            "pydantic_forward_ref": (
                f"Pydantic forward reference error: '{group1}' not defined"
                if group1
                else "Pydantic forward reference error"
            ),
            "circular_import": "Circular import detected",
            "grid_structure": "Grid layout issue in documentation",
            "docstring_markup": "Docstring formatting issue",
            "docstring_block_quote": "Docstring block quote formatting issue",
            "docstring_definition": "Docstring definition list formatting issue",
            "docstring_indentation": "Docstring indentation issue",
            "docstring_indentation_error": "Docstring indentation error",
            "duplicate_object": (
                f"Duplicate documentation for '{group1}'"
                if group1
                else "Duplicate object documentation"
            ),
            "extension_error": (
                f"Extension '{group1}' failed" if group1 else "Extension error"
            ),
            "orphan_document": "Document not included in any toctree",
            "undefined_reference": (
                f"Undefined reference: '{group1}'" if group1 else "Undefined reference"
            ),
        }

        return messages.get(category, line.strip())

    def _generate_suggestion(
        self, category: str, match: re.Match, file_path: Optional[str]
    ) -> Optional[str]:
        """Generate fix suggestions for common errors.

        Args:
            category: Error category
            match: Regex match object
            file_path: Path to the file with the error

        Returns:
            Suggestion for fixing the error
        """
        # Safely get match groups
        group1 = (
            match.group(1)
            if match and match.lastindex and match.lastindex >= 1
            else None
        )

        suggestions = {
            "pydantic_forward_ref": (
                f"Use TYPE_CHECKING import:\n"
                f"   from typing import TYPE_CHECKING\n"
                f"   if TYPE_CHECKING:\n"
                f"       from module import {group1}"
                if group1
                else "Use TYPE_CHECKING imports to avoid forward reference issues"
            ),
            "circular_import": (
                "Break circular dependency:\n"
                "   1. Use TYPE_CHECKING imports for type hints\n"
                "   2. Move shared types to a common module\n"
                "   3. Use string annotations with 'from __future__ import annotations'"
            ),
            "grid_structure": (
                "Fix grid structure:\n"
                "   .. grid:: 2\n"
                "      .. grid-item::\n"
                "         Content here"
            ),
            "docstring_markup": (
                "Add blank line after explicit markup:\n"
                "   .. note::\n"
                "   \n"
                "      Note content here"
            ),
            "docstring_block_quote": (
                "Add blank line after block quote:\n"
                "   Block quote text\n"
                "   \n"
                "   Regular text here"
            ),
            "docstring_indentation": (
                "Fix indentation in docstring:\n"
                "   Ensure consistent indentation levels"
            ),
            "duplicate_object": (
                f"Add :no-index: to one occurrence of {group1}:\n"
                f"   .. automethod:: {group1}\n"
                f"      :no-index:"
                if group1
                else "Add :no-index: to duplicate object documentation"
            ),
            "module_not_found": (
                f"Ensure {group1} is installed:\n"
                f"   poetry add {group1}\n"
                f"   # or check import path"
                if group1
                else "Check that the module is installed and import path is correct"
            ),
            "orphan_document": (
                "Add document to a toctree:\n"
                "   In index.rst or another toctree, add:\n"
                "   .. toctree::\n"
                "      :maxdepth: 2\n"
                "      \n"
                "      your_document"
            ),
        }

        return suggestions.get(category)

    def process_output(self, output: str) -> None:
        """Process complete build output and classify all errors.

        Args:
            output: Complete build output to process
        """
        for line in output.splitlines():
            self.classify_line(line)

    def get_summary(self) -> Dict[str, any]:
        """Get summary of all errors found.

        Returns:
            Dictionary with error counts and categorized errors
        """
        return {
            "package": self.package_name,
            "total_errors": len(self.errors),
            "counts": dict(self.error_counts),
            "critical_errors": [
                e for e in self.errors if e.severity == ErrorSeverity.CRITICAL
            ],
            "warnings": [e for e in self.errors if e.severity == ErrorSeverity.WARNING],
            "has_critical": self.error_counts[ErrorSeverity.CRITICAL] > 0,
        }

    def print_summary(
        self, show_warnings: bool = True, show_suggestions: bool = True
    ) -> None:
        """Print a formatted summary of errors.

        Args:
            show_warnings: Whether to show warnings
            show_suggestions: Whether to show fix suggestions
        """
        summary = self.get_summary()

        if not self.errors:
            return

        # Print package header
        if self.package_name:
            click.echo(f"\n📦 {self.package_name}")
            click.echo("─" * (len(self.package_name) + 3))

        # Show critical errors first
        if summary["critical_errors"]:
            click.echo(f"\n❌ Critical Errors ({len(summary['critical_errors'])})")
            for error in summary["critical_errors"][:5]:  # Show max 5
                self._print_error(error, show_suggestions)

            if len(summary["critical_errors"]) > 5:
                click.echo(
                    f"   ... and {len(summary['critical_errors']) - 5} more critical errors"
                )

        # Show warnings if requested
        if show_warnings and summary["warnings"]:
            click.echo(f"\n⚠️  Warnings ({len(summary['warnings'])})")

            # Group warnings by category
            warning_groups = {}
            for warning in summary["warnings"]:
                if warning.category not in warning_groups:
                    warning_groups[warning.category] = []
                warning_groups[warning.category].append(warning)

            # Show summary by category
            for category, warnings in warning_groups.items():
                click.echo(f"   • {category}: {len(warnings)} occurrences")
                if len(warnings) <= 2:
                    for w in warnings:
                        if w.file_path:
                            click.echo(f"     → {Path(w.file_path).name}")

    def _print_error(self, error: BuildError, show_suggestion: bool = True) -> None:
        """Print a single error with formatting.

        Args:
            error: Error to print
            show_suggestion: Whether to show fix suggestion
        """
        # Print main error message
        click.echo(f"\n   {error.message}")

        # Print file location if available
        if error.file_path:
            try:
                # Try to make path relative to current directory
                file_path = Path(error.file_path)
                if file_path.is_absolute():
                    try:
                        file_display = file_path.relative_to(Path.cwd())
                    except ValueError:
                        # If not relative to cwd, just use the path as is
                        file_display = error.file_path
                else:
                    file_display = error.file_path
            except Exception:
                # Fallback to original path if any error
                file_display = error.file_path

            if error.line_number:
                click.echo(f"   📄 {file_display}:{error.line_number}")
            else:
                click.echo(f"   📄 {file_display}")

        # Print suggestion if available
        if show_suggestion and error.suggestion:
            click.echo(f"   💡 {error.suggestion}")

    def should_fail_build(self) -> bool:
        """Determine if build should fail based on errors.

        Returns:
            True if build should fail, False otherwise
        """
        return self.error_counts[ErrorSeverity.CRITICAL] > 0

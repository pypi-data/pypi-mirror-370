"""Auto-fix utilities for common pydevelop-docs issues."""

import re
from pathlib import Path
from typing import Any, Dict, List

import tomlkit


class AutoFixer:
    """Handles automatic fixes for common issues."""

    def __init__(self, project_path: Path, display=None):
        self.project_path = project_path
        self.display = display
        self.fixes_applied = []

    def analyze_and_fix(
        self, analysis: Dict[str, Any], apply_fixes: bool = True
    ) -> List[str]:
        """Analyze issues and apply fixes if requested."""
        available_fixes = []

        # Check dependency issues
        if not analysis["dependencies"]["valid"]:
            for issue in analysis["dependencies"]["issues"]:
                if "Duplicate dependency" in issue:
                    fix = self._prepare_duplicate_fix(issue)
                    if fix:
                        available_fixes.append(fix)
                        if apply_fixes:
                            self._apply_duplicate_fix(fix)

        return available_fixes

    def _prepare_duplicate_fix(self, issue: str) -> Dict[str, Any]:
        """Prepare fix for duplicate dependency."""
        # Extract dependency name and line numbers from issue
        # Format: "Duplicate dependency 'dep-name' (lines 123, 456)"
        match = re.search(
            r"Duplicate dependency '([^']+)' \(lines (\d+), (\d+)\)", issue
        )
        if not match:
            return None

        dep_name, line1, line2 = match.groups()
        return {
            "type": "duplicate_dependency",
            "dependency": dep_name,
            "lines": [int(line1), int(line2)],
            "description": f"Remove duplicate {dep_name} from line {line2}",
        }

    def _apply_duplicate_fix(self, fix: Dict[str, Any]) -> None:
        """Apply duplicate dependency fix using proper TOML structure handling."""
        pyproject_path = self.project_path / "pyproject.toml"

        try:
            # Use tomlkit to properly handle TOML structure
            with open(pyproject_path, "r") as f:
                content = f.read()

            doc = tomlkit.parse(content)

            # Handle different types of duplicates
            dependency_name = fix["dependency"]

            # Check in dependencies section
            if "dependencies" in doc.get("tool", {}).get("poetry", {}):
                deps = doc["tool"]["poetry"]["dependencies"]
                if dependency_name in deps:
                    # For regular dependencies, keep the first occurrence
                    # This is already handled properly by tomlkit
                    pass

            # Check in dependency groups
            if "group" in doc.get("tool", {}).get("poetry", {}):
                for group_name, group_deps in doc["tool"]["poetry"]["group"].items():
                    if (
                        "dependencies" in group_deps
                        and dependency_name in group_deps["dependencies"]
                    ):
                        # For group dependencies, keep the first occurrence
                        pass

            # Check in sources (most common corruption case)
            if "source" in doc.get("tool", {}).get("poetry", {}):
                sources = doc["tool"]["poetry"]["source"]
                if isinstance(sources, list):
                    # Find duplicate sources by name
                    seen_names = set()
                    indices_to_remove = []

                    for i, source in enumerate(sources):
                        if isinstance(source, dict) and "name" in source:
                            name = source["name"]
                            if name == dependency_name:
                                if name in seen_names:
                                    # This is a duplicate, mark for removal
                                    indices_to_remove.append(i)
                                else:
                                    seen_names.add(name)

                    # Remove duplicates in reverse order to maintain indices
                    for index in reversed(indices_to_remove):
                        del sources[index]

            # Write the corrected TOML back
            with open(pyproject_path, "w") as f:
                f.write(tomlkit.dumps(doc))

            self.fixes_applied.append(
                f"Removed duplicate {fix['dependency']} using TOML-aware fix"
            )

            if self.display:
                self.display.success(
                    f"Fixed: Removed duplicate {fix['dependency']} (TOML-safe)"
                )

        except Exception as e:
            if self.display:
                self.display.error(f"Failed to fix duplicate dependency: {e}")

            # Fallback to line-based fix if TOML parsing fails
            self._apply_duplicate_fix_fallback(fix)

    def _apply_duplicate_fix_fallback(self, fix: Dict[str, Any]) -> None:
        """Fallback line-based duplicate fix (original method)."""
        pyproject_path = self.project_path / "pyproject.toml"

        try:
            with open(pyproject_path, "r") as f:
                lines = f.readlines()

            # Remove the higher line number (keep the first occurrence)
            line_to_remove = max(fix["lines"]) - 1  # Convert to 0-based index

            if line_to_remove < len(lines):
                removed_line = lines[line_to_remove].strip()
                del lines[line_to_remove]

                # Write back the file
                with open(pyproject_path, "w") as f:
                    f.writelines(lines)

                self.fixes_applied.append(
                    f"Removed duplicate {fix['dependency']} from line {line_to_remove + 1} (fallback)"
                )

                if self.display:
                    self.display.warning(
                        f"Fixed: Removed duplicate {fix['dependency']} (fallback method - may need manual review)"
                    )

        except Exception as e:
            if self.display:
                self.display.error(f"Fallback fix also failed: {e}")

    def fix_toml_syntax(self) -> bool:
        """Attempt to fix basic TOML syntax issues."""
        pyproject_path = self.project_path / "pyproject.toml"

        try:
            with open(pyproject_path, "r") as f:
                content = f.read()

            # Try to parse and identify issues
            try:
                tomlkit.parse(content)
                return True  # Already valid
            except Exception as parse_error:
                # Common fixes
                fixed_content = content

                # Fix common quote issues
                fixed_content = re.sub(r'([^"\s])(")', r"\1\n\2", fixed_content)

                # Try parsing again
                try:
                    tomlkit.parse(fixed_content)
                    with open(pyproject_path, "w") as f:
                        f.write(fixed_content)

                    self.fixes_applied.append("Fixed TOML syntax issues")
                    if self.display:
                        self.display.success("Fixed TOML syntax")
                    return True

                except:
                    if self.display:
                        self.display.error(
                            f"Could not auto-fix TOML syntax: {parse_error}"
                        )
                    return False

        except Exception as e:
            if self.display:
                self.display.error(f"Failed to read pyproject.toml: {e}")
            return False

    def ensure_shared_config(self, package_path: Path, package_name: str) -> bool:
        """Ensure package uses shared pydevelop_docs config."""
        conf_py_path = package_path / "docs" / "source" / "conf.py"

        if not conf_py_path.exists():
            return False

        try:
            content = conf_py_path.read_text()

            # Check if already using shared config
            if "pydevelop_docs.config" in content:
                return True

            # Generate new conf.py with shared config
            new_content = f'''"""Sphinx configuration for {package_name} documentation."""

import os
import sys

from sphinx.application import Sphinx

# Path setup
sys.path.insert(0, os.path.abspath("../../src"))

# Import shared Haive configuration from pydevelop-docs package
from pydevelop_docs.config import get_haive_config

# Get package-specific configuration
package_name = "{package_name}"
package_path = "../../src"

config = get_haive_config(
    package_name=package_name,
    package_path=package_path,
    is_central_hub=False
)

# Apply configuration to globals
globals().update(config)
'''

            conf_py_path.write_text(new_content)
            self.fixes_applied.append(f"Updated {package_name} to use shared config")

            if self.display:
                self.display.success(
                    f"Updated {package_name} conf.py to use shared config"
                )

            return True

        except Exception as e:
            if self.display:
                self.display.error(f"Failed to update {package_name} config: {e}")
            return False

    def create_changelog(self, package_path: Path, package_name: str) -> bool:
        """Create changelog.rst file for package."""
        changelog_path = package_path / "docs" / "source" / "changelog.rst"

        if changelog_path.exists():
            return True

        try:
            changelog_path.parent.mkdir(parents=True, exist_ok=True)

            content = f"""Changelog
=========

This page tracks changes to {package_name} using both manual entries and Git history.

Release Notes
-------------

.. changelog::
   :towncrier: ../../
   :towncrier-skip-if-empty:

Recent Documentation Updates
----------------------------

.. git_changelog::
   :revisions: 10
   :rev-list-extra: --first-parent

**How to Use This Page:**

- **Release Notes**: Structured changelog entries for each version
- **Recent Changes**: Git-based documentation updates  
- **Manual Entries**: Important changes added via towncrier fragments
- **Commit History**: Automatic tracking of all documentation changes

**Adding Changelog Entries:**

To add a changelog entry for this package:

.. code-block:: bash

   # From the package directory
   poetry run towncrier create <issue>.<type>.md --content "Description of change"
   
   # Types: feature, bugfix, improvement, deprecation, breaking, security, performance, docs, dev, misc

This ensures both structured release notes and detailed commit history are available for tracking changes.
"""

            changelog_path.write_text(content)
            self.fixes_applied.append(f"Created changelog.rst for {package_name}")

            if self.display:
                self.display.success(f"Created changelog.rst for {package_name}")

            return True

        except Exception as e:
            if self.display:
                self.display.error(
                    f"Failed to create changelog for {package_name}: {e}"
                )
            return False

    def update_index_rst(self, package_path: Path, package_name: str) -> bool:
        """Update index.rst to include changelog."""
        index_path = package_path / "docs" / "source" / "index.rst"

        if not index_path.exists():
            return False

        try:
            content = index_path.read_text()

            # Check if changelog is already included
            if "changelog" in content:
                return True

            # Find where to insert changelog section
            # Look for toctree sections and add before "Indices and tables"
            lines = content.split("\n")
            insert_index = -1

            for i, line in enumerate(lines):
                if "Indices and tables" in line or "Indices and Tables" in line:
                    insert_index = i
                    break

            if insert_index == -1:
                # Append at the end
                insert_index = len(lines)

            # Insert changelog section
            changelog_section = [
                "",
                "Changelog",
                "---------",
                "",
                ".. toctree::",
                "   :maxdepth: 2",
                "   :caption: Changelog",
                "   ",
                "   changelog",
                "",
            ]

            # Insert the section
            for i, line in enumerate(changelog_section):
                lines.insert(insert_index + i, line)

            index_path.write_text("\n".join(lines))
            self.fixes_applied.append(f"Updated index.rst for {package_name}")

            if self.display:
                self.display.success(f"Updated index.rst for {package_name}")

            return True

        except Exception as e:
            if self.display:
                self.display.error(
                    f"Failed to update index.rst for {package_name}: {e}"
                )
            return False

    def get_applied_fixes(self) -> List[str]:
        """Get list of fixes that were applied."""
        return self.fixes_applied.copy()

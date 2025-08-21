"""Simplified command implementations for pydevelop-docs."""

import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
import tomlkit
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class DocsCommand:
    """Base class for documentation commands."""

    def __init__(self, project_path: Path = None):
        self.project_path = project_path or Path.cwd()
        self.console = console

    def find_packages(
        self,
        packages_dir: List[str] = None,
        include_root: bool = False,
        patterns: List[str] = None,
    ) -> List[Path]:
        """Find packages to document."""
        packages = []

        # Use patterns if provided
        if patterns:
            for pattern in patterns:
                packages.extend(self.project_path.glob(pattern))

        # Use directory search
        elif packages_dir:
            for dir_name in packages_dir:
                dir_path = self.project_path / dir_name
                if dir_path.exists():
                    for item in dir_path.iterdir():
                        if item.is_dir() and not item.name.startswith("."):
                            # Check if it's a valid package
                            if any(
                                (item / f).exists()
                                for f in ["pyproject.toml", "setup.py", "__init__.py"]
                            ):
                                packages.append(item)

        # Include root if requested
        if include_root:
            packages.insert(0, self.project_path)

        return packages


class InitCommand(DocsCommand):
    """Initialize documentation for packages."""

    def run(
        self,
        packages_dir: List[str] = None,
        include_root: bool = False,
        packages: List[str] = None,
        dry_run: bool = False,
        force: bool = False,
    ) -> bool:
        """Run the initialization."""

        # Find packages
        if packages:
            # Specific packages requested
            found = [Path(p) for p in packages]
        else:
            # Discover packages
            found = self.find_packages(packages_dir, include_root)

        if not found:
            self.console.print("[red]No packages found to document![/red]")
            return False

        # Show what will be done
        self.console.print(f"\n[bold]Found {len(found)} package(s) to document:[/bold]")
        for pkg in found:
            self.console.print(
                f"  📦 {pkg.relative_to(self.project_path) if pkg != self.project_path else '(root)'}"
            )

        if dry_run:
            self.console.print("\n[yellow]Dry run - no changes will be made[/yellow]")
            self._show_changes(found)
            return True

        # Confirm
        if not force and not click.confirm("\nProceed with initialization?"):
            return False

        # Initialize each package
        success = True
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:

            for pkg in found:
                task = progress.add_task(f"Initializing {pkg.name}...", total=None)

                try:
                    self._init_package(pkg, force)
                    progress.update(task, completed=True)
                except Exception as e:
                    self.console.print(
                        f"[red]Failed to initialize {pkg.name}: {e}[/red]"
                    )
                    success = False

        if success:
            self.console.print(
                "\n[green]✅ Documentation initialized successfully![/green]"
            )
            self._show_next_steps(found)

        return success

    def _init_package(self, package_path: Path, force: bool = False):
        """Initialize documentation for a single package."""
        docs_path = package_path / "docs"

        # Check if exists
        if docs_path.exists() and not force:
            raise Exception("Documentation already exists! Use --force to overwrite.")

        # Create structure
        self._create_structure(package_path)

        # Generate files
        self._generate_conf_py(package_path)
        self._generate_index_rst(package_path)
        self._generate_changelog_rst(package_path)
        self._generate_makefile(package_path)

        # Add dependencies if poetry
        if (package_path / "pyproject.toml").exists():
            self._add_dependencies(package_path)

    def _create_structure(self, package_path: Path):
        """Create documentation directory structure."""
        dirs = [
            "docs/source",
            "docs/source/_static/css",
            "docs/source/_static/js",
            "docs/source/_templates",
            "docs/build",
            "scripts",
        ]

        for dir_path in dirs:
            (package_path / dir_path).mkdir(parents=True, exist_ok=True)

    def _generate_conf_py(self, package_path: Path):
        """Generate Sphinx configuration."""
        name = self._get_package_name(package_path)

        conf_content = f'''"""Sphinx configuration for {name}.

This configuration uses pydevelop-docs shared configuration system
with 43+ Sphinx extensions from PyAutoDoc.
"""

import os
import sys

# Add source to path
sys.path.insert(0, os.path.abspath("../.."))

# Import the complete 600+ line shared configuration from pydevelop-docs
try:
    from pydevelop_docs.config import get_haive_config
    
    # Get the full configuration with all 43+ extensions
    config = get_haive_config(
        package_name="{name}",
        package_path="../..",
        is_central_hub=False,
        extra_extensions=[]  # Add package-specific extensions here
    )
    
    # Apply all configuration to globals
    globals().update(config)
    
    # Package-specific overrides can go here
    # Example:
    # html_theme_options["announcement"] = "Custom announcement"
    
except ImportError:
    # Fallback if pydevelop-docs is not installed
    print("Warning: pydevelop-docs not found. Using minimal configuration.")
    print("Install with: pip install pydevelop-docs")
    
    # Minimal fallback configuration
    project = "{name}"
    extensions = [
        "sphinx.ext.autodoc",
        "sphinx.ext.napoleon",
        "sphinx_autoapi.extension",
        "myst_parser",
    ]
    html_theme = "furo"
    autoapi_dirs = ["../.."]
    
# End of configuration
'''

        conf_path = package_path / "docs" / "source" / "conf.py"
        conf_path.write_text(conf_content)

    def _generate_index_rst(self, package_path: Path):
        """Generate index.rst file."""
        name = self._get_package_name(package_path)

        content = f"""
{name} Documentation
{'=' * (len(name) + 14)}

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   autoapi/index
   changelog
   
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
"""

        index_path = package_path / "docs" / "source" / "index.rst"
        index_path.write_text(content)

    def _generate_changelog_rst(self, package_path: Path):
        """Generate changelog.rst file with towncrier integration."""
        name = self._get_package_name(package_path)

        content = f"""Changelog
=========

This page tracks changes to {name} using both manual entries and Git history.

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

        changelog_path = package_path / "docs" / "source" / "changelog.rst"
        changelog_path.write_text(content)

    def _generate_makefile(self, package_path: Path):
        """Copy Makefile template."""
        # This would copy from templates
        makefile_content = """# Minimal makefile for Sphinx documentation

SPHINXOPTS    = -W --keep-going
SPHINXBUILD   = sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

help:
\t@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

%: Makefile
\t@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean:
\trm -rf $(BUILDDIR)/* $(SOURCEDIR)/autoapi

livehtml:
\tsphinx-autobuild -b html $(SPHINXOPTS) $(SOURCEDIR) $(BUILDDIR)/html
"""

        makefile_path = package_path / "docs" / "Makefile"
        makefile_path.write_text(makefile_content)

    def _add_dependencies(self, package_path: Path):
        """Add documentation dependencies to pyproject.toml."""
        pyproject_path = package_path / "pyproject.toml"

        with open(pyproject_path) as f:
            doc = tomlkit.load(f)

        # Ensure structure
        if "tool" not in doc:
            doc["tool"] = {}
        if "poetry" not in doc["tool"]:
            doc["tool"]["poetry"] = {}
        if "group" not in doc["tool"]["poetry"]:
            doc["tool"]["poetry"]["group"] = {}
        if "docs" not in doc["tool"]["poetry"]["group"]:
            doc["tool"]["poetry"]["group"]["docs"] = {"dependencies": {}}

        # Add minimal deps
        deps = doc["tool"]["poetry"]["group"]["docs"]["dependencies"]
        deps.update(
            {
                "sphinx": "^8.2.3",
                "sphinx-autoapi": "^3.6.0",
                "furo": "^2024.8.6",
                "myst-parser": "^4.0.1",
            }
        )

        # Add haive-docs if this is a haive package
        if self._is_haive_package(package_path):
            deps["pydevelop-docs"] = {
                "path": "../../tools/pydevelop-docs",
                "develop": True,
            }

        with open(pyproject_path, "w") as f:
            tomlkit.dump(doc, f)

    def _get_package_name(self, package_path: Path) -> str:
        """Get package name."""
        if package_path == self.project_path:
            return self.project_path.name

        # Try pyproject.toml
        pyproject = package_path / "pyproject.toml"
        if pyproject.exists():
            with open(pyproject) as f:
                data = tomlkit.load(f)
            if "tool" in data and "poetry" in data["tool"]:
                return data["tool"]["poetry"].get("name", package_path.name)
            elif "project" in data:
                return data["project"].get("name", package_path.name)

        return package_path.name

    def _is_haive_package(self, package_path: Path) -> bool:
        """Check if this is a Haive package."""
        name = self._get_package_name(package_path)
        return name.startswith("haive-")

    def _show_changes(self, packages: List[Path]):
        """Show what would be created."""
        self.console.print("\n[yellow]The following would be created:[/yellow]")

        for pkg in packages:
            self.console.print(f"\n📦 {pkg.name}:")
            self.console.print("  📁 docs/")
            self.console.print("    📁 source/")
            self.console.print("      📄 conf.py")
            self.console.print("      📄 index.rst")
            self.console.print("    📁 build/")
            self.console.print("    📄 Makefile")

            if (pkg / "pyproject.toml").exists():
                self.console.print(
                    "  ✏️  Updated pyproject.toml (add docs dependencies)"
                )

    def _show_next_steps(self, packages: List[Path]):
        """Show next steps."""
        self.console.print("\n[bold]Next steps:[/bold]")
        self.console.print("1. Install dependencies:")
        self.console.print("   [cyan]poetry install --with docs[/cyan]")
        self.console.print("\n2. Build documentation:")
        self.console.print("   [cyan]haive-docs build[/cyan]")
        self.console.print("\n3. View documentation:")
        self.console.print("   [cyan]open docs/build/html/index.html[/cyan]")


class BuildCommand(DocsCommand):
    """Build documentation."""

    def run(
        self,
        packages_dir: List[str] = None,
        include_root: bool = False,
        packages: List[str] = None,
        clean: bool = False,
        parallel: bool = True,
        open_after: bool = False,
    ) -> bool:
        """Run the build."""

        # Find packages to build
        if packages:
            found = [Path(p) for p in packages]
        else:
            found = self.find_packages(packages_dir, include_root)

        # Filter to those with docs
        buildable = [p for p in found if (p / "docs").exists()]

        if not buildable:
            self.console.print("[red]No documented packages found![/red]")
            self.console.print("Run [cyan]haive-docs init[/cyan] first.")
            return False

        # Build each
        self.console.print(f"\n[bold]Building {len(buildable)} package(s):[/bold]")

        success = True
        built = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:

            for pkg in buildable:
                task = progress.add_task(f"Building {pkg.name}...", total=None)

                try:
                    if self._build_package(pkg, clean, parallel):
                        built.append(pkg)
                    progress.update(task, completed=True)
                except Exception as e:
                    self.console.print(f"[red]Failed to build {pkg.name}: {e}[/red]")
                    success = False

        if success:
            self.console.print(
                f"\n[green]✅ Successfully built {len(built)} package(s)![/green]"
            )

            if open_after and built:
                self._open_docs(built[0])

        return success

    def _build_package(self, package_path: Path, clean: bool, parallel: bool) -> bool:
        """Build documentation for a package."""
        docs_path = package_path / "docs"

        # Clean first if requested
        if clean:
            build_path = docs_path / "build"
            if build_path.exists():
                shutil.rmtree(build_path)

        # Build command
        cmd = ["sphinx-build", "-b", "html", "-W", "--keep-going"]

        if parallel:
            cmd.extend(["-j", "auto"])

        cmd.extend(["source", "build/html"])

        # Run build
        result = subprocess.run(cmd, cwd=docs_path, capture_output=True, text=True)

        return result.returncode == 0

    def _open_docs(self, package_path: Path):
        """Open documentation in browser."""
        index = package_path / "docs" / "build" / "html" / "index.html"
        if index.exists():
            import webbrowser

            webbrowser.open(f"file://{index}")


class QuickCommands:
    """Quick command implementations."""

    @staticmethod
    def init_monorepo(include_root: bool = True, dry_run: bool = False):
        """Quick init for monorepo projects."""
        cmd = InitCommand()
        return cmd.run(
            packages_dir=["packages", "tools"],
            include_root=include_root,
            dry_run=dry_run,
        )

    @staticmethod
    def init_single(dry_run: bool = False):
        """Quick init for single package."""
        cmd = InitCommand()
        return cmd.run(include_root=True, dry_run=dry_run)

    @staticmethod
    def build_all(clean: bool = False):
        """Build all documented packages."""
        cmd = BuildCommand()
        return cmd.run(
            packages_dir=["packages", "tools", "."], include_root=True, clean=clean
        )

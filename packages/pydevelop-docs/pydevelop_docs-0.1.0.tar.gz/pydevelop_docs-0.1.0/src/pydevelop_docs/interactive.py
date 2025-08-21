"""Interactive CLI for pydevelop-docs."""

from pathlib import Path
from typing import Any, Dict, List, Optional

import click
import questionary
import tomlkit
import yaml
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.tree import Tree

console = Console()


class InteractiveCLI:
    """Interactive command-line interface for pydevelop-docs."""

    def __init__(self):
        self.console = console
        self.project_path = Path.cwd()
        self.config = {}

    def run(self):
        """Run the interactive CLI."""
        self.console.print(
            Panel.fit(
                "[bold blue]PyDevelop Documentation Tool[/bold blue]\n"
                "Interactive setup and management for Python documentation",
                border_style="blue",
            )
        )

        # Main menu
        while True:
            choice = questionary.select(
                "What would you like to do?",
                choices=[
                    "🚀 Initialize documentation",
                    "🔨 Build documentation",
                    "📦 Manage dependencies",
                    "🔧 Configure settings",
                    "🧹 Clean build artifacts",
                    "❌ Exit",
                ],
            ).ask()

            if not choice or "Exit" in choice:
                break

            if "Initialize" in choice:
                self.initialize_docs()
            elif "Build" in choice:
                self.build_docs()
            elif "dependencies" in choice:
                self.manage_dependencies()
            elif "Configure" in choice:
                self.configure_settings()
            elif "Clean" in choice:
                self.clean_artifacts()

    def initialize_docs(self):
        """Interactive documentation initialization."""
        self.console.print("\n[bold]Documentation Initialization[/bold]\n")

        # Analyze project
        with self.console.status("Analyzing project structure..."):
            analysis = self._analyze_project()

        # Show project info
        self._show_project_info(analysis)

        # Get user preferences
        config = {}

        # Project type
        project_type = questionary.select(
            "Project type:",
            choices=[
                "Single package",
                "Monorepo (multiple packages)",
                "Hybrid (root + packages)",
            ],
        ).ask()

        if "Single" in project_type:
            config["type"] = "single"
        elif "Monorepo" in project_type:
            config["type"] = "monorepo"

            # Ask for package directories
            package_dirs = questionary.checkbox(
                "Select package directories:",
                choices=self._find_package_dirs() + ["Custom..."],
            ).ask()

            if "Custom..." in package_dirs:
                custom = questionary.text(
                    "Enter package directories (comma-separated):"
                ).ask()
                package_dirs = [d.strip() for d in custom.split(",")]

            config["packages_dir"] = package_dirs

            # Include root?
            config["include_root"] = questionary.confirm(
                "Include root-level documentation?"
            ).ask()
        else:
            config["type"] = "hybrid"
            config["include_root"] = True

        # Documentation paths
        if questionary.confirm("Customize documentation paths?", default=False).ask():
            config["paths"] = {
                "docs_dir": questionary.text(
                    "Documentation directory name:", default="docs"
                ).ask(),
                "source_dir": questionary.text(
                    "Source directory name:", default="source"
                ).ask(),
                "build_dir": questionary.text(
                    "Build directory name:", default="build"
                ).ask(),
            }

        # Theme selection
        theme = questionary.select(
            "Documentation theme:",
            choices=[
                "Furo (modern, dark mode)",
                "Sphinx RTD (classic)",
                "PyData (scientific)",
                "Book Theme (educational)",
            ],
        ).ask()

        config["theme"] = theme.split()[0].lower()

        # Extensions
        extensions = questionary.checkbox(
            "Additional features:",
            choices=[
                "API documentation (autoapi)",
                "Jupyter notebook support",
                "Mermaid diagrams",
                "PlantUML diagrams",
                "Copy button for code",
                "Dark/light mode toggle",
                "Version selector",
                "PDF generation",
            ],
            default=["API documentation (autoapi)", "Copy button for code"],
        ).ask()

        config["extensions"] = self._map_extensions(extensions)

        # Dry run first?
        if questionary.confirm("Preview changes first? (dry-run)", default=True).ask():
            self._dry_run_init(config)

            if not questionary.confirm("Proceed with initialization?").ask():
                return

        # Initialize
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Initializing documentation...", total=None)

            try:
                self._do_initialize(config, progress, task)
                self.console.print(
                    "\n[green]✅ Documentation initialized successfully![/green]"
                )

                # Next steps
                self._show_next_steps(config)

            except Exception as e:
                self.console.print(f"\n[red]❌ Error: {e}[/red]")

    def build_docs(self):
        """Interactive documentation building."""
        self.console.print("\n[bold]Build Documentation[/bold]\n")

        # Find buildable packages
        packages = self._find_documented_packages()

        if not packages:
            self.console.print("[yellow]No documented packages found![/yellow]")
            if questionary.confirm("Initialize documentation first?").ask():
                self.initialize_docs()
            return

        # What to build?
        choices = ["All packages"] + [f"📦 {p.name}" for p in packages]

        selected = questionary.checkbox(
            "Select packages to build:",
            choices=choices,
            default=["All packages"] if len(packages) > 1 else choices,
        ).ask()

        # Build options
        options = {
            "clean": questionary.confirm("Clean before building?", default=False).ask(),
            "parallel": questionary.confirm(
                "Use parallel building?", default=True
            ).ask(),
            "open": questionary.confirm("Open in browser after?", default=True).ask(),
        }

        # Builder type
        builder = (
            questionary.select(
                "Output format:",
                choices=["HTML", "PDF", "ePub", "LaTeX"],
                default="HTML",
            )
            .ask()
            .lower()
        )

        # Build
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:

            if "All packages" in selected:
                to_build = packages
            else:
                to_build = [p for p in packages if f"📦 {p.name}" in selected]

            for package in to_build:
                task = progress.add_task(f"Building {package.name}...", total=None)

                try:
                    self._build_package(package, builder, options)
                    progress.update(task, completed=True)

                except Exception as e:
                    self.console.print(
                        f"[red]❌ Failed to build {package.name}: {e}[/red]"
                    )

        self.console.print("\n[green]✅ Build complete![/green]")

        if options["open"] and builder == "html":
            self._open_docs(to_build[0])

    def manage_dependencies(self):
        """Manage documentation dependencies."""
        self.console.print("\n[bold]Dependency Management[/bold]\n")

        action = questionary.select(
            "What would you like to do?",
            choices=[
                "View current dependencies",
                "Add dependencies to packages",
                "Sync dependencies across packages",
                "Check for conflicts",
                "Update all dependencies",
            ],
        ).ask()

        if "View" in action:
            self._show_dependencies()
        elif "Add" in action:
            self._add_dependencies()
        elif "Sync" in action:
            self._sync_dependencies()
        elif "conflicts" in action:
            self._check_conflicts()
        elif "Update" in action:
            self._update_dependencies()

    def configure_settings(self):
        """Configure pydevelop-docs settings."""
        self.console.print("\n[bold]Configuration Settings[/bold]\n")

        # Check for existing config
        config_file = self.project_path / ".pydevelop-docs.yaml"

        if config_file.exists():
            if questionary.confirm("Configuration file exists. Load it?").ask():
                with open(config_file) as f:
                    self.config = yaml.safe_load(f)

        # Edit configuration
        self.config = self._edit_config(self.config)

        # Save?
        if questionary.confirm("Save configuration?").ask():
            with open(config_file, "w") as f:
                yaml.dump(self.config, f, default_flow_style=False)
            self.console.print("[green]✅ Configuration saved![/green]")

    def clean_artifacts(self):
        """Clean build artifacts."""
        self.console.print("\n[bold]Clean Build Artifacts[/bold]\n")

        # Find artifacts
        artifacts = self._find_artifacts()

        if not artifacts:
            self.console.print("[green]No build artifacts found![/green]")
            return

        # Show what will be cleaned
        self.console.print("Found artifacts:")
        for artifact in artifacts:
            self.console.print(f"  • {artifact}")

        if questionary.confirm(f"Remove {len(artifacts)} artifacts?").ask():
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task = progress.add_task("Cleaning...", total=len(artifacts))

                for artifact in artifacts:
                    artifact.unlink() if artifact.is_file() else self._rmtree(artifact)
                    progress.update(task, advance=1)

            self.console.print("\n[green]✅ Cleaned successfully![/green]")

    # Helper methods
    def _analyze_project(self) -> Dict[str, Any]:
        """Analyze current project structure."""
        analysis = {
            "name": self.project_path.name,
            "type": "unknown",
            "has_packages": (self.project_path / "packages").exists(),
            "has_pyproject": (self.project_path / "pyproject.toml").exists(),
            "has_setup": (self.project_path / "setup.py").exists(),
            "package_dirs": [],
            "python_files": 0,
        }

        # Find package directories
        for item in self.project_path.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                if any(
                    (item / sub).exists()
                    for sub in ["pyproject.toml", "setup.py", "__init__.py"]
                ):
                    analysis["package_dirs"].append(item.name)

        # Count Python files
        analysis["python_files"] = len(list(self.project_path.rglob("*.py")))

        # Determine type
        if analysis["has_packages"]:
            analysis["type"] = "monorepo"
        elif analysis["has_pyproject"] or analysis["has_setup"]:
            analysis["type"] = "single"

        return analysis

    def _show_project_info(self, analysis: Dict[str, Any]):
        """Display project analysis results."""
        table = Table(title="Project Analysis", show_header=False)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Project Name", analysis["name"])
        table.add_row("Type", analysis["type"])
        table.add_row("Python Files", str(analysis["python_files"]))

        if analysis["package_dirs"]:
            table.add_row("Package Dirs", ", ".join(analysis["package_dirs"]))

        self.console.print(table)
        self.console.print()

    def _find_package_dirs(self) -> List[str]:
        """Find potential package directories."""
        dirs = []
        for name in ["packages", "libs", "apps", "src", "tools"]:
            if (self.project_path / name).exists():
                dirs.append(name)
        return dirs

    def _map_extensions(self, selected: List[str]) -> List[str]:
        """Map user selections to extension names."""
        mapping = {
            "API documentation": ["sphinx_autoapi"],
            "Jupyter notebook": ["nbsphinx", "myst_nb"],
            "Mermaid diagrams": ["sphinxcontrib.mermaid"],
            "PlantUML diagrams": ["sphinxcontrib.plantuml"],
            "Copy button": ["sphinx_copybutton"],
            "Dark/light mode": ["sphinx_togglebutton"],
            "Version selector": ["sphinx_multiversion"],
            "PDF generation": ["rst2pdf"],
        }

        extensions = []
        for selection in selected:
            for key, exts in mapping.items():
                if key in selection:
                    extensions.extend(exts)

        return extensions

    def _dry_run_init(self, config: Dict[str, Any]):
        """Show what would be created."""
        self.console.print(
            "\n[yellow]Dry Run - The following would be created:[/yellow]\n"
        )

        tree = Tree("📁 Project Root")

        # Add docs structure
        docs = tree.add("📁 docs/")
        docs.add("📁 source/")
        docs.add("📁 build/")
        docs.add("📄 Makefile")

        # Add package docs
        if config.get("packages_dir"):
            for pkg_dir in config["packages_dir"]:
                pkg = tree.add(f"📁 {pkg_dir}/")
                for item in (self.project_path / pkg_dir).iterdir():
                    if item.is_dir():
                        pkg_docs = pkg.add(f"📁 {item.name}/docs/")

        self.console.print(tree)
        self.console.print()

    def _show_next_steps(self, config: Dict[str, Any]):
        """Show next steps after initialization."""
        self.console.print("\n[bold]Next Steps:[/bold]")
        self.console.print(
            "1. Install dependencies: [cyan]poetry install --with docs[/cyan]"
        )
        self.console.print("2. Build documentation: [cyan]pydevelop-docs build[/cyan]")
        self.console.print(
            "3. View documentation: [cyan]open docs/build/html/index.html[/cyan]"
        )

    def _find_documented_packages(self) -> List[Path]:
        """Find packages with documentation."""
        packages = []

        # Check root
        if (self.project_path / "docs").exists():
            packages.append(self.project_path)

        # Check subdirectories
        for pattern in ["packages/*", "*/docs", "tools/*"]:
            for path in self.project_path.glob(pattern):
                if path.is_dir() and (path / "docs").exists():
                    packages.append(path)

        return packages

    def _find_artifacts(self) -> List[Path]:
        """Find build artifacts to clean."""
        artifacts = []
        patterns = [
            "docs/build",
            "docs/source/autoapi",
            "**/docs/build",
            "**/docs/source/autoapi",
            "**/_build",
            "**/.doctrees",
        ]

        for pattern in patterns:
            artifacts.extend(self.project_path.glob(pattern))

        return artifacts


def interactive_cli():
    """Run the interactive CLI."""
    cli = InteractiveCLI()
    cli.run()


if __name__ == "__main__":
    interactive_cli()

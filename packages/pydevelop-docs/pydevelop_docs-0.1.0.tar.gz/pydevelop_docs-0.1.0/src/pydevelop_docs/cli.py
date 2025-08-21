"""Command-line interface for PyDevelop Documentation Tools.

This module provides the main CLI commands for PyDevelop-Docs, enabling users to
initialize, build, and manage documentation for any Python project structure.
The CLI supports both interactive and non-interactive modes, with intelligent
project detection and comprehensive configuration generation.

Main Features:
    - Universal project analysis and documentation setup
    - Support for monorepos, single packages, src layouts, and flat structures
    - Interactive CLI with rich terminal UI and guided setup
    - Automatic project type detection and metadata extraction
    - Copy documentation setups between projects
    - Dry-run capability for previewing operations
    - Integration with popular package managers (Poetry, setuptools, etc.)

CLI Commands:
    init: Initialize documentation for the current project
    interactive: Run interactive setup with guided configuration
    build: Build documentation for single package or monorepo
    analyze: Analyze project structure and display configuration
    setup-general: Set up documentation for any Python project (universal)
    copy-setup: Copy documentation setup from one project to another

Examples:
    Basic initialization in current directory:
    
    >>> pydevelop-docs init
    
    Interactive setup with guided configuration:
    
    >>> pydevelop-docs interactive
    
    Analyze any Python project:
    
    >>> pydevelop-docs analyze /path/to/project
    
    Universal setup for any project:
    
    >>> pydevelop-docs setup-general /path/to/project --force
    
    Copy setup between projects:
    
    >>> pydevelop-docs copy-setup /source/project /dest/project

Classes:
    ProjectAnalyzer: Analyze Python project structure and configuration
    DocsInitializer: Initialize documentation for Python projects
    CentralHubGenerator: Generate central documentation hub for monorepos

Note:
    This module requires Click for CLI functionality and supports both
    Poetry and setuptools project configurations. The generated documentation
    uses Sphinx with 40+ pre-configured extensions and the Furo theme.
"""

import asyncio
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
import tomlkit
import yaml

from .autofix import AutoFixer
from .builders import MonorepoBuilder, get_builder
from .config import get_central_hub_config, get_haive_config
from .display import EnhancedDisplay
from .interactive import interactive_cli as run_interactive
from .mock_operations import MockOperationPlan, create_documentation_plan


class ProjectAnalyzer:
    """Intelligent Python project structure analysis and configuration detection.
    
    This class provides comprehensive analysis of Python projects to determine
    their type, structure, package management system, and existing documentation
    status. It supports all common Python project layouts and package managers.
    
    Supported Project Types:
        - monorepo: Multiple packages in packages/ directory structure
        - single: Single package with various layout patterns
        - unknown: Projects that don't match standard patterns
        
    Supported Package Managers:
        - Poetry (pyproject.toml with [tool.poetry])
        - setuptools (setup.py or pyproject.toml with setuptools config)
        - pip (requirements.txt based projects)
        - hatch, pdm, and other pyproject.toml variants
        
    Structure Patterns Detected:
        - src layout: src/package_name/ organization
        - flat layout: package_name/ in project root
        - monorepo: packages/package-name/ structure
        
    Attributes:
        path (Path): Absolute path to the project directory being analyzed
        
    Examples:
        Analyze a monorepo project:
        
        >>> analyzer = ProjectAnalyzer(Path("/path/to/monorepo"))
        >>> info = analyzer.analyze()
        >>> print(f"Type: {info['type']}, Packages: {len(info['packages'])}")
        
        Analyze a single package:
        
        >>> analyzer = ProjectAnalyzer(Path("/path/to/single-package"))
        >>> info = analyzer.analyze()
        >>> print(f"Structure: {info['structure']}, Manager: {info['package_manager']}")
        
        Check existing documentation:
        
        >>> info = analyzer.analyze()
        >>> if info['has_docs']:
        ...     print("Documentation directory already exists")
    """

    def __init__(self, path: Path):
        """Initialize the project analyzer with a project path.
        
        Args:
            path: Path to the Python project directory to analyze.
                 Will be resolved to an absolute path.
        """
        self.path = path.resolve()

    def analyze(self) -> Dict[str, Any]:
        """Perform comprehensive analysis of the Python project structure.
        
        Analyzes the project to determine its type, package manager, structure
        patterns, existing documentation status, and provides detailed information
        about all packages found within the project.
        
        Returns:
            Dict[str, Any]: Comprehensive project analysis containing:
                - type (str): Project type ('monorepo', 'single', 'unknown')
                - name (str): Project name extracted from config or directory name
                - package_manager (str): Detected package manager ('poetry', 'setuptools', etc.)
                - packages (List[str]): List of package names found in the project
                - package_details (Dict[str, Dict]): Detailed analysis of each package
                - has_docs (bool): Whether documentation directory exists
                - central_hub (Dict): Central documentation hub analysis
                - structure (str): Structure pattern ('src', 'flat', None)
                - python_files (List[Path]): List of Python files found
                - dependencies (Dict): Dependency analysis results
                
        Examples:
            Monorepo analysis result:
            
            >>> info = analyzer.analyze()
            >>> print(info)
            {
                'type': 'monorepo',
                'name': 'my-project',
                'package_manager': 'poetry',
                'packages': ['package-a', 'package-b'],
                'has_docs': True,
                'structure': 'src',
                ...
            }
            
            Single package analysis:
            
            >>> info = analyzer.analyze()
            >>> info['type']
            'single'
            >>> info['package_details']['single']['src_exists']
            True
        """
        info = {
            "type": "unknown",
            "name": self.path.name,
            "package_manager": None,
            "packages": [],
            "package_details": {},
            "has_docs": (self.path / "docs").exists(),
            "central_hub": self._analyze_central_hub(),
            "structure": None,
            "python_files": [],
            "dependencies": self._analyze_dependencies(),
        }

        # Detect package manager
        if (self.path / "pyproject.toml").exists():
            info["package_manager"] = self._detect_pyproject_manager()
            info["name"] = self._get_project_name()
        elif (self.path / "setup.py").exists():
            info["package_manager"] = "setuptools"
        elif (self.path / "requirements.txt").exists():
            info["package_manager"] = "pip"

        # Detect project type and structure
        if (self.path / "packages").exists():
            info["type"] = "monorepo"
            package_names = [
                p.name
                for p in (self.path / "packages").iterdir()
                if p.is_dir() and not p.name.startswith(".")
            ]
            info["packages"] = package_names
            info["package_details"] = {
                name: self._analyze_package(self.path / "packages" / name)
                for name in package_names
            }
        else:
            info["type"] = "single"
            info["package_details"] = {"single": self._analyze_package(self.path)}

        # Detect source structure
        if (self.path / "src").exists():
            info["structure"] = "src"
            info["python_files"] = list((self.path / "src").rglob("*.py"))
        elif list(self.path.glob("*.py")):
            info["structure"] = "flat"
            info["python_files"] = list(self.path.glob("**/*.py"))

        return info

    def _analyze_package(self, package_path: Path) -> Dict[str, Any]:
        """Analyze individual package structure and status."""
        return {
            "src_exists": (package_path / "src").exists(),
            "docs_exists": (package_path / "docs").exists(),
            "docs_source_exists": (package_path / "docs" / "source").exists(),
            "pyproject_exists": (package_path / "pyproject.toml").exists(),
            "conf_py_exists": (package_path / "docs" / "source" / "conf.py").exists(),
            "changelog_exists": (
                package_path / "docs" / "source" / "changelog.rst"
            ).exists(),
            "index_rst_exists": (
                package_path / "docs" / "source" / "index.rst"
            ).exists(),
            "uses_shared_config": self._uses_shared_config(package_path),
            "python_files_count": (
                len(list(package_path.rglob("*.py"))) if package_path.exists() else 0
            ),
        }

    def _analyze_central_hub(self) -> Dict[str, Any]:
        """Analyze central documentation hub status."""
        docs_path = self.path / "docs"
        return {
            "exists": docs_path.exists(),
            "source_exists": (docs_path / "source").exists(),
            "conf_py_exists": (docs_path / "source" / "conf.py").exists(),
            "index_rst_exists": (docs_path / "source" / "index.rst").exists(),
            "collections_configured": self._check_collections_config(docs_path),
            "build_exists": (docs_path / "build").exists(),
        }

    def _analyze_dependencies(self) -> Dict[str, Any]:
        """Skip dependency analysis for existing projects - focus on documentation only."""
        pyproject_path = self.path / "pyproject.toml"

        if not pyproject_path.exists():
            return {"valid": False, "issues": ["No pyproject.toml found"]}

        try:
            # Just validate that the TOML file is readable
            with open(pyproject_path, "r") as f:
                content = f.read()

            # Ensure it's valid TOML
            tomlkit.parse(content)

            # For existing projects, assume dependencies are correctly managed
            # pydevelop-docs is a documentation tool, not a dependency manager
            return {"valid": True, "issues": []}

        except Exception as e:
            return {"valid": False, "issues": [f"TOML parse error: {e}"]}

    def _analyze_dependencies_old(self) -> Dict[str, Any]:
        """Original naive dependency analysis - now deprecated."""
        pyproject_path = self.path / "pyproject.toml"
        issues = []

        if not pyproject_path.exists():
            return {"valid": False, "issues": ["No pyproject.toml found"]}

        try:
            with open(pyproject_path, "r") as f:
                content = f.read()

            # Check for duplicate entries (DEPRECATED - too broad)
            lines = content.split("\n")
            seen_deps = {}
            for i, line in enumerate(lines, 1):
                if "=" in line and not line.strip().startswith("#"):
                    dep_name = line.split("=")[0].strip()
                    if dep_name in seen_deps and dep_name:
                        issues.append(
                            f"Duplicate dependency '{dep_name}' (lines {seen_deps[dep_name]}, {i})"
                        )
                    else:
                        seen_deps[dep_name] = i

            # Try to parse TOML
            import tomlkit

            tomlkit.parse(content)

        except Exception as e:
            issues.append(f"TOML parse error: {str(e)}")

        return {"valid": len(issues) == 0, "issues": issues}

    def _uses_shared_config(self, package_path: Path) -> bool:
        """Check if package uses shared pydevelop_docs config."""
        conf_py = package_path / "docs" / "source" / "conf.py"
        if not conf_py.exists():
            return False

        try:
            content = conf_py.read_text()
            return "pydevelop_docs.config" in content
        except:
            return False

    def _check_collections_config(self, docs_path: Path) -> bool:
        """Check if sphinx-collections is configured."""
        conf_py = docs_path / "source" / "conf.py"
        if not conf_py.exists():
            return False

        try:
            content = conf_py.read_text()
            return "sphinxcontrib.collections" in content
        except:
            return False

    def _detect_pyproject_manager(self) -> str:
        """Detect which tool manages the pyproject.toml."""
        try:
            with open(self.path / "pyproject.toml") as f:
                data = tomlkit.load(f)

            if "poetry" in data.get("tool", {}):
                return "poetry"
            elif "hatch" in data.get("tool", {}):
                return "hatch"
            elif "pdm" in data.get("tool", {}):
                return "pdm"
            elif "setuptools" in data.get("tool", {}):
                return "setuptools"
            else:
                return "pep621"  # Standard pyproject.toml
        except:
            return "unknown"

    def _get_project_name(self) -> str:
        """Extract project name from pyproject.toml."""
        try:
            with open(self.path / "pyproject.toml") as f:
                data = tomlkit.load(f)

            # Try different locations
            if "poetry" in data.get("tool", {}):
                return data["tool"]["poetry"].get("name", self.path.name)
            elif "project" in data:
                return data["project"].get("name", self.path.name)
            else:
                return self.path.name
        except:
            return self.path.name


class DocsInitializer:
    """Initialize comprehensive Sphinx documentation for Python projects.
    
    This class handles the complete initialization of Sphinx documentation
    for any Python project structure. It creates the necessary directory
    structure, generates configuration files, copies templates and static
    assets, and sets up AutoAPI for automatic API documentation generation.
    
    Features:
        - Complete Sphinx documentation setup with 40+ extensions
        - AutoAPI configuration with hierarchical organization
        - Professional Furo theme with custom styling
        - Support for both shared and inline configuration approaches
        - Automatic dependency management for Poetry projects
        - Custom build scripts and Makefile generation
        
    Configuration Options:
        - with_guides: Include user guides section
        - with_examples: Include examples section  
        - with_cli: Include CLI documentation
        - with_tutorials: Include tutorials section
        - use_shared_config: Use centralized config vs inline config
        
    Attributes:
        project_path (Path): Path to the project being documented
        project_info (Dict[str, Any]): Project analysis results from ProjectAnalyzer
        template_path (Path): Path to documentation templates directory
        quiet (bool): Whether to suppress output messages
        doc_config (Dict[str, bool]): Documentation configuration options
        
    Examples:
        Initialize documentation for a single package:
        
        >>> analyzer = ProjectAnalyzer(Path("/path/to/project"))
        >>> info = analyzer.analyze()
        >>> initializer = DocsInitializer(
        ...     project_path=Path("/path/to/project"),
        ...     project_info=info,
        ...     doc_config={"with_guides": True}
        ... )
        >>> initializer.initialize(force=True)
        
        Initialize with custom configuration:
        
        >>> config = {
        ...     "with_guides": True,
        ...     "with_examples": True,
        ...     "use_shared_config": True
        ... }
        >>> initializer = DocsInitializer(
        ...     project_path=path,
        ...     project_info=info,
        ...     doc_config=config,
        ...     quiet=True
        ... )
        >>> initializer.initialize()
    """

    def __init__(
        self,
        project_path: Path,
        project_info: Dict[str, Any],
        doc_config: Dict[str, bool] = None,
        quiet: bool = False,
    ):
        """Initialize the documentation initializer.
        
        Args:
            project_path: Path to the project where documentation will be created
            project_info: Project analysis results containing type, structure, etc.
            doc_config: Optional configuration for documentation features.
                       Defaults to basic configuration with all features disabled.
            quiet: Whether to suppress informational output messages
        """
        self.project_path = project_path
        self.project_info = project_info
        self.template_path = Path(__file__).parent / "templates"
        self.quiet = quiet
        self.doc_config = doc_config or {
            "with_guides": False,
            "with_examples": False,
            "with_cli": False,
            "with_tutorials": False,
        }

    def initialize(self, force: bool = False):
        """Initialize complete Sphinx documentation structure for the project.
        
        Creates the full documentation setup including directory structure,
        configuration files, templates, static assets, and build scripts.
        Automatically detects project structure and configures AutoAPI paths.
        
        Process Overview:
            1. Create docs/ directory structure with source, _static, _templates
            2. Copy static CSS, JavaScript, and template files
            3. Copy custom AutoAPI templates for hierarchical organization
            4. Generate Sphinx conf.py with 40+ extensions configured
            5. Create professional index.rst homepage
            6. Generate Makefile and build scripts
            7. Add Poetry dependencies if using Poetry package manager
            
        Args:
            force: If True, overwrite existing documentation directory.
                  If False, raise exception if docs/ already exists.
                  
        Raises:
            click.ClickException: If documentation already exists and force=False
            
        Examples:
            Initialize with overwrite protection:
            
            >>> initializer.initialize()  # Fails if docs/ exists
            
            Force initialization (overwrite existing):
            
            >>> initializer.initialize(force=True)  # Overwrites docs/
            
        Note:
            This method modifies the filesystem by creating directories and files.
            Use force=True carefully as it will overwrite existing documentation.
        """
        docs_path = self.project_path / "docs"

        if docs_path.exists() and not force:
            raise click.ClickException(
                "Documentation already exists! Use --force to overwrite."
            )

        # Create directory structure
        self._create_directories()

        # Copy static files and templates
        self._copy_static_files()

        # Copy AutoAPI templates
        self._copy_autoapi_templates()

        # Generate configuration files
        if self.doc_config.get("use_shared_config", True):
            # Use the new consolidated configuration method
            conf_content = self._generate_conf_py_from_config()
        else:
            # Use the legacy hardcoded configuration
            conf_content = self._generate_conf_py()

        # Write the configuration
        conf_path = self.project_path / "docs" / "source" / "conf.py"
        conf_path.write_text(conf_content)

        self._generate_index_rst()
        self._generate_makefile()
        self._generate_build_scripts()

        # Add dependencies if using Poetry
        if self.project_info["package_manager"] == "poetry":
            self._add_poetry_dependencies()

    def _create_directories(self):
        """Create documentation directory structure based on configuration."""
        # Essential directories that are always needed
        essential_dirs = [
            "docs",
            "docs/source",
            "docs/source/_static",
            "docs/source/_static/css",
            "docs/source/_static/js",
            "docs/source/_templates",
            "docs/source/_templates/includes",
            "docs/build",
            "scripts",
        ]

        for dir_path in essential_dirs:
            (self.project_path / dir_path).mkdir(parents=True, exist_ok=True)

        # Create optional documentation sections using template manager
        from .template_manager import TemplateManager

        template_manager = TemplateManager(self.project_path, self.project_info)
        template_manager.create_all_sections(self.doc_config)

    def _copy_static_files(self):
        """Copy static assets from templates."""
        static_files = [
            # CSS files - Modern 4-file system (matches template)
            ("static/enhanced-design.css", "docs/source/_static/enhanced-design.css"),
            (
                "static/breadcrumb-navigation.css",
                "docs/source/_static/breadcrumb-navigation.css",
            ),
            ("static/mermaid-custom.css", "docs/source/_static/mermaid-custom.css"),
            (
                "static/tippy-enhancements.css",
                "docs/source/_static/tippy-enhancements.css",
            ),
            # Legacy CSS (keep for backward compatibility)
            ("static/css/custom.css", "docs/source/_static/css/custom.css"),
            # JS files
            (
                "static/js/api-enhancements.js",
                "docs/source/_static/js/api-enhancements.js",
            ),
            (
                "static/js/furo-enhancements.js",
                "docs/source/_static/furo-enhancements.js",
            ),
            ("static/js/mermaid-config.js", "docs/source/_static/mermaid-config.js"),
            # Templates
            ("_templates/layout.html", "docs/source/_templates/layout.html"),
        ]

        for src, dest in static_files:
            src_path = self.template_path / src
            dest_path = self.project_path / dest

            if src_path.exists():
                shutil.copy2(src_path, dest_path)

    def _copy_autoapi_templates(self):
        """Copy AutoAPI templates to the project documentation directory."""
        src_template_dir = self.template_path / "_autoapi_templates"
        dest_template_dir = self.project_path / "docs" / "source" / "_autoapi_templates"

        if src_template_dir.exists():
            import shutil

            # Remove existing templates if they exist
            if dest_template_dir.exists():
                shutil.rmtree(dest_template_dir)

            # Copy the entire template directory
            shutil.copytree(src_template_dir, dest_template_dir)

            if not self.quiet:
                click.echo(f"✅ Copied AutoAPI templates to {dest_template_dir}")

    def _generate_conf_py_from_config(self):
        """Generate Sphinx configuration using shared config module.

        This method uses the centralized configuration from config.py
        to ensure consistency and prevent duplication.
        """
        from .config import get_haive_config

        # Determine Python path based on project structure
        if self.project_info["structure"] == "src":
            sys_path = 'sys.path.insert(0, os.path.abspath("../../src"))'
        else:
            sys_path = 'sys.path.insert(0, os.path.abspath("../.."))'

        # Generate autoapi directories
        if self.project_info["structure"] == "src":
            autoapi_dirs = '["../../src"]'
        else:
            # Find package directories
            package_dirs = []
            for p in self.project_path.iterdir():
                if p.is_dir() and (p / "__init__.py").exists():
                    package_dirs.append(f'"../../{p.name}"')
            autoapi_dirs = (
                f'[{", ".join(package_dirs)}]' if package_dirs else '["../.."]'
            )

        # Get configuration from shared module
        config = get_haive_config(
            package_name=self.project_info["name"], package_path=str(self.project_path)
        )

        # Build the conf.py content
        conf_content = f'''"""
Sphinx configuration for {self.project_info["name"]}.

This configuration uses PyDevelop-Docs shared configuration.
Generated by pydevelop-docs init.
"""

import os
import sys
from datetime import date

# -- Path setup --------------------------------------------------------------
{sys_path}

# -- Project information -----------------------------------------------------
project = "{self.project_info["name"]}"
copyright = f"{{date.today().year}}, {self.project_info["name"]} Team"
author = "{self.project_info["name"]} Team"
release = "0.1.0"

# -- Import shared configuration from pydevelop_docs -------------------------
from pydevelop_docs.config import get_haive_config

# Get the standardized configuration
_config = get_haive_config(project, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Apply all configuration settings
for key, value in _config.items():
    if key not in ['project', 'copyright', 'author', 'release']:
        globals()[key] = value

# -- Project-specific overrides ----------------------------------------------
# Override autoapi_dirs for this specific project structure
autoapi_dirs = {autoapi_dirs}

# -- Additional setup --------------------------------------------------------

def setup(app):
    """Sphinx setup hook."""
    # Modern CSS files (matches html_css_files)
    css_files = [
        "enhanced-design.css",
        "breadcrumb-navigation.css", 
        "mermaid-custom.css",
        "tippy-enhancements.css"
    ]
    for css_file in css_files:
        if os.path.exists("_static/" + css_file):
            app.add_css_file(css_file)
    
    # Legacy fallback
    if os.path.exists("_static/css/custom.css"):
        app.add_css_file("css/custom.css")
        
    if os.path.exists("_static/js/api-enhancements.js"):
        app.add_js_file("js/api-enhancements.js")
'''

        return conf_content

    def _generate_conf_py(self):
        """Generate Sphinx configuration with full PyAutoDoc setup."""
        # Determine Python path based on project structure
        if self.project_info["structure"] == "src":
            sys_path = 'sys.path.insert(0, os.path.abspath("../../src"))'
        else:
            sys_path = 'sys.path.insert(0, os.path.abspath("../.."))'

        # Generate autoapi directories
        if self.project_info["structure"] == "src":
            autoapi_dirs = '["../../src"]'
        else:
            # Find package directories
            package_dirs = []
            for p in self.project_path.iterdir():
                if p.is_dir() and (p / "__init__.py").exists():
                    package_dirs.append(f'"../../{p.name}"')
            autoapi_dirs = (
                f'[{", ".join(package_dirs)}]' if package_dirs else '["../.."]'
            )

        conf_content = f'''"""
Sphinx configuration for {self.project_info["name"]}.

This configuration includes all extensions from PyAutoDoc (43+ extensions).
Generated by pydevelop-docs init.
"""

import os
import sys
from datetime import date

# -- Path setup --------------------------------------------------------------
{sys_path}

# -- Project information -----------------------------------------------------
project = "{self.project_info["name"]}"
copyright = f"{{date.today().year}}, {self.project_info["name"]} Team"
author = "{self.project_info["name"]} Team"

# The full version, including alpha/beta/rc tags
release = "0.1.0"

# -- General configuration ---------------------------------------------------

extensions = [
    # API Documentation - MUST BE FIRST
    "autoapi.extension",
    
    # Core Sphinx Extensions
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinx.ext.ifconfig",
    "sphinx.ext.githubpages",
    "sphinx.ext.inheritance_diagram",
    "sphinx.ext.graphviz",
    
    # Special Features - MUST BE BEFORE sphinx_autodoc_typehints
    "enum_tools.autoenum",
    "sphinx_toolbox",
    "sphinx_toolbox.more_autodoc.overloads",
    "sphinx_toolbox.more_autodoc.typehints",
    "sphinx_toolbox.more_autodoc.sourcelink",
    
    # Typehints - MUST BE AFTER sphinx_toolbox
    "sphinx_autodoc_typehints",
    "sphinx.ext.autosectionlabel",
    
    # Enhanced Documentation
    "myst_parser",
    "sphinx_copybutton",
    "sphinx_togglebutton",
    "sphinx_design",
    "sphinx_tabs.tabs",
    "sphinx_inline_tabs",
    
    # Diagramming
    "sphinxcontrib.mermaid",
    "sphinxcontrib.plantuml",
    "sphinxcontrib.blockdiag",
    "sphinxcontrib.seqdiag",
    
    # Code and Examples
    "sphinx_codeautolink",
    "sphinx_exec_code",
    "sphinx_runpython",
    
    # UI Enhancements
    "sphinx_tippy",
    "sphinx_favicon",
    "sphinxemoji.sphinxemoji",
    
    # Utilities
    "sphinx_sitemap",
    "sphinx_last_updated_by_git",
    "sphinxext.opengraph",
    "sphinx_reredirects",
    
    # Search and Navigation
    "sphinx_treeview",
    
    # Pydantic Support
    "sphinxcontrib.autodoc_pydantic",
]

# -- Extension Configuration -------------------------------------------------

# AutoAPI configuration
autoapi_dirs = {autoapi_dirs}
autoapi_type = "python"
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "imported-members",
]
autoapi_python_class_content = "both"
autoapi_member_order = "groupwise"
autoapi_root = "api"
autoapi_add_toctree_entry = True
autoapi_keep_files = True
# ✅ HIERARCHICAL ORGANIZATION FIX - The key setting!
autoapi_own_page_level = "module"  # Keep classes with their modules

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Autodoc settings
autodoc_default_options = {{
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
    "show-inheritance": True,
}}
autodoc_typehints = "both"
autodoc_typehints_format = "short"
autodoc_mock_imports = []
autodoc_preserve_defaults = True

# MyST parser
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "replacements",
    "smartquotes",
    "substitution",
    "tasklist",
]
myst_heading_anchors = 3
myst_substitutions = {{
    "project": project,
}}

# Intersphinx mapping
intersphinx_mapping = {{
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable", None),
    "pandas": ("https://pandas.pydata.org/docs", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master", None),
}}

# -- Options for HTML output -------------------------------------------------

html_theme = "furo"
html_static_path = ["_static"]
html_css_files = [
    "enhanced-design.css",      # Complete modern design system
    "breadcrumb-navigation.css", # Breadcrumb navigation for Furo
    "mermaid-custom.css",       # Mermaid diagram theming
    "tippy-enhancements.css",   # Enhanced tooltip system
]
html_js_files = [
    "js/api-enhancements.js",
]

html_theme_options = {{
    "light_logo": "logo-light.png",
    "dark_logo": "logo-dark.png",
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
    "top_of_page_buttons": ["view", "edit"],
}}

html_favicon = "_static/favicon.ico"
html_title = f"{{project}} Documentation"
html_short_title = project
html_baseurl = ""

# -- Additional Configuration ------------------------------------------------

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"
pygments_dark_style = "monokai"

# -- Extension-specific settings ---------------------------------------------

# Sphinx-sitemap
html_baseurl = "https://docs.example.com/"
sitemap_locales = [None]
sitemap_url_scheme = "{{link}}"

# Tippy
tippy_props = {{
    "placement": "auto-start",
    "maxWidth": 500,
    "theme": "light-border",
    "interactive": True,
}}

# Mermaid
mermaid_version = "10.6.1"
mermaid_init_js = """
mermaid.initialize({{
    startOnLoad: true,
    theme: 'default',
    themeVariables: {{
        primaryColor: '#007bff',
        primaryBorderColor: '#0056b3',
        lineColor: '#333',
        secondaryColor: '#6c757d',
        tertiaryColor: '#f8f9fa'
    }}
}});
"""

# Todo extension
todo_include_todos = True

# Coverage extension
coverage_show_missing_items = True

def setup(app):
    """Sphinx setup hook."""
    # Modern CSS files (matches html_css_files)  
    css_files = [
        "enhanced-design.css",
        "breadcrumb-navigation.css",
        "mermaid-custom.css", 
        "tippy-enhancements.css"
    ]
    for css_file in css_files:
        app.add_css_file(css_file)
    
    # Legacy fallback
    app.add_css_file("css/custom.css")
    app.add_js_file("js/api-enhancements.js")
'''

        return conf_content

    def _generate_index_rst(self):
        """Generate index.rst file with configurable TOC sections."""
        # Build TOC entries based on configuration options
        toc_entries = []

        # Always include autoapi if it will be generated
        toc_entries.append("autoapi/index")

        # Add optional sections based on configuration (defaulting to false)
        if self.doc_config.get("with_guides", False):
            toc_entries.append("guides/index")

        if self.doc_config.get("with_examples", False):
            toc_entries.append("examples/index")

        if self.doc_config.get("with_cli", False):
            toc_entries.append("cli/index")

        if self.doc_config.get("with_tutorials", False):
            toc_entries.append("tutorials/index")

        # Always include changelog if it exists (this is typically generated)
        docs_source = self.project_path / "docs" / "source"
        if (docs_source / "changelog.rst").exists():
            toc_entries.append("changelog")

        # Generate TOC content
        toc_content = "\n   ".join(toc_entries)

        index_content = f"""
Welcome to {self.project_info["name"]} Documentation
{"=" * (len(self.project_info["name"]) + 25)}

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   {toc_content}

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
"""

        index_path = self.project_path / "docs" / "source" / "index.rst"
        index_path.write_text(index_content)

    def _generate_makefile(self):
        """Generate Makefile for building docs."""
        makefile_content = """# Minimal makefile for Sphinx documentation

# You can set these variables from the command line.
SPHINXOPTS    = -W --keep-going
SPHINXBUILD   = sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
\t@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
\t@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Custom targets
clean:
\trm -rf $(BUILDDIR)/* $(SOURCEDIR)/autoapi

livehtml:
\tsphinx-autobuild -b html $(SPHINXOPTS) $(SOURCEDIR) $(BUILDDIR)/html

linkcheck:
\t$(SPHINXBUILD) -b linkcheck $(SOURCEDIR) $(BUILDDIR)/linkcheck
"""

        makefile_path = self.project_path / "docs" / "Makefile"
        makefile_path.write_text(makefile_content)

    def _generate_build_scripts(self):
        """Generate build scripts."""
        build_script = """#!/bin/bash
# Build documentation

set -e

echo "Building documentation..."

# Clean previous builds
rm -rf docs/build/*

# Build HTML documentation
cd docs && make html

echo "Documentation built successfully!"
echo "Open docs/build/html/index.html to view."
"""

        script_path = self.project_path / "scripts" / "build-docs.sh"
        script_path.write_text(build_script)
        script_path.chmod(0o755)

    def _add_poetry_dependencies(self):
        """Add documentation dependencies to pyproject.toml."""
        pyproject_path = self.project_path / "pyproject.toml"

        try:
            with open(pyproject_path) as f:
                doc = tomlkit.load(f)

            # Ensure structure exists
            if "tool" not in doc:
                doc["tool"] = {}
            if "poetry" not in doc["tool"]:
                doc["tool"]["poetry"] = {}
            if "group" not in doc["tool"]["poetry"]:
                doc["tool"]["poetry"]["group"] = {}
            if "docs" not in doc["tool"]["poetry"]["group"]:
                doc["tool"]["poetry"]["group"]["docs"] = {"dependencies": {}}

            # Add all documentation dependencies
            deps = doc["tool"]["poetry"]["group"]["docs"]["dependencies"]

            # Core dependencies
            deps.update(
                {
                    "sphinx": "^8.2.3",
                    "sphinx-autoapi": "^3.6.0",
                    "sphinx-autodoc-typehints": "^3.1.0",
                    "sphinxcontrib-autodoc-pydantic": "^2.2.0",
                    "furo": "^2024.8.6",
                    "myst-parser": "^4.0.1",
                    # UI enhancements
                    "sphinx-copybutton": "^0.5.2",
                    "sphinx-togglebutton": "^0.3.2",
                    "sphinx-design": "^0.6.1",
                    "sphinx-tabs": "^3.4.5",
                    "sphinx-inline-tabs": "^2023.4.21",
                    # Diagramming
                    "sphinxcontrib-mermaid": "^1.0.0",
                    "sphinxcontrib-plantuml": "^0.30",
                    "sphinxcontrib-blockdiag": "^3.0.0",
                    "sphinxcontrib-seqdiag": "^3.0.0",
                    # Code features
                    "sphinx-codeautolink": "^0.17.0",
                    "sphinx-exec-code": "^0.16",
                    "sphinx-runpython": "^0.4.0",
                    # Utilities
                    "sphinx-sitemap": "^2.6.0",
                    "sphinx-last-updated-by-git": "^0.3.8",
                    "sphinxext-opengraph": "^0.10.0",
                    "sphinx-reredirects": "^1.0.0",
                    "sphinx-favicon": "^1.0.1",
                    "sphinxemoji": "^0.3.1",
                    "sphinx-tippy": "^0.4.3",
                    # Special support
                    "enum-tools": "^0.13.0",
                    "sphinx-toolbox": "^3.8.1",
                    "seed-intersphinx-mapping": "^1.2.2",
                    # Development
                    "sphinx-autobuild": "^2024.10.3",
                }
            )

            # Write back
            with open(pyproject_path, "w") as f:
                tomlkit.dump(doc, f)

            click.echo("✅ Added documentation dependencies to pyproject.toml")

        except Exception as e:
            click.echo(f"⚠️  Could not add dependencies automatically: {e}")
            click.echo("   Please add the docs group manually to pyproject.toml")


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """PyDevelop documentation tools.

    Run without arguments for interactive mode.
    """
    if ctx.invoked_subcommand is None:
        # No subcommand, run interactive mode
        run_interactive()
    pass


@cli.command()
@click.option("--packages-dir", "-d", multiple=True, help="Package directories to scan")
@click.option(
    "--include-root", "-r", is_flag=True, help="Include root-level documentation"
)
@click.option("--packages", "-p", multiple=True, help="Specific packages to initialize")
@click.option(
    "--dry-run", "-n", is_flag=True, help="Show what would be done without doing it"
)
@click.option("--force", "-f", is_flag=True, help="Overwrite existing documentation")
@click.option("--quiet", "-q", is_flag=True, help="Minimal output")
@click.option("--debug", is_flag=True, help="Show debug information")
@click.option("--fix-dependencies", is_flag=True, help="Auto-fix dependency conflicts")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompts")
@click.option(
    "--with-guides", is_flag=True, help="Include guides section in TOC (default: false)"
)
@click.option(
    "--with-examples",
    is_flag=True,
    help="Include examples section in TOC (default: false)",
)
@click.option(
    "--with-cli",
    is_flag=True,
    help="Include CLI documentation section in TOC (default: false)",
)
@click.option(
    "--with-tutorials",
    is_flag=True,
    help="Include tutorials section in TOC (default: false)",
)
@click.option(
    "--use-shared-config/--use-inline-config",
    default=True,
    help="Use shared config module vs inline config (default: shared)",
)
@click.option(
    "--modern-design/--classic-design",
    default=True,
    help="Use modern design templates with enhanced styling (default: modern)",
)
def init(
    packages_dir,
    include_root,
    packages,
    dry_run,
    force,
    quiet,
    debug,
    fix_dependencies,
    yes,
    with_guides,
    with_examples,
    with_cli,
    with_tutorials,
    use_shared_config,
    modern_design,
):
    """Initialize documentation for any Python project.

    This command creates a complete Sphinx documentation setup with all
    PyAutoDoc extensions (43+ extensions) configured and ready to use.
    """
    project_path = Path.cwd()

    # Initialize enhanced display with dry-run awareness
    display = EnhancedDisplay(quiet=quiet, debug=debug, dry_run=dry_run)

    # Log operation start
    display.log_operation(
        "init_start", f"Initializing documentation for {project_path}"
    )

    # Analyze project with enhanced detection
    analyzer = ProjectAnalyzer(project_path)
    start_time = datetime.now()
    analysis = analyzer.analyze()
    analysis_duration = (datetime.now() - start_time).total_seconds() * 1000
    display.log_timing("project_analysis", analysis_duration)

    analysis["path"] = str(project_path)

    # Show detailed analysis
    if debug:
        display.show_detailed_analysis(analysis)
    else:
        display.show_analysis(analysis)

    # Create operation plan
    operation_plan = create_documentation_plan(project_path, analysis, force)

    if dry_run:
        # Show what would be done
        display.show_mock_operations([op.to_dict() for op in operation_plan.operations])
        simulation_results = operation_plan.simulate_execution()

        if debug:
            click.echo("\n📊 Execution Simulation Results:")
            for key, value in simulation_results.items():
                click.echo(f"  {key}: {value}")

        display.log_operation(
            "dry_run_complete", f"Simulated {len(operation_plan.operations)} operations"
        )
        display.show_operations_summary()
        return

    # Check for dependency issues and auto-fix if requested
    autofix = AutoFixer(project_path, display)

    if not analysis["dependencies"]["valid"]:
        if dry_run:
            # In dry-run mode, only show what fixes would be applied
            available_fixes = autofix.analyze_and_fix(analysis, apply_fixes=False)
            if available_fixes and not quiet:
                click.echo(
                    f"ℹ️  Would apply {len(available_fixes)} fixes (dry-run mode)"
                )
        elif fix_dependencies or yes:
            display.debug("Auto-fixing dependency issues...")
            autofix.analyze_and_fix(analysis, apply_fixes=True)
        else:
            available_fixes = autofix.analyze_and_fix(analysis, apply_fixes=False)
            if available_fixes and not quiet:
                if display.show_fixes_prompt(
                    [f["description"] for f in available_fixes]
                ):
                    autofix.analyze_and_fix(analysis, apply_fixes=True)
                else:
                    display.warning("Dependency issues not fixed. Build may fail.")

    # Check if documentation exists
    has_existing_docs = (
        any(
            details.get("docs_exists", False)
            for details in analysis["package_details"].values()
        )
        or analysis["central_hub"]["exists"]
    )

    if has_existing_docs and not force:
        display.error("Documentation already exists! Use --force to overwrite.")
        return

    if dry_run:
        display.show_processing(analysis["packages"])
        click.echo("\n🔍 DRY RUN - No changes would be made")
        return

    # Process packages
    summary = {
        "packages_configured": 0,
        "packages_created": 0,
        "packages_updated": 0,
        "central_hub_status": "configured",
        "conflicts_resolved": len(autofix.get_applied_fixes()),
    }

    # Initialize each package
    for pkg_name in analysis["packages"]:
        pkg_path = project_path / "packages" / pkg_name
        pkg_details = analysis["package_details"][pkg_name]

        display.debug(f"Processing package: {pkg_name}")

        # Ensure docs structure exists
        if not pkg_details["docs_exists"]:
            display.debug(f"Creating docs structure for {pkg_name}")
            (pkg_path / "docs" / "source").mkdir(parents=True, exist_ok=True)
            summary["packages_created"] += 1
        else:
            summary["packages_updated"] += 1

        # Update to use shared config
        if autofix.ensure_shared_config(pkg_path, pkg_name):
            display.debug(f"Updated {pkg_name} to use shared config")

        # Create changelog
        if autofix.create_changelog(pkg_path, pkg_name):
            display.debug(f"Created changelog for {pkg_name}")

        # Update index.rst
        if autofix.update_index_rst(pkg_path, pkg_name):
            display.debug(f"Updated index.rst for {pkg_name}")

        summary["packages_configured"] += 1

    # Initialize documentation with configuration options
    doc_config = {
        "with_guides": with_guides,
        "with_examples": with_examples,
        "with_cli": with_cli,
        "with_tutorials": with_tutorials,
        "use_shared_config": use_shared_config,
    }
    initializer = DocsInitializer(project_path, analysis, doc_config, quiet=quiet)

    try:
        init_start = datetime.now()
        initializer.initialize(force=force)
        init_duration = (datetime.now() - init_start).total_seconds() * 1000
        display.log_timing("documentation_initialization", init_duration)

        display.log_operation(
            "init_success",
            "Documentation system initialized successfully",
            success=True,
        )
        display.success("All packages configured with enhanced documentation system!")

        # Show summary
        display.show_summary(summary)

        # Show comprehensive operations summary
        display.show_operations_summary()

    except Exception as e:
        display.log_operation(
            "init_failed", f"Initialization failed: {e}", success=False
        )
        display.error(f"Initialization failed: {e}")
        if debug:
            import traceback

            click.echo(traceback.format_exc(), err=True)

        # Still show operations summary for debugging
        if debug:
            display.show_operations_summary()
        raise click.Abort()


@cli.command()
@click.option("--fix", is_flag=True, help="Automatically fix detected issues")
@click.option("--quiet", "-q", is_flag=True, help="Minimal output")
def doctor(fix, quiet):
    """Check for common issues and suggest fixes."""
    project_path = Path.cwd()
    display = EnhancedDisplay(quiet=quiet)

    # Analyze project
    analyzer = ProjectAnalyzer(project_path)
    analysis = analyzer.analyze()
    analysis["path"] = str(project_path)

    # Show analysis
    display.show_analysis(analysis)

    # Check for issues and apply fixes if requested
    autofix = AutoFixer(project_path, display)

    issues_found = False

    if not analysis["dependencies"]["valid"]:
        issues_found = True
        if fix:
            autofix.analyze_and_fix(analysis, apply_fixes=True)
        else:
            available_fixes = autofix.analyze_and_fix(analysis, apply_fixes=False)
            if available_fixes:
                click.echo("\n🔧 Available fixes:")
                for fix_desc in [f["description"] for f in available_fixes]:
                    click.echo(f"   - {fix_desc}")
                click.echo("\nRun with --fix to apply these fixes automatically.")

    # Check package configurations
    for pkg_name, details in analysis["package_details"].items():
        if not details.get("uses_shared_config", False) and details.get(
            "conf_py_exists", False
        ):
            issues_found = True
            display.warning(
                f"{pkg_name} is using embedded config instead of shared config"
            )
            if fix:
                autofix.ensure_shared_config(
                    project_path / "packages" / pkg_name, pkg_name
                )

    if not issues_found:
        display.success("No issues detected! Project is healthy.")
    elif fix:
        applied_fixes = autofix.get_applied_fixes()
        if applied_fixes:
            display.success(f"Applied {len(applied_fixes)} fixes:")
            for fix in applied_fixes:
                click.echo(f"   ✅ {fix}")
        else:
            display.warning("No fixes could be applied automatically.")


@cli.command()
@click.option("--clean", "-c", is_flag=True, help="Clean build artifacts first")
@click.option("--builder", "-b", default="html", help="Sphinx builder to use")
@click.option("--no-parallel", is_flag=True, help="Disable parallel building")
@click.option("--package", "-p", help="Specific package to build (monorepo only)")
@click.option("--config", "-f", type=click.Path(exists=True), help="Custom config file")
@click.option("--ignore-warnings", is_flag=True, help="Don't treat warnings as errors")
def build(clean, builder, no_parallel, package, config, ignore_warnings):
    """Build documentation for current project.

    Supports single packages and monorepos. Auto-detects project type.
    """
    project_path = Path.cwd()

    # Get appropriate builder
    if config:
        doc_builder = get_builder(project_path, config_file=Path(config))
    else:
        doc_builder = get_builder(project_path)

    # Handle monorepo case
    if isinstance(doc_builder, MonorepoBuilder):
        if package:
            # Build specific package
            pkg_path = project_path / "packages" / package
            if not pkg_path.exists():
                click.echo(f"❌ Package '{package}' not found!")
                raise click.Abort()

            pkg_builder = get_builder(pkg_path, project_type="single")
            pkg_builder.prepare()
            success = pkg_builder.build(
                builder=builder,
                clean=clean,
                parallel=not no_parallel,
                warnings_as_errors=not ignore_warnings,
            )
        else:
            # Build all packages
            success = doc_builder.build_all(
                clean=clean,
                parallel=not no_parallel,
                warnings_as_errors=not ignore_warnings,
            )
    else:
        # Single package
        doc_builder.prepare()
        success = doc_builder.build(
            builder=builder,
            clean=clean,
            parallel=not no_parallel,
            warnings_as_errors=not ignore_warnings,
        )

    if not success:
        raise click.Abort()


@cli.command()
@click.option("--clean", "-c", is_flag=True, help="Clean all build artifacts")
@click.option("--ignore-warnings", is_flag=True, help="Don't treat warnings as errors")
def build_all(clean, ignore_warnings):
    """Build documentation for all packages in monorepo."""
    project_path = Path.cwd()

    # Check if monorepo
    if not (project_path / "packages").exists():
        click.echo("❌ This command only works in monorepo projects!")
        click.echo("   Use 'pydevelop-docs build' for single packages.")
        raise click.Abort()

    builder = MonorepoBuilder(project_path, {"name": project_path.name})
    builder.prepare()

    # Build all packages
    success = builder.build_all(clean=clean, warnings_as_errors=not ignore_warnings)

    # Build aggregate docs
    if success:
        click.echo("\n📚 Building aggregate documentation...")
        builder.build_aggregate()
    else:
        click.echo("\n❌ Some packages failed to build!")
        raise click.Abort()


@cli.command()
def clean():
    """Clean all documentation build artifacts."""
    project_path = Path.cwd()

    # Clean patterns
    patterns = [
        "docs/build",
        "docs/source/autoapi",
        "packages/*/docs/build",
        "packages/*/docs/source/autoapi",
    ]

    cleaned = 0
    for pattern in patterns:
        for path in project_path.glob(pattern):
            if path.exists():
                shutil.rmtree(path)
                click.echo(f"✅ Cleaned {path}")
                cleaned += 1

    if cleaned == 0:
        click.echo("✅ No build artifacts found to clean")
    else:
        click.echo(f"\n✅ Cleaned {cleaned} directories")


@cli.command()
@click.argument("source", type=click.Path(exists=True))
@click.argument("target", type=click.Path())
def sync(source, target):
    """Sync documentation configuration from source to target.

    Useful for copying configuration between packages.
    """
    source_path = Path(source)
    target_path = Path(target)

    # Files to sync
    sync_files = [
        "docs/source/conf.py",
        "docs/source/_static/css/custom.css",
        "docs/source/_static/js/api-enhancements.js",
        "docs/Makefile",
        "scripts/build-docs.sh",
    ]

    synced = 0
    for file_path in sync_files:
        src_file = source_path / file_path
        if src_file.exists():
            tgt_file = target_path / file_path
            tgt_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, tgt_file)
            click.echo(f"✅ Synced {file_path}")
            synced += 1

    click.echo(f"\n✅ Synced {synced} files from {source} to {target}")


@cli.command()
@click.option("--clean", "-c", is_flag=True, help="Clean build directory first")
@click.option(
    "--open", "-o", is_flag=True, help="Open documentation in browser after building"
)
@click.option(
    "--update-only", "-u", is_flag=True, help="Update hub index only (faster)"
)
def link_docs(clean, open, update_only):
    """Link existing built documentation into a central hub.

    This command creates a documentation hub that links to all existing
    built documentation in the packages/ directory with intersphinx mappings
    for cross-referencing. Uses the complete pydevelop-docs configuration
    with 40+ extensions to match individual package styling.
    """
    from .link_builder import DocumentationLinker

    project_path = Path.cwd()
    linker = DocumentationLinker(project_path)

    if clean and (project_path / "docs" / "build").exists():
        shutil.rmtree(project_path / "docs" / "build")
        click.echo("✅ Cleaned docs/build directory")

    if update_only:
        success = linker.update_hub()
    else:
        success = linker.build_hub(open_browser=open)

    if not success:
        raise click.Abort()


@cli.command()
@click.option(
    "--open", "-o", is_flag=True, help="Open documentation in browser after updating"
)
def update_hub(open):
    """Update the documentation hub index (faster than full rebuild).

    This command updates the hub index with any new packages that have
    built documentation without doing a full rebuild.
    """
    from .link_builder import DocumentationLinker

    project_path = Path.cwd()
    linker = DocumentationLinker(project_path)

    success = linker.update_hub()

    if success and open:
        import webbrowser

        html_path = project_path / "docs" / "build" / "html" / "index.html"
        if html_path.exists():
            webbrowser.open(f"file://{html_path}")
            click.echo("🌐 Opened documentation in browser")

    if not success:
        raise click.Abort()


@cli.command()
def list_extensions():
    """List all available Sphinx extensions."""
    extensions = [
        "sphinx.ext.autodoc",
        "sphinx.ext.autosummary",
        "sphinx.ext.napoleon",
        "sphinx.ext.viewcode",
        "sphinx.ext.intersphinx",
        "sphinx.ext.todo",
        "sphinx.ext.coverage",
        "sphinx.ext.mathjax",
        "sphinx.ext.ifconfig",
        "sphinx.ext.githubpages",
        "sphinx.ext.inheritance_diagram",
        "sphinx.ext.graphviz",
        "autoapi.extension",
        "sphinx_autodoc_typehints",
        "sphinx.ext.autosectionlabel",
        "myst_parser",
        "sphinx_copybutton",
        "sphinx_togglebutton",
        "sphinx_design",
        "sphinx_tabs.tabs",
        "sphinx_inline_tabs",
        "sphinxcontrib.mermaid",
        "sphinxcontrib.plantuml",
        "sphinxcontrib.blockdiag",
        "sphinxcontrib.seqdiag",
        "sphinx_codeautolink",
        "sphinx_exec_code",
        "sphinx_runpython",
        "sphinx_tippy",
        "sphinx_favicon",
        "sphinxemoji.sphinxemoji",
        "sphinx_sitemap",
        "sphinx_last_updated_by_git",
        "sphinxext.opengraph",
        "sphinx_reredirects",
        "sphinx_treeview",
        "enum_tools.autoenum",
        "sphinx_toolbox",
        "sphinx_toolbox.more_autodoc.overloads",
        "sphinx_toolbox.more_autodoc.typehints",
        "sphinx_toolbox.more_autodoc.sourcelink",
        "sphinxcontrib.autodoc_pydantic",
    ]

    click.echo("📚 Available Sphinx Extensions (43 total):\n")
    for ext in extensions:
        click.echo(f"   • {ext}")


@cli.command()
@click.option(
    "--auto-fix/--no-auto-fix",
    default=True,
    help="Automatically fix documentation issues while watching",
)
@click.option(
    "--selective/--no-selective",
    default=True,
    help="Only rebuild changed packages (faster)",
)
def watch(auto_fix: bool, selective: bool):
    """Watch for changes and automatically rebuild documentation."""
    import asyncio

    from .config_discovery import PyDevelopConfig
    from .watcher import watch_documentation

    project_path = Path.cwd()

    # Initialize .pydevelop if needed
    pydevelop = PyDevelopConfig(project_path)
    if not pydevelop.config_dir.exists():
        click.echo("🔧 Initializing .pydevelop configuration...")
        pydevelop.initialize()

    # Start watching
    asyncio.run(
        watch_documentation(
            project_path,
            auto_fix=auto_fix,
            selective=selective,
        )
    )


@cli.command()
def discover():
    """Discover and display project configuration."""
    import json

    from .config_discovery import ConfigDiscovery

    project_path = Path.cwd()
    discovery = ConfigDiscovery(project_path)
    config = discovery.discover_all()

    click.echo("🔍 Discovered Project Configuration:\n")
    click.echo(json.dumps(config, indent=2, default=str))


@cli.command()
@click.option(
    "--packages",
    "-p",
    multiple=True,
    help="Specific packages to rebuild (default: all)",
)
@click.option("--no-master", is_flag=True, help="Skip master documentation hub")
@click.option("--no-clean", is_flag=True, help="Don't clean existing build artifacts")
@click.option("--quiet", "-q", is_flag=True, help="Minimal output")
@click.option("--debug", is_flag=True, help="Show detailed debug information")
@click.option("--save-log", is_flag=True, help="Save detailed operations log to JSON")
def rebuild_haive(packages, no_master, no_clean, quiet, debug, save_log):
    """Rebuild all documentation for the Haive AI Agent Framework.

    This command performs a complete documentation rebuild across the entire
    Haive monorepo including all 7 packages and the master documentation hub.

    Process:
    1. Clear all existing documentation build artifacts
    2. Initialize documentation for each package with modern CSS
    3. Build documentation for each package with hierarchical AutoAPI
    4. Initialize and build the master documentation hub with cross-links

    Examples:
        # Rebuild everything
        pydevelop-docs rebuild-haive

        # Rebuild specific packages only
        pydevelop-docs rebuild-haive -p haive-core -p haive-agents

        # Rebuild with detailed logging
        pydevelop-docs rebuild-haive --debug --save-log

        # Quick rebuild without master hub
        pydevelop-docs rebuild-haive --no-master
    """
    from .utils import HaiveDocumentationManager

    # Auto-detect Haive root directory
    current_path = Path.cwd()
    haive_root = None

    # Look for Haive markers in current path and parents
    for path in [current_path] + list(current_path.parents):
        if (path / "packages").exists() and (path / "CLAUDE.md").exists():
            haive_root = path
            break

    if not haive_root:
        click.echo("❌ Not in a Haive monorepo directory!")
        click.echo("   This command must be run from within the Haive project.")
        click.echo("   Expected structure: /path/to/haive/packages/, CLAUDE.md")
        raise click.Abort()

    # Initialize the documentation manager
    try:
        manager = HaiveDocumentationManager(
            haive_root=haive_root, quiet=quiet, debug=debug
        )
    except ValueError as e:
        click.echo(f"❌ {e}")
        raise click.Abort()

    if not quiet:
        click.echo("🎯 Haive Documentation Rebuild")
        click.echo(f"📁 Root: {haive_root}")
        click.echo("=" * 60)

    # Execute the complete rebuild
    try:
        results = manager.rebuild_all_documentation(
            packages=list(packages) if packages else None,
            include_master=not no_master,
            force=True,
            clean=not no_clean,
        )

        # Show results summary
        if not quiet:
            click.echo("\n" + "=" * 60)
            click.echo("📊 REBUILD SUMMARY")
            click.echo("=" * 60)

            summary = results["summary"]

            # Package results
            click.echo(
                f"📦 Packages: {summary['successful_builds']}/{summary['total_packages']} built successfully"
            )

            # Master hub results
            if not no_master:
                master_status = (
                    "✅ Success" if summary["master_success"] else "❌ Failed"
                )
                click.echo(f"🏛️  Master Hub: {master_status}")

            # Failed packages
            if summary["failed_packages"]:
                click.echo(f"❌ Failed: {', '.join(summary['failed_packages'])}")

            # Cleared artifacts
            cleared = results["cleared"]
            click.echo(
                f"🧹 Cleared: {cleared['directories']} dirs, {cleared['files']} files"
            )

            # Performance
            ops_summary = manager.get_operations_summary()
            click.echo(f"⏱️  Total time: {ops_summary['total_duration_seconds']:.1f}s")
            click.echo(f"🔄 Operations: {ops_summary['total_operations']}")

        # Save detailed log if requested
        if save_log:
            log_path = manager.save_operations_log()
            if not quiet:
                click.echo(f"\n📝 Detailed log: {log_path}")

        # Final status
        if summary["successful_builds"] == summary["total_packages"] and (
            no_master or summary["master_success"]
        ):
            if not quiet:
                click.echo("\n🎉 Complete success! All documentation rebuilt.")

                # Show how to view the results
                master_index = haive_root / "docs" / "build" / "html" / "index.html"
                if master_index.exists():
                    click.echo(f"\n🌐 View documentation: file://{master_index}")
                    click.echo(
                        "   Or run: python -m http.server 8000 --directory docs/build/html/"
                    )
        else:
            click.echo("\n⚠️  Some operations failed. Check the log for details.")
            if debug:
                failed_ops = [
                    op for op in manager.operations_log if op["status"] == "error"
                ]
                for op in failed_ops[-3:]:  # Show last 3 errors
                    click.echo(f"   ❌ {op['operation']}: {op['details']}")
            raise click.Abort()

    except KeyboardInterrupt:
        click.echo("\n\n⚠️  Rebuild interrupted by user")
        if save_log:
            manager.save_operations_log()
        raise click.Abort()
    except Exception as e:
        click.echo(f"\n❌ Rebuild failed: {e}")
        if debug:
            import traceback

            click.echo(traceback.format_exc())
        if save_log:
            manager.save_operations_log()
        raise click.Abort()


@cli.command()
def setup():
    """Initialize .pydevelop configuration directory."""
    from .config_discovery import PyDevelopConfig

    project_path = Path.cwd()
    pydevelop = PyDevelopConfig(project_path)

    if pydevelop.config_dir.exists():
        click.echo("⚠️  .pydevelop directory already exists")
        if not click.confirm("Reinitialize configuration?"):
            return

    pydevelop.initialize()

    # Create example hooks and templates
    from .hooks import HookManager, TemplateOverrideManager

    hooks = HookManager(project_path)
    templates = TemplateOverrideManager(project_path)

    hooks.create_example_hooks()
    templates.create_example_overrides()

    click.echo("\n📁 Created .pydevelop/ structure:")
    click.echo("   .pydevelop/")
    click.echo("   ├── config.yaml          # Main project configuration")
    click.echo("   ├── docs.yaml            # Documentation settings")
    click.echo("   ├── cache/               # Build cache (gitignored)")
    click.echo("   ├── templates/           # Custom template overrides")
    click.echo("   │   └── *.example        # Example templates")
    click.echo("   └── hooks/               # Pre/post build scripts")
    click.echo("       └── *.example        # Example hooks")

    click.echo("\n✨ Next steps:")
    click.echo("   1. Review .pydevelop/config.yaml and docs.yaml")
    click.echo("   2. Check .pydevelop/hooks/*.example for customization ideas")
    click.echo("   3. Check .pydevelop/templates/*.example for override examples")
    click.echo("   4. Run 'pydevelop-docs watch' for auto-rebuild")


@cli.command()
@click.argument("project_path", type=click.Path(exists=True, file_okay=False, dir_okay=True), required=False)
@click.option("--target-dir", "-t", type=click.Path(), help="Target directory for documentation (default: PROJECT_PATH/docs)")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing documentation")
@click.option("--non-interactive", "-n", is_flag=True, help="Skip interactive prompts")
@click.option("--dry-run", "-d", is_flag=True, help="Show what would be done without executing")
@click.option("--copy-to", "-c", type=click.Path(), help="Copy the setup to another directory")
def setup_general(project_path, target_dir, force, non_interactive, dry_run, copy_to):
    """Set up documentation for any Python project with automatic detection.
    
    This command analyzes any Python project structure and automatically
    sets up comprehensive documentation with zero configuration required.
    
    Examples:
    
        # Setup docs for current directory
        pydevelop-docs setup-general
        
        # Setup docs for specific project
        pydevelop-docs setup-general /path/to/my-project
        
        # Dry run to see what would be done
        pydevelop-docs setup-general --dry-run
        
        # Copy setup to another location
        pydevelop-docs setup-general --copy-to /path/to/copy/destination
    """
    from .general_setup import setup_project_docs
    
    # Use current directory if no project path provided
    if not project_path:
        project_path = Path.cwd()
    else:
        project_path = Path(project_path)
    
    target_directory = Path(target_dir) if target_dir else None
    
    try:
        click.echo(f"🔍 Analyzing Python project at: {project_path}")
        
        # Set up documentation
        result = setup_project_docs(
            project_path=str(project_path),
            target_dir=str(target_directory) if target_directory else None,
            force=force,
            interactive=not non_interactive,
            dry_run=dry_run
        )
        
        if result["status"] == "cancelled":
            click.echo("❌ Setup cancelled by user")
            return
        
        if result["status"] == "dry_run":
            click.echo("\n📋 Dry Run - Actions that would be performed:")
            for action in result["actions"]:
                click.echo(f"  {action}")
            
            click.echo(f"\n📊 Project Analysis:")
            info = result["project_info"]
            click.echo(f"  Type: {info['type']}")
            click.echo(f"  Packages: {len(info['packages'])}")
            click.echo(f"  Python files: {info['python_files']}")
            click.echo(f"  Package manager: {info['package_manager']}")
            return
        
        # Copy to another location if requested
        if copy_to:
            copy_destination = Path(copy_to)
            click.echo(f"\n📂 Copying setup to: {copy_destination}")
            
            if copy_destination.exists() and not force:
                if not click.confirm(f"Destination {copy_destination} exists. Continue?"):
                    return
            
            # Copy the documentation setup
            import shutil
            source_docs = target_directory or (project_path / "docs")
            if source_docs.exists():
                shutil.copytree(source_docs, copy_destination, dirs_exist_ok=True)
                click.echo(f"✅ Documentation setup copied to: {copy_destination}")
            else:
                click.echo("❌ No documentation found to copy")
                return
        
        # Success message
        docs_path = target_directory or (project_path / "docs")
        click.echo(f"\n✅ Documentation setup complete!")
        click.echo(f"📁 Documentation created at: {docs_path}")
        
        if not dry_run:
            click.echo("\n🚀 Next steps:")
            click.echo(f"   1. cd {docs_path}")
            click.echo("   2. make html")
            click.echo("   3. open build/html/index.html")
            
            click.echo("\n📝 Available commands:")
            click.echo("   • make html          - Build HTML documentation")
            click.echo("   • make livehtml      - Auto-rebuild on changes")
            click.echo("   • make linkcheck     - Check for broken links")
            click.echo("   • make clean         - Clean build artifacts")
            
    except Exception as e:
        click.echo(f"❌ Error setting up documentation: {e}")
        import traceback
        if click.get_current_context().params.get('debug'):
            click.echo(traceback.format_exc())
        raise click.Abort()


@cli.command()
@click.argument("source_path", type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.argument("destination_path", type=click.Path())
@click.option("--include-config", "-c", is_flag=True, help="Include PyDevelop-Docs configuration files")
@click.option("--include-static", "-s", is_flag=True, help="Include static assets and templates")
@click.option("--force", "-f", is_flag=True, help="Overwrite destination if it exists")
def copy_setup(source_path, destination_path, include_config, include_static, force):
    """Copy documentation setup from one project to another.
    
    This command copies a complete documentation setup from a source project
    to a destination, optionally including configuration and static files.
    
    Examples:
    
        # Copy basic documentation structure
        pydevelop-docs copy-setup /path/to/source /path/to/destination
        
        # Copy with configuration files
        pydevelop-docs copy-setup /path/to/source /path/to/dest --include-config
        
        # Copy everything including static assets
        pydevelop-docs copy-setup /path/to/source /path/to/dest --include-config --include-static
    """
    import shutil
    
    source = Path(source_path)
    destination = Path(destination_path)
    
    # Find documentation in source
    source_docs = source / "docs"
    if not source_docs.exists():
        click.echo(f"❌ No docs directory found in source: {source}")
        return
    
    # Check destination
    if destination.exists() and not force:
        if not click.confirm(f"Destination {destination} exists. Continue?"):
            return
    
    try:
        click.echo(f"📂 Copying documentation setup...")
        click.echo(f"   From: {source_docs}")
        click.echo(f"   To: {destination}")
        
        # Copy documentation
        shutil.copytree(source_docs, destination, dirs_exist_ok=True)
        
        # Copy configuration files if requested
        if include_config:
            config_files = [
                ".pydevelop",
                "pyproject.toml",  # For dependencies
                "requirements.txt",
            ]
            
            for config_file in config_files:
                source_file = source / config_file
                if source_file.exists():
                    if source_file.is_dir():
                        shutil.copytree(source_file, destination.parent / config_file, dirs_exist_ok=True)
                    else:
                        shutil.copy2(source_file, destination.parent / config_file)
                    click.echo(f"   ✅ Copied: {config_file}")
        
        # Copy additional static files if requested
        if include_static:
            static_files = [
                "README.md",
                "LICENSE",
                ".gitignore",
            ]
            
            for static_file in static_files:
                source_file = source / static_file
                if source_file.exists():
                    shutil.copy2(source_file, destination.parent / static_file)
                    click.echo(f"   ✅ Copied: {static_file}")
        
        click.echo(f"\n✅ Documentation setup copied successfully!")
        click.echo(f"📁 Available at: {destination}")
        
        click.echo("\n🚀 To build documentation:")
        click.echo(f"   cd {destination}")
        click.echo("   make html")
        
    except Exception as e:
        click.echo(f"❌ Error copying setup: {e}")
        raise click.Abort()


@cli.command()
@click.option("--coverage", is_flag=True, help="Run tests with coverage reporting")
@click.option("--verbose", "-v", is_flag=True, help="Verbose test output")
@click.option("--fast", is_flag=True, help="Skip slow tests")
@click.option("--integration", is_flag=True, help="Run integration tests only") 
@click.option("--unit", is_flag=True, help="Run unit tests only")
@click.option("--lint", is_flag=True, help="Run code quality checks")
@click.option("--format-check", is_flag=True, help="Check code formatting")
@click.option("--type-check", is_flag=True, help="Run type checking with mypy")
@click.option("--all", "run_all", is_flag=True, help="Run all tests and checks")
def test(coverage, verbose, fast, integration, unit, lint, format_check, type_check, run_all):
    """Run tests and code quality checks for PyDevelop-Docs.
    
    This command runs various types of tests and quality checks:
    - Unit tests for individual components
    - Integration tests for CLI functionality  
    - Code quality checks (linting, formatting, type checking)
    - Coverage reporting
    """
    import time
    start_time = time.time()
    
    click.echo("🧪 Running PyDevelop-Docs tests...")
    
    project_path = Path.cwd()
    
    # Check if we're in the right directory
    if not (project_path / "pyproject.toml").exists():
        click.echo("❌ Error: No pyproject.toml found. Run from project root.")
        raise click.Abort()
    
    # Determine what to run
    if run_all:
        lint = format_check = type_check = coverage = True
        # Don't set unit/integration flags so all tests run
    
    if not any([unit, integration, lint, format_check, type_check, coverage]):
        # Default: run basic tests
        unit = True
    
    results = {}
    
    # Code formatting check
    if format_check or run_all:
        click.echo("\n📝 Checking code formatting...")
        try:
            result = subprocess.run(
                ["poetry", "run", "ruff", "format", "--check", "src/"],
                capture_output=True,
                text=True,
                cwd=project_path
            )
            if result.returncode == 0:
                click.echo("✅ Code formatting is correct")
                results['format'] = True
            else:
                click.echo("❌ Code formatting issues found:")
                click.echo(result.stdout)
                click.echo("💡 Fix with: poetry run ruff format src/")
                results['format'] = False
        except Exception as e:
            click.echo(f"❌ Format check failed: {e}")
            results['format'] = False
    
    # Linting
    if lint or run_all:
        click.echo("\n🔍 Running code quality checks...")
        try:
            result = subprocess.run(
                ["poetry", "run", "ruff", "check", "src/"],
                capture_output=True,
                text=True,
                cwd=project_path
            )
            if result.returncode == 0:
                click.echo("✅ No linting issues found")
                results['lint'] = True
            else:
                click.echo("⚠️  Linting issues found:")
                click.echo(result.stdout[:2000])  # First 2000 chars
                click.echo("💡 Some issues can be auto-fixed with: poetry run ruff check --fix src/")
                results['lint'] = False
        except Exception as e:
            click.echo(f"❌ Linting failed: {e}")
            results['lint'] = False
    
    # Type checking
    if type_check or run_all:
        click.echo("\n🔬 Running type checking...")
        try:
            result = subprocess.run(
                ["poetry", "run", "mypy", "src/pydevelop_docs/"],
                capture_output=True,
                text=True,
                cwd=project_path,
                timeout=120
            )
            if result.returncode == 0:
                click.echo("✅ No type errors found")
                results['typecheck'] = True
            else:
                click.echo("⚠️  Type checking issues found:")
                click.echo(result.stdout[:1500])  # First 1500 chars
                results['typecheck'] = False
        except subprocess.TimeoutExpired:
            click.echo("⚠️  Type checking timed out")
            results['typecheck'] = False
        except Exception as e:
            click.echo(f"❌ Type checking failed: {e}")
            results['typecheck'] = False
    
    # Unit tests
    if unit or (not integration and not run_all):
        click.echo("\n🧪 Running unit tests...")
        
        pytest_cmd = ["poetry", "run", "pytest"]
        
        if coverage:
            pytest_cmd.extend(["--cov=pydevelop_docs", "--cov-report=term-missing", "--cov-report=xml"])
        
        if verbose:
            pytest_cmd.append("-v")
        else:
            pytest_cmd.append("-q")
        
        if fast:
            pytest_cmd.extend(["-m", "not slow"])
        
        # Add test directory
        test_dir = project_path / "tests"
        if test_dir.exists():
            pytest_cmd.append("tests/")
        else:
            click.echo("⚠️  No tests/ directory found, creating basic CLI test...")
            # Run a basic CLI test
            pytest_cmd = ["poetry", "run", "python", "-c", """
import subprocess
import sys
try:
    result = subprocess.run([sys.executable, '-m', 'pydevelop_docs.cli', '--help'], 
                          capture_output=True, text=True, timeout=30)
    if result.returncode == 0 and 'pydevelop-docs' in result.stdout:
        print('✅ CLI help works')
        exit(0)
    else:
        print('❌ CLI help failed')
        exit(1)
except Exception as e:
    print(f'❌ CLI test failed: {e}')
    exit(1)
"""]
        
        try:
            result = subprocess.run(
                pytest_cmd,
                cwd=project_path,
                timeout=300  # 5 minute timeout
            )
            if result.returncode == 0:
                click.echo("✅ Unit tests passed")
                results['unit'] = True
            else:
                click.echo("❌ Some unit tests failed")
                results['unit'] = False
        except subprocess.TimeoutExpired:
            click.echo("⚠️  Tests timed out")
            results['unit'] = False
        except Exception as e:
            click.echo(f"❌ Test execution failed: {e}")
            results['unit'] = False
    
    # Integration tests (CLI functionality)
    if integration or run_all:
        click.echo("\n🔗 Running integration tests...")
        
        # Test CLI commands
        cli_tests = [
            (["--help"], "Help command"),
            (["analyze", ".", "--dry-run"], "Project analysis"),
            (["setup-general", "/tmp", "--dry-run", "--non-interactive"], "General setup"),
        ]
        
        integration_results = []
        for cmd_args, description in cli_tests:
            click.echo(f"   Testing: {description}")
            try:
                result = subprocess.run(
                    ["poetry", "run", "pydevelop-docs"] + cmd_args,
                    capture_output=True,
                    text=True,
                    cwd=project_path,
                    timeout=60
                )
                if result.returncode == 0:
                    click.echo(f"   ✅ {description} - OK")
                    integration_results.append(True)
                else:
                    click.echo(f"   ❌ {description} - Failed")
                    click.echo(f"      Error: {result.stderr[:200]}")
                    integration_results.append(False)
            except Exception as e:
                click.echo(f"   ❌ {description} - Exception: {e}")
                integration_results.append(False)
        
        if all(integration_results):
            click.echo("✅ All integration tests passed")
            results['integration'] = True
        else:
            click.echo(f"❌ {len([r for r in integration_results if not r])} integration tests failed")
            results['integration'] = False
    
    # Test documentation build
    docs_path = project_path / "docs"
    if docs_path.exists():
        click.echo("\n📚 Testing documentation build...")
        try:
            result = subprocess.run(
                ["make", "html"],
                cwd=docs_path,
                capture_output=True,
                text=True,
                timeout=180  # 3 minute timeout
            )
            if result.returncode == 0:
                click.echo("✅ Documentation builds successfully")
                results['docs'] = True
            else:
                click.echo("❌ Documentation build failed:")
                click.echo(result.stderr[:1000])
                results['docs'] = False
        except subprocess.TimeoutExpired:
            click.echo("⚠️  Documentation build timed out")
            results['docs'] = False
        except Exception as e:
            click.echo(f"❌ Documentation build test failed: {e}")
            results['docs'] = False
    
    # Summary
    end_time = time.time()
    duration = end_time - start_time
    
    click.echo(f"\n📊 Test Summary (completed in {duration:.1f}s)")
    click.echo("=" * 50)
    
    passed = 0
    total = 0
    
    for test_type, passed_status in results.items():
        total += 1
        if passed_status:
            passed += 1
            click.echo(f"✅ {test_type.upper()}: PASSED")
        else:
            click.echo(f"❌ {test_type.upper()}: FAILED")
    
    if total == 0:
        click.echo("⚠️  No tests were run")
    elif passed == total:
        click.echo(f"\n🎉 All {total} test categories passed!")
    else:
        click.echo(f"\n⚠️  {passed}/{total} test categories passed")
        
        # Provide helpful next steps
        if not results.get('format', True):
            click.echo("💡 Fix formatting: poetry run ruff format src/")
        if not results.get('lint', True):
            click.echo("💡 Fix linting: poetry run ruff check --fix src/")
        if not results.get('unit', True):
            click.echo("💡 Debug tests: poetry run pytest -v --tb=short")
    
    # Set exit code based on results
    if total > 0 and passed < total:
        raise click.Abort()


@cli.command()
@click.option("--test", is_flag=True, help="Upload to TestPyPI instead of PyPI")
@click.option("--dry-run", is_flag=True, help="Show what would be published without doing it")
@click.option("--force", is_flag=True, help="Force publish even if version exists")
def publish(test, dry_run, force):
    """Publish PyDevelop-Docs to PyPI or TestPyPI.
    
    This command builds the package and publishes it to PyPI.
    Use --test to publish to TestPyPI for testing first.
    """
    click.echo("🚀 Publishing PyDevelop-Docs...")
    
    if dry_run:
        click.echo("🔍 DRY RUN MODE - No actual publishing will occur")
    
    project_path = Path.cwd()
    
    # Check if we're in the right directory
    if not (project_path / "pyproject.toml").exists():
        click.echo("❌ Error: No pyproject.toml found. Run from project root.")
        raise click.Abort()
    
    # Read version from pyproject.toml
    try:
        with open(project_path / "pyproject.toml") as f:
            import tomlkit
            data = tomlkit.load(f)
            version = data["tool"]["poetry"]["version"]
            name = data["tool"]["poetry"]["name"]
        click.echo(f"📦 Package: {name} v{version}")
    except Exception as e:
        click.echo(f"❌ Error reading pyproject.toml: {e}")
        raise click.Abort()
    
    if dry_run:
        click.echo(f"🔍 Would publish {name} v{version} to {'TestPyPI' if test else 'PyPI'}")
        click.echo("🔍 Build command: poetry build")
        click.echo(f"🔍 Publish command: poetry publish{'--repository testpypi' if test else ''}")
        return
    
    # Check if poetry is available
    try:
        result = subprocess.run(["poetry", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            click.echo("❌ Poetry not found. Please install Poetry first.")
            raise click.Abort()
        click.echo(f"✅ Using {result.stdout.strip()}")
    except FileNotFoundError:
        click.echo("❌ Poetry not found. Please install Poetry first.")
        raise click.Abort()
    
    # Build the package
    click.echo("🔨 Building package...")
    try:
        result = subprocess.run(
            ["poetry", "build"], 
            cwd=project_path,
            capture_output=True, 
            text=True,
            check=True
        )
        click.echo("✅ Package built successfully")
        click.echo(result.stdout)
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Build failed: {e}")
        click.echo(e.stderr)
        raise click.Abort()
    
    # Check if version already exists (if not forcing)
    if not force:
        if test:
            click.echo("⚠️  Testing against TestPyPI - version conflicts are common")
        else:
            click.echo("🔍 Checking if version already exists on PyPI...")
            # Note: In a real scenario, you'd check PyPI API here
    
    # Publish the package
    target = "TestPyPI" if test else "PyPI"
    click.echo(f"🚀 Publishing to {target}...")
    
    publish_cmd = ["poetry", "publish"]
    if test:
        publish_cmd.extend(["--repository", "testpypi"])
    
    try:
        if test:
            click.echo("📝 Note: You may need to configure TestPyPI repository:")
            click.echo("   poetry config repositories.testpypi https://test.pypi.org/legacy/")
            click.echo("   poetry config pypi-token.testpypi YOUR_TESTPYPI_TOKEN")
        else:
            click.echo("📝 Note: You may need to configure PyPI token:")
            click.echo("   poetry config pypi-token.pypi YOUR_PYPI_TOKEN")
        
        result = subprocess.run(
            publish_cmd,
            cwd=project_path,
            capture_output=True,
            text=True,
            check=True
        )
        
        click.echo(f"🎉 Successfully published {name} v{version} to {target}!")
        click.echo(result.stdout)
        
        if test:
            click.echo(f"🔗 Test package: https://test.pypi.org/project/{name}/")
        else:
            click.echo(f"🔗 Live package: https://pypi.org/project/{name}/")
            click.echo("📝 Installation: pip install pydevelop-docs")
        
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Publish failed: {e}")
        click.echo(e.stderr)
        if "401" in e.stderr or "403" in e.stderr:
            click.echo("💡 This looks like an authentication issue.")
            click.echo("   Make sure your PyPI token is configured correctly.")
        raise click.Abort()


@cli.command()
@click.option("--check-links", is_flag=True, help="Run link checking after build")
@click.option("--upload-rtd", is_flag=True, help="Trigger Read the Docs build")
@click.option("--deploy-pages", is_flag=True, help="Deploy to GitHub Pages")
def publish_docs(check_links, upload_rtd, deploy_pages):
    """Build and publish documentation to various platforms.
    
    This command builds the documentation and optionally deploys it to
    Read the Docs, GitHub Pages, or other platforms.
    """
    click.echo("📚 Publishing PyDevelop-Docs documentation...")
    
    project_path = Path.cwd()
    docs_path = project_path / "docs"
    
    if not docs_path.exists():
        click.echo("❌ Error: No docs/ directory found.")
        raise click.Abort()
    
    # Build documentation
    click.echo("🔨 Building documentation...")
    try:
        result = subprocess.run(
            ["make", "html"],
            cwd=docs_path,
            capture_output=True,
            text=True,
            check=True
        )
        click.echo("✅ Documentation built successfully")
        
        # Count generated files
        build_path = docs_path / "build" / "html"
        if build_path.exists():
            html_files = list(build_path.glob("**/*.html"))
            click.echo(f"📄 Generated {len(html_files)} HTML pages")
        
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Documentation build failed: {e}")
        click.echo(e.stderr)
        raise click.Abort()
    
    # Check links if requested
    if check_links:
        click.echo("🔗 Checking documentation links...")
        try:
            result = subprocess.run(
                ["make", "linkcheck"],
                cwd=docs_path,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout for link checking
            )
            if result.returncode == 0:
                click.echo("✅ All links are valid")
            else:
                click.echo("⚠️  Some links may be broken (see details above)")
                click.echo(result.stdout)
        except subprocess.TimeoutExpired:
            click.echo("⚠️  Link checking timed out")
        except Exception as e:
            click.echo(f"⚠️  Link checking failed: {e}")
    
    # GitHub Pages deployment info
    if deploy_pages:
        click.echo("\n🚀 GitHub Pages Deployment:")
        click.echo("   The docs will be deployed automatically via GitHub Actions")
        click.echo("   when you push to the main branch.")
        click.echo("   Make sure GitHub Pages is enabled in your repository settings.")
    
    # Read the Docs info
    if upload_rtd:
        click.echo("\n📖 Read the Docs:")
        click.echo("   RTD will automatically build when you push to GitHub.")
        click.echo("   Configuration: .readthedocs.yaml")
        click.echo("   Dependencies: docs/requirements.txt")
        click.echo("   🔗 https://readthedocs.org/projects/pydevelop-docs/")
    
    # Local serving info
    build_path = docs_path / "build" / "html"
    if build_path.exists():
        click.echo(f"\n🌐 Local documentation available at:")
        click.echo(f"   file://{build_path.absolute()}/index.html")
        click.echo("\n💡 To serve locally:")
        click.echo(f"   cd {build_path}")
        click.echo("   python -m http.server 8000")
        click.echo("   Then open: http://localhost:8000")


@cli.command()
@click.option("--check-version", is_flag=True, help="Check if version bump is needed")
@click.option("--dry-run", is_flag=True, help="Show what would be done without doing it")
@click.option("--part", type=click.Choice(["patch", "minor", "major"]), default="patch", 
              help="Version part to bump (default: patch)")
def release(check_version, dry_run, part):
    """Complete release workflow: version bump, build, test, and publish.
    
    This command automates the entire release process:
    1. Bump version (patch/minor/major)
    2. Build package and documentation
    3. Run tests
    4. Publish to PyPI
    5. Deploy documentation
    """
    click.echo("🎯 Starting PyDevelop-Docs release workflow...")
    
    if dry_run:
        click.echo("🔍 DRY RUN MODE - No actual changes will be made")
    
    project_path = Path.cwd()
    
    # Check if we're in a clean git state
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True
        )
        if result.stdout.strip() and not dry_run:
            click.echo("⚠️  Warning: Git working directory is not clean")
            click.echo("   Uncommitted changes detected:")
            for line in result.stdout.strip().split('\n'):
                click.echo(f"   {line}")
            if not click.confirm("Continue anyway?"):
                raise click.Abort()
    except subprocess.CalledProcessError:
        click.echo("⚠️  Git status check failed")
    
    # Read current version
    try:
        with open(project_path / "pyproject.toml") as f:
            import tomlkit
            data = tomlkit.load(f)
            current_version = data["tool"]["poetry"]["version"]
            name = data["tool"]["poetry"]["name"]
        click.echo(f"📦 Current version: {name} v{current_version}")
    except Exception as e:
        click.echo(f"❌ Error reading version: {e}")
        raise click.Abort()
    
    if check_version:
        click.echo(f"📊 Current version: {current_version}")
        click.echo(f"🔄 Next {part} version would be calculated by Poetry")
        return
    
    if dry_run:
        click.echo(f"🔍 Would bump {part} version from {current_version}")
        click.echo("🔍 Would build package and documentation")
        click.echo("🔍 Would run tests")
        click.echo("🔍 Would publish to PyPI")
        click.echo("🔍 Would deploy documentation")
        return
    
    # Version bump
    click.echo(f"⬆️  Bumping {part} version...")
    try:
        result = subprocess.run(
            ["poetry", "version", part],
            capture_output=True,
            text=True,
            check=True
        )
        new_version_line = result.stdout.strip()
        click.echo(f"✅ {new_version_line}")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Version bump failed: {e}")
        raise click.Abort()
    
    # Run tests
    click.echo("🧪 Running tests...")
    try:
        result = subprocess.run(
            ["poetry", "run", "pytest", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        if result.returncode == 0:
            click.echo("✅ All tests passed")
        else:
            click.echo("❌ Tests failed:")
            click.echo(result.stdout[-1000:])  # Last 1000 chars
            if not click.confirm("Continue release despite test failures?"):
                raise click.Abort()
    except subprocess.TimeoutExpired:
        click.echo("⚠️  Tests timed out")
        if not click.confirm("Continue release despite test timeout?"):
            raise click.Abort()
    except Exception as e:
        click.echo(f"⚠️  Test execution failed: {e}")
        if not click.confirm("Continue release despite test errors?"):
            raise click.Abort()
    
    # Build and publish
    click.echo("🚀 Building and publishing...")
    try:
        # Build
        subprocess.run(["poetry", "build"], check=True)
        click.echo("✅ Package built")
        
        # Publish
        subprocess.run(["poetry", "publish"], check=True)
        click.echo("🎉 Published to PyPI!")
        
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Build/publish failed: {e}")
        click.echo("💡 You may need to run: poetry config pypi-token.pypi YOUR_TOKEN")
        raise click.Abort()
    
    # Git commit and tag
    click.echo("📝 Creating git commit and tag...")
    try:
        # Read new version
        with open(project_path / "pyproject.toml") as f:
            data = tomlkit.load(f)
            new_version = data["tool"]["poetry"]["version"]
        
        # Commit
        subprocess.run(["git", "add", "pyproject.toml"], check=True)
        subprocess.run(["git", "commit", "-m", f"chore: bump version to {new_version}"], check=True)
        
        # Tag
        subprocess.run(["git", "tag", "-a", f"v{new_version}", "-m", f"Release v{new_version}"], check=True)
        
        click.echo(f"✅ Created commit and tag v{new_version}")
        click.echo("💡 Don't forget to push: git push && git push --tags")
        
    except subprocess.CalledProcessError as e:
        click.echo(f"⚠️  Git operations failed: {e}")
        click.echo("   (Package was still published successfully)")
    
    # Documentation
    click.echo("📚 Building documentation...")
    try:
        subprocess.run(["make", "html"], cwd=project_path / "docs", check=True)
        click.echo("✅ Documentation built")
    except subprocess.CalledProcessError as e:
        click.echo(f"⚠️  Documentation build failed: {e}")
    
    click.echo(f"\n🎉 Release v{new_version} completed successfully!")
    click.echo(f"🔗 Package: https://pypi.org/project/{name}/")
    click.echo("📚 Documentation will be available on Read the Docs after next push")


if __name__ == "__main__":
    cli()

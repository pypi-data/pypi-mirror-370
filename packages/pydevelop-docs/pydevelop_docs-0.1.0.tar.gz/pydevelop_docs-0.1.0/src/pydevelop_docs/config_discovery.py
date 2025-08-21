"""Configuration discovery and management for PyDevelop-Docs."""

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import click
import yaml


class ConfigDiscovery:
    """Auto-discover project configuration from various sources."""

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.pydevelop_dir = project_path / ".pydevelop"
        self._cache: Dict[str, Any] = {}

    def discover_all(self) -> Dict[str, Any]:
        """Discover all available configuration."""
        config = {}

        # Load from various sources
        config.update(self._discover_from_pyproject())
        config.update(self._discover_from_git())
        config.update(self._discover_from_package_json())
        config.update(self._discover_from_setup_py())
        config.update(self._discover_from_pypi())

        # Auto-detect common patterns
        config.update(self._auto_detect_paths())

        return config

    def _discover_from_pyproject(self) -> Dict[str, Any]:
        """Extract info from pyproject.toml."""
        pyproject_path = self.project_path / "pyproject.toml"
        if not pyproject_path.exists():
            return {}

        try:
            import tomlkit

            with open(pyproject_path) as f:
                data = tomlkit.load(f)

            config = {}

            # PEP 621 project section
            if "project" in data:
                project = data["project"]
                config["name"] = project.get("name")
                config["version"] = project.get("version")
                config["description"] = project.get("description")
                config["license"] = project.get("license", {}).get("text")
                config["authors"] = self._parse_authors(project.get("authors", []))
                config["urls"] = project.get("urls", {})
                config["dependencies"] = project.get("dependencies", [])

            # Poetry section
            elif "tool" in data and "poetry" in data["tool"]:
                poetry = data["tool"]["poetry"]
                config["name"] = poetry.get("name")
                config["version"] = poetry.get("version")
                config["description"] = poetry.get("description")
                config["license"] = poetry.get("license")
                config["authors"] = poetry.get("authors", [])
                config["homepage"] = poetry.get("homepage")
                config["repository"] = poetry.get("repository")
                config["documentation"] = poetry.get("documentation")

                # Extract dependencies for intersphinx
                deps = []
                if "dependencies" in poetry:
                    deps.extend(
                        [k for k in poetry["dependencies"].keys() if k != "python"]
                    )
                config["dependencies"] = deps

            return config

        except Exception as e:
            click.echo(f"Warning: Could not parse pyproject.toml: {e}", err=True)
            return {}

    def _discover_from_git(self) -> Dict[str, Any]:
        """Extract info from git repository."""
        config = {}

        try:
            # Get remote URL
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                remote_url = result.stdout.strip()
                config["repository"] = self._clean_git_url(remote_url)

                # Extract GitHub/GitLab info
                if "github.com" in remote_url:
                    config["github"] = self._parse_github_url(remote_url)
                elif "gitlab.com" in remote_url:
                    config["gitlab"] = self._parse_gitlab_url(remote_url)

            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                config["branch"] = result.stdout.strip()

            # Get latest commit info
            result = subprocess.run(
                ["git", "log", "-1", "--format=%h %s"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                config["latest_commit"] = result.stdout.strip()

            # Get author info from git config
            result = subprocess.run(
                ["git", "config", "user.name"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                name = result.stdout.strip()

                result = subprocess.run(
                    ["git", "config", "user.email"],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    email = result.stdout.strip()
                    config["git_author"] = f"{name} <{email}>"

        except Exception:
            pass

        return config

    def _discover_from_package_json(self) -> Dict[str, Any]:
        """Extract info from package.json if present."""
        package_json = self.project_path / "package.json"
        if not package_json.exists():
            return {}

        try:
            with open(package_json) as f:
                data = json.load(f)

            config = {
                "name": data.get("name"),
                "version": data.get("version"),
                "description": data.get("description"),
                "license": data.get("license"),
                "author": data.get("author"),
                "homepage": data.get("homepage"),
            }

            if "repository" in data:
                repo = data["repository"]
                if isinstance(repo, dict):
                    config["repository"] = repo.get("url")
                else:
                    config["repository"] = repo

            return {k: v for k, v in config.items() if v is not None}

        except Exception:
            return {}

    def _discover_from_setup_py(self) -> Dict[str, Any]:
        """Extract info from setup.py if present."""
        setup_py = self.project_path / "setup.py"
        if not setup_py.exists():
            return {}

        try:
            # Parse setup.py without executing it
            with open(setup_py) as f:
                content = f.read()

            config = {}

            # Simple regex patterns to extract common fields
            patterns = {
                "name": r'name\s*=\s*["\']([^"\']+)["\']',
                "version": r'version\s*=\s*["\']([^"\']+)["\']',
                "description": r'description\s*=\s*["\']([^"\']+)["\']',
                "author": r'author\s*=\s*["\']([^"\']+)["\']',
                "author_email": r'author_email\s*=\s*["\']([^"\']+)["\']',
                "url": r'url\s*=\s*["\']([^"\']+)["\']',
                "license": r'license\s*=\s*["\']([^"\']+)["\']',
            }

            for key, pattern in patterns.items():
                match = re.search(pattern, content)
                if match:
                    config[key] = match.group(1)

            return config

        except Exception:
            return {}

    def _discover_from_pypi(self) -> Dict[str, Any]:
        """Check if package exists on PyPI."""
        # Only check if we have a package name
        if "name" not in self._cache:
            return {}

        package_name = self._cache.get("name")

        try:
            import requests

            response = requests.get(
                f"https://pypi.org/pypi/{package_name}/json", timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                info = data.get("info", {})

                return {
                    "pypi_url": f"https://pypi.org/project/{package_name}/",
                    "pypi_version": info.get("version"),
                    "pypi_downloads": info.get("downloads", {}).get("last_month", 0),
                }

        except Exception:
            pass

        return {}

    def _auto_detect_paths(self) -> Dict[str, Any]:
        """Auto-detect common project paths."""
        config = {}

        # Detect logo
        logo_patterns = ["logo.png", "logo.svg", "icon.png", "icon.svg"]
        for pattern in logo_patterns:
            for path in [
                self.project_path / pattern,
                self.project_path / "docs" / pattern,
                self.project_path / "docs" / "_static" / pattern,
                self.project_path / "docs" / "source" / "_static" / pattern,
                self.project_path / "assets" / pattern,
                self.project_path / "images" / pattern,
            ]:
                if path.exists():
                    config["logo"] = str(path.relative_to(self.project_path))
                    break
            if "logo" in config:
                break

        # Detect README
        for readme in ["README.md", "README.rst", "readme.md", "readme.rst"]:
            if (self.project_path / readme).exists():
                config["readme"] = readme
                break

        # Detect source directory
        for src in ["src", "lib", self.project_path.name]:
            if (self.project_path / src).exists():
                config["source_dir"] = src
                break

        # Detect if monorepo
        if (self.project_path / "packages").exists():
            config["project_type"] = "monorepo"
            config["packages"] = [
                p.name
                for p in (self.project_path / "packages").iterdir()
                if p.is_dir() and not p.name.startswith(".")
            ]
        else:
            config["project_type"] = "single"

        return config

    def _clean_git_url(self, url: str) -> str:
        """Clean git URL to HTTPS format."""
        # Convert SSH to HTTPS
        if url.startswith("git@"):
            url = url.replace(":", "/", 1).replace("git@", "https://")
        # Remove .git suffix
        if url.endswith(".git"):
            url = url[:-4]
        return url

    def _parse_github_url(self, url: str) -> Dict[str, str]:
        """Parse GitHub URL for owner and repo."""
        clean_url = self._clean_git_url(url)
        parts = clean_url.split("/")
        if len(parts) >= 2:
            return {
                "owner": parts[-2],
                "repo": parts[-1],
                "url": clean_url,
            }
        return {}

    def _parse_gitlab_url(self, url: str) -> Dict[str, str]:
        """Parse GitLab URL for owner and repo."""
        return self._parse_github_url(url)  # Same format

    def _parse_authors(self, authors: List[Union[str, Dict]]) -> List[str]:
        """Parse author information from various formats."""
        parsed = []
        for author in authors:
            if isinstance(author, str):
                parsed.append(author)
            elif isinstance(author, dict):
                name = author.get("name", "")
                email = author.get("email", "")
                if email:
                    parsed.append(f"{name} <{email}>")
                else:
                    parsed.append(name)
        return parsed

    def resolve_value(self, value: Any, discovered: Dict[str, Any]) -> Any:
        """Resolve ${auto:} placeholders in configuration values."""
        if not isinstance(value, str):
            return value

        # Check for ${auto:...} pattern
        pattern = r"\$\{auto:([^}]+)\}"
        matches = re.findall(pattern, value)

        if not matches:
            return value

        result = value
        for match in matches:
            # Simple key lookup
            if match in discovered:
                replacement = discovered.get(match, "")
                result = result.replace(f"${{auto:{match}}}", str(replacement))
            # Nested key lookup (e.g., github.owner)
            elif "." in match:
                parts = match.split(".")
                current = discovered
                for part in parts:
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        current = ""
                        break
                result = result.replace(f"${{auto:{match}}}", str(current))
            # Special cases
            elif match == "find-logo":
                logo = discovered.get("logo", "")
                result = result.replace(f"${{auto:{match}}}", logo)
            elif match == "year":
                import datetime

                result = result.replace(
                    f"${{auto:{match}}}", str(datetime.datetime.now().year)
                )

        return result


class PyDevelopConfig:
    """Manage .pydevelop configuration directory."""

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.config_dir = project_path / ".pydevelop"
        self.discovery = ConfigDiscovery(project_path)
        self._discovered: Optional[Dict[str, Any]] = None

    @property
    def discovered(self) -> Dict[str, Any]:
        """Lazy load discovered configuration."""
        if self._discovered is None:
            self._discovered = self.discovery.discover_all()
        return self._discovered

    def initialize(self) -> None:
        """Initialize .pydevelop directory structure."""
        # Create directory structure
        self.config_dir.mkdir(exist_ok=True)
        (self.config_dir / "cache").mkdir(exist_ok=True)
        (self.config_dir / "templates").mkdir(exist_ok=True)
        (self.config_dir / "hooks").mkdir(exist_ok=True)

        # Create default config files if they don't exist
        self._create_default_config()
        self._create_default_docs_config()

        # Add .pydevelop to .gitignore
        self._update_gitignore()

        click.echo(f"✅ Initialized .pydevelop configuration directory")

    def _create_default_config(self) -> None:
        """Create default config.yaml."""
        config_path = self.config_dir / "config.yaml"
        if config_path.exists():
            return

        # Auto-discover values
        discovered = self.discovered

        config = {
            "project": {
                "name": discovered.get("name", "${auto:name}"),
                "version": discovered.get("version", "${auto:version}"),
                "description": discovered.get("description", "${auto:description}"),
                "authors": discovered.get("authors", ["${auto:git_author}"]),
                "license": discovered.get("license", "${auto:license}"),
                "repository": discovered.get("repository", "${auto:repository}"),
                "homepage": discovered.get("homepage", "${auto:homepage}"),
            },
            "discovery": {
                "auto_detect": True,
                "sources": [
                    "pyproject.toml",
                    "package.json",
                    "setup.py",
                    "git",
                    "pypi",
                ],
            },
        }

        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        click.echo(f"📝 Created {config_path}")

    def _create_default_docs_config(self) -> None:
        """Create default docs.yaml."""
        docs_path = self.config_dir / "docs.yaml"
        if docs_path.exists():
            return

        discovered = self.discovered

        config = {
            "documentation": {
                "theme": "furo",
                "logo": discovered.get("logo", "${auto:find-logo}"),
                "favicon": "${auto:find-favicon}",
                "copyright": "${auto:year} "
                + discovered.get("name", "${auto:name}")
                + " contributors",
            },
            "build": {
                "auto_fix": True,
                "selective_rebuild": True,
                "parallel": True,
                "clean_build": False,
            },
            "watch": {
                "enabled": True,
                "patterns": [
                    "**/*.py",
                    "**/*.rst",
                    "**/*.md",
                    "**/conf.py",
                    ".pydevelop/**/*.yaml",
                ],
                "ignore": [
                    ".venv/**",
                    "**/build/**",
                    "**/__pycache__/**",
                    "**/.pytest_cache/**",
                    "**/node_modules/**",
                ],
                "rebuild_delay": 2,  # seconds
                "batch_changes": True,
            },
            "api": {
                "hierarchical": True,  # Our key fix!
                "show_private": False,
                "show_inherited": True,
                "member_order": "groupwise",
                "class_content": "both",
            },
            "intersphinx": {
                "auto_detect": True,
                "mappings": {
                    "python": "https://docs.python.org/3",
                    "sphinx": "https://www.sphinx-doc.org/en/master",
                },
            },
            "extensions": {
                "enable_all": True,
                "custom": [],
                "disable": [],
            },
        }

        # Add discovered dependencies to intersphinx
        if "dependencies" in discovered:
            for dep in discovered["dependencies"]:
                # Map common packages to their docs
                if dep == "pydantic":
                    config["intersphinx"]["mappings"][
                        "pydantic"
                    ] = "https://docs.pydantic.dev/latest"
                elif dep == "fastapi":
                    config["intersphinx"]["mappings"][
                        "fastapi"
                    ] = "https://fastapi.tiangolo.com"
                elif dep.startswith("langchain"):
                    config["intersphinx"]["mappings"][
                        "langchain"
                    ] = "https://api.python.langchain.com/en/latest/"

        with open(docs_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        click.echo(f"📝 Created {docs_path}")

    def _update_gitignore(self) -> None:
        """Add .pydevelop/cache to .gitignore."""
        gitignore_path = self.project_path / ".gitignore"

        patterns_to_add = [
            "\n# PyDevelop-Docs",
            ".pydevelop/cache/",
            ".pydevelop/hooks/*.log",
            ".pydevelop/templates/_build/",
        ]

        if gitignore_path.exists():
            with open(gitignore_path, "r") as f:
                content = f.read()

            # Check if already added
            if ".pydevelop/cache/" in content:
                return

            # Append patterns
            with open(gitignore_path, "a") as f:
                f.write("\n".join(patterns_to_add) + "\n")
        else:
            # Create new .gitignore
            with open(gitignore_path, "w") as f:
                f.write("\n".join(patterns_to_add) + "\n")

    def load_config(self) -> Dict[str, Any]:
        """Load and resolve all configuration."""
        config = {}

        # Load config.yaml
        config_path = self.config_dir / "config.yaml"
        if config_path.exists():
            with open(config_path) as f:
                config_data = yaml.safe_load(f) or {}
                config.update(self._resolve_config(config_data))

        # Load docs.yaml
        docs_path = self.config_dir / "docs.yaml"
        if docs_path.exists():
            with open(docs_path) as f:
                docs_data = yaml.safe_load(f) or {}
                config.update(self._resolve_config(docs_data))

        return config

    def _resolve_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively resolve ${auto:} placeholders."""
        if isinstance(config, dict):
            return {k: self._resolve_config(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._resolve_config(v) for v in config]
        else:
            return self.discovery.resolve_value(config, self.discovered)

    def get_cache_path(self, key: str) -> Path:
        """Get path for cache file."""
        return self.config_dir / "cache" / f"{key}.json"

    def load_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Load cache data."""
        cache_path = self.get_cache_path(key)
        if cache_path.exists():
            try:
                with open(cache_path) as f:
                    return json.load(f)
            except Exception:
                pass
        return None

    def save_cache(self, key: str, data: Dict[str, Any]) -> None:
        """Save cache data."""
        cache_path = self.get_cache_path(key)
        cache_path.parent.mkdir(parents=True, exist_ok=True)

        with open(cache_path, "w") as f:
            json.dump(data, f, indent=2)

"""Hook system for PyDevelop-Docs customization."""

import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import click


class HookManager:
    """Manage pre/post hooks for various PyDevelop-Docs operations."""

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.hooks_dir = project_path / ".pydevelop" / "hooks"

    def run_hook(
        self, hook_name: str, context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Run a specific hook if it exists.

        Args:
            hook_name: Name of the hook (e.g., 'pre-build', 'post-init')
            context: Optional context dictionary passed to Python hooks

        Returns:
            True if hook ran successfully or doesn't exist, False on error
        """
        if not self.hooks_dir.exists():
            return True

        # Look for hook files with various extensions
        hook_files = [
            self.hooks_dir / f"{hook_name}.py",
            self.hooks_dir / f"{hook_name}.sh",
            self.hooks_dir / f"{hook_name}.js",
            self.hooks_dir / f"{hook_name}",  # Executable without extension
        ]

        for hook_file in hook_files:
            if hook_file.exists() and hook_file.is_file():
                return self._execute_hook(hook_file, context)

        return True

    def _execute_hook(
        self, hook_file: Path, context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Execute a hook file based on its type."""
        click.echo(f"🪝 Running hook: {hook_file.name}")

        try:
            if hook_file.suffix == ".py":
                return self._run_python_hook(hook_file, context)
            elif hook_file.suffix == ".sh":
                return self._run_shell_hook(hook_file)
            elif hook_file.suffix == ".js":
                return self._run_node_hook(hook_file)
            else:
                # Try to execute as shell script
                return self._run_shell_hook(hook_file)

        except Exception as e:
            click.echo(f"❌ Hook failed: {e}", err=True)
            return False

    def _run_python_hook(
        self, hook_file: Path, context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Run a Python hook."""
        # Add project path to Python path
        original_path = sys.path.copy()
        sys.path.insert(0, str(self.project_path))

        try:
            # Create hook context
            hook_context = {
                "project_path": self.project_path,
                "hooks_dir": self.hooks_dir,
                "pydevelop_dir": self.hooks_dir.parent,
                **(context or {}),
            }

            # Execute the hook
            with open(hook_file) as f:
                code = compile(f.read(), str(hook_file), "exec")
                exec(code, {"__file__": str(hook_file), **hook_context})

            return True

        finally:
            sys.path = original_path

    def _run_shell_hook(self, hook_file: Path) -> bool:
        """Run a shell script hook."""
        # Make sure it's executable
        os.chmod(hook_file, 0o755)

        result = subprocess.run(
            [str(hook_file)],
            cwd=self.project_path,
            capture_output=True,
            text=True,
        )

        if result.stdout:
            click.echo(result.stdout)
        if result.stderr:
            click.echo(result.stderr, err=True)

        return result.returncode == 0

    def _run_node_hook(self, hook_file: Path) -> bool:
        """Run a Node.js hook."""
        result = subprocess.run(
            ["node", str(hook_file)],
            cwd=self.project_path,
            capture_output=True,
            text=True,
        )

        if result.stdout:
            click.echo(result.stdout)
        if result.stderr:
            click.echo(result.stderr, err=True)

        return result.returncode == 0

    def create_example_hooks(self) -> None:
        """Create example hook files."""
        self.hooks_dir.mkdir(parents=True, exist_ok=True)

        # Example pre-build hook
        pre_build = self.hooks_dir / "pre-build.sh.example"
        pre_build.write_text(
            '''#!/bin/bash
# Example pre-build hook
# This runs before documentation is built

echo "🔨 Running pre-build checks..."

# Example: Check for missing docstrings
echo "Checking for missing docstrings..."
find src -name "*.py" -exec grep -L '"""' {} \\; | head -5

# Example: Update version number
# sed -i 's/version = ".*"/version = "'$(git describe --tags)'"/' docs/source/conf.py

echo "✅ Pre-build checks complete"
'''
        )

        # Example post-build hook
        post_build = self.hooks_dir / "post-build.py.example"
        post_build.write_text(
            '''#!/usr/bin/env python
"""Example post-build hook - runs after documentation is built."""

import os
from pathlib import Path

# The hook receives these variables:
# - project_path: Path to the project root
# - hooks_dir: Path to the hooks directory
# - pydevelop_dir: Path to .pydevelop directory

print("📦 Running post-build processing...")

# Example: Add custom footer to all HTML files
build_dir = project_path / "docs" / "build" / "html"
if build_dir.exists():
    footer_html = """
    <div class="custom-footer">
        Built with PyDevelop-Docs | 
        <a href="https://github.com/yourusername/yourproject">GitHub</a>
    </div>
    """
    
    for html_file in build_dir.rglob("*.html"):
        content = html_file.read_text()
        if "</body>" in content and "custom-footer" not in content:
            content = content.replace("</body>", f"{footer_html}</body>")
            html_file.write_text(content)
            
    print(f"✅ Added custom footer to HTML files")

# Example: Generate a build info file
build_info = {
    "timestamp": __import__("datetime").datetime.now().isoformat(),
    "git_commit": os.popen("git rev-parse HEAD").read().strip(),
    "git_branch": os.popen("git branch --show-current").read().strip(),
}

import json
info_file = build_dir / "build-info.json"
info_file.write_text(json.dumps(build_info, indent=2))
print(f"✅ Created {info_file}")
'''
        )

        # Example post-init hook
        post_init = self.hooks_dir / "post-init.py.example"
        post_init.write_text(
            '''#!/usr/bin/env python
"""Example post-init hook - runs after project initialization."""

from pathlib import Path

print("🎨 Customizing documentation setup...")

# Example: Add custom CSS
css_dir = project_path / "docs" / "source" / "_static" / "css"
css_dir.mkdir(parents=True, exist_ok=True)

custom_css = css_dir / "custom.css"
if not custom_css.exists():
    custom_css.write_text("""
/* Custom PyDevelop-Docs styles */
.custom-note {
    background-color: #e8f4f8;
    border-left: 4px solid #2196F3;
    padding: 12px;
    margin: 20px 0;
}

.custom-warning {
    background-color: #fff3cd;
    border-left: 4px solid #ff9800;
    padding: 12px;
    margin: 20px 0;
}

/* Add your custom styles here */
""")
    print(f"✅ Created {custom_css}")

# Example: Add custom JavaScript
js_dir = project_path / "docs" / "source" / "_static" / "js"
js_dir.mkdir(parents=True, exist_ok=True)

custom_js = js_dir / "custom.js"
if not custom_js.exists():
    custom_js.write_text("""
// Custom PyDevelop-Docs JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('PyDevelop-Docs: Custom JS loaded');
    
    // Example: Add copy buttons to all code blocks
    const codeBlocks = document.querySelectorAll('pre');
    codeBlocks.forEach(block => {
        // Your custom code here
    });
});
""")
    print(f"✅ Created {custom_js}")

print("✅ Post-init customization complete")
'''
        )

        # Example watch hook
        on_change = self.hooks_dir / "on-change.sh.example"
        on_change.write_text(
            """#!/bin/bash
# Example on-change hook
# This runs when files change during watch mode

changed_file="$1"
echo "📝 File changed: $changed_file"

# Example: Run linter on Python files
if [[ "$changed_file" == *.py ]]; then
    echo "Running linter..."
    ruff check "$changed_file" || true
fi

# Example: Validate RST files
if [[ "$changed_file" == *.rst ]]; then
    echo "Validating RST..."
    rst2html "$changed_file" > /dev/null 2>&1 || echo "⚠️ RST validation failed"
fi
"""
        )

        # Make examples readable
        for example in self.hooks_dir.glob("*.example"):
            example.chmod(0o644)

        click.echo(f"📝 Created example hooks in {self.hooks_dir}")
        click.echo("   Rename .example files to use them")


class TemplateOverrideManager:
    """Manage template overrides in .pydevelop/templates/"""

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.templates_dir = project_path / ".pydevelop" / "templates"

    def get_override(self, template_name: str) -> Optional[Path]:
        """Check if a template override exists."""
        override_path = self.templates_dir / template_name
        if override_path.exists():
            return override_path
        return None

    def list_overrides(self) -> List[Path]:
        """List all template overrides."""
        if not self.templates_dir.exists():
            return []
        return list(self.templates_dir.rglob("*"))

    def create_example_overrides(self) -> None:
        """Create example template overrides."""
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        # Example conf.py override
        conf_override = self.templates_dir / "conf.py.override.example"
        conf_override.write_text(
            '''# Example conf.py override
# Rename to conf.py to use this instead of the generated version

# This example shows how to extend the generated configuration
# while keeping PyDevelop-Docs features

# First, import the base configuration
from pydevelop_docs.config import get_haive_config
config = get_haive_config(__name__, project_root="../..")

# Apply base configuration
for key, value in config.items():
    globals()[key] = value

# Now add your customizations
# =============================

# Custom theme options
html_theme_options.update({
    "announcement": "📢 Custom announcement here!",
    "custom_option": True,
})

# Add custom extensions
extensions.append("my_custom_extension")

# Custom static files
html_static_path.append("_custom_static")

# Custom templates
templates_path.insert(0, "_custom_templates")

# Advanced customization
def setup(app):
    """Sphinx setup hook for advanced customization."""
    # Add custom CSS
    app.add_css_file("css/my-custom.css")
    
    # Add custom JavaScript
    app.add_js_file("js/my-custom.js")
    
    # Connect to Sphinx events
    app.connect("doctree-resolved", my_custom_processor)
    
def my_custom_processor(app, doctree, docname):
    """Process the doctree after it's resolved."""
    # Your custom processing here
    pass
'''
        )

        # Example custom RST template
        custom_rst_dir = self.templates_dir / "rst_templates"
        custom_rst_dir.mkdir(exist_ok=True)

        custom_index = custom_rst_dir / "index.rst.example"
        custom_index.write_text(
            """.. Custom Index Template
   ====================

Welcome to {{ project }} documentation!
=======================================

.. note::
   This is a custom index template from .pydevelop/templates/

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting-started
   api/index
   examples/index
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. raw:: html

   <div class="custom-footer">
   This documentation was built with PyDevelop-Docs
   </div>
"""
        )

        click.echo(f"📝 Created example template overrides in {self.templates_dir}")
        click.echo("   Rename .example files to use them")

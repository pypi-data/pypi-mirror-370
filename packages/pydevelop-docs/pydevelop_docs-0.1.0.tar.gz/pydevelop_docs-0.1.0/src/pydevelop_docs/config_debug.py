"""Debug configuration enhancements for PyDevelop Docs.

This module provides debug-enhanced configuration options that integrate
with Sphinx's built-in logging and third-party debug extensions.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from sphinx.util import logging

logger = logging.getLogger(__name__)


def get_debug_config(
    debug_level: int = 0,
    enable_profiling: bool = False,
    enable_measurement: bool = False,
    warning_categories: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Get debug configuration for Sphinx builds.

    Args:
        debug_level: Verbosity level (0-3, corresponds to -v flags)
        enable_profiling: Enable performance profiling
        enable_measurement: Enable sphinx-needs measurement
        warning_categories: Categories to track (None = all)

    Returns:
        Dictionary of debug configuration options
    """
    config = {}

    # Core debug settings
    config["pydevelop_debug_level"] = debug_level
    config["pydevelop_debug_categories"] = warning_categories or []

    # Enable debug extensions based on level
    debug_extensions = []

    if debug_level >= 1:
        # Basic debug info
        if _is_extension_available("sphinx_debuginfo"):
            debug_extensions.append("sphinx_debuginfo")
            logger.info("✅ Enabling sphinx-debuginfo extension")

    if enable_profiling or debug_level >= 2:
        # Performance profiling
        if _is_extension_available("sphinx_needs"):
            debug_extensions.append("sphinx_needs")
            config["needs_debug_measurement"] = True
            logger.info("✅ Enabling sphinx-needs measurement")

    # Add our custom debug extension
    debug_extensions.append("pydevelop_docs.sphinx_debug")

    config["debug_extensions"] = debug_extensions

    # Configure warning suppression for cleaner output
    if debug_level < 2:  # Less verbose modes
        config["suppress_warnings"] = [
            "autoapi.python_import_resolution",  # Import resolution warnings
            "ref.python",  # Python reference warnings
        ]

    # Enable detailed error reporting
    config["show_warning_types"] = True

    # Configure nitpicky mode for higher debug levels
    if debug_level >= 3:
        config["nitpicky"] = True
        config["nitpick_ignore"] = []

    return config


def enhance_config_with_debug(
    base_config: Dict[str, Any],
    debug_mode: bool = False,
    ci_mode: bool = False,
) -> Dict[str, Any]:
    """Enhance existing configuration with debug features.

    Args:
        base_config: Base Sphinx configuration
        debug_mode: Enable debug mode (auto-detects from env)
        ci_mode: Enable CI-specific settings

    Returns:
        Enhanced configuration dictionary
    """
    # Auto-detect debug mode from environment
    if debug_mode or os.environ.get("SPHINX_DEBUG"):
        debug_level = int(os.environ.get("SPHINX_DEBUG_LEVEL", "2"))
        logger.info(f"🔍 Debug mode enabled (level {debug_level})")

        # Get debug config
        debug_config = get_debug_config(
            debug_level=debug_level,
            enable_profiling=True,
            enable_measurement=True,
        )

        # Merge debug extensions
        if "extensions" not in base_config:
            base_config["extensions"] = []

        base_config["extensions"].extend(debug_config.get("debug_extensions", []))

        # Apply debug settings
        base_config.update(
            {k: v for k, v in debug_config.items() if k != "debug_extensions"}
        )

    # CI mode enhancements
    if ci_mode or os.environ.get("CI"):
        logger.info("🏗️ CI mode enabled")

        # Strict mode in CI
        base_config["nitpicky"] = True
        base_config["warning_is_error"] = True

        # Parallel builds in CI
        if "SPHINX_PARALLEL" in os.environ:
            base_config["parallel"] = int(os.environ["SPHINX_PARALLEL"])

        # Disable interactive features
        base_config["sphinx_tabs_disable_tab_closing"] = True

    return base_config


def setup_logging_filters(
    app,
    ignore_patterns: Optional[List[str]] = None,
    log_file: Optional[Path] = None,
):
    """Setup custom logging filters for cleaner output.

    Args:
        app: Sphinx application
        ignore_patterns: Regex patterns for warnings to ignore
        log_file: Optional file to write filtered logs
    """
    import re

    from sphinx.util.logging import WarningStreamHandler

    class FilteredWarningHandler(WarningStreamHandler):
        """Custom handler that filters warnings."""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.ignore_patterns = [
                re.compile(pattern) for pattern in (ignore_patterns or [])
            ]
            self.log_file = log_file
            if self.log_file:
                self.log_file.parent.mkdir(parents=True, exist_ok=True)

        def emit(self, record):
            # Check if should ignore
            message = self.format(record)
            for pattern in self.ignore_patterns:
                if pattern.search(message):
                    # Log to file if specified
                    if self.log_file:
                        with open(self.log_file, "a") as f:
                            f.write(f"{message}\n")
                    return

            # Otherwise emit normally
            super().emit(record)

    # Replace default handler
    logger = logging.getLogger("sphinx")
    for handler in logger.handlers[:]:
        if isinstance(handler, WarningStreamHandler):
            logger.removeHandler(handler)
            logger.addHandler(FilteredWarningHandler())
            break


def _is_extension_available(extension_name: str) -> bool:
    """Check if a Sphinx extension is available."""
    try:
        __import__(extension_name)
        return True
    except ImportError:
        return False


# Pre-configured debug profiles
DEBUG_PROFILES = {
    "minimal": {
        "debug_level": 0,
        "enable_profiling": False,
        "enable_measurement": False,
    },
    "standard": {
        "debug_level": 1,
        "enable_profiling": False,
        "enable_measurement": False,
    },
    "verbose": {
        "debug_level": 2,
        "enable_profiling": True,
        "enable_measurement": False,
    },
    "full": {
        "debug_level": 3,
        "enable_profiling": True,
        "enable_measurement": True,
    },
}


def get_debug_profile(profile_name: str = "standard") -> Dict[str, Any]:
    """Get a pre-configured debug profile.

    Args:
        profile_name: Profile name (minimal, standard, verbose, full)

    Returns:
        Debug configuration for the profile
    """
    if profile_name not in DEBUG_PROFILES:
        logger.warning(f"Unknown debug profile: {profile_name}, using 'standard'")
        profile_name = "standard"

    return get_debug_config(**DEBUG_PROFILES[profile_name])


# Debugging utilities for conf.py
def debug_extension_load(app, extension_name: str):
    """Debug helper for extension loading."""
    from sphinx.util import logging

    logger = logging.getLogger("pydevelop.extensions")

    try:
        start = time.time()
        app.setup_extension(extension_name)
        duration = time.time() - start
        logger.info(f"✅ Loaded {extension_name} in {duration:.3f}s")
    except Exception as e:
        logger.error(f"❌ Failed to load {extension_name}: {e}")
        raise


def create_debug_conf_snippet() -> str:
    """Generate conf.py snippet for debug mode."""
    return """
# Debug Configuration (add to conf.py)
# =====================================

# Enable debug mode from environment
import os
if os.environ.get('SPHINX_DEBUG'):
    from pydevelop_docs.config_debug import enhance_config_with_debug
    
    # Get current config as dict
    current_config = {k: v for k, v in globals().items() if not k.startswith('_')}
    
    # Enhance with debug features
    debug_config = enhance_config_with_debug(
        current_config,
        debug_mode=True,
        ci_mode=os.environ.get('CI') is not None
    )
    
    # Apply enhanced config
    globals().update(debug_config)
    
    # Setup logging filters
    def setup(app):
        from pydevelop_docs.config_debug import setup_logging_filters
        from pathlib import Path
        
        # Filter noisy warnings to log file
        setup_logging_filters(
            app,
            ignore_patterns=[
                r'Cannot resolve import',
                r'pkg_resources is deprecated',
            ],
            log_file=Path(app.outdir) / '_debug' / 'filtered_warnings.log'
        )

# Run builds with debug:
# SPHINX_DEBUG=1 make html              # Basic debug
# SPHINX_DEBUG_LEVEL=3 make html        # Full debug
# SPHINX_DEBUG=1 sphinx-autobuild . _build/html  # With live reload
"""

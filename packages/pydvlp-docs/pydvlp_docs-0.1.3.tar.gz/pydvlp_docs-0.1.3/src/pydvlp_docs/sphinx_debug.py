"""Enhanced Sphinx debugging and logging utilities.

Implements best practices from Sphinx's built-in logging API and integrates
with third-party debug extensions for comprehensive build analysis.
"""

import json
import os
import sys
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from sphinx.application import Sphinx
from sphinx.util import logging

# Get logger using Sphinx's namespace
logger = logging.getLogger(__name__)


class SphinxDebugExtension:
    """Enhanced debugging extension for Sphinx builds."""

    def __init__(self, app: Sphinx):
        self.app = app
        self.start_time = time.time()
        self.phase_times = {}
        self.warning_categories = {}
        self.error_count = 0
        self.file_count = 0
        self.extension_load_times = {}

        # Configure based on debug level
        self.debug_level = self._get_debug_level()

    def _get_debug_level(self) -> int:
        """Determine debug level from verbosity."""
        if hasattr(self.app, "verbosity"):
            return self.app.verbosity
        return 0

    @contextmanager
    def phase_timer(self, phase_name: str):
        """Time a build phase."""
        start = time.time()
        logger.info(f"📍 Starting phase: {phase_name}")
        try:
            yield
        finally:
            duration = time.time() - start
            self.phase_times[phase_name] = duration
            logger.info(f"✅ Completed {phase_name} in {duration:.2f}s")

    def log_warning_analysis(self, warning_msg: str, location: str = None):
        """Analyze and categorize warnings."""
        # Categorize the warning
        category = self._categorize_warning(warning_msg)

        if category not in self.warning_categories:
            self.warning_categories[category] = []

        self.warning_categories[category].append(
            {
                "message": warning_msg,
                "location": location,
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Log with appropriate detail based on debug level
        if self.debug_level >= 2:  # -vv or higher
            logger.verbose(
                f"Warning category '{category}': {warning_msg}", location=location
            )

    def _categorize_warning(self, warning_msg: str) -> str:
        """Categorize warning messages."""
        msg_lower = warning_msg.lower()

        if "cannot resolve import" in msg_lower:
            return "import_resolution"
        elif "deprecated" in msg_lower:
            return "deprecation"
        elif "duplicate" in msg_lower:
            return "duplicate_reference"
        elif "undefined" in msg_lower:
            return "undefined_reference"
        elif "extension" in msg_lower:
            return "extension"
        elif "autoapi" in msg_lower:
            return "autoapi"
        else:
            return "general"

    def generate_debug_report(self):
        """Generate comprehensive debug report."""
        total_time = time.time() - self.start_time

        report = {
            "build_summary": {
                "total_duration": f"{total_time:.2f}s",
                "files_processed": self.file_count,
                "errors": self.error_count,
                "warnings": sum(
                    len(warns) for warns in self.warning_categories.values()
                ),
                "debug_level": self.debug_level,
            },
            "phase_timings": {
                phase: f"{duration:.2f}s ({duration/total_time*100:.1f}%)"
                for phase, duration in self.phase_times.items()
            },
            "warning_breakdown": {
                category: len(warnings)
                for category, warnings in self.warning_categories.items()
            },
            "extension_load_times": self.extension_load_times,
            "recommendations": self._generate_recommendations(),
        }

        # Save debug report
        debug_dir = Path(self.app.outdir) / "_debug"
        debug_dir.mkdir(exist_ok=True)

        with open(debug_dir / "build_debug.json", "w") as f:
            json.dump(report, f, indent=2)

        # Also create HTML debug page if sphinx-debuginfo is available
        self._create_debug_html(debug_dir, report)

        logger.info(f"📊 Debug report saved to {debug_dir / 'build_debug.json'}")

    def _generate_recommendations(self) -> List[str]:
        """Generate build recommendations."""
        recommendations = []

        # Import resolution issues
        import_errors = len(self.warning_categories.get("import_resolution", []))
        if import_errors > 50:
            recommendations.append(
                f"🔗 {import_errors} import resolution warnings. "
                "Consider: autoapi_ignore_patterns or fixing import paths"
            )

        # Slow phases
        for phase, duration in self.phase_times.items():
            if duration > 30:
                recommendations.append(
                    f"⏱️ Phase '{phase}' took {duration:.1f}s. "
                    "Consider optimization or parallel builds"
                )

        # Extension issues
        slow_extensions = [
            (ext, time) for ext, time in self.extension_load_times.items() if time > 1.0
        ]
        if slow_extensions:
            recommendations.append(
                f"🔌 Slow extensions: {', '.join(ext for ext, _ in slow_extensions)}"
            )

        return recommendations

    def _create_debug_html(self, debug_dir: Path, report: Dict[str, Any]):
        """Create HTML debug page."""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Sphinx Build Debug Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #2563eb; }}
        .metric {{ background: #f0f9ff; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        .warning {{ background: #fef3c7; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        .error {{ background: #fee2e2; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background: #f0f9ff; }}
    </style>
</head>
<body>
    <h1>🔍 Sphinx Build Debug Report</h1>
    
    <div class="metric">
        <h2>Build Summary</h2>
        <ul>
            <li>Duration: {report['build_summary']['total_duration']}</li>
            <li>Files: {report['build_summary']['files_processed']}</li>
            <li>Warnings: {report['build_summary']['warnings']}</li>
            <li>Errors: {report['build_summary']['errors']}</li>
        </ul>
    </div>
    
    <h2>⏱️ Phase Timings</h2>
    <table>
        <tr><th>Phase</th><th>Duration</th></tr>
        {''.join(f"<tr><td>{phase}</td><td>{duration}</td></tr>" 
                 for phase, duration in report['phase_timings'].items())}
    </table>
    
    <h2>⚠️ Warning Categories</h2>
    <table>
        <tr><th>Category</th><th>Count</th></tr>
        {''.join(f"<tr><td>{cat}</td><td>{count}</td></tr>" 
                 for cat, count in report['warning_breakdown'].items())}
    </table>
    
    <h2>💡 Recommendations</h2>
    <ul>
        {''.join(f"<li>{rec}</li>" for rec in report['recommendations'])}
    </ul>
    
    <p><em>Generated at {datetime.now().isoformat()}</em></p>
</body>
</html>
"""

        with open(debug_dir / "debug_report.html", "w") as f:
            f.write(html_content)


def setup_debug_logging(app: Sphinx):
    """Configure enhanced debug logging for Sphinx."""
    # Create debug extension instance
    debug_ext = SphinxDebugExtension(app)
    app.debug_ext = debug_ext

    # Hook into build phases
    def on_config_inited(app, config):
        """Configuration initialized."""
        logger.info("📋 Configuration initialized", location="conf.py")

        # Log debug settings
        if hasattr(config, "needs_debug_measurement"):
            logger.info(f"needs_debug_measurement = {config.needs_debug_measurement}")

        # Check for debug extensions
        debug_extensions = ["sphinx_debuginfo", "sphinx_needs", "sphinx_autobuild"]
        for ext in debug_extensions:
            if ext in config.extensions:
                logger.info(f"✅ Debug extension loaded: {ext}")

    def on_builder_inited(app):
        """Builder initialized."""
        with debug_ext.phase_timer("builder_init"):
            logger.info(f"🏗️ Builder: {app.builder.name}")
            logger.info(f"📁 Source: {app.srcdir}")
            logger.info(f"📁 Output: {app.outdir}")

    def on_source_read(app, docname, source):
        """Source file read."""
        debug_ext.file_count += 1
        if debug_ext.debug_level >= 3:  # -vvv
            logger.debug(f"📄 Reading: {docname}")

    def on_doctree_resolved(app, doctree, docname):
        """Document tree resolved."""
        if debug_ext.debug_level >= 2:
            logger.verbose(f"🌳 Resolved doctree: {docname}")

    def on_build_finished(app, exception):
        """Build finished."""
        if exception:
            logger.error(f"❌ Build failed: {exception}")
            debug_ext.error_count += 1
        else:
            logger.info("✅ Build completed successfully")

        # Generate debug report
        debug_ext.generate_debug_report()

    # Connect event handlers
    app.connect("config-inited", on_config_inited)
    app.connect("builder-inited", on_builder_inited)
    app.connect("source-read", on_source_read)
    app.connect("doctree-resolved", on_doctree_resolved)
    app.connect("build-finished", on_build_finished)


def setup(app: Sphinx):
    """Setup the debug extension."""
    logger.info("🔍 PyDevelop Debug Extension loaded")

    # Setup debug logging
    setup_debug_logging(app)

    # Add configuration values
    app.add_config_value("pydevelop_debug_level", 0, "html")
    app.add_config_value("pydevelop_debug_categories", [], "html")
    app.add_config_value("pydevelop_debug_output", "_debug", "html")

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


# Utility functions for manual debugging
def trace_suspicious_directive(name: str, debug: bool = False):
    """Decorator to trace directive execution."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            if debug:
                logger.debug(f"🔍 Directive '{name}' called with args: {args}")
                start = time.time()

            result = func(*args, **kwargs)

            if debug:
                duration = time.time() - start
                logger.debug(f"✅ Directive '{name}' completed in {duration:.3f}s")

            return result

        return wrapper

    return decorator


@contextmanager
def measure_time(operation_name: str, logger=logger):
    """Context manager to measure operation time."""
    start = time.time()
    logger.verbose(f"⏱️ Starting: {operation_name}")
    try:
        yield
    finally:
        duration = time.time() - start
        logger.info(f"⏱️ {operation_name}: {duration:.3f}s")


def log_once(message: str, level: str = "warning", location: str = None):
    """Log a message only once per build."""
    if not hasattr(log_once, "_seen"):
        log_once._seen = set()

    key = (message, level, location)
    if key not in log_once._seen:
        log_once._seen.add(key)

        if level == "warning":
            logger.warning(message, location=location)
        elif level == "info":
            logger.info(message)
        elif level == "debug":
            logger.debug(message)


# Integration with sphinx-needs measurement
try:
    from sphinx_needs.utils import measure_time as needs_measure_time

    HAS_SPHINX_NEEDS = True
except ImportError:
    HAS_SPHINX_NEEDS = False
    needs_measure_time = measure_time  # Fallback to our implementation

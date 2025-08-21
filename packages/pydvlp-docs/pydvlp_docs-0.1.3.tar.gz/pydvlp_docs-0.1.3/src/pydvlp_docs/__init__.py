"""Pydvlp Documentation Tools.

Universal Python documentation generator with 40+ Sphinx extensions pre-configured.
Turn any Python project into beautiful documentation with zero configuration.

Features:
    - 🎯 Zero Configuration: Works out-of-the-box with any Python project
    - 📦 Universal Support: Single packages, monorepos, any structure  
    - 🎨 Beautiful Themes: Pre-configured Furo theme with dark mode
    - 🔧 40+ Extensions: Complete extension suite included
    - ⚡ Smart Detection: Automatically detects project structure
    - 🚀 Interactive CLI: Guided setup with rich terminal UI
    - 🔄 Copy & Share: Transfer documentation setups between projects

Quick Start:
    1. Install: pip install pydvlp-docs
    2. Initialize: pydvlp-docs setup-general /path/to/your/project
    3. Build: cd /path/to/your/project/docs && make html

    Your documentation is ready at docs/build/html/index.html!

Examples:
    Set up documentation for any Python project:

    >>> from pydvlp_docs.general_setup import setup_project_docs
    >>> result = setup_project_docs("/path/to/project")
    >>> print(f"Documentation created at: {result['target_dir']}")

    Or use the configuration directly:

    >>> from pydvlp_docs.config import get_haive_config
    >>> config = get_haive_config(
    ...     package_name="my-package",
    ...     package_path="../../src"
    ... )
    >>> globals().update(config)
"""

__version__ = "0.1.3"
__author__ = "William R. Astley"

# Export main configuration functions
from .config import get_central_hub_config, get_haive_config

# Export generalized setup functions
from .general_setup import ProjectDetector, GeneralDocumentationSetup, setup_project_docs

# Export builders and utilities (if available)
try:
    from .build_error_classifier import BuildErrorClassifier, ErrorSeverity
    from .builders import (
        BaseDocumentationBuilder,
        CustomConfigBuilder,
        MonorepoBuilder,
        SinglePackageBuilder,
        get_builder,
    )
    from .utils import HaiveDocumentationManager

    __all__ = [
        "get_haive_config",
        "get_central_hub_config", 
        "ProjectDetector",
        "GeneralDocumentationSetup",
        "setup_project_docs",
        "BaseDocumentationBuilder",
        "SinglePackageBuilder",
        "MonorepoBuilder",
        "CustomConfigBuilder",
        "get_builder",
        "BuildErrorClassifier",
        "ErrorSeverity",
        "HaiveDocumentationManager",
    ]
except ImportError:
    # CLI dependencies might not be installed
    __all__ = [
        "get_haive_config", 
        "get_central_hub_config",
        "ProjectDetector",
        "GeneralDocumentationSetup", 
        "setup_project_docs"
    ]

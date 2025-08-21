"""Central documentation hub configuration using sphinx-collections.

This configuration aggregates documentation from all packages into
a single unified documentation site.
"""

import os
import sys
from pathlib import Path

# Add pydvlp-docs to path if needed
sys.path.insert(0, os.path.abspath("."))

# Import the complete shared configuration
from pydvlp_docs.config import get_central_hub_config

# Get central hub configuration with sphinx-collections support
config = get_central_hub_config()

# Apply all configuration
globals().update(config)

# Override for central hub
project = "Haive AI Agent Framework"
html_title = "Haive Documentation Hub"

# Sphinx-collections configuration for aggregating packages
collections = {
    # Core packages
    "haive-core": {
        "driver": "copy_folder",
        "source": "../packages/haive-core/docs/build/html",
        "target": "packages/haive-core",
        "active": True,
    },
    "haive-agents": {
        "driver": "copy_folder",
        "source": "../packages/haive-agents/docs/build/html",
        "target": "packages/haive-agents",
        "active": True,
    },
    "haive-tools": {
        "driver": "copy_folder",
        "source": "../packages/haive-tools/docs/build/html",
        "target": "packages/haive-tools",
        "active": True,
    },
    "haive-dataflow": {
        "driver": "copy_folder",
        "source": "../packages/haive-dataflow/docs/build/html",
        "target": "packages/haive-dataflow",
        "active": True,
    },
    "haive-games": {
        "driver": "copy_folder",
        "source": "../packages/haive-games/docs/build/html",
        "target": "packages/haive-games",
        "active": True,
    },
    "haive-mcp": {
        "driver": "copy_folder",
        "source": "../packages/haive-mcp/docs/build/html",
        "target": "packages/haive-mcp",
        "active": True,
    },
    "haive-prebuilt": {
        "driver": "copy_folder",
        "source": "../packages/haive-prebuilt/docs/build/html",
        "target": "packages/haive-prebuilt",
        "active": True,
    },
    # Development tools
    "haive-cli": {
        "driver": "copy_folder",
        "source": "../tools/haive-cli/docs/build/html",
        "target": "tools/haive-cli",
        "active": True,
    },
    "haive-dev": {
        "driver": "copy_folder",
        "source": "../tools/haive-dev/docs/build/html",
        "target": "tools/haive-dev",
        "active": True,
    },
    "haive-testing": {
        "driver": "copy_folder",
        "source": "../tools/haive-testing/docs/build/html",
        "target": "tools/haive-testing",
        "active": True,
    },
}

# Add collections to extensions if not already there
if "sphinxcontrib.collections" not in extensions:
    extensions.append("sphinxcontrib.collections")

# Custom index for the hub
html_additional_pages = {
    "index": "hub_index.html",
}

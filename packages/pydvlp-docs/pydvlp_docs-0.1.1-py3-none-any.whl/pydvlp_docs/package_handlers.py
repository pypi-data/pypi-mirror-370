"""Package-specific handlers for different Python project types."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import tomlkit
import yaml


class PackageHandler:
    """Base handler for different package types."""

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.package_info = self.detect_package_info()

    def detect_package_info(self) -> Dict[str, Any]:
        """Detect package information."""
        info = {
            "name": self.project_path.name,
            "type": "unknown",
            "version": "0.1.0",
            "packages": [],
            "source_dirs": [],
        }

        # Check for various package files
        if (self.project_path / "pyproject.toml").exists():
            info.update(self._parse_pyproject())
        elif (self.project_path / "setup.py").exists():
            info.update(self._parse_setuppy())
        elif (self.project_path / "setup.cfg").exists():
            info.update(self._parse_setupcfg())

        # Detect source directories
        info["source_dirs"] = self._find_source_dirs()

        return info

    def _parse_pyproject(self) -> Dict[str, Any]:
        """Parse pyproject.toml for package info."""
        with open(self.project_path / "pyproject.toml") as f:
            data = tomlkit.load(f)

        info = {"type": "pyproject"}

        # Check for Poetry
        if "poetry" in data.get("tool", {}):
            poetry = data["tool"]["poetry"]
            info.update(
                {
                    "manager": "poetry",
                    "name": poetry.get("name", self.project_path.name),
                    "version": poetry.get("version", "0.1.0"),
                    "packages": poetry.get("packages", []),
                }
            )

        # Check for Hatch
        elif "hatch" in data.get("tool", {}):
            info["manager"] = "hatch"
            if "project" in data:
                info["name"] = data["project"].get("name", self.project_path.name)
                info["version"] = data["project"].get("version", "0.1.0")

        # Check for PDM
        elif "pdm" in data.get("tool", {}):
            info["manager"] = "pdm"
            if "project" in data:
                info["name"] = data["project"].get("name", self.project_path.name)
                info["version"] = data["project"].get("version", "0.1.0")

        # Standard PEP 621
        elif "project" in data:
            info.update(
                {
                    "manager": "pep621",
                    "name": data["project"].get("name", self.project_path.name),
                    "version": data["project"].get("version", "0.1.0"),
                }
            )

        return info

    def _parse_setuppy(self) -> Dict[str, Any]:
        """Parse setup.py for package info."""
        # This is tricky without executing the file
        # For now, return basic info
        return {
            "type": "setuptools",
            "manager": "setuptools",
        }

    def _parse_setupcfg(self) -> Dict[str, Any]:
        """Parse setup.cfg for package info."""
        import configparser

        config = configparser.ConfigParser()
        config.read(self.project_path / "setup.cfg")

        info = {"type": "setuptools", "manager": "setuptools"}

        if "metadata" in config:
            info["name"] = config["metadata"].get("name", self.project_path.name)
            info["version"] = config["metadata"].get("version", "0.1.0")

        return info

    def _find_source_dirs(self) -> List[str]:
        """Find Python source directories."""
        dirs = []

        # Check standard locations
        if (self.project_path / "src").exists():
            dirs.append("src")

        # Check for direct package directories
        for item in self.project_path.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                if item.name not in ["tests", "docs", "examples", "scripts"]:
                    dirs.append(item.name)

        # If nothing found, assume current directory
        if not dirs:
            dirs.append(".")

        return dirs

    def get_autoapi_dirs(self) -> List[str]:
        """Get directories for AutoAPI to scan."""
        dirs = []

        for source_dir in self.package_info["source_dirs"]:
            if source_dir == ".":
                dirs.append("../..")
            elif source_dir == "src":
                dirs.append("../../src")
            else:
                dirs.append(f"../../{source_dir}")

        return dirs

    def get_dependencies(self) -> Dict[str, str]:
        """Get documentation dependencies for this package type."""
        # Base dependencies for all packages
        deps = {
            "sphinx": "^8.2.3",
            "sphinx-autoapi": "^3.6.0",
            "furo": "^2024.8.6",
            "myst-parser": "^4.0.1",
        }

        # Add manager-specific dependencies
        if self.package_info.get("manager") == "poetry":
            deps["sphinxcontrib-poetry"] = "^0.1.0"

        return deps


class HaivePackageHandler(PackageHandler):
    """Special handler for Haive packages."""

    def __init__(self, project_path: Path):
        super().__init__(project_path)
        self.is_haive_package = self._detect_haive_package()

    def _detect_haive_package(self) -> bool:
        """Detect if this is a Haive package."""
        # Check package name
        if self.package_info["name"].startswith("haive-"):
            return True

        # Check imports
        for source_dir in self.package_info["source_dirs"]:
            src_path = self.project_path / source_dir
            if src_path.exists():
                for py_file in src_path.rglob("*.py"):
                    try:
                        content = py_file.read_text()
                        if "from haive" in content or "import haive" in content:
                            return True
                    except:
                        pass

        return False

    def get_dependencies(self) -> Dict[str, str]:
        """Get Haive-specific documentation dependencies."""
        deps = super().get_dependencies()

        # Add Haive-specific dependencies
        deps.update(
            {
                "pydvlp-docs": {
                    "path": "../../tools/pydvlp-docs",
                    "develop": True,
                },
                "sphinxcontrib-mermaid": "^1.0.0",
                "sphinx-copybutton": "^0.5.2",
                "sphinx-togglebutton": "^0.3.2",
            }
        )

        return deps

    def get_theme_config(self) -> Dict[str, Any]:
        """Get Haive-specific theme configuration."""
        # Package-specific colors
        package_colors = {
            "haive-core": {"primary": "#dc3545", "secondary": "#c82333"},
            "haive-agents": {"primary": "#28a745", "secondary": "#218838"},
            "haive-tools": {"primary": "#17a2b8", "secondary": "#138496"},
            "haive-dataflow": {"primary": "#ffc107", "secondary": "#e0a800"},
            "haive-games": {"primary": "#6610f2", "secondary": "#520dc2"},
            "haive-mcp": {"primary": "#e83e8c", "secondary": "#d91a72"},
            "haive-prebuilt": {"primary": "#20c997", "secondary": "#1aa179"},
        }

        colors = package_colors.get(
            self.package_info["name"], {"primary": "#007bff", "secondary": "#0056b3"}
        )

        return {
            "theme": "furo",
            "theme_options": {
                "light_css_variables": {
                    "color-brand-primary": colors["primary"],
                    "color-brand-content": colors["secondary"],
                },
                "dark_css_variables": {
                    "color-brand-primary": colors["primary"],
                    "color-brand-content": colors["secondary"],
                },
            },
        }


class MonorepoHandler(PackageHandler):
    """Handler for monorepo projects."""

    def __init__(self, project_path: Path):
        super().__init__(project_path)
        self.packages = self._discover_packages()

    def _discover_packages(self) -> List[Dict[str, Any]]:
        """Discover all packages in the monorepo."""
        packages = []

        # Check standard monorepo locations
        for location in ["packages", "libs", "apps", "services"]:
            pkg_dir = self.project_path / location
            if pkg_dir.exists():
                for item in pkg_dir.iterdir():
                    if item.is_dir() and not item.name.startswith("."):
                        handler = PackageHandler(item)
                        packages.append(
                            {
                                "path": item,
                                "name": handler.package_info["name"],
                                "info": handler.package_info,
                            }
                        )

        return packages

    def get_collections_config(self) -> Dict[str, Any]:
        """Get sphinx-collections configuration for monorepo."""
        collections = {}

        for pkg in self.packages:
            name = pkg["name"]
            path = pkg["path"].relative_to(self.project_path)

            collections[name] = {
                "driver": "copy_folder",
                "source": str(path / "docs" / "build" / "html"),
                "target": f"packages/{name}",
            }

        return collections

    def generate_index_content(self) -> str:
        """Generate index.rst content for monorepo."""
        content = f"""
{self.package_info['name']} Documentation
{'=' * (len(self.package_info['name']) + 14)}

Welcome to the documentation for {self.package_info['name']}.

Packages
--------

.. toctree::
   :maxdepth: 1
   :caption: Available Packages:

"""

        for pkg in self.packages:
            content += f"   {pkg['name']} <packages/{pkg['name']}/index>\n"

        content += """

Quick Links
-----------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
"""

        return content


def get_package_handler(project_path: Path) -> PackageHandler:
    """Get appropriate handler for the project."""
    # Check if monorepo
    if any((project_path / loc).exists() for loc in ["packages", "libs", "apps"]):
        return MonorepoHandler(project_path)

    # Check if Haive package
    handler = HaivePackageHandler(project_path)
    if handler.is_haive_package:
        return handler

    # Default handler
    return PackageHandler(project_path)

"""
Template manager for generating documentation content.

Handles rendering of Jinja2 templates for documentation sections.
"""

from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, Template


class TemplateManager:
    """Manages documentation templates and rendering."""

    def __init__(self, project_path: Path, project_info: Dict[str, Any]):
        """Initialize template manager.

        Args:
            project_path: Root path of the project
            project_info: Project metadata (name, structure, etc.)
        """
        self.project_path = project_path
        self.project_info = project_info
        self.template_dir = Path(__file__).parent / "templates" / "doc_templates"
        self.all_templates_dir = Path(__file__).parent / "templates"

        # Set up Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Common context for all templates
        self.base_context = {
            "project_name": project_info.get("name", "Project"),
            "package_name": self._get_package_name(),
            "github_org": self._extract_github_org(),
            "github_repo": project_info.get("name", "repo"),
        }

    def _get_package_name(self) -> str:
        """Get the package name for pip install."""
        name = self.project_info.get("name", "project")
        return name.lower().replace(" ", "-")

    def _extract_github_org(self) -> str:
        """Extract GitHub organization from git remote or use default."""
        # TODO: Implement git remote parsing
        return "your-org"

    def _write_file(self, file_path: str, content: str) -> None:
        """Write content to file with proper directory creation.

        Args:
            file_path: Path to the file to write
            content: Content to write to the file
        """
        output_file = Path(file_path)
        if not output_file.is_absolute():
            output_file = self.project_path / file_path
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(content, encoding="utf-8")

    def render_template(
        self, template_name: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Render a template with the given context.

        Args:
            template_name: Name of the template file
            context: Additional context to merge with base context

        Returns:
            Rendered template content
        """
        template = self.env.get_template(template_name)
        full_context = {**self.base_context, **(context or {})}
        return template.render(**full_context)

    def write_template(
        self,
        template_name: str,
        output_path: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Render and write a template to a file.

        Args:
            template_name: Name of the template file
            output_path: Relative path from project root for output
            context: Additional context to merge with base context
        """
        content = self.render_template(template_name, context)

        output_file = self.project_path / output_path
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(content)

    def create_section_index(self, section_type: str, output_dir: str) -> None:
        """Create an index.rst for a documentation section.

        Args:
            section_type: Type of section ('guides', 'examples', 'tutorials', 'cli')
            output_dir: Directory path relative to project root
        """
        section_configs = {
            "guides": {
                "title": "User Guides",
                "name": "guides",
                "has_quickstart": True,
            },
            "examples": {
                "title": "Examples",
                "name": "examples",
            },
            "tutorials": {
                "title": "Tutorials",
                "name": "tutorials",
            },
            "cli": {
                "title": "CLI Reference",
                "name": "CLI reference",
            },
        }

        config = section_configs.get(section_type, {})
        context = {
            "section_title": config.get("title", section_type.title()),
            "section_name": config.get("name", section_type),
            "section_type": section_type,
            "has_quickstart": config.get("has_quickstart", False),
        }

        self.write_template(
            "section_index.rst.jinja2", f"{output_dir}/index.rst", context
        )

    def create_quickstart(
        self, output_path: str = "docs/source/guides/quickstart.rst"
    ) -> None:
        """Create a quickstart guide.

        Args:
            output_path: Path for the quickstart file
        """
        self.write_template("quickstart.rst.jinja2", output_path)

    def create_installation(
        self, output_path: str = "docs/source/guides/installation.rst"
    ) -> None:
        """Create an installation guide.

        Args:
            output_path: Path for the installation file
        """
        self.write_template("installation.rst.jinja2", output_path)

    def create_configuration(
        self, output_path: str = "docs/source/guides/configuration.rst"
    ) -> None:
        """Create a configuration guide.

        Args:
            output_path: Path for the configuration file
        """
        self.write_template("configuration.rst.jinja2", output_path)

    def create_all_sections(self, doc_config: Dict[str, bool]) -> None:
        """Create all enabled documentation sections.

        Args:
            doc_config: Configuration dict with section flags
        """
        if doc_config.get("with_guides", False):
            self.create_section_index("guides", "docs/source/guides")
            self.create_quickstart()
            self.create_installation()
            self.create_configuration()

        if doc_config.get("with_examples", False):
            self.create_section_index("examples", "docs/source/examples")

        if doc_config.get("with_cli", False):
            self.create_section_index("cli", "docs/source/cli")

        if doc_config.get("with_tutorials", False):
            self.create_section_index("tutorials", "docs/source/tutorials")

    def create_central_hub_config(
        self,
        output_path: str = "docs/source/conf.py",
        collections_config: Optional[Dict[str, Any]] = None,
        custom_extensions: Optional[list] = None,
    ) -> None:
        """Create central hub configuration file.

        Args:
            output_path: Path for the conf.py file
            collections_config: Custom collections configuration
            custom_extensions: Additional Sphinx extensions
        """
        # Use all templates directory for this
        env = Environment(
            loader=FileSystemLoader(self.all_templates_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        template = env.get_template("central_hub_conf.py.jinja2")

        context = {
            **self.base_context,
            "collections_paths": collections_config,
            "custom_extensions": custom_extensions or [],
            "source_path": "..",  # Default relative path
        }

        self._write_file(output_path, template.render(context))

    def create_central_hub_index(
        self,
        output_path: str = "docs/source/index.rst",
        package_info: Optional[Dict[str, Dict[str, Any]]] = None,
        include_tools: bool = False,
    ) -> None:
        """Create central hub index.rst with package navigation.

        Args:
            output_path: Path for the index.rst file
            package_info: Package metadata for organized display
            include_tools: Whether to include tools section
        """
        # Use all templates directory for this
        env = Environment(
            loader=FileSystemLoader(self.all_templates_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        template = env.get_template("central_hub_index.rst.jinja2")

        context = {
            **self.base_context,
            "package_info": package_info,
            "include_tools": include_tools,
        }

        self._write_file(output_path, template.render(context))

    def auto_detect_packages(
        self, packages_dir: str = "packages"
    ) -> Dict[str, Dict[str, Any]]:
        """Auto-detect packages for collections configuration.

        Args:
            packages_dir: Directory containing packages

        Returns:
            Dictionary with collections configuration
        """
        packages_path = self.project_path / packages_dir
        collections = {}

        if packages_path.exists():
            for package_dir in packages_path.iterdir():
                if package_dir.is_dir() and not package_dir.name.startswith("."):
                    docs_path = package_dir / "docs" / "build" / "html"
                    relative_source = (
                        f"../{packages_dir}/{package_dir.name}/docs/build/html"
                    )

                    collections[package_dir.name] = {
                        "driver": "copy_folder",
                        "source": relative_source,
                        "target": f"_collections/packages/{package_dir.name}",
                        "active": True,
                    }

        return collections

    def create_unified_documentation_setup(
        self,
        packages_dir: str = "packages",
        hub_dir: str = "docs",
        include_tools: bool = False,
    ) -> None:
        """Create complete unified documentation setup.

        Args:
            packages_dir: Directory containing packages
            hub_dir: Directory for central hub documentation
            include_tools: Whether to include tools in navigation
        """
        # Auto-detect packages
        collections_config = self.auto_detect_packages(packages_dir)

        # Create hub directory structure
        hub_path = self.project_path / hub_dir
        source_path = hub_path / "source"
        source_path.mkdir(parents=True, exist_ok=True)

        # Create conf.py
        self.create_central_hub_config(
            output_path=str(source_path / "conf.py"),
            collections_config=collections_config,
        )

        # Create index.rst
        self.create_central_hub_index(
            output_path=str(source_path / "index.rst"), include_tools=include_tools
        )

        # Create basic structure
        for subdir in ["_static", "_templates"]:
            (source_path / subdir).mkdir(exist_ok=True)

        print(f"✅ Created unified documentation setup in {hub_dir}/")
        print(f"📦 Detected {len(collections_config)} packages")
        print("🔨 Next steps:")
        print(
            f"   1. Build individual package docs: cd {packages_dir}/package-name/docs && sphinx-build -b html source build/html"
        )
        print(
            f"   2. Build central hub: cd {hub_dir} && sphinx-build -b html source build"
        )

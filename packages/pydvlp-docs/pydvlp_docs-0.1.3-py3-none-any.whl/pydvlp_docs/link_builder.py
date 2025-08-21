"""Link existing built documentation into a central hub."""

import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

import click


class DocumentationLinker:
    """Links existing built documentation from multiple packages."""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.packages_dir = root_path / "packages"
        self.root_docs = root_path / "docs"

    def discover_built_docs(self) -> Dict[str, Dict[str, Path]]:
        """Discover all packages with built documentation."""
        packages = {}

        if not self.packages_dir.exists():
            return packages

        for package_dir in self.packages_dir.iterdir():
            if not package_dir.is_dir() or package_dir.name.startswith("."):
                continue

            # Check for built docs
            html_dir = package_dir / "docs" / "build" / "html"
            objects_inv = html_dir / "objects.inv"

            if html_dir.exists() and objects_inv.exists():
                packages[package_dir.name] = {
                    "path": package_dir,
                    "html_dir": html_dir,
                    "objects_inv": objects_inv,
                    "index": html_dir / "index.html",
                }

        return packages

    def create_intersphinx_mapping(
        self, packages: Dict[str, Dict[str, Path]]
    ) -> Dict[str, tuple]:
        """Create intersphinx mapping for cross-referencing."""
        mapping = {
            "python": ("https://docs.python.org/3", None),
            "sphinx": ("https://www.sphinx-doc.org/en/master", None),
        }

        # Add each package
        for name, info in packages.items():
            # Use relative paths from hub docs build to package docs
            relative_path = f"../../../packages/{name}/docs/build/html"
            mapping[name] = (relative_path, None)

        return mapping

    def create_hub_index(self, packages: Dict[str, Dict[str, Path]]) -> str:
        """Create a hub index.rst that links to all packages."""
        content = """Haive Documentation Hub
=======================

Welcome to the Haive AI Agent Framework documentation!

This hub provides centralized access to all package documentation with cross-referencing capabilities.

Start Your Journey
==================

.. grid:: 1 2 2 3
   :gutter: 3

   .. grid-item-card:: 🚀 Build Your First Agent
      :link: tutorials/research-assistant
      :shadow: md
      :class-card: start-card
      
      **Quick Start Tutorial** - Create a research assistant in 15 minutes
      
      *Build → Test → Deploy*

   .. grid-item-card:: 📚 Browse All Tutorials  
      :link: tutorials/index
      :shadow: md
      :class-card: tutorials-card
      
      **Step-by-step guides** - From basics to advanced patterns
      
      *Learn by doing*

   .. grid-item-card:: 🔍 Explore Packages
      :link: #framework-packages
      :shadow: md
      :class-card: explore-card
      
      **Framework components** - Find the right tools for your project
      
      *Mix and match*

Framework Packages
==================

Click any package to explore its documentation:

.. grid:: 2 2 3 3
   :gutter: 3
   
"""

        # Add each package as a card
        for name, info in sorted(packages.items()):
            # Count HTML files for stats
            html_files = list(info["html_dir"].glob("**/*.html"))

            # Create better display name and relative path
            display_name = self._get_display_name(name)
            # Calculate correct relative path from hub docs/build/html to package docs
            relative_path = f"../../../packages/{name}/docs/build/html/index.html"
            content += f"""   .. grid-item-card:: {display_name}
      :link: {relative_path}
      :shadow: md
      
      {self._get_package_description(name)}
      
      **{len(html_files)}** documentation pages
      
"""

        # Add comprehensive navigation
        content += """

Documentation Navigation
=======================

.. toctree::
   :maxdepth: 2
   :caption: 📚 Learning
   
   tutorials/index

.. toctree::
   :maxdepth: 1
   :caption: 🔍 Reference
   
   search
   genindex

Quick Links
===========

* 🔍 :ref:`search` - Search across all packages
* 📖 :ref:`genindex` - Complete API index  
* 🔗 Cross-package references work automatically

**Need help?** Use the search box above or browse the tutorials to get started.
"""
        return content

    def _get_display_name(self, name: str) -> str:
        """Get user-friendly display name for packages."""
        display_names = {
            "haive-core": "Core Framework (haive-core)",
            "haive-agents": "Agents (haive-agents)",
            "haive-tools": "Tools (haive-tools)",
            "haive-games": "Games (haive-games)",
            "haive-mcp": "MCP Integration (haive-mcp)",
            "haive-dataflow": "Data Flow (haive-dataflow)",
            "haive-prebuilt": "Prebuilt (haive-prebuilt)",
            "haive-models": "Models (haive-models)",
        }
        return display_names.get(name, name)

    def _get_package_description(self, name: str) -> str:
        """Get package description with use cases and key features."""
        descriptions = {
            "haive-core": "⚙️ **Foundation** - Agent engine, state management, and core infrastructure",
            "haive-agents": "🤖 **Ready-to-Use Agents** - ReactAgent, SimpleAgent, and specialized implementations",
            "haive-tools": "🛠️ **Tool Integration** - Web search, APIs, file operations, and utilities",
            "haive-games": "🎮 **Game Environments** - Chess, strategy games, and multi-agent competitions",
            "haive-mcp": "🔗 **External Connections** - Model Context Protocol for tool integration",
            "haive-dataflow": "📊 **Data Processing** - Streaming, pipelines, and data transformation",
            "haive-prebuilt": "🚀 **Quick Deploy** - Pre-configured agents ready for production",
            "haive-models": "🧠 **Model Hub** - LLM integrations and model configurations",
        }
        return descriptions.get(name, f"Documentation for {name}")

    def create_hub_config(self, packages: Dict[str, Dict[str, Path]]) -> str:
        """Create hub conf.py with theming inherited from individual packages."""
        intersphinx = self.create_intersphinx_mapping(packages)

        content = f'''"""
Haive Documentation Hub Configuration.

This configuration inherits theming and styling from individual packages
while using only hub-safe extensions for reliability.
"""

import os
import sys
from pathlib import Path

# Import theming configuration from pydvlp-docs
from pydvlp_docs.config import get_haive_config

# Get base configuration for theming inheritance
base_config = get_haive_config("haive-hub", "", is_central_hub=True)

# Project information
project = "Haive AI Agent Framework" 
author = "Haive Team"
copyright = "2025, Haive Team"
release = "0.1.0"

# Hub-safe extensions (curated from full suite)
extensions = [
    # Core documentation
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon", 
    "sphinx.ext.viewcode", 
    "sphinx.ext.intersphinx",
    # Content & Design - Essential theming extensions
    "myst_parser",
    "sphinx_design",  # Grid cards, badges, buttons
    "sphinx_togglebutton",  # Collapsible sections
    "sphinx_copybutton",  # Code copy buttons
    "sphinx_tabs.tabs",  # Tabbed content
    # Social & SEO - Safe utilities
    "sphinxext.opengraph",  # Social media cards
    "sphinx_favicon",  # Consistent branding
    "sphinx_sitemap",  # SEO optimization
    "sphinx_last_updated_by_git",  # Git integration
    "notfound.extension",  # Custom 404 pages
]

# Intersphinx mapping to all packages
intersphinx_mapping = {repr(intersphinx)}

# INHERIT THEMING from individual packages
html_theme = base_config.get("html_theme", "furo")
html_title = "Haive Documentation Hub"

# Get theme options from base config and enhance for hub
html_theme_options = base_config.get("html_theme_options", {{}}).copy()
html_theme_options.update({{
    "announcement": "🚀 Central hub for all Haive AI Agent Framework documentation",
    "source_directory": "docs/",
    "navigation_with_keys": True,
    "top_of_page_buttons": ["view"],
}})

# INHERIT STYLING from individual packages  
html_static_path = base_config.get("html_static_path", ["_static"])
html_css_files = ["css/hub.css"]  # Hub-specific CSS

# Add package CSS files if they exist
if "html_css_files" in base_config:
    html_css_files.extend(base_config["html_css_files"])

templates_path = base_config.get("templates_path", ["_templates"])

# INHERIT MYST CONFIGURATION from individual packages
myst_enable_extensions = base_config.get("myst_enable_extensions", [
    "deflist", "tasklist", "html_image", "colon_fence",
    "smartquotes", "replacements", "linkify", "strikethrough",
    "attrs_inline", "attrs_block"
])
myst_heading_anchors = base_config.get("myst_heading_anchors", 3)
myst_fence_as_directive = base_config.get("myst_fence_as_directive", ["mermaid", "note", "warning"])

# INHERIT SPHINX DESIGN CONFIGURATION
sd_fontawesome_latex = base_config.get("sd_fontawesome_latex", True)

# INHERIT COPY BUTTON CONFIGURATION  
copybutton_prompt_text = base_config.get("copybutton_prompt_text", r">>> |\\.\\.\\. |\\$ |In \\[\\d*\\]: | {{2,5}}\\.\\.\\.: | {{5,8}}: ")
copybutton_prompt_is_regexp = base_config.get("copybutton_prompt_is_regexp", True)
copybutton_remove_prompts = base_config.get("copybutton_remove_prompts", True)

# INHERIT TOGGLE BUTTON CONFIGURATION
togglebutton_hint = base_config.get("togglebutton_hint", "Click to expand")
togglebutton_hint_hide = base_config.get("togglebutton_hint_hide", "Click to collapse")

# INHERIT OPENGRAPH CONFIGURATION
ogp_site_url = "https://docs.haive.ai/"
ogp_site_name = base_config.get("ogp_site_name", "Haive AI Agent Framework")
ogp_site_description = "Central hub for all Haive AI Agent Framework documentation"
ogp_type = base_config.get("ogp_type", "website")
ogp_locale = base_config.get("ogp_locale", "en_US")

# INHERIT GIT INTEGRATION
sphinx_git_show_branch = base_config.get("sphinx_git_show_branch", True)
sphinx_git_show_tags = base_config.get("sphinx_git_show_tags", True)

# INHERIT 404 PAGE CONFIGURATION with hub-specific content
notfound_context = {{
    "title": "Page Not Found",
    "body": """
<h1>🚀 Oops! Page Not Found</h1>
<p>The page you're looking for seems to have wandered off into the documentation cosmos.</p>

<div class="admonition tip">
<p class="admonition-title">Try these options:</p>
<ul>
<li><strong>Search:</strong> Use the search box above to find what you need</li>
<li><strong>Packages:</strong> Browse individual <a href="packages/index.html">package documentation</a></li>
<li><strong>Home:</strong> Return to the <a href="index.html">main documentation hub</a></li>
<li><strong>API Reference:</strong> Check the complete API documentation in each package</li>
</ul>
</div>

<p>Still can't find what you're looking for? <a href="https://github.com/haive-ai/haive/issues">Report an issue</a> and we'll help you out!</p>
""",
}}
notfound_template = base_config.get("notfound_template", "page.html")
notfound_no_urls_prefix = base_config.get("notfound_no_urls_prefix", True)

# INHERIT SITEMAP CONFIGURATION
sitemap_url_scheme = base_config.get("sitemap_url_scheme", "{{link}}")

# INHERIT GENERAL CONFIGURATION
exclude_patterns = base_config.get("exclude_patterns", [
    "_build", "Thumbs.db", ".DS_Store"
])
exclude_patterns.append("autoapi")  # Exclude autoapi for hub

add_module_names = base_config.get("add_module_names", False)
toc_object_entries_show_parents = base_config.get("toc_object_entries_show_parents", "hide")

# INHERIT TOC CONFIGURATION
navigation_with_keys = base_config.get("navigation_with_keys", True)
toctree_maxdepth = base_config.get("toctree_maxdepth", 4)
toctree_collapse = base_config.get("toctree_collapse", False)
toctree_titles_only = base_config.get("toctree_titles_only", False)
'''
        return content

    def create_hub_structure(self):
        """Create the complete hub structure."""
        # Create directories
        source_dir = self.root_docs / "source"
        source_dir.mkdir(parents=True, exist_ok=True)

        static_dir = source_dir / "_static"
        static_dir.mkdir(exist_ok=True)

        css_dir = static_dir / "css"
        css_dir.mkdir(exist_ok=True)

        # Discover packages
        packages = self.discover_built_docs()

        if not packages:
            click.echo("❌ No packages with built documentation found!")
            return False

        click.echo(f"📦 Found {len(packages)} packages with built docs:")
        for name in sorted(packages.keys()):
            click.echo(f"   ✅ {name}")

        # Create index
        index_content = self.create_hub_index(packages)
        index_path = source_dir / "index.rst"
        index_path.write_text(index_content)
        click.echo("✅ Created hub index.rst")

        # Create conf.py
        conf_content = self.create_hub_config(packages)
        conf_path = source_dir / "conf.py"
        conf_path.write_text(conf_content)
        click.echo("✅ Created hub conf.py with intersphinx mappings")

        # Create CSS
        css_content = """
/* Hub documentation styles */

/* Hide the ugly back-to-top button completely */
.back-to-top {
    display: none !important;
}

/* Clean up TOC tree - hide empty sections */
.sidebar-tree .toctree-l1:has(ul:empty) {
    display: none;
}

/* Better card styling */
.sd-card {
    height: 100%;
    transition: all 0.2s ease;
    cursor: pointer;
}

.sd-card-body {
    display: flex;
    flex-direction: column;
    padding: 1.5rem;
}

.sd-card-body > :last-child {
    margin-top: auto;
}

/* Enhanced hover effects for all cards */
.sd-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

/* Journey cards with distinct styling */
.start-card {
    border-left: 4px solid #10b981 !important; /* Green */
    background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%);
}

.tutorials-card {
    border-left: 4px solid #3b82f6 !important; /* Blue */
    background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
}

.explore-card {
    border-left: 4px solid #f59e0b !important; /* Orange */
    background: linear-gradient(135deg, #fffbeb 0%, #ffffff 100%);
}

/* Package cards with category styling */
.sd-card[class*="haive-core"] {
    border-left: 4px solid #6366f1; /* Indigo - Foundation */
}

.sd-card[class*="haive-agents"] {
    border-left: 4px solid #10b981; /* Green - Ready to use */
}

.sd-card[class*="haive-tools"] {
    border-left: 4px solid #f59e0b; /* Orange - Tools */
}

.sd-card[class*="haive-games"] {
    border-left: 4px solid #ec4899; /* Pink - Games */
}

.sd-card[class*="haive-mcp"] {
    border-left: 4px solid #8b5cf6; /* Purple - Connections */
}

.sd-card[class*="haive-dataflow"] {
    border-left: 4px solid #06b6d4; /* Cyan - Data */
}

.sd-card[class*="haive-prebuilt"] {
    border-left: 4px solid #84cc16; /* Lime - Quick deploy */
}

.sd-card[class*="haive-models"] {
    border-left: 4px solid #f97316; /* Orange-red - Models */
}

/* Dark mode adjustments */
body[data-theme="dark"] .start-card {
    background: linear-gradient(135deg, #064e3b 0%, #1f2937 100%);
}

body[data-theme="dark"] .tutorials-card {
    background: linear-gradient(135deg, #1e3a8a 0%, #1f2937 100%);
}

body[data-theme="dark"] .explore-card {
    background: linear-gradient(135deg, #92400e 0%, #1f2937 100%);
}

/* Better typography for cards */
.sd-card-title {
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    margin-bottom: 0.5rem !important;
}

.sd-card-text {
    font-size: 0.9rem;
    line-height: 1.4;
}

/* Icon spacing */
.sd-card-title::before {
    margin-right: 0.5rem;
}

/* Remove redundant sections from sidebar */
.sidebar-tree p.caption:has(+ ul:empty) {
    display: none;
}

.sidebar-tree ul:empty {
    display: none;
}

/* Cleaner search box */
.sidebar-search {
    margin-bottom: 1rem;
}

/* Better section headers */
section h1, section h2 {
    margin-top: 2rem;
    margin-bottom: 1rem;
}

section h1:first-child, section h2:first-child {
    margin-top: 0;
}
"""
        css_path = css_dir / "hub.css"
        css_path.write_text(css_content)

        # Create packages index
        packages_dir = source_dir / "packages"
        packages_dir.mkdir(exist_ok=True)

        packages_index = """Package Documentation
====================

Detailed documentation for each package:

.. toctree::
   :maxdepth: 1
   
"""
        for name in sorted(packages.keys()):
            # Path from hub docs/source/packages/index.rst to package docs
            packages_index += (
                f"   {name} <../../../../packages/{name}/docs/build/html/index>\n"
            )

        (packages_dir / "index.rst").write_text(packages_index)

        return True

    def build_hub(self, open_browser: bool = False):
        """Build the hub documentation.

        Args:
            open_browser: Whether to open the documentation in browser after building
        """
        if not self.create_hub_structure():
            return False

        # Build command
        cmd = [
            "sphinx-build",
            "-b",
            "html",
            str(self.root_docs / "source"),
            str(self.root_docs / "build" / "html"),
        ]

        click.echo("\n🔨 Building documentation hub...")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                click.echo("✅ Hub documentation built successfully!")
                html_path = self.root_docs / "build" / "html" / "index.html"
                click.echo(f"📖 View at: {html_path}")

                # Generate summary report
                self._generate_summary_report()

                # Open in browser if requested
                if open_browser:
                    import webbrowser

                    webbrowser.open(f"file://{html_path}")
                    click.echo("🌐 Opened documentation in browser")

                return True
            else:
                click.echo("❌ Build failed:")
                click.echo(result.stderr)
                return False

        except Exception as e:
            click.echo(f"❌ Build error: {e}")
            return False

    def _generate_summary_report(self):
        """Generate a summary report of the documentation hub."""
        packages = self.discover_built_docs()

        click.echo("\n📊 Documentation Hub Summary:")
        click.echo("=" * 50)

        total_pages = 0
        for name, info in sorted(packages.items()):
            html_files = list(info["html_dir"].glob("**/*.html"))
            page_count = len(html_files)
            total_pages += page_count
            click.echo(f"  📦 {name:<20} {page_count:>5} pages")

        click.echo("=" * 50)
        click.echo(f"  📚 Total:              {total_pages:>5} pages")
        click.echo(f"  🔗 Intersphinx enabled: ✅")
        click.echo(f"  🌐 Cross-references:    ✅")

    def update_hub(self):
        """Update the hub without full rebuild (only regenerate index)."""
        packages = self.discover_built_docs()

        if not packages:
            click.echo("❌ No packages with built documentation found!")
            return False

        click.echo(f"📦 Updating hub for {len(packages)} packages...")

        # Update index.rst
        source_dir = self.root_docs / "source"
        if source_dir.exists():
            index_content = self.create_hub_index(packages)
            index_path = source_dir / "index.rst"
            index_path.write_text(index_content)
            click.echo("✅ Updated hub index.rst")

            # Quick rebuild (only HTML, not full rebuild)
            cmd = [
                "sphinx-build",
                "-b",
                "html",
                "-E",  # Don't use cached environment
                str(source_dir),
                str(self.root_docs / "build" / "html"),
            ]

            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    click.echo("✅ Hub updated successfully!")
                    self._generate_summary_report()
                    return True
                else:
                    click.echo("❌ Update failed")
                    return False
            except Exception as e:
                click.echo(f"❌ Update error: {e}")
                return False
        else:
            click.echo("❌ Hub not initialized. Run 'link-docs' first.")
            return False

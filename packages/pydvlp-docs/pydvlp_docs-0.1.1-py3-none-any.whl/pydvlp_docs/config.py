"""PyDevelop Documentation Configuration.

This module provides a complete Sphinx configuration system with 40+ pre-configured
extensions for beautiful, feature-rich Python documentation.

Features:
    - Zero-configuration setup for any Python project
    - Professional Furo theme with dark mode
    - 40+ Sphinx extensions pre-configured
    - Automatic API documentation with AutoAPI
    - Pydantic model documentation
    - Mermaid diagrams, copy buttons, and more
    - SEO optimization and social media previews
    - Git-based change tracking

Example:
    Basic usage for a single package:

    >>> from pydvlp_docs.config import get_haive_config
    >>> config = get_haive_config(
    ...     package_name="my-package",
    ...     package_path="../src"
    ... )
    >>> # Use config in your conf.py:
    >>> globals().update(config)

    For a monorepo central hub:

    >>> config = get_central_hub_config()
    >>> globals().update(config)
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional


def get_haive_config(
    package_name: str,
    package_path: str,
    is_central_hub: bool = False,
    extra_extensions: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Get complete PyDevelop Sphinx configuration for a package.

    This function returns a comprehensive Sphinx configuration with 40+ extensions
    pre-configured for professional Python documentation. Works with any project
    structure and provides zero-configuration setup.

    Args:
        package_name: Name of the package (e.g., "my-package", "haive-core")
            Used for project titles, URLs, and branding.
        package_path: Relative path to the package source code from docs/source/
            (e.g., "../../src", "../my_package")
        is_central_hub: Whether this is a central documentation hub for monorepos.
            Enables sphinx-collections for aggregating multiple package docs.
        extra_extensions: Additional Sphinx extensions to include beyond the 40+
            that are already configured.

    Returns:
        Dictionary containing complete Sphinx configuration settings including:
        - Project metadata (name, author, version)
        - All 40+ extensions with optimal configurations
        - Furo theme with professional styling
        - AutoAPI configuration for automatic API docs
        - Intersphinx mappings for cross-references
        - SEO and social media optimization
        - Git integration for change tracking

    Example:
        In your package's docs/source/conf.py:

        >>> from pydvlp_docs.config import get_haive_config
        >>>
        >>> # Configure for this package
        >>> config = get_haive_config(
        ...     package_name="my-awesome-package",
        ...     package_path="../../src"
        ... )
        >>>
        >>> # Apply all settings to this Sphinx configuration
        >>> globals().update(config)
    """

    # Base project info
    display_name = package_name.replace("haive-", "").replace("-", " ").title()
    if package_name == "haive-docs":
        display_name = "Haive AI Agent Framework"

    config = {
        # Project information
        "project": (
            f"Haive {display_name}" if package_name != "haive-docs" else display_name
        ),
        "author": "William R. Astley",
        "copyright": "2025, William R. Astley",
        "release": "0.1.0",
        # Extensions - Complete 40+ extension system with optimal configurations
        "extensions": _get_complete_extensions(
            is_central_hub, extra_extensions, package_name
        ),
        # General configuration
        "templates_path": ["_templates"],
        "html_static_path": ["_static"],
        "exclude_patterns": [
            "_build",
            "Thumbs.db",
            ".DS_Store",
            "**/CVS",
            "**/.git",
            "_collections/*/_collections",  # Prevent nested collection directories
            "**/symlink_loops",  # Prevent symlink loop directories
        ],
        "add_module_names": False,
        "toc_object_entries_show_parents": "hide",
        # TOC Configuration - Enhanced nesting and presentation
        "html_sidebars": {
            "**": [
                "sidebar/brand.html",
                "sidebar/search.html",
                "sidebar/scroll-start.html",
                "sidebar/navigation.html",
                "sidebar/ethical-ads.html",
                "sidebar/scroll-end.html",
            ]
        },
        # Furo-specific TOC options
        "navigation_with_keys": True,
        "top_of_page_button": "edit",
        # Sphinx TOC settings
        "toctree_maxdepth": 4,  # Maximum depth for nested TOC
        "toctree_collapse": False,  # Don't collapse by default
        "toctree_titles_only": False,  # Show full titles
        "toctree_includehidden": True,  # Include hidden TOC entries
        # Jinja2 options
        "jinja_env_options": {"extensions": ["jinja2.ext.do"]},
        # AutoAPI configuration (if not central hub)
        **(_get_complete_autoapi_config(package_path) if not is_central_hub else {}),
        # Napoleon configuration
        "napoleon_google_docstring": True,
        "napoleon_numpy_docstring": True,
        "napoleon_include_init_with_doc": False,
        "napoleon_include_private_with_doc": False,
        # Intersphinx configuration
        "pkg_requirements_source": "pyproject",  # Read dependencies from pyproject.toml
        "repository_root": "../..",  # Path to repo root from docs/source
        "intersphinx_mapping": _get_complete_intersphinx_mapping(),
        # Pydantic configuration - COMPLETE
        "autodoc_pydantic_model_show_json": True,
        "autodoc_pydantic_model_show_config_summary": True,
        "autodoc_pydantic_model_show_validator_summary": True,
        "autodoc_pydantic_model_show_field_summary": True,
        "autodoc_pydantic_model_show_validator_members": True,
        "autodoc_pydantic_field_list_validators": True,
        "autodoc_pydantic_field_show_constraints": True,
        "autodoc_pydantic_model_erdantic_figure": False,
        "autodoc_pydantic_model_erdantic_figure_collapsed": False,
        # Type hints configuration
        "typehints_fully_qualified": False,
        "typehints_use_signature": True,
        # sphinx-autodoc-typehints configuration (works as fallback when codeautolink fails)
        "always_use_bars_union": True,  # Use | syntax for unions (Python 3.10+)
        "typehints_use_rtype": True,  # Show return types
        "typehints_defaults": "comma",  # How to show defaults
        # MyST Parser configuration - COMPLETE
        "myst_enable_extensions": [
            "deflist",
            "tasklist",
            "html_image",
            "colon_fence",
            "smartquotes",
            "replacements",
            "linkify",
            "strikethrough",
            "attrs_inline",
            "attrs_block",
        ],
        "myst_heading_anchors": 3,
        "myst_fence_as_directive": ["mermaid", "note", "warning"],
        # Sphinx Design configuration - INTENSE THEMING
        "sd_fontawesome_latex": True,
        # Toggle button configuration
        "togglebutton_hint": "Click to expand",
        "togglebutton_hint_hide": "Click to collapse",
        # Copy button configuration
        "copybutton_prompt_text": r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: ",
        "copybutton_prompt_is_regexp": True,
        "copybutton_remove_prompts": True,
        # Tabs configuration
        "sphinx_tabs_disable_tab_closing": True,
        # Execution extensions configuration
        "programoutput_use_ansi": True,
        # Mermaid configuration - CUSTOM THEMING
        "mermaid_params": [
            "--theme",
            "neutral",
            "--width",
            "800",
            "--backgroundColor",
            "transparent",
        ],
        "mermaid_verbose": True,
        # PlantUML configuration
        "plantuml_output_format": "svg",
        "plantuml": "plantuml",
        # Sitemap configuration
        "html_baseurl": (
            f"https://docs.haive.ai/packages/{package_name}/"
            if not is_central_hub
            else "https://docs.haive.ai/"
        ),
        # Code autolink configuration
        "codeautolink_autodoc_inject": True,
        "codeautolink_concat_default": True,
        # Treeview configuration
        "treeview_expand_all": False,
        "treeview_collapse_inactive": True,
        "treeview_max_depth": 4,
        # Toggle prompt configuration
        "toggleprompt_offset_right": 30,
        "toggleprompt_default_hidden": "true",
        # Git last updated configuration
        "git_last_updated_show_commit_hash": True,
        "git_last_updated_format": "%Y-%m-%d %H:%M",
        # Inline code configuration
        "inlinecode_highlight_language": "python",
        # Library configuration
        "library_show_summary": True,
        "library_group_by_type": True,
        # iContract configuration
        "icontract_include_repr": True,
        "icontract_include_snapshot": False,
        # Comments configuration
        "comments_config": {
            "hypothesis": True,
            "utterances": False,
        },
        # Contributors configuration
        "contributors_show_contribution_counts": True,
        "contributors_sort_by_contribution": True,
        # Issues configuration
        "issues_github_path": "haive-ai/haive",
        "issues_uri": "https://github.com/haive-ai/haive/issues/{issue}",
        # Sphinx Tippy configuration - Enhanced hover tooltips
        "tippy_props": {
            "placement": "auto-start",
            "maxWidth": 600,
            "theme": "light-border",
            "delay": [200, 100],
            "duration": [200, 100],
            "interactive": True,
        },
        "tippy_enable_mathjax": True,
        "tippy_enable_doitips": True,
        "tippy_enable_wikitips": True,
        "tippy_enable_footnotes": True,
        "tippy_rtd_urls": ["https://docs.haive.ai"],
        "tippy_anchor_parent_selector": "article.bd-article",
        "tippy_skip_anchor_classes": ["headerlink", "sd-stretched-link"],
        "tippy_add_class": "has-tooltip",
        # Sphinx-prompt configuration
        "prompt_modifiers": "auto",
        "prompt_default_prompts": ["$", ">>>", "..."],
        # Sphinx-needs configuration - Requirements tracking
        "needs_types": [
            {
                "directive": "req",
                "title": "Requirement",
                "prefix": "R_",
                "color": "#BFD8D2",
                "style": "node",
            },
            {
                "directive": "spec",
                "title": "Specification",
                "prefix": "S_",
                "color": "#FEDCD2",
                "style": "node",
            },
            {
                "directive": "test",
                "title": "Test Case",
                "prefix": "T_",
                "color": "#DF744A",
                "style": "node",
            },
        ],
        "needs_statuses": [
            {"name": "open", "description": "New requirement"},
            {"name": "in_progress", "description": "Being implemented"},
            {"name": "implemented", "description": "Completed"},
            {"name": "closed", "description": "Done and verified"},
        ],
        "needs_tags": [
            {"name": "security", "description": "Security related"},
            {"name": "performance", "description": "Performance critical"},
            {"name": "ui", "description": "User interface"},
        ],
        # Sphinx-notfound-page configuration
        "notfound_context": {
            "title": "Page Not Found",
            "body": f"""
<h1>🚀 Oops! Page Not Found</h1>
<p>The page you're looking for seems to have wandered off into the documentation cosmos.</p>

<div class="admonition tip">
<p class="admonition-title">Try these options:</p>
<ul>
<li><strong>Search:</strong> Use the search box above to find what you need</li>
<li><strong>API Reference:</strong> Check our <a href="/autoapi/">complete API documentation</a></li> 
<li><strong>Home:</strong> Return to the <a href="/">main documentation</a></li>
</ul>
</div>

<p>Still can't find what you're looking for? <a href="https://github.com/haive-ai/haive/issues">Report an issue</a> and we'll help you out!</p>
            """,
        },
        "notfound_template": "page.html",
        "notfound_no_urls_prefix": True,
        # Sphinx-reredirects configuration
        "redirects": {},
        # Rediraffe configuration
        "rediraffe_redirects": {},
        "rediraffe_branch": "main",
        "rediraffe_auto_redirect_perc": 50,
        # Sphinx-git configuration
        "sphinx_git_changelog": True,
        "sphinx_git_changelog_title": "📝 Documentation Changes",
        "sphinx_git_show_tags": True,
        "sphinx_git_show_branch": True,
        "sphinx_git_tracked_files": ["docs/source/"],
        "sphinx_git_untracked": False,
        # Sphinx-changelog configuration
        "changelog_sections_past": 10,  # How many past releases to show
        "changelog_inner_tag_sort": ["breaking", "feature", "bugfix", "improvement"],
        # Debug info configuration
        "debuginfo_enable": True,
        "debuginfo_show_performance": True,
        "debuginfo_show_warnings": True,
        "debuginfo_show_extensions": True,
        # OpenGraph configuration
        "ogp_site_url": (
            "https://docs.haive.ai/"
            if is_central_hub
            else f"https://docs.haive.ai/packages/{package_name}/"
        ),
        "ogp_site_name": display_name,
        "ogp_site_description": f"{display_name} - Part of the Haive AI Agent Framework",
        "ogp_image": "_static/social-preview.png",
        "ogp_image_alt": f"{display_name} Documentation",
        "ogp_type": "website",
        "ogp_locale": "en_US",
        "ogp_social_cards": {
            "enable": True,
            "image": "_static/social-card-template.png",
            "line_color": "#2563eb",
            "text_color": "#ffffff",
        },
        # Sphinx-tags configuration
        "tags_create_tags": True,
        "tags_create_index": True,
        "tags_create_badges": True,
        "tags_page_title": "Documentation Tags",
        "tags_intro_text": "Browse documentation content by tags",
        "tags_extension": [".rst", ".md"],
        "tags_badge_colors": {
            "security": "#dc3545",
            "performance": "#28a745",
            "ui": "#007bff",
            "api": "#6f42c1",
            "config": "#fd7e14",
            "tutorial": "#20c997",
            "reference": "#6c757d",
        },
        # Sphinx-favicon configuration
        "favicons": [
            {
                "rel": "icon",
                "sizes": "32x32",
                "href": "favicon-32x32.png",
                "type": "image/png",
            },
            {
                "rel": "icon",
                "sizes": "16x16",
                "href": "favicon-16x16.png",
                "type": "image/png",
            },
            {
                "rel": "apple-touch-icon",
                "sizes": "180x180",
                "href": "apple-touch-icon.png",
                "type": "image/png",
            },
            {
                "rel": "shortcut icon",
                "href": "favicon.ico",
                "type": "image/x-icon",
            },
        ],
        # Collections configuration (only for central hub)
        **(_get_collections_config() if is_central_hub else {}),
        # Theme configuration - INTENSE FURO THEMING
        "html_theme": "furo",
        "html_theme_options": _get_complete_theme_options(package_name, is_central_hub),
        # Custom CSS and JS files - SIMPLIFIED for clean documentation
        "html_css_files": [
            "css/furo-intense.css",  # CRITICAL: Dark mode fixes for code visibility
            "breadcrumb-navigation.css",  # Breadcrumb navigation for Furo
            "mermaid-custom.css",  # Keep diagram-specific styling
            "tippy-enhancements.css",  # Keep tooltip-specific styling
        ],
        "html_js_files": [
            "furo-enhancements.js",
            "mermaid-config.js",
            "js/api-enhancements.js",
        ],
    }

    # Note: Using viewcode extension for local source viewing
    # This works better with Furo theme than linkcode

    return config


def get_central_hub_config(package_names: List[str] = None) -> Dict[str, Any]:
    """Get configuration specific to the central documentation hub.

    Args:
        package_names: List of package names to include in hub (optional).

    This includes sphinx-collections configuration for aggregating
    all package documentation.

    Returns:
        Dictionary with complete central hub configuration
    """
    if package_names is None:
        package_names = []

    return get_haive_config(
        package_name="haive-docs", package_path="", is_central_hub=True
    )


def _get_complete_extensions(
    is_central_hub: bool,
    extra_extensions: Optional[List[str]] = None,
    package_name: str = "",
) -> List[str]:
    """Get the complete 40+ Sphinx extension system.

    This function returns a carefully curated list of Sphinx extensions that work
    well together and provide comprehensive documentation features.

    Args:
        is_central_hub: If True, includes sphinx-collections for monorepo docs
        extra_extensions: Additional extensions to append to the list

    Returns:
        List of extension names, optimized for compatibility and functionality
    """
    extensions = [
        # Core (Priority 1-10) - AutoAPI FIRST as requested
        "sphinx.ext.autodoc",
        "sphinx.ext.napoleon",
        "sphinx.ext.viewcode",  # Local source code viewing (works with Furo)
        # "sphinx.ext.linkcode",  # Disabled - conflicts with viewcode
        "sphinx.ext.intersphinx",
        "seed_intersphinx_mapping",  # Auto-populate intersphinx from pyproject.toml
        # Enhanced API (Priority 11-20)
        "sphinxcontrib.autodoc_pydantic",
        "sphinx_autodoc_typehints",
        # Content & Design (Priority 21-30) - INTENSE FURO FOCUS
        "myst_parser",
        "sphinx_design",  # KEY for intense theming
        "sphinx_togglebutton",
        "sphinx_copybutton",
        "sphinx_tabs.tabs",
        # Execution (Priority 31-40) - TESTING FOCUS
        "sphinxcontrib.programoutput",
        # "sphinx_runpython",  # Disabled - has no setup() function
        "sphinx_exec_code",
        # Diagrams (Priority 41-50) - MERMAID FOCUS
        "sphinx.ext.graphviz",
        "sphinxcontrib.mermaid",
        "sphinxcontrib.plantuml",
        "sphinxcontrib.blockdiag",
        "sphinxcontrib.seqdiag",
        "sphinxcontrib.nwdiag",
        "sphinxcontrib.actdiag",
        # Utilities (Priority 51-60)
        "sphinx_sitemap",
        # "sphinx_codeautolink",  # Temporarily disabled - causes TypeError with union types
        # TOC Enhancements (Priority 61-70)
        "sphinx_treeview",
        # Enhanced Features (Priority 71-80)
        "sphinx_toggleprompt",
        "sphinx_prompt",
        "sphinx_last_updated_by_git",
        # "sphinx_inlinecode",  # Temporarily disabled - causes issues with metaclasses
        "sphinx_library",
        "sphinx_icontract",
        "sphinx_tippy",
        # Documentation Tools (Priority 81-90)
        "sphinx_comments",
        "sphinx_contributors",
        "sphinx_issues",
        "sphinx_needs",
        "sphinxarg.ext",
        "notfound.extension",
        "sphinx_reredirects",
        "sphinxext.rediraffe",
        "sphinx_git",
        "sphinx_debuginfo",
        "sphinxext.opengraph",
        "sphinx_tags",
        "sphinx_favicon",
        "sphinx_combine",
    ]

    # Add AutoAPI for individual packages
    if not is_central_hub:
        extensions.insert(1, "autoapi.extension")

    # Add collections for central hub
    if is_central_hub:
        extensions.append("sphinxcontrib.collections")

    # Add extra extensions
    if extra_extensions:
        extensions.extend(extra_extensions)

    # Note about sphinx_codeautolink
    if "sphinx_codeautolink" in extensions:
        # Known to have issues with Python 3.10 union syntax but we accept the warnings
        pass

    return extensions


def _get_complete_autoapi_config(package_path: str) -> Dict[str, Any]:
    """Get complete AutoAPI configuration with hierarchical organization.

    ✅ INCLUDES AUTOAPI HIERARCHICAL FIX - Issue #4 Solution
    This configuration applies the validated solution that transforms flat
    alphabetical API listings into organized hierarchical structure.

    Uses default AutoAPI templates which have proven to work perfectly
    with the hierarchical organization fix.
    """
    return {
        "autoapi_type": "python",
        "autoapi_dirs": [package_path],
        "autoapi_add_toctree_entry": True,
        "autoapi_generate_api_docs": True,
        "autoapi_keep_files": True,
        # ✅ HIERARCHICAL ORGANIZATION FIX - The key setting!
        "autoapi_own_page_level": "module",  # Keep classes with their modules (not individual pages)
        "autoapi_options": [
            "members",
            "undoc-members",
            "show-inheritance",
            "show-module-summary",  # Critical for hierarchical organization
            "private-members",
            "special-members",
            "imported-members",
        ],
        "autoapi_python_class_content": "both",
        "autoapi_add_class_diagram": True,
        "autoapi_class_diagram_depth": 2,
        "autoapi_member_order": "groupwise",
        "autoapi_root": "autoapi",
        "autoapi_toctree_depth": 3,
        # Enable custom templates with hierarchical support
        "autoapi_template_dir": os.path.join(
            os.path.dirname(__file__), "templates", "_autoapi_templates"
        ),
        # Skip problematic patterns
        "autoapi_ignore": [
            "**/test_*.py",
            "**/tests/*",
            "**/tests/**",
            "**/test/**",
            "**/*_test.py",
            "**/*_tests.py",
            "**/conftest.py",
            "**/pytest.ini",
            "**/engine_node_test/**",  # Test directory in wrong location
            "**/engine_node_test/*",  # All files in engine_node_test
            # Skip metaclass files that cause issues
            "**/graph/state_graph/base.py",  # Contains SerializableModelMetaclass
            # Skip test files in wrong location
            "**/engine_node_test.py",  # Test file in src directory
            # Skip additional problematic patterns
            "**/debug_*.py",
            "**/archive/**",
            "**/archives/**",
        ],
    }


def _get_collections_config() -> Dict[str, Any]:
    """Get sphinx-collections configuration for central hub."""
    return {
        "collections": {
            "packages": {
                "driver": "copy_folder",
                "source_folder": "../../../packages/*/docs/build/html/",
                "target_folder": "_collections/packages/",
                "active": True,
                "clean": True,
            },
        },
        "collections_clean": True,
        "collections_final_clean": False,
    }


def _get_complete_theme_options(
    package_name: str, is_central_hub: bool
) -> Dict[str, Any]:
    """Get complete Furo theme options with intense theming.

    ✅ INCLUDES AUTOAPI HIERARCHICAL FIX SUPPORT - Issue #4 Solution
    These theme options work perfectly with autoapi_own_page_level='module'
    to provide beautiful hierarchical navigation instead of flat listings.
    """
    return {
        "sidebar_hide_name": False,
        # REMOVED unsupported Furo options that caused warnings:
        # navigation_depth, collapse_navigation, sticky_navigation,
        # includehidden, titles_only, breadcrumb, breadcrumb_separator, breadcrumb_depth
        # Furo handles navigation automatically - no need to override
        # Intense branding colors
        "light_css_variables": {
            "color-brand-primary": "#2563eb",  # Blue-600
            "color-brand-content": "#1d4ed8",  # Blue-700
            "color-background-primary": "#ffffff",
            "color-background-secondary": "#f8fafc",  # Slate-50
            "color-background-hover": "#e2e8f0",  # Slate-200
            "color-background-border": "#cbd5e1",  # Slate-300
            "color-code-background": "#1e293b",  # Slate-800
            "color-code-foreground": "#e2e8f0",  # Slate-200
            "color-sidebar-background": "#0f172a",  # Slate-900
            "color-sidebar-foreground": "#cbd5e1",  # Slate-300
            "color-api-background": "#f1f5f9",  # Slate-100
            "color-api-background-hover": "#e2e8f0",  # Slate-200
            # Removed color-admonition-background to let Furo handle semantic colors
        },
        "dark_css_variables": {
            "color-brand-primary": "#60a5fa",  # Blue-400
            "color-brand-content": "#3b82f6",  # Blue-500
            "color-background-primary": "#0f172a",  # Slate-900
            "color-background-secondary": "#1e293b",  # Slate-800
            "color-background-hover": "#334155",  # Slate-700
            "color-background-border": "#475569",  # Slate-600
            "color-code-background": "#0f172a",  # Slate-900
            "color-code-foreground": "#cbd5e1",  # Slate-300
            "color-sidebar-background": "#020617",  # Slate-950
            "color-sidebar-foreground": "#94a3b8",  # Slate-400
        },
        # Repository integration
        "source_repository": "https://github.com/haive-ai/haive/",
        "source_branch": "main",
        "source_directory": (
            f"packages/{package_name}/docs/"
            if not is_central_hub
            else "tools/pydvlp-docs/docs/"
        ),
        # Announcements
        "announcement": (
            "🚀 <strong>Haive AI Agent Framework</strong> - Complete monorepo documentation system!"
            if is_central_hub
            else f'🎯 <a href="../../index.html">← Back to Haive Docs</a> | {package_name} - Part of the Haive AI Agent Framework'
        ),
        # Footer icons
        "footer_icons": [
            {
                "name": "GitHub",
                "url": "https://github.com/haive-ai/haive/",
                "html": """<svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path>
                </svg>""",
            },
        ],
    }


def _get_complete_intersphinx_mapping() -> Dict[str, tuple]:
    """Get complete intersphinx mapping for cross-references."""
    return {
        "python": ("https://docs.python.org/3", None),
        "sphinx": ("https://www.sphinx-doc.org/en/master", None),
        "pydantic": ("https://docs.pydantic.dev/latest", None),
        "langchain": ("https://api.python.langchain.com/en/latest/", None),
        "fastapi": ("https://fastapi.tiangolo.com/", None),
        # Add other Haive packages as they become available
        # "haive-core": ("https://docs.haive.ai/packages/haive-core/", None),
        # "haive-agents": ("https://docs.haive.ai/packages/haive-agents/", None),
    }


def autodoc_skip_member(app, what, name, obj, skip, options):
    """Skip members that shouldn't be documented."""
    # Skip metaclasses to avoid autodoc_pydantic errors
    if what == "class" and isinstance(obj, type) and issubclass(obj.__class__, type):
        # Check if this is a metaclass (its class is a subclass of type)
        if "metaclass" in obj.__name__.lower() or obj.__class__.__name__ != "type":
            app.debug(f"Skipping metaclass: {name}")
            return True

    # Skip objects that have __pydantic_decorators__ missing but are expected to have it
    if hasattr(obj, "__class__") and "Metaclass" in getattr(
        obj.__class__, "__name__", ""
    ):
        app.debug(f"Skipping object with metaclass: {name}")
        return True

    return skip


def process_docstring(app, what, name, obj, options, lines):
    """Process docstrings to fix common RST formatting issues."""
    if not lines:
        return

    # Fix improper indentation in docstrings
    # This handles cases where code examples are indented without proper RST formatting
    in_example_block = False
    fixed_lines = []

    for i, line in enumerate(lines):
        # Check if we're starting an example block
        if line.strip().lower() in ["example:", "examples:", "usage:"]:
            in_example_block = True
            fixed_lines.append(line)
            # Add :: to create a proper code block
            if i + 1 < len(lines) and lines[i + 1].strip():
                fixed_lines.append("")
                fixed_lines.append("    ::")
                fixed_lines.append("")
            continue

        # If we're in an example block and hit a non-indented line, we're done
        if in_example_block and line and not line[0].isspace():
            in_example_block = False

        # If we're in an example block, ensure proper indentation
        if in_example_block and line.strip():
            # Ensure at least 4 spaces of indentation
            stripped = line.lstrip()
            current_indent = len(line) - len(stripped)
            if current_indent < 4:
                line = "    " + stripped
            else:
                # Add 4 more spaces to existing indentation
                line = "    " + line

        fixed_lines.append(line)

    # Replace the original lines
    lines.clear()
    lines.extend(fixed_lines)


def linkcode_resolve(domain, info):
    """Generate GitHub source links for AutoAPI documentation.

    This function is called by sphinx.ext.linkcode to generate source code links
    that point to the actual source files on GitHub.

    Args:
        domain: The language domain (e.g., 'py' for Python)
        info: Dictionary containing module and object information

    Returns:
        String URL pointing to the source code on GitHub, or None if not found
    """
    if domain != "py":
        return None

    if not info.get("module"):
        return None

    # Get the module name and convert to file path
    module_name = info["module"]

    # Handle different package structures
    if module_name.startswith("haive."):
        # Remove haive prefix and convert to path
        module_path = module_name.replace("haive.", "").replace(".", "/")

        # Determine which package this belongs to
        if module_path.startswith("core"):
            package_prefix = "packages/haive-core/src/haive"
        elif module_path.startswith("agents"):
            package_prefix = "packages/haive-agents/src/haive"
        elif module_path.startswith("tools"):
            package_prefix = "packages/haive-tools/src/haive"
        elif module_path.startswith("games"):
            package_prefix = "packages/haive-games/src/haive"
        elif module_path.startswith("mcp"):
            package_prefix = "packages/haive-mcp/src/haive"
            module_path = module_path  # mcp is already the top level
        else:
            # Default to core for unknown modules
            package_prefix = "packages/haive-core/src/haive"
    else:
        # Non-haive module, try to map directly
        package_prefix = "src"
        module_path = module_name.replace(".", "/")

    # Construct the full file path
    file_path = f"{package_prefix}/{module_path}.py"

    # Generate GitHub URL
    github_base = "https://github.com/prim8/haive"
    branch = "main"

    return f"{github_base}/blob/{branch}/{file_path}"


def setup(app):
    """Setup Sphinx application with custom handlers and intelligent templates."""
    # Add autodoc skip handler to prevent processing metaclasses
    app.connect("autodoc-skip-member", autodoc_skip_member)

    # DISABLED: Let Napoleon handle Google-style docstrings properly
    # app.connect("autodoc-process-docstring", process_docstring)

    # Note: sphinx-codeautolink may warn about Python 3.10 union syntax
    # We accept these warnings and continue with the build

    # Add minimal custom CSS
    app.add_css_file("css/custom.css", priority=600)
    # Removed tippy-enhancements.css - already in html_css_files
    # Removed api-docs.css - too aggressive with badges and gradients

    # Add custom JS for API enhancements
    app.add_js_file("js/api-enhancements.js", {"defer": "defer"})

    # Custom Jinja configuration removed - using default AutoAPI templates
    # The hierarchical organization is achieved through configuration, not custom templates

    return {
        "version": "1.0.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

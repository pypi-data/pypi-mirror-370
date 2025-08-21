# PyDevelop-Docs

> **Universal Python documentation generator with 40+ Sphinx extensions pre-configured**

[![PyPI version](https://badge.fury.io/py/pydvlp-docs.svg)](https://badge.fury.io/py/pydvlp-docs)
[![Python Support](https://img.shields.io/pypi/pyversions/pydvlp-docs.svg)](https://pypi.org/project/pydvlp-docs/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Transform any Python project into beautiful, professional documentation with **zero configuration**. PyDevelop-Docs automatically detects your project structure and generates a complete Sphinx documentation setup with modern themes, extensive features, and intelligent API documentation.

## ✨ Features

### 🎯 **Zero Configuration**
- **Works immediately** with any Python project structure
- **Automatic detection** of monorepos, single packages, src layouts, flat layouts
- **Smart path configuration** for AutoAPI and asset management
- **Intelligent metadata extraction** from pyproject.toml, setup.py

### 📦 **Universal Project Support**
- **Monorepos**: `packages/package-name/` structures
- **Src Layout**: `src/package_name/` organization  
- **Flat Layout**: Package in project root
- **Simple Projects**: Basic Python files

### 🎨 **Professional Appearance**
- **Beautiful Furo theme** with dark mode support
- **Responsive design** for all devices
- **Custom CSS enhancements** for better readability
- **Professional navigation** with hierarchical organization

### 🔧 **40+ Pre-configured Extensions**
- **AutoAPI** with hierarchical organization (not flat alphabetical!)
- **Syntax highlighting** with copy buttons
- **Mermaid diagrams** and PlantUML support
- **Interactive elements** with sphinx-design
- **SEO optimization** with sitemaps and OpenGraph
- **And much more!** See [complete extension list](#included-extensions)

### ⚡ **Smart CLI Commands**
- **`setup-general`**: Analyze and set up any Python project
- **`copy-setup`**: Transfer documentation between projects  
- **Interactive and non-interactive** modes available
- **Dry-run capability** for previewing actions

## 🚀 Quick Start

### Installation
```bash
pip install pydvlp-docs
```

### One-Command Setup
```bash
# Set up documentation for any Python project
pydvlp-docs setup-general /path/to/your/project

# Navigate and build
cd /path/to/your/project/docs
make html

# Your documentation is ready at build/html/index.html! 🎉
```

That's it! PyDevelop-Docs automatically:
- ✅ Detects your project type and structure
- ✅ Configures 40+ Sphinx extensions
- ✅ Sets up AutoAPI with proper paths
- ✅ Creates professional homepage and navigation
- ✅ Installs beautiful theme with custom styling

## 📋 Project Types Supported

### Monorepo Structure
```
my-monorepo/
├── packages/
│   ├── package-a/
│   │   └── src/package_a/
│   ├── package-b/ 
│   │   └── src/package_b/
│   └── package-c/
│       └── src/package_c/
└── pyproject.toml
```
**Detection**: ✅ Monorepo | **AutoAPI**: `['../packages']`

### Src Layout
```
my-package/
├── src/
│   └── my_package/
├── tests/
├── docs/  # ← Created here
└── pyproject.toml
```
**Detection**: ✅ Single Package | **AutoAPI**: `['../../src']`

### Flat Layout  
```
my-package/
├── my_package/
├── tests/
├── docs/  # ← Created here
└── pyproject.toml
```
**Detection**: ✅ Single Package | **AutoAPI**: `['../my_package']`

### Simple Project
```
my-scripts/
├── main.py
├── utils.py
├── docs/  # ← Created here
└── requirements.txt
```
**Detection**: ✅ Simple Project | **AutoAPI**: `['..']`

## 🛠️ Usage Examples

### Command Line Interface

```bash
# Interactive setup with project analysis
pydvlp-docs setup-general /path/to/project

# Non-interactive setup
pydvlp-docs setup-general /path/to/project --non-interactive --force

# Preview what will be created
pydvlp-docs setup-general /path/to/project --dry-run

# Custom documentation directory
pydvlp-docs setup-general /path/to/project --target-dir /custom/docs/path

# Copy documentation setup between projects
pydvlp-docs copy-setup /source/project /destination/project --include-config
```

### Python API

```python
from pydevelop_docs import setup_project_docs

# One-line setup
result = setup_project_docs("/path/to/project")
print(f"Documentation created at: {result['target_dir']}")

# Non-interactive with custom options
result = setup_project_docs(
    "/path/to/project",
    target_dir="/custom/location",
    force=True,
    interactive=False
)

# Preview without executing
plan = setup_project_docs("/path/to/project", dry_run=True)
for action in plan['actions']:
    print(f"Would create: {action}")
```

### Advanced Configuration

```python
from pydevelop_docs.config import get_haive_config

# Get pre-configured Sphinx configuration
config = get_haive_config(
    package_name="my-package",
    package_path="/path/to/package"
)

# Use in your docs/source/conf.py
globals().update(config)
```

### Project Analysis

```python
from pydevelop_docs.general_setup import ProjectDetector
from pathlib import Path

# Analyze any Python project
detector = ProjectDetector(Path("/path/to/project"))
info = detector.detect_project_type()

print(f"Project type: {info['type']}")  # monorepo, single_package, etc.
print(f"Package manager: {info['package_manager']}")  # poetry, setuptools, etc.
print(f"Found {len(info['packages'])} packages")
print(f"Structure: {info['structure']['pattern']}")
```

## 📖 Generated Documentation Structure

PyDevelop-Docs creates a complete documentation setup:

```
docs/
├── Makefile                    # Build automation
├── requirements.txt            # Documentation dependencies  
├── source/
│   ├── conf.py                # Complete Sphinx configuration
│   ├── index.rst              # Professional homepage
│   ├── _static/               # CSS, JavaScript, assets
│   │   ├── css/
│   │   │   ├── custom.css     # Custom styling
│   │   │   └── furo-intense.css # Dark mode fixes
│   │   └── js/
│   │       └── api-enhancements.js
│   ├── _templates/            # Custom Jinja2 templates
│   └── autoapi/               # Auto-generated API docs
│       └── index.rst          # API reference (hierarchical!)
└── build/
    └── html/                  # Built documentation
        └── index.html         # Your beautiful docs! 🎉
```

## 🎨 Theme and Styling

### Furo Theme with Enhancements
- **Modern responsive design** that works on all devices
- **Dark/light mode toggle** with proper contrast
- **Smooth animations** and professional typography
- **Enhanced navigation** with improved sidebar
- **Custom color scheme** optimized for readability

### Key Styling Features
- **Hierarchical API navigation** (not flat alphabetical lists!)
- **Improved code block styling** with copy buttons
- **Better table and admonition styling**
- **Enhanced mobile experience**
- **Professional color scheme** with accessibility focus

## 🔧 Included Extensions

PyDevelop-Docs includes 40+ carefully selected and pre-configured Sphinx extensions:

### Core Documentation
- `sphinx.ext.autodoc` - Automatic API documentation
- `sphinx.ext.napoleon` - Google/NumPy docstring support
- `sphinx.ext.viewcode` - Source code links
- `sphinx.ext.intersphinx` - Cross-project linking

### API Documentation  
- `autoapi.extension` - Automatic API reference (with hierarchical fix!)
- `sphinx_autodoc_typehints` - Type hint documentation
- `sphinxcontrib.autodoc_pydantic` - Pydantic model documentation

### Enhanced Features
- `myst_parser` - Markdown support
- `sphinx_copybutton` - Copy code buttons
- `sphinx_design` - Modern UI components
- `sphinx_tabs` - Tabbed content
- `sphinxcontrib.mermaid` - Diagram support

### SEO and Discovery
- `sphinx_sitemap` - SEO sitemaps
- `sphinxext.opengraph` - Social media previews
- `sphinx_favicon` - Custom favicons

### And Many More!
See the [complete extension list](docs/extensions.md) with configuration details.

## ⚙️ Configuration Details

### AutoAPI Hierarchical Organization

**The Problem**: Default AutoAPI creates flat, alphabetical lists of 200+ classes that are impossible to navigate.

**Our Solution**: Hierarchical organization that follows your project structure:

```python
# Key configuration in generated conf.py
autoapi_own_page_level = "module"  # Keep classes with their modules!
autoapi_options = [
    "members",
    "undoc-members", 
    "show-inheritance",
    "show-module-summary",  # Enables hierarchical grouping
]
```

**Result**: Beautiful organized navigation like:
```
📦 my_package
├── 📁 core
│   ├── 📄 engine (3 classes)
│   └── 📄 schema (5 classes)  
└── 📁 utils
    └── 📄 helpers (2 functions)
```

Instead of:
```
❌ All Classes (A-Z)
├── AgentConfig
├── BaseModel
├── Calculator
├── [197 more in flat list...]
```

### Smart Path Detection

PyDevelop-Docs automatically configures AutoAPI directories based on your project structure:

- **Monorepo**: `autoapi_dirs = ['../packages']`
- **Src Layout**: `autoapi_dirs = ['../../src']`  
- **Flat Layout**: `autoapi_dirs = ['../package_name']`
- **Simple Project**: `autoapi_dirs = ['..']`

No manual configuration needed! 🎯

## 🚧 Development

### Setting up for Development
```bash
git clone https://github.com/your-org/pydvlp-docs.git
cd pydvlp-docs

# Install with development dependencies
poetry install --with dev,docs

# Run tests
poetry run pytest

# Build documentation
cd docs && make html
```

### Running Tests
```bash
# Full test suite
poetry run pytest

# Test with coverage
poetry run pytest --cov=pydevelop_docs

# Test specific functionality
poetry run pytest tests/test_general_setup.py -v
```

### Building Documentation
```bash
# Build your own docs (meta!)
cd docs
make html

# Or use the tool on itself
pydvlp-docs setup-general . --force
cd docs && make html
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Contribution Setup
```bash
# Fork and clone
git clone https://github.com/your-username/pydvlp-docs.git
cd pydvlp-docs

# Install development dependencies  
poetry install --with dev,docs,test

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and test
poetry run pytest
poetry run ruff check
poetry run mypy

# Submit pull request! 🎉
```

## 📊 Comparison

| Feature | PyDevelop-Docs | Manual Sphinx | Other Tools |
|---------|----------------|---------------|-------------|
| **Setup Time** | < 1 minute | Hours | Minutes |
| **Project Detection** | ✅ Automatic | ❌ Manual | ⚠️ Limited |
| **Extension Count** | 40+ | 0 | 5-10 |
| **Theme Quality** | ✅ Professional | ⚠️ Basic | ⚠️ Varies |
| **AutoAPI Hierarchy** | ✅ Fixed | ❌ Flat | ❌ Flat |
| **Mobile Responsive** | ✅ Yes | ❌ No | ⚠️ Sometimes |
| **Dark Mode** | ✅ Yes | ❌ No | ⚠️ Sometimes |
| **SEO Ready** | ✅ Yes | ❌ No | ❌ No |

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Sphinx Team** - For the amazing documentation framework
- **Furo Theme** - For the beautiful modern theme
- **AutoAPI** - For automatic API documentation
- **All Extension Authors** - For creating the tools that make this possible

## 👨‍💻 Author

**William R. Astley**
- Website: [will.astley.dev](https://will.astley.dev)
- GitHub: [@pr1m8](https://github.com/pr1m8)

## 📞 Support

- **Documentation**: [Full Documentation](https://pydvlp-docs.readthedocs.io/)
- **Issues**: [GitHub Issues](https://github.com/pr1m8/pydvlp-docs/issues)
- **Discussions**: [GitHub Discussions](https://github.com/pr1m8/pydvlp-docs/discussions)

---

**🚀 From zero to professional documentation in under a minute!**

*Made with ❤️ for the Python community*
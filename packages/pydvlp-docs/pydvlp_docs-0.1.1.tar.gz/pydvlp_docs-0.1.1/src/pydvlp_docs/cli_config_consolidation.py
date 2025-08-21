"""
CLI Configuration Consolidation Plan

This shows how to refactor the CLI to use the config module instead of duplicating configuration.
"""

# CURRENT PROBLEM:
# cli.py has 400+ lines of hardcoded Sphinx configuration
# config.py has the same configuration properly maintained
# They're out of sync (CLI was missing hierarchical fix until recently)

# SOLUTION APPROACHES:


# Approach 1: Minimal Change - Import at conf.py generation time
def approach1_import_at_generation():
    """
    Modify _generate_conf_py to use config module when building the string.
    """
    # In cli.py, change _generate_conf_py to:

    def _generate_conf_py(self):
        """Generate Sphinx configuration using shared config module."""
        from .config import get_haive_config

        # Get config
        config = get_haive_config(self.project_info["name"])

        # Build conf.py that imports from config at runtime
        return f"""
from pydvlp_docs.config import get_haive_config

# Get configuration
config = get_haive_config("{self.project_info["name"]}")

# Apply all settings
for key, value in config.items():
    globals()[key] = value

# Override with project-specific settings
project = "{self.project_info["name"]}"
copyright = f"{{date.today().year}}, {self.project_info["name"]} Team"
"""


# Approach 2: Generate Static conf.py from config module
def approach2_static_generation():
    """
    Extract values from config module and generate a static conf.py.
    This removes runtime dependency on pydevelop_docs.
    """
    # See cli_refactor.py for full implementation
    pass


# Approach 3: Hybrid - Use config module but allow overrides
def approach3_hybrid():
    """
    Import base config but allow CLI to override specific settings.
    """
    return """
# Base configuration from pydvlp_docs
from pydvlp_docs.config import get_haive_config
config = get_haive_config(project)

# Apply base configuration
extensions = config['extensions']
autoapi_own_page_level = config['autoapi_own_page_level']  # ✅ Gets hierarchical fix!

# Project-specific overrides
project = "MyProject"
autoapi_dirs = ["../../src"]  # Custom for this project
"""


# RECOMMENDED APPROACH:
# 1. Create a new method in cli.py that generates conf.py using config module
# 2. Keep existing method as legacy/fallback
# 3. Add a --use-shared-config flag to CLI

# BENEFITS:
# - Single source of truth (config.py)
# - Automatic inclusion of all fixes
# - Easier maintenance
# - Backward compatibility

# IMPLEMENTATION STEPS:
# 1. Add new method to cli.py: _generate_conf_py_from_config()
# 2. Update _create_docs_structure to use new method when flag is set
# 3. Make it default in next major version
# 4. Eventually remove duplicated configuration

# QUICK FIX FOR NOW:
# Since CLI already has the hierarchical fix at line 460, we're good!
# But consolidation should still happen to prevent future divergence.

"""Haive-specific utilities for managing documentation across the entire monorepo.

This module provides specialized tools for working with the Haive AI Agent Framework's
complex monorepo structure with 7 packages and central documentation hub.
"""

import json
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import click

from .build_error_classifier import BuildErrorClassifier, ErrorSeverity
from .build_monitor import BuildMonitor


class HaiveDocumentationManager:
    """Comprehensive documentation management for the Haive monorepo."""

    def __init__(self, haive_root: Path, quiet: bool = False, debug: bool = False):
        """Initialize the Haive documentation manager.

        Args:
            haive_root: Path to the Haive monorepo root directory
            quiet: Suppress most output
            debug: Show detailed debug information
        """
        self.haive_root = Path(haive_root).resolve()
        self.quiet = quiet
        self.debug = debug
        self.packages_dir = self.haive_root / "packages"
        self.master_docs = self.haive_root / "docs"

        # Track operations for reporting
        self.operations_log = []
        self.start_time = datetime.now()

        # Haive package structure
        self.packages = [
            "haive-core",
            "haive-agents",
            "haive-tools",
            "haive-games",
            "haive-mcp",
            "haive-prebuilt",
            "haive-dataflow",
        ]

        # Validate Haive structure
        if not self._validate_haive_structure():
            raise ValueError(f"Invalid Haive structure at {haive_root}")

    def _validate_haive_structure(self) -> bool:
        """Validate this is a proper Haive monorepo."""
        # Check for key markers
        if not (self.haive_root / "packages").exists():
            return False
        if not (self.haive_root / "CLAUDE.md").exists():
            return False
        if not (self.haive_root / "pyproject.toml").exists():
            return False

        # Check for at least some packages
        existing_packages = [p.name for p in self.packages_dir.iterdir() if p.is_dir()]
        return len(set(existing_packages) & set(self.packages)) >= 3

    def log_operation(
        self, operation: str, status: str, details: str = "", duration: float = 0
    ):
        """Log an operation with timestamp and details."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "status": status,
            "details": details,
            "duration_ms": round(duration * 1000, 2),
        }
        self.operations_log.append(entry)

        if not self.quiet:
            status_icon = (
                "✅" if status == "success" else "❌" if status == "error" else "🔄"
            )
            duration_str = f" ({duration:.2f}s)" if duration > 0 else ""
            click.echo(f"{status_icon} {operation}: {details}{duration_str}")

    def clear_all_documentation(self) -> Dict[str, int]:
        """Clear all documentation build artifacts from Haive monorepo.

        Returns:
            Dict with counts of cleared directories and files
        """
        if not self.quiet:
            click.echo("🧹 Clearing all Haive documentation...")

        start_time = time.time()
        cleared_dirs = 0
        cleared_files = 0

        # Patterns to clean across the entire monorepo
        clean_patterns = [
            # Master docs
            "docs/build",
            "docs/source/autoapi",
            "docs/source/_templates/autoapi",
            # Package docs
            "packages/*/docs/build",
            "packages/*/docs/source/autoapi",
            "packages/*/docs/source/_templates/autoapi",
            # Cache and temp files
            "**/.sphinx_cache",
            "**/__pycache__",
            "**/docs/source/_static/.doctrees",
        ]

        for pattern in clean_patterns:
            for path in self.haive_root.glob(pattern):
                if path.exists():
                    try:
                        if path.is_dir():
                            shutil.rmtree(path)
                            cleared_dirs += 1
                            if self.debug:
                                click.echo(
                                    f"   🗑️  Removed directory: {path.relative_to(self.haive_root)}"
                                )
                        else:
                            path.unlink()
                            cleared_files += 1
                            if self.debug:
                                click.echo(
                                    f"   🗑️  Removed file: {path.relative_to(self.haive_root)}"
                                )
                    except Exception as e:
                        self.log_operation(
                            "clear_failed", "error", f"Failed to remove {path}: {e}"
                        )

        duration = time.time() - start_time
        result = {"directories": cleared_dirs, "files": cleared_files}

        self.log_operation(
            "clear_all",
            "success",
            f"Cleared {cleared_dirs} directories, {cleared_files} files",
            duration,
        )

        return result

    def initialize_package_docs(self, package_name: str, force: bool = True) -> bool:
        """Initialize documentation for a specific package.

        Args:
            package_name: Name of the package (e.g., 'haive-core')
            force: Force overwrite existing documentation

        Returns:
            True if successful, False otherwise
        """
        package_path = self.packages_dir / package_name

        if not package_path.exists():
            self.log_operation(
                "init_package", "error", f"Package {package_name} not found"
            )
            return False

        if not self.quiet:
            click.echo(f"📚 Initializing docs for {package_name}...")

        start_time = time.time()

        try:
            # Change to package directory
            original_cwd = Path.cwd()
            package_path_abs = package_path.resolve()

            # Run pydvlp-docs init
            cmd = [
                "poetry",
                "run",
                "pydvlp-docs",
                "init",
                "--use-shared-config",  # Use modern shared config
                "--modern-design",  # Use modern CSS system
            ]

            if force:
                cmd.append("--force")

            if self.quiet:
                cmd.append("--quiet")

            if self.debug:
                cmd.append("--debug")

            # Execute in package directory
            result = subprocess.run(
                cmd,
                cwd=package_path_abs,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            duration = time.time() - start_time

            if result.returncode == 0:
                self.log_operation(
                    "init_package", "success", f"Initialized {package_name}", duration
                )

                if self.debug and result.stdout:
                    click.echo(f"   📋 Output: {result.stdout.strip()}")

                return True
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                self.log_operation(
                    "init_package",
                    "error",
                    f"Failed to initialize {package_name}: {error_msg}",
                    duration,
                )

                if self.debug:
                    click.echo(f"   ❌ Error output: {error_msg}")

                return False

        except subprocess.TimeoutExpired:
            self.log_operation(
                "init_package", "error", f"Timeout initializing {package_name}"
            )
            return False
        except Exception as e:
            self.log_operation(
                "init_package", "error", f"Exception initializing {package_name}: {e}"
            )
            return False

    def build_package_docs(self, package_name: str, clean: bool = True) -> bool:
        """Build documentation for a specific package.

        Args:
            package_name: Name of the package (e.g., 'haive-core')
            clean: Clean build artifacts first

        Returns:
            True if successful, False otherwise
        """
        package_path = self.packages_dir / package_name

        if not package_path.exists():
            self.log_operation(
                "build_package", "error", f"Package {package_name} not found"
            )
            return False

        # Check if docs exist
        docs_path = package_path / "docs"
        if not docs_path.exists():
            self.log_operation(
                "build_package", "error", f"No docs directory in {package_name}"
            )
            return False

        if not self.quiet:
            click.echo(f"🔨 Building docs for {package_name}...")

        start_time = time.time()

        # Create error classifier for this package
        error_classifier = BuildErrorClassifier(package_name)

        try:
            # Build using sphinx-build directly for better control
            source_dir = docs_path / "source"
            build_dir = docs_path / "build" / "html"

            if clean and build_dir.exists():
                shutil.rmtree(build_dir)

            # Ensure build directory exists
            build_dir.parent.mkdir(parents=True, exist_ok=True)

            cmd = [
                "poetry",
                "run",
                "sphinx-build",
                "-b",
                "html",  # HTML builder
                # Remove -W flag that treats warnings as errors
                "--keep-going",  # Continue building despite errors
                "-j",
                "auto",  # Use multiple processes
                str(source_dir),  # Source directory
                str(build_dir),  # Output directory
            ]

            if self.debug:
                cmd.extend(["-v", "-T"])  # Verbose output and full tracebacks
            elif self.quiet:
                cmd.append("-q")  # Quiet mode

            # Execute build
            result = subprocess.run(
                cmd,
                cwd=package_path,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout for builds
            )

            duration = time.time() - start_time

            # Process output through classifier
            combined_output = ""
            if result.stdout:
                combined_output += result.stdout
            if result.stderr:
                combined_output += "\n" + result.stderr

            error_classifier.process_output(combined_output)

            # Get error summary
            summary = error_classifier.get_summary()

            # Print intelligent summary instead of raw output
            if not self.quiet:
                error_classifier.print_summary(
                    show_warnings=(self.debug or summary["has_critical"]),
                    show_suggestions=True,
                )

            # Determine if build succeeded based on critical errors, not return code
            build_success = not summary["has_critical"]

            if build_success:
                # Check if index.html was created
                index_file = build_dir / "index.html"
                if index_file.exists():
                    self.log_operation(
                        "build_package",
                        "success",
                        f"Built {package_name} ({index_file.stat().st_size // 1024}KB) with {summary['counts'][ErrorSeverity.WARNING]} warnings",
                        duration,
                    )
                    return True
                else:
                    self.log_operation(
                        "build_package",
                        "error",
                        f"Build completed but no index.html created for {package_name}",
                    )
                    return False
            else:
                # Build failed due to critical errors
                critical_count = summary["counts"][ErrorSeverity.CRITICAL]
                self.log_operation(
                    "build_package",
                    "error",
                    f"Failed to build {package_name}: {critical_count} critical errors",
                    duration,
                )

                # Show first critical error details
                if summary["critical_errors"]:
                    first_error = summary["critical_errors"][0]
                    click.echo(f"\n   🔥 First critical error: {first_error.message}")
                    if first_error.file_path:
                        click.echo(f"      File: {first_error.file_path}")
                    if first_error.suggestion:
                        click.echo(f"      💡 {first_error.suggestion}")

                return False

        except subprocess.TimeoutExpired:
            self.log_operation(
                "build_package", "error", f"Build timeout for {package_name}"
            )
            return False
        except Exception as e:
            self.log_operation(
                "build_package", "error", f"Exception building {package_name}: {e}"
            )
            return False

    def initialize_master_docs(self, force: bool = True) -> bool:
        """Initialize the master documentation hub.

        Args:
            force: Force overwrite existing documentation

        Returns:
            True if successful, False otherwise
        """
        if not self.quiet:
            click.echo("🏛️  Initializing master documentation hub...")

        start_time = time.time()

        try:
            cmd = [
                "poetry",
                "run",
                "pydvlp-docs",
                "init",
                "--include-root",  # Include root-level docs
                "--use-shared-config",  # Use modern shared config
                "--modern-design",  # Use modern CSS system
            ]

            if force:
                cmd.append("--force")

            if self.quiet:
                cmd.append("--quiet")

            if self.debug:
                cmd.append("--debug")

            # Execute in Haive root
            result = subprocess.run(
                cmd,
                cwd=self.haive_root,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            duration = time.time() - start_time

            if result.returncode == 0:
                self.log_operation(
                    "init_master",
                    "success",
                    "Initialized master documentation hub",
                    duration,
                )

                if self.debug and result.stdout:
                    click.echo(f"   📋 Output: {result.stdout.strip()}")

                return True
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                self.log_operation(
                    "init_master",
                    "error",
                    f"Failed to initialize master docs: {error_msg}",
                    duration,
                )

                if self.debug:
                    click.echo(f"   ❌ Error output: {error_msg}")

                return False

        except subprocess.TimeoutExpired:
            self.log_operation(
                "init_master", "error", "Timeout initializing master docs"
            )
            return False
        except Exception as e:
            self.log_operation(
                "init_master", "error", f"Exception initializing master docs: {e}"
            )
            return False

    def build_master_docs(self, clean: bool = True) -> bool:
        """Build the master documentation hub.

        Args:
            clean: Clean build artifacts first

        Returns:
            True if successful, False otherwise
        """
        if not self.master_docs.exists():
            self.log_operation(
                "build_master", "error", "No master docs directory found"
            )
            return False

        if not self.quiet:
            click.echo("🏛️  Building master documentation hub...")

        start_time = time.time()

        try:
            # Use pydvlp-docs link-docs command for master hub
            cmd = ["poetry", "run", "pydvlp-docs", "link-docs"]

            if clean:
                cmd.append("--clean")

            if self.debug:
                cmd.append("--debug")

            # Execute in Haive root
            result = subprocess.run(
                cmd,
                cwd=self.haive_root,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
            )

            duration = time.time() - start_time

            if result.returncode == 0:
                # Check if master index was created
                master_index = self.master_docs / "build" / "html" / "index.html"
                if master_index.exists():
                    self.log_operation(
                        "build_master",
                        "success",
                        f"Built master hub ({master_index.stat().st_size // 1024}KB)",
                        duration,
                    )

                    if self.debug and result.stdout:
                        click.echo(f"   📋 Build output: {result.stdout.strip()}")

                    return True
                else:
                    self.log_operation(
                        "build_master",
                        "error",
                        "Master build completed but no index.html",
                    )
                    return False
            else:
                error_msg = result.stderr.strip() if result.stderr else "Build failed"
                self.log_operation(
                    "build_master",
                    "error",
                    f"Failed to build master docs: {error_msg}",
                    duration,
                )

                if self.debug:
                    click.echo(f"   ❌ Build errors: {error_msg}")

                return False

        except subprocess.TimeoutExpired:
            self.log_operation("build_master", "error", "Master build timeout")
            return False
        except Exception as e:
            self.log_operation(
                "build_master", "error", f"Exception building master docs: {e}"
            )
            return False

    def rebuild_all_documentation(
        self,
        packages: Optional[List[str]] = None,
        include_master: bool = True,
        force: bool = True,
        clean: bool = True,
    ) -> Dict[str, any]:
        """Rebuild all documentation in the Haive monorepo.

        Args:
            packages: List of specific packages to rebuild (default: all)
            include_master: Whether to rebuild master documentation hub
            force: Force overwrite existing documentation
            clean: Clean build artifacts first

        Returns:
            Summary of operations with success/failure counts
        """
        if not self.quiet:
            click.echo("🚀 Starting complete Haive documentation rebuild...")
            click.echo(f"   📁 Root: {self.haive_root}")
            click.echo(f"   📦 Packages: {len(packages or self.packages)}")
            click.echo(f"   🏛️  Master hub: {'Yes' if include_master else 'No'}")

        # Clear everything first
        clear_result = self.clear_all_documentation()

        # Determine packages to process
        packages_to_process = packages or self.packages
        existing_packages = [
            p for p in packages_to_process if (self.packages_dir / p).exists()
        ]

        if len(existing_packages) != len(packages_to_process):
            missing = set(packages_to_process) - set(existing_packages)
            self.log_operation("validation", "warning", f"Missing packages: {missing}")

        # Results tracking
        results = {
            "cleared": clear_result,
            "packages": {},
            "master": None,
            "summary": {
                "total_packages": len(existing_packages),
                "successful_inits": 0,
                "successful_builds": 0,
                "failed_packages": [],
                "master_success": False,
            },
        }

        # Phase 1: Initialize all packages
        if not self.quiet:
            click.echo(
                f"\n📚 Phase 1: Initializing {len(existing_packages)} packages..."
            )

        for package in existing_packages:
            init_success = self.initialize_package_docs(package, force=force)
            results["packages"][package] = {"init": init_success, "build": False}

            if init_success:
                results["summary"]["successful_inits"] += 1
            else:
                results["summary"]["failed_packages"].append(f"{package} (init)")

        # Phase 2: Build all packages
        if not self.quiet:
            click.echo(f"\n🔨 Phase 2: Building {len(existing_packages)} packages...")

        for package in existing_packages:
            if results["packages"][package]["init"]:  # Only build if init succeeded
                build_success = self.build_package_docs(package, clean=clean)
                results["packages"][package]["build"] = build_success

                if build_success:
                    results["summary"]["successful_builds"] += 1
                else:
                    results["summary"]["failed_packages"].append(f"{package} (build)")

        # Phase 3: Initialize and build master hub
        if include_master:
            if not self.quiet:
                click.echo("\n🏛️  Phase 3: Building master documentation hub...")

            master_init = self.initialize_master_docs(force=force)
            master_build = False

            if master_init:
                master_build = self.build_master_docs(clean=clean)

            results["master"] = {"init": master_init, "build": master_build}
            results["summary"]["master_success"] = master_init and master_build

            if not results["summary"]["master_success"]:
                results["summary"]["failed_packages"].append("master-hub")

        # Final summary
        total_duration = (datetime.now() - self.start_time).total_seconds()
        self.log_operation(
            "rebuild_complete",
            "success",
            f"Rebuilt {results['summary']['successful_builds']}/{results['summary']['total_packages']} packages",
            total_duration,
        )

        return results

    def get_operations_summary(self) -> Dict[str, any]:
        """Get a comprehensive summary of all operations performed."""
        total_duration = (datetime.now() - self.start_time).total_seconds()

        # Categorize operations
        operations_by_type = {}
        for op in self.operations_log:
            op_type = op["operation"]
            if op_type not in operations_by_type:
                operations_by_type[op_type] = {"success": 0, "error": 0, "warning": 0}
            operations_by_type[op_type][op["status"]] += 1

        return {
            "total_operations": len(self.operations_log),
            "total_duration_seconds": round(total_duration, 2),
            "operations_by_type": operations_by_type,
            "timeline": self.operations_log,
            "haive_root": str(self.haive_root),
            "packages_found": len(
                [p for p in self.packages if (self.packages_dir / p).exists()]
            ),
        }

    def save_operations_log(self, output_path: Optional[Path] = None) -> Path:
        """Save the operations log to a JSON file."""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.haive_root / f"haive_docs_rebuild_{timestamp}.json"

        summary = self.get_operations_summary()

        with open(output_path, "w") as f:
            json.dump(summary, f, indent=2, default=str)

        if not self.quiet:
            click.echo(f"📊 Operations log saved to: {output_path}")

        return output_path

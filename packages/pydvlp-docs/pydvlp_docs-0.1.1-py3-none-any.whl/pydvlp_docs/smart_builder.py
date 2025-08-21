#!/usr/bin/env python3
"""Smart documentation builder that handles large monorepos efficiently."""

import json
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import click

from .build_monitor import BuildMonitor
from .package_auditor import PackageAuditor


class SmartDocBuilder:
    """Smart documentation builder for large monorepos."""

    def __init__(self, root_path: Path, output_dir: Path = None):
        """Initialize smart builder."""
        self.root_path = Path(root_path)
        self.output_dir = output_dir or Path.cwd() / "smart_build_output"
        self.output_dir.mkdir(exist_ok=True)

        self.build_order = []
        self.results = {}
        self.start_time = datetime.now()

    def analyze_and_plan(self) -> Dict:
        """Analyze monorepo and create build plan."""
        click.echo("🔍 Analyzing monorepo structure...")

        # Run audit
        auditor = PackageAuditor(self.root_path)
        audit_data = auditor.audit_monorepo()

        # Save audit
        audit_file = self.output_dir / "build_audit.json"
        auditor.save_audit(audit_file)
        auditor.print_summary()

        # Create build plan based on dependencies and size
        self.build_order = self._determine_build_order(audit_data)

        # Save build plan
        plan = {
            "timestamp": datetime.now().isoformat(),
            "total_packages": len(self.build_order),
            "build_order": self.build_order,
            "estimated_time_minutes": sum(
                p["estimated_minutes"] for p in self.build_order
            ),
            "strategy": "individual" if len(audit_data["packages"]) > 5 else "combined",
        }

        plan_file = self.output_dir / "build_plan.json"
        with open(plan_file, "w") as f:
            json.dump(plan, f, indent=2)

        click.echo(f"\n📋 Build Plan saved to: {plan_file}")
        return plan

    def _determine_build_order(self, audit_data: Dict) -> List[Dict]:
        """Determine optimal build order."""
        packages = []

        # Core packages first (they're dependencies)
        priority_order = ["haive-core", "haive-tools", "haive-agents", "haive-games"]

        # Sort packages by priority then by size
        all_packages = list(audit_data["packages"].keys())

        # Priority packages first
        for pkg_name in priority_order:
            if pkg_name in all_packages:
                pkg_data = audit_data["packages"][pkg_name]
                packages.append(
                    {
                        "name": pkg_name,
                        "files": pkg_data["python_files"],
                        "estimated_minutes": round(
                            pkg_data["python_files"] * 0.6 / 60, 1
                        ),
                        "priority": "high",
                    }
                )
                all_packages.remove(pkg_name)

        # Then remaining packages by size (smallest first for quick wins)
        remaining = []
        for pkg_name in all_packages:
            pkg_data = audit_data["packages"][pkg_name]
            remaining.append(
                {
                    "name": pkg_name,
                    "files": pkg_data["python_files"],
                    "estimated_minutes": round(pkg_data["python_files"] * 0.6 / 60, 1),
                    "priority": "normal",
                }
            )

        remaining.sort(key=lambda x: x["files"])
        packages.extend(remaining)

        return packages

    def build_package(self, package_name: str, monitor_dir: Path) -> Tuple[bool, float]:
        """Build documentation for a single package with monitoring."""
        click.echo(f"\n{'='*60}")
        click.echo(f"📦 Building {package_name}")
        click.echo(f"{'='*60}")

        package_path = self.root_path / "packages" / package_name
        if not package_path.exists():
            click.echo(f"❌ Package {package_name} not found")
            return False, 0

        # Check prerequisites
        docs_path = package_path / "docs"
        pyproject_path = package_path / "pyproject.toml"

        if not docs_path.exists():
            click.echo(f"⚠️  No docs directory for {package_name}, skipping")
            return False, 0

        if not pyproject_path.exists():
            click.echo(
                f"⚠️  No pyproject.toml for {package_name}, skipping (required by seed_intersphinx_mapping)"
            )
            return False, 0

        # Create package-specific monitor
        monitor = BuildMonitor(monitor_dir, package_name)

        source_dir = docs_path / "source"
        build_dir = docs_path / "build" / "html"

        # Clean build directory
        if build_dir.exists():
            shutil.rmtree(build_dir)

        cmd = [
            "poetry",
            "run",
            "sphinx-build",
            "-b",
            "html",
            "--keep-going",  # Continue on errors
            "-j",
            "auto",  # Parallel build
            str(source_dir),
            str(build_dir),
            "-v",  # Verbose for monitoring
        ]

        # Run build with monitoring
        start_time = time.time()
        click.echo(f"⏱️  Starting at {datetime.now().strftime('%H:%M:%S')}")

        try:
            process = subprocess.Popen(
                cmd,
                cwd=package_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            # Monitor output
            for line in iter(process.stdout.readline, ""):
                if line:
                    monitor.process_line(line.strip())

            return_code = process.wait()
            elapsed = time.time() - start_time

            # Finalize monitoring
            monitor.finalize()

            # Check success
            success = return_code == 0 or not monitor.classifier.should_fail_build()

            # Print summary
            monitor.print_summary()
            click.echo(f"\n⏱️  Completed in {elapsed/60:.1f} minutes")

            return success, elapsed

        except Exception as e:
            click.echo(f"❌ Build failed with exception: {e}")
            monitor.finalize()
            return False, time.time() - start_time

    def build_all(self, parallel: bool = False):
        """Build all packages according to plan."""
        click.echo("\n🚀 Starting Smart Documentation Build")
        click.echo(f"📊 Total packages: {len(self.build_order)}")
        click.echo(
            f"⏱️  Estimated time: {sum(p['estimated_minutes'] for p in self.build_order):.1f} minutes"
        )

        # Create results tracking
        results_file = self.output_dir / "build_results.json"
        results = {
            "start_time": self.start_time.isoformat(),
            "packages": {},
            "summary": {},
        }

        successful = 0
        failed = 0
        total_time = 0

        # Build each package
        for i, package_info in enumerate(self.build_order, 1):
            package_name = package_info["name"]

            click.echo(f"\n📦 Package {i}/{len(self.build_order)}: {package_name}")
            click.echo(f"   Files: {package_info['files']}")
            click.echo(f"   Estimated: {package_info['estimated_minutes']} minutes")

            # Create package-specific monitoring directory
            package_monitor_dir = self.output_dir / package_name
            package_monitor_dir.mkdir(exist_ok=True)

            # Build package
            success, elapsed = self.build_package(package_name, package_monitor_dir)

            # Track results
            results["packages"][package_name] = {
                "success": success,
                "elapsed_seconds": round(elapsed, 2),
                "elapsed_minutes": round(elapsed / 60, 1),
                "estimated_minutes": package_info["estimated_minutes"],
                "files": package_info["files"],
            }

            if success:
                successful += 1
            else:
                failed += 1

            total_time += elapsed

            # Save intermediate results
            results["summary"] = {
                "completed": i,
                "successful": successful,
                "failed": failed,
                "total_elapsed_minutes": round(total_time / 60, 1),
                "average_seconds_per_file": round(
                    total_time / sum(p["files"] for p in self.build_order[:i]), 2
                ),
            }

            with open(results_file, "w") as f:
                json.dump(results, f, indent=2)

            # Short break between packages
            if i < len(self.build_order):
                click.echo("\n⏸️  Pausing 5 seconds before next package...")
                time.sleep(5)

        # Final summary
        self._print_final_summary(results)

    def _print_final_summary(self, results: Dict):
        """Print final build summary."""
        summary = results["summary"]

        click.echo("\n" + "=" * 60)
        click.echo("🏁 BUILD COMPLETE")
        click.echo("=" * 60)
        click.echo(f"Total Packages:     {summary['completed']}")
        click.echo(f"Successful:         {summary['successful']} ✅")
        click.echo(f"Failed:             {summary['failed']} ❌")
        click.echo(f"Total Time:         {summary['total_elapsed_minutes']} minutes")
        click.echo(f"Avg Time/File:      {summary['average_seconds_per_file']} seconds")

        if results["packages"]:
            click.echo("\n📊 Package Results:")
            for pkg_name, pkg_result in results["packages"].items():
                status = "✅" if pkg_result["success"] else "❌"
                click.echo(
                    f"   {status} {pkg_name:15} {pkg_result['elapsed_minutes']:5.1f}m (est: {pkg_result['estimated_minutes']}m)"
                )

        click.echo(f"\n📁 Full results saved to: {self.output_dir}")


def smart_build_docs(root_path: Path, output_dir: Path = None):
    """Run smart documentation build."""
    builder = SmartDocBuilder(root_path, output_dir)

    # Analyze and plan
    plan = builder.analyze_and_plan()

    # Ask for confirmation
    total_est = plan["estimated_time_minutes"]
    click.echo(f"\n🤔 Ready to build {plan['total_packages']} packages")
    click.echo(f"⏱️  Estimated total time: {total_est:.1f} minutes")

    if total_est > 30:
        click.echo("\n⚠️  This is a long build. Consider:")
        click.echo("   - Running with nohup for stability")
        click.echo("   - Building priority packages first")
        click.echo("   - Using a powerful machine")

    if click.confirm("\nProceed with build?", default=True):
        builder.build_all()
    else:
        click.echo("❌ Build cancelled")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        root = Path(sys.argv[1])
    else:
        root = Path.cwd()

    smart_build_docs(root)

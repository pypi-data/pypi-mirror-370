#!/usr/bin/env python3
"""Build monitoring system with separate error and progress tracking."""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .build_error_classifier import BuildError, BuildErrorClassifier, ErrorSeverity


class BuildMonitor:
    """Monitor long-running documentation builds with structured output."""

    def __init__(self, output_dir: Path, package_name: str = ""):
        """Initialize build monitor.

        Args:
            output_dir: Directory for output files
            package_name: Name of package being built
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.package_name = package_name

        # Output file paths
        self.progress_file = self.output_dir / "build_progress.log"
        self.errors_file = self.output_dir / "build_errors.json"
        self.raw_output_file = self.output_dir / "build_raw.log"
        self.summary_file = self.output_dir / "build_summary.json"

        # Initialize classifier
        self.classifier = BuildErrorClassifier(package_name)

        # Tracking
        self.start_time = datetime.now()
        self.last_update = self.start_time
        self.line_count = 0
        self.phase = "initializing"

        # Write initial files
        self._write_initial_files()

    def _write_initial_files(self):
        """Write initial content to monitoring files."""
        # Progress file header
        with open(self.progress_file, "w") as f:
            f.write(
                f"Build Monitor Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            f.write(f"Package: {self.package_name}\n")
            f.write("=" * 60 + "\n\n")

        # Initial summary
        self._update_summary()

    def process_line(self, line: str):
        """Process a single line of build output.

        Args:
            line: Line from build output
        """
        self.line_count += 1

        # Always write to raw output
        with open(self.raw_output_file, "a") as f:
            f.write(line + "\n")

        # Classify the line
        error = self.classifier.classify_line(line)

        # Update phase based on content
        self._detect_phase(line)

        # Write progress updates
        if self._is_progress_line(line):
            self._write_progress(line)

        # Update summary periodically
        if (datetime.now() - self.last_update).total_seconds() > 5:
            self._update_summary()
            self.last_update = datetime.now()

    def _detect_phase(self, line: str):
        """Detect current build phase from output."""
        if "reading sources" in line.lower():
            self.phase = "reading_sources"
        elif "building [" in line.lower():
            self.phase = "building"
        elif "writing output" in line.lower():
            self.phase = "writing_output"
        elif "copying static files" in line.lower():
            self.phase = "copying_files"
        elif "dumping object inventory" in line.lower():
            self.phase = "finalizing"
        elif "build succeeded" in line.lower():
            self.phase = "completed"
        elif "build finished with" in line.lower() and "error" in line.lower():
            self.phase = "failed"

    def _is_progress_line(self, line: str) -> bool:
        """Check if line contains progress information."""
        progress_indicators = [
            "reading sources",
            "building [",
            "writing output",
            "copying",
            "dumping",
            "%",
            "finished",
            "succeeded",
            "failed",
        ]
        return any(indicator in line.lower() for indicator in progress_indicators)

    def _write_progress(self, line: str):
        """Write progress update to progress file."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        with open(self.progress_file, "a") as f:
            f.write(f"[{timestamp}] [{self.phase:15}] {line.strip()}\n")

    def _update_summary(self):
        """Update summary file with current state."""
        summary = self.classifier.get_summary()

        # Add monitor metadata
        elapsed = (datetime.now() - self.start_time).total_seconds()

        # Convert error counts to serializable format
        error_counts = {}
        for severity, count in summary["counts"].items():
            error_counts[severity.value] = count

        # Create serializable summary
        serializable_summary = {
            "package": summary["package"],
            "total_errors": summary["total_errors"],
            "counts": error_counts,
            "has_critical": summary["has_critical"],
        }

        monitor_data = {
            "package": self.package_name,
            "start_time": self.start_time.isoformat(),
            "elapsed_seconds": round(elapsed, 2),
            "phase": self.phase,
            "lines_processed": self.line_count,
            "error_summary": serializable_summary,
            "critical_errors": [
                self._serialize_error(e) for e in summary["critical_errors"]
            ],
            "last_update": datetime.now().isoformat(),
        }

        # Write summary
        with open(self.summary_file, "w") as f:
            json.dump(monitor_data, f, indent=2)

        # Write errors file
        if summary["critical_errors"] or summary["warnings"]:
            errors_data = {
                "package": self.package_name,
                "timestamp": datetime.now().isoformat(),
                "critical": [
                    self._serialize_error(e) for e in summary["critical_errors"]
                ],
                "warnings": [self._serialize_error(e) for e in summary["warnings"]],
            }
            with open(self.errors_file, "w") as f:
                json.dump(errors_data, f, indent=2)

    def _serialize_error(self, error: BuildError) -> Dict:
        """Convert BuildError to serializable dict."""
        return {
            "severity": error.severity.value,
            "category": error.category,
            "message": error.message,
            "file_path": error.file_path,
            "line_number": error.line_number,
            "suggestion": error.suggestion,
            "raw_error": error.raw_error,
        }

    def finalize(self):
        """Finalize monitoring and write final summary."""
        self._update_summary()

        # Write final progress entry
        elapsed = (datetime.now() - self.start_time).total_seconds()
        with open(self.progress_file, "a") as f:
            f.write(f"\n{'=' * 60}\n")
            f.write(
                f"Build Monitor Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            f.write(f"Total Duration: {elapsed:.2f} seconds\n")
            f.write(f"Final Phase: {self.phase}\n")
            f.write(f"Total Lines: {self.line_count}\n")

    def print_summary(self):
        """Print a summary to console."""
        summary = self.classifier.get_summary()
        print(f"\n📊 Build Summary for {self.package_name}")
        print("=" * 40)
        print(f"Phase: {self.phase}")
        print(f"Critical Errors: {summary['counts'][ErrorSeverity.CRITICAL]}")
        print(f"Warnings: {summary['counts'][ErrorSeverity.WARNING]}")
        print(f"Lines Processed: {self.line_count}")

        if summary["has_critical"]:
            print("\n❌ Critical errors detected - build will fail")
        else:
            print("\n✅ No critical errors - build should succeed")


def tail_monitor_files(output_dir: Path, follow: bool = True):
    """Tail the monitor files for real-time monitoring.

    Args:
        output_dir: Directory containing monitor files
        follow: Whether to follow file updates
    """
    progress_file = output_dir / "build_progress.log"
    summary_file = output_dir / "build_summary.json"

    print(f"📊 Monitoring build in: {output_dir}")
    print(f"📄 Progress: {progress_file}")
    print(f"📋 Summary: {summary_file}")
    print("=" * 60)

    if follow:
        import subprocess

        # Use tail -f to follow progress
        subprocess.run(["tail", "-f", str(progress_file)])
    else:
        # Just show current state
        if summary_file.exists():
            with open(summary_file) as f:
                summary = json.load(f)

            print(f"\nPhase: {summary['phase']}")
            print(f"Elapsed: {summary['elapsed_seconds']}s")
            print(f"Critical Errors: {summary['error_summary']['counts']['critical']}")
            print(f"Warnings: {summary['error_summary']['counts']['warning']}")

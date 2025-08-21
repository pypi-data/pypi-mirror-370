"""Mock operations system for comprehensive dry-run and testing capabilities."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import tomlkit


class MockOperation:
    """Represents a mock operation that can be executed or simulated."""

    def __init__(
        self,
        operation_type: str,
        description: str,
        target: Union[str, Path] = "",
        details: List[str] = None,
        reversible: bool = True,
        risk_level: str = "low",
    ):
        self.operation_type = operation_type
        self.description = description
        self.target = str(target) if target else ""
        self.details = details or []
        self.reversible = reversible
        self.risk_level = risk_level  # low, medium, high
        self.timestamp = datetime.now()
        self.executed = False
        self.success = None
        self.error_message = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "type": self.operation_type,
            "description": self.description,
            "target": self.target,
            "details": self.details,
            "reversible": self.reversible,
            "risk_level": self.risk_level,
            "timestamp": self.timestamp.isoformat(),
            "executed": self.executed,
            "success": self.success,
            "error_message": self.error_message,
        }

    def __repr__(self) -> str:
        return f"MockOperation({self.operation_type}: {self.description})"


class MockFileOperation(MockOperation):
    """Mock operation for file system operations."""

    def __init__(
        self,
        operation_type: str,
        source_path: Path,
        target_path: Path = None,
        content: str = None,
        backup: bool = True,
    ):
        self.source_path = Path(source_path)
        self.target_path = Path(target_path) if target_path else None
        self.content = content
        self.backup = backup
        self.operation_type = operation_type  # Store operation_type before using it

        # Generate description
        if operation_type == "create_file":
            description = f"Create file {self.source_path}"
        elif operation_type == "copy_file":
            description = f"Copy {self.source_path} to {self.target_path}"
        elif operation_type == "edit_file":
            description = f"Edit file {self.source_path}"
        elif operation_type == "delete_file":
            description = f"Delete file {self.source_path}"
        else:
            description = f"{operation_type} on {self.source_path}"

        super().__init__(
            operation_type=operation_type,
            description=description,
            target=str(self.target_path or self.source_path),
            details=self._get_details(),
            reversible=backup and operation_type != "create_file",
            risk_level=self._assess_risk(),
        )

    def _get_details(self) -> List[str]:
        """Get operation details."""
        details = []
        if self.source_path.exists():
            details.append(f"Source exists: {self.source_path}")
        if self.target_path and self.target_path.exists():
            details.append(f"Target exists: {self.target_path}")
        if self.content:
            details.append(f"Content length: {len(self.content)} chars")
        if self.backup:
            details.append("Backup will be created")
        return details

    def _assess_risk(self) -> str:
        """Assess risk level of operation."""
        if self.operation_type == "delete_file":
            return "high" if not self.backup else "medium"
        elif self.operation_type == "edit_file":
            return "medium" if not self.backup else "low"
        else:
            return "low"


class MockDependencyOperation(MockOperation):
    """Mock operation for dependency management."""

    def __init__(
        self,
        operation_type: str,
        package_name: str,
        version: str = None,
        group: str = None,
        pyproject_path: Path = None,
    ):
        self.package_name = package_name
        self.version = version
        self.group = group
        self.pyproject_path = pyproject_path or Path("pyproject.toml")

        description = f"{operation_type} {package_name}"
        if version:
            description += f" v{version}"
        if group:
            description += f" to {group} group"

        super().__init__(
            operation_type=operation_type,
            description=description,
            target=str(self.pyproject_path),
            details=self._get_details(),
            reversible=True,
            risk_level="medium",
        )

    def _get_details(self) -> List[str]:
        """Get operation details."""
        details = [f"Package: {self.package_name}"]
        if self.version:
            details.append(f"Version: {self.version}")
        if self.group:
            details.append(f"Group: {self.group}")
        details.append(f"Target file: {self.pyproject_path}")
        return details


class MockOperationPlan:
    """A plan containing multiple mock operations."""

    def __init__(self, name: str = "Unnamed Plan"):
        self.name = name
        self.operations: List[MockOperation] = []
        self.created_at = datetime.now()
        self.executed = False

    def add_operation(self, operation: MockOperation) -> None:
        """Add an operation to the plan."""
        self.operations.append(operation)

    def add_file_operation(
        self,
        operation_type: str,
        source_path: Path,
        target_path: Path = None,
        content: str = None,
        backup: bool = True,
    ) -> MockFileOperation:
        """Add a file operation to the plan."""
        op = MockFileOperation(
            operation_type, source_path, target_path, content, backup
        )
        self.add_operation(op)
        return op

    def add_dependency_operation(
        self,
        operation_type: str,
        package_name: str,
        version: str = None,
        group: str = None,
        pyproject_path: Path = None,
    ) -> MockDependencyOperation:
        """Add a dependency operation to the plan."""
        op = MockDependencyOperation(
            operation_type, package_name, version, group, pyproject_path
        )
        self.add_operation(op)
        return op

    def get_operations_by_type(self, operation_type: str) -> List[MockOperation]:
        """Get all operations of a specific type."""
        return [op for op in self.operations if op.operation_type == operation_type]

    def get_operations_by_risk(self, risk_level: str) -> List[MockOperation]:
        """Get all operations of a specific risk level."""
        return [op for op in self.operations if op.risk_level == risk_level]

    def get_high_risk_operations(self) -> List[MockOperation]:
        """Get all high-risk operations."""
        return self.get_operations_by_risk("high")

    def simulate_execution(self) -> Dict[str, Any]:
        """Simulate execution and return results."""
        results = {
            "plan_name": self.name,
            "total_operations": len(self.operations),
            "operations_by_type": {},
            "operations_by_risk": {"low": 0, "medium": 0, "high": 0},
            "high_risk_operations": [],
            "estimated_duration": self._estimate_duration(),
            "reversible_operations": 0,
            "irreversible_operations": 0,
        }

        # Analyze operations
        for op in self.operations:
            # Count by type
            op_type = op.operation_type
            results["operations_by_type"][op_type] = (
                results["operations_by_type"].get(op_type, 0) + 1
            )

            # Count by risk
            results["operations_by_risk"][op.risk_level] += 1

            # Track reversibility
            if op.reversible:
                results["reversible_operations"] += 1
            else:
                results["irreversible_operations"] += 1

            # Collect high-risk operations
            if op.risk_level == "high":
                results["high_risk_operations"].append(op.to_dict())

        return results

    def _estimate_duration(self) -> float:
        """Estimate execution duration in seconds."""
        # Simple estimation based on operation types
        duration_map = {
            "create_file": 0.1,
            "copy_file": 0.2,
            "edit_file": 0.15,
            "delete_file": 0.05,
            "add_dependency": 1.0,
            "remove_dependency": 0.5,
            "update_dependency": 0.8,
        }

        total = 0
        for op in self.operations:
            total += duration_map.get(op.operation_type, 0.2)

        return total

    def to_dict(self) -> Dict[str, Any]:
        """Convert plan to dictionary for serialization."""
        return {
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "executed": self.executed,
            "operations": [op.to_dict() for op in self.operations],
        }

    def save_to_file(self, file_path: Path) -> None:
        """Save plan to JSON file."""
        with open(file_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_file(cls, file_path: Path) -> "MockOperationPlan":
        """Load plan from JSON file."""
        with open(file_path, "r") as f:
            data = json.load(f)

        plan = cls(data["name"])
        plan.created_at = datetime.fromisoformat(data["created_at"])
        plan.executed = data["executed"]

        for op_data in data["operations"]:
            # Reconstruct operation based on type
            if op_data["type"] in [
                "create_file",
                "copy_file",
                "edit_file",
                "delete_file",
            ]:
                op = MockFileOperation.__new__(MockFileOperation)
                op.__dict__.update(op_data)
            elif op_data["type"] in [
                "add_dependency",
                "remove_dependency",
                "update_dependency",
            ]:
                op = MockDependencyOperation.__new__(MockDependencyOperation)
                op.__dict__.update(op_data)
            else:
                op = MockOperation.__new__(MockOperation)
                op.__dict__.update(op_data)

            plan.operations.append(op)

        return plan


def create_documentation_plan(
    project_path: Path, analysis: Dict[str, Any], force: bool = False
) -> MockOperationPlan:
    """Create a mock operation plan for documentation initialization."""
    plan = MockOperationPlan("Documentation Initialization")

    # Analyze what needs to be done
    docs_path = project_path / "docs"
    source_path = docs_path / "source"

    # Check if docs exist
    if docs_path.exists() and not force:
        plan.add_operation(
            MockOperation(
                "skip",
                "Documentation already exists",
                target=str(docs_path),
                details=["Use --force to overwrite"],
                risk_level="low",
            )
        )
        return plan

    # Create directories
    plan.add_file_operation("create_directory", docs_path)
    plan.add_file_operation("create_directory", source_path)
    plan.add_file_operation("create_directory", source_path / "_static")
    plan.add_file_operation("create_directory", source_path / "_templates")

    # Create configuration files
    plan.add_file_operation(
        "create_file",
        source_path / "conf.py",
        content="# Sphinx configuration file\n# Generated by pydvlp-docs",
    )

    plan.add_file_operation(
        "create_file",
        source_path / "index.rst",
        content=f"# {analysis.get('name', 'Project')} Documentation\n",
    )

    # Create Makefile
    plan.add_file_operation(
        "create_file", docs_path / "Makefile", content="# Documentation build Makefile"
    )

    # Add documentation dependencies
    if analysis.get("package_manager") == "poetry":
        plan.add_dependency_operation("add_dependency", "pydvlp-docs", group="docs")

    return plan


def create_package_docs_plan(
    package_path: Path, package_name: str, shared_config: bool = True
) -> MockOperationPlan:
    """Create a mock operation plan for individual package documentation."""
    plan = MockOperationPlan(f"Package Documentation: {package_name}")

    docs_path = package_path / "docs"
    source_path = docs_path / "source"

    # Create package-specific directories
    plan.add_file_operation("create_directory", docs_path)
    plan.add_file_operation("create_directory", source_path)

    if shared_config:
        # Use shared configuration
        conf_content = f"""\"\"\"Sphinx configuration for {package_name}.\"\"\"

from pydvlp_docs.config import get_haive_config

config = get_haive_config(
    package_name="{package_name}",
    package_path="../../src",
    is_central_hub=False
)

globals().update(config)
"""
    else:
        # Standalone configuration
        conf_content = f"""\"\"\"Sphinx configuration for {package_name}.\"\"\"

project = "{package_name}"
author = "Team"
extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon"]
"""

    plan.add_file_operation(
        "create_file", source_path / "conf.py", content=conf_content
    )

    # Create package index
    index_content = f"""{package_name}
{'=' * len(package_name)}

.. automodule:: {package_name.replace('-', '.')}
   :members:
"""

    plan.add_file_operation(
        "create_file", source_path / "index.rst", content=index_content
    )

    return plan

"""Custom Jinja2 filters for intelligent template system."""

import json
import re
from typing import Any, Dict, List, Optional, Union


def is_pydantic_model(obj: Dict[str, Any]) -> bool:
    """Check if object is a Pydantic model."""
    bases = obj.get("bases", [])
    return any("BaseModel" in str(base) or "pydantic" in str(base) for base in bases)


def is_agent_class(obj: Dict[str, Any]) -> bool:
    """Check if object is an Agent class."""
    bases = obj.get("bases", [])
    name = obj.get("name", "")
    return any("Agent" in str(base) for base in bases) or "Agent" in name


def is_tool_class(obj: Dict[str, Any]) -> bool:
    """Check if object is a Tool class."""
    bases = obj.get("bases", [])
    name = obj.get("name", "")
    return any("Tool" in str(base) for base in bases) or "Tool" in name


def is_enum_class(obj: Dict[str, Any]) -> bool:
    """Check if object is an Enum class."""
    bases = obj.get("bases", [])
    return any("Enum" in str(base) for base in bases)


def is_dataclass(obj: Dict[str, Any]) -> bool:
    """Check if object is a dataclass."""
    decorators = obj.get("decorators", [])
    return any("dataclass" in str(dec) for dec in decorators)


def format_annotation(annotation: str) -> str:
    """Format type annotation for better readability."""
    # Remove typing module prefix
    annotation = re.sub(r"\btyping\.", "", annotation)
    annotation = re.sub(r"\bcollections\.abc\.", "", annotation)

    # Format Union types
    annotation = re.sub(
        r"Union\[([^]]+)\]", lambda m: " | ".join(m.group(1).split(", ")), annotation
    )

    # Format Optional
    annotation = re.sub(r"Optional\[([^]]+)\]", r"\1 | None", annotation)

    return annotation


def extract_type_params(annotation: str) -> List[str]:
    """Extract type parameters from generic annotation."""
    match = re.search(r"\[([^]]+)\]", annotation)
    if match:
        return [param.strip() for param in match.group(1).split(",")]
    return []


def is_async_function(obj: Dict[str, Any]) -> bool:
    """Check if function is async."""
    return obj.get("is_async", False) or "async" in obj.get("properties", [])


def get_decorator_names(obj: Dict[str, Any]) -> List[str]:
    """Get list of decorator names."""
    decorators = obj.get("decorators", [])
    names = []
    for dec in decorators:
        # Extract decorator name from string representation
        if isinstance(dec, str):
            match = re.search(r"@(\w+)", dec)
            if match:
                names.append(match.group(1))
        else:
            names.append(str(dec))
    return names


def has_decorator(obj: Dict[str, Any], decorator_name: str) -> bool:
    """Check if object has specific decorator."""
    decorators = get_decorator_names(obj)
    return decorator_name in decorators


def get_complexity_score(obj: Dict[str, Any]) -> int:
    """Calculate complexity score for progressive disclosure."""
    score = 0

    # Base scores by type
    if obj.get("type") == "class":
        score += 10
    elif obj.get("type") == "function":
        score += 5

    # Add for various features
    if obj.get("methods"):
        score += len(obj.get("methods", []))
    if obj.get("attributes"):
        score += len(obj.get("attributes", []))
    if obj.get("parameters"):
        score += len(obj.get("parameters", []))
    if is_async_function(obj):
        score += 3
    if obj.get("decorators"):
        score += 2

    return score


def should_show_expanded(obj: Dict[str, Any]) -> bool:
    """Determine if section should be expanded by default."""
    # Important items that should be expanded
    if obj.get("type") == "module" and "core" in obj.get("name", ""):
        return True
    if obj.get("type") == "class" and obj.get("is_exception"):
        return True
    if get_complexity_score(obj) < 15:
        return True
    return False


def group_by_category(items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group items by their category."""
    categories = {
        "models": [],
        "agents": [],
        "tools": [],
        "exceptions": [],
        "enums": [],
        "utilities": [],
        "other": [],
    }

    for item in items:
        if is_pydantic_model(item):
            categories["models"].append(item)
        elif is_agent_class(item):
            categories["agents"].append(item)
        elif is_tool_class(item):
            categories["tools"].append(item)
        elif item.get("is_exception"):
            categories["exceptions"].append(item)
        elif is_enum_class(item):
            categories["enums"].append(item)
        elif item.get("type") == "function":
            categories["utilities"].append(item)
        else:
            categories["other"].append(item)

    # Remove empty categories
    return {k: v for k, v in categories.items() if v}


def get_method_category(method: Dict[str, Any]) -> str:
    """Categorize method for better organization."""
    name = method.get("name", "")

    # Magic methods
    if name.startswith("__") and name.endswith("__"):
        return "magic"

    # Private methods
    if name.startswith("_"):
        return "private"

    # Common patterns
    if name.startswith(("get_", "fetch_")):
        return "getters"
    if name.startswith(("set_", "update_")):
        return "setters"
    if name.startswith(("is_", "has_", "can_")):
        return "predicates"
    if name.startswith(("to_", "as_", "from_")):
        return "converters"
    if name.startswith(("validate_", "check_")):
        return "validators"
    if name.startswith(("handle_", "process_")):
        return "handlers"

    return "public"


def group_methods(methods: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group methods by category."""
    grouped = {}
    for method in methods:
        category = get_method_category(method)
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(method)
    return grouped


def format_parameter_list(params: List[Dict[str, Any]]) -> str:
    """Format parameter list for display."""
    if not params:
        return "()"

    parts = []
    for param in params:
        part = param.get("name", "")
        if param.get("annotation"):
            part += f": {format_annotation(param['annotation'])}"
        if param.get("default"):
            part += f" = {param['default']}"
        parts.append(part)

    return f"({', '.join(parts)})"


def get_summary_stats(obj: Dict[str, Any]) -> Dict[str, int]:
    """Get summary statistics for an object."""
    stats = {
        "methods": len(obj.get("methods", [])),
        "attributes": len(obj.get("attributes", [])),
        "properties": len(
            [m for m in obj.get("methods", []) if has_decorator(m, "property")]
        ),
        "classmethods": len(
            [m for m in obj.get("methods", []) if has_decorator(m, "classmethod")]
        ),
        "staticmethods": len(
            [m for m in obj.get("methods", []) if has_decorator(m, "staticmethod")]
        ),
        "subclasses": len(obj.get("subclasses", [])),
    }
    return {k: v for k, v in stats.items() if v > 0}


def to_snake_case(text: str) -> str:
    """Convert text to snake_case."""
    # Handle camelCase
    text = re.sub(r"([a-z])([A-Z])", r"\1_\2", text)
    # Handle multiple capitals
    text = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", text)
    return text.lower()


def to_kebab_case(text: str) -> str:
    """Convert text to kebab-case."""
    return to_snake_case(text).replace("_", "-")


def pluralize(word: str, count: int) -> str:
    """Simple pluralization."""
    if count == 1:
        return word

    # Common patterns
    if word.endswith("y"):
        return word[:-1] + "ies"
    if word.endswith(("s", "x", "z", "ch", "sh")):
        return word + "es"
    return word + "s"


def truncate_with_ellipsis(text: str, length: int = 80) -> str:
    """Truncate text with ellipsis."""
    if len(text) <= length:
        return text
    return text[: length - 3] + "..."


def highlight_code(code: str, language: str = "python") -> str:
    """Format code for highlighting."""
    # This is a placeholder - actual highlighting would use Pygments
    return f"```{language}\n{code}\n```"


def extract_first_sentence(text: str) -> str:
    """Extract first sentence from docstring."""
    if not text:
        return ""

    # Find first sentence ending
    match = re.search(r"^[^.!?]+[.!?]", text.strip())
    if match:
        return match.group(0).strip()
    return text.split("\n")[0].strip()


def count_lines(text: str) -> int:
    """Count lines in text."""
    return len(text.splitlines())


def get_indentation_level(line: str) -> int:
    """Get indentation level of a line."""
    return len(line) - len(line.lstrip())


def create_anchor(text: str) -> str:
    """Create HTML anchor from text."""
    return re.sub(r"[^\w\s-]", "", text.lower()).replace(" ", "-")


def json_pretty(obj: Any, indent: int = 2) -> str:
    """Pretty print JSON."""
    return json.dumps(obj, indent=indent, sort_keys=True)


# Export all filters
FILTERS = {
    "is_pydantic_model": is_pydantic_model,
    "is_agent_class": is_agent_class,
    "is_tool_class": is_tool_class,
    "is_enum_class": is_enum_class,
    "is_dataclass": is_dataclass,
    "format_annotation": format_annotation,
    "extract_type_params": extract_type_params,
    "is_async_function": is_async_function,
    "get_decorator_names": get_decorator_names,
    "has_decorator": has_decorator,
    "get_complexity_score": get_complexity_score,
    "should_show_expanded": should_show_expanded,
    "group_by_category": group_by_category,
    "get_method_category": get_method_category,
    "group_methods": group_methods,
    "format_parameter_list": format_parameter_list,
    "get_summary_stats": get_summary_stats,
    "to_snake_case": to_snake_case,
    "to_kebab_case": to_kebab_case,
    "pluralize": pluralize,
    "truncate_with_ellipsis": truncate_with_ellipsis,
    "highlight_code": highlight_code,
    "extract_first_sentence": extract_first_sentence,
    "count_lines": count_lines,
    "get_indentation_level": get_indentation_level,
    "create_anchor": create_anchor,
    "json_pretty": json_pretty,
}

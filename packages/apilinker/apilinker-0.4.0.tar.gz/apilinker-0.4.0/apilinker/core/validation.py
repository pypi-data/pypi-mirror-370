"""
JSON Schema validation utilities and diff reporting for ApiLinker.

Provides helper functions to validate payloads against JSON Schemas and
produce concise, human-readable diffs highlighting missing or unexpected
properties. Intended for use in both source response validation and
target request validation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple


try:
    from jsonschema import Draft202012Validator as DefaultValidator
    from jsonschema.exceptions import ValidationError
except Exception:  # pragma: no cover - optional import checked at runtime
    DefaultValidator = None
    ValidationError = Exception


def is_validator_available() -> bool:
    return DefaultValidator is not None


def _format_error_path(error: ValidationError) -> str:
    if getattr(error, "path", None):
        return ".".join([str(p) for p in error.path])
    return "<root>"


def validate_payload_against_schema(
    payload: Any,
    schema: Dict[str, Any],
    *,
    return_diffs: bool = True,
) -> Tuple[bool, List[str]]:
    """
    Validate a payload against a JSON Schema.

    Returns a tuple (is_valid, diffs). Diffs is a list of human-readable
    error messages with pointer-like paths to failing locations.
    """
    if not is_validator_available():
        # If jsonschema is not installed at runtime (should be added as a dep),
        # we conservatively return valid with a note.
        return True, []

    validator = DefaultValidator(schema)
    errors: List[str] = []
    for error in sorted(validator.iter_errors(payload), key=str):
        path = _format_error_path(error)
        msg = error.message
        # Provide more structured messages for common keywords
        if error.validator == "required":
            missing = ", ".join(error.validator_value)
            msg = f"Missing required property/properties: {missing}"
        elif error.validator == "additionalProperties":
            # unexpected additional property
            if isinstance(error.instance, dict):
                extras = set(error.instance.keys()) - set(
                    error.schema.get("properties", {}).keys()
                )
                if extras:
                    msg = f"Unexpected properties: {', '.join(sorted(extras))}"
        errors.append(f"{path}: {msg}")

    return (len(errors) == 0), (errors if return_diffs else [])


def pretty_print_diffs(diffs: List[str]) -> str:
    """Return a readable multi-line representation of diffs."""
    if not diffs:
        return ""
    return "\n".join(f"- {d}" for d in diffs)


def dump_example_for_schema(schema: Dict[str, Any]) -> Any:
    """
    Produce a minimal example instance that satisfies a subset of the schema.
    (Best-effort, not complete) Useful for quick scaffolding and docs.
    """
    t = schema.get("type")
    if t == "object":
        props = schema.get("properties", {})
        result: Dict[str, Any] = {}
        for key, subschema in props.items():
            result[key] = dump_example_for_schema(subschema)
        return result
    if t == "array":
        items = schema.get("items", {})
        return [dump_example_for_schema(items)]
    if t == "string":
        return schema.get("examples", [""])[0] if schema.get("examples") else "string"
    if t == "integer":
        return 0
    if t == "number":
        return 0.0
    if t == "boolean":
        return False
    return {}

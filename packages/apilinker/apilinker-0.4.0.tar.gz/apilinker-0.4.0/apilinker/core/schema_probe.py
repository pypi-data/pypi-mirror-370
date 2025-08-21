"""
Schema probing utilities to suggest initial mapping templates from sampled responses.

Given example JSON payloads, infer a lightweight structural schema and
produce a mapping template skeleton (source paths only) to accelerate
configuration authoring.
"""

from __future__ import annotations

from typing import Any, Dict, List


def _infer_type(value: Any) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "null"


def infer_schema(sample: Any, max_depth: int = 5) -> Dict[str, Any]:
    """Infer a minimal JSON-like schema from a sample instance."""
    if max_depth < 0:
        return {"type": "object"}

    t = _infer_type(sample)
    if t == "object":
        props: Dict[str, Any] = {}
        for k, v in sample.items():
            props[k] = infer_schema(v, max_depth=max_depth - 1)
        return {"type": "object", "properties": props}
    if t == "array":
        item_schema = (
            infer_schema(sample[0], max_depth=max_depth - 1)
            if sample
            else {"type": "object"}
        )
        return {"type": "array", "items": item_schema}
    return {"type": t}


def _collect_paths(sample: Any, prefix: str = "") -> List[str]:
    paths: List[str] = []
    if isinstance(sample, dict):
        for k, v in sample.items():
            base = f"{prefix}.{k}" if prefix else k
            paths.extend(_collect_paths(v, base))
    elif isinstance(sample, list):
        # represent first item path for arrays
        base = f"{prefix}[0]" if prefix else "[0]"
        paths.extend(_collect_paths(sample[0], base) if sample else [base])
    else:
        paths.append(prefix or "<root>")
    return paths


def suggest_mapping_template(source_sample: Any, target_sample: Any) -> Dict[str, Any]:
    """
    Produce a naive mapping suggestion by pairing source and target leaf paths
    positionally. Intended as a starting point; requires human review.
    """
    source_paths = _collect_paths(source_sample)
    target_paths = _collect_paths(target_sample)
    pairs = zip(source_paths, target_paths)
    fields = [{"source": s, "target": t} for s, t in pairs]
    return {"fields": fields}

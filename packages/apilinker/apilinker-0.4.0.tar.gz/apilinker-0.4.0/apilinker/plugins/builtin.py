"""
Built-in plugins for ApiLinker.

This module contains the built-in plugins that are available by default
in ApiLinker, including transformers, connectors, and authentication plugins.
"""

from typing import Any

from apilinker.core.plugins import TransformerPlugin


class JsonPathTransformer(TransformerPlugin):
    """
    A transformer that extracts values from a JSON object using JSONPath syntax.
    """

    plugin_name = "jsonpath"
    plugin_type = "transformer"

    def transform(
        self, value: Any, path: str = "", default: Any = None, **kwargs: Any
    ) -> Any:
        """
        Extract a value from a JSON object using JSONPath syntax.

        Args:
            value: JSON object to extract from
            path: JSONPath expression
            default: Default value if path not found
            **kwargs: Additional parameters

        Returns:
            Extracted value or default if not found
        """
        if not value or not path:
            return default

        try:
            # Simple dot notation implementation (for full JSONPath, use jsonpath-ng)
            parts = path.split(".")
            result = value

            for part in parts:
                # Handle array indexing
                if "[" in part and part.endswith("]"):
                    name, index_str = part.split("[", 1)
                    index = int(index_str[:-1])

                    if name:
                        if isinstance(result, dict) and name in result:
                            result = result[name]
                        else:
                            return default

                    if isinstance(result, list) and 0 <= index < len(result):
                        result = result[index]
                    else:
                        return default
                # Handle normal property access
                elif isinstance(result, dict) and part in result:
                    result = result[part]
                else:
                    return default

            return result
        except Exception:
            return default


class TemplateTransformer(TransformerPlugin):
    """
    A transformer that applies a template to a value.
    """

    plugin_name = "template"
    plugin_type = "transformer"

    def transform(self, value: Any, template: str = "", **kwargs: Any) -> str:
        """
        Apply a template to a value.

        Args:
            value: Value to transform
            template: Template string with {placeholders}
            **kwargs: Additional values for the template

        Returns:
            Formatted template string
        """
        if not template:
            return str(value) if value is not None else ""

        context = {"value": value}
        if kwargs:
            context.update(kwargs)

        try:
            return template.format(**context)
        except Exception as e:
            return f"Template Error: {str(e)}"


class ArrayOperationsTransformer(TransformerPlugin):
    """
    A transformer that performs operations on arrays.
    """

    plugin_name = "array_ops"
    plugin_type = "transformer"

    def transform(self, value: Any, operation: str = "count", **kwargs: Any) -> Any:
        """
        Perform operations on arrays.

        Args:
            value: Array to operate on
            operation: Operation to perform (count, sum, avg, min, max, join)
            **kwargs: Additional parameters for the operation

        Returns:
            Result of the operation
        """
        if not isinstance(value, list):
            if value is None:
                value = []
            else:
                value = [value]

        if operation == "count":
            return len(value)
        elif operation == "sum":
            return sum(
                float(x)
                for x in value
                if isinstance(x, (int, float, str)) and str(x).strip()
            )
        elif operation == "avg":
            nums = [
                float(x)
                for x in value
                if isinstance(x, (int, float, str)) and str(x).strip()
            ]
            return sum(nums) / len(nums) if nums else 0
        elif operation == "min":
            nums = [
                float(x)
                for x in value
                if isinstance(x, (int, float, str)) and str(x).strip()
            ]
            return min(nums) if nums else None
        elif operation == "max":
            nums = [
                float(x)
                for x in value
                if isinstance(x, (int, float, str)) and str(x).strip()
            ]
            return max(nums) if nums else None
        elif operation == "join":
            separator = kwargs.get("separator", ",")
            return separator.join(str(x) for x in value if x is not None)
        else:
            return value

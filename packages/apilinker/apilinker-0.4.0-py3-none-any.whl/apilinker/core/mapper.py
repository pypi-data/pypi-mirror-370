"""
Field mapper for transforming data between source and target APIs.
"""

import importlib
import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class FieldMapper:
    """
    Maps fields between source and target APIs, including transformations.

    This class handles the mapping of fields from source to target format,
    including nested fields, transformations, and filtering.
    """

    def __init__(self) -> None:
        self.mappings: List[Dict[str, Any]] = []
        self.transformers: Dict[str, Callable] = self._register_built_in_transformers()
        logger.debug("Initialized FieldMapper")

    def _register_built_in_transformers(self) -> Dict[str, Callable]:
        """Register built-in transformation functions."""
        return {
            # Date/time transformations
            "iso_to_timestamp": lambda v: (
                int(datetime.fromisoformat(v.replace("Z", "+00:00")).timestamp())
                if v
                else None
            ),
            "timestamp_to_iso": lambda v: (
                datetime.fromtimestamp(int(v)).isoformat() if v else None
            ),
            # String transformations
            "lowercase": lambda v: v.lower() if v else None,
            "uppercase": lambda v: v.upper() if v else None,
            "strip": lambda v: v.strip() if v else None,
            # Type conversions
            "to_string": lambda v: str(v) if v is not None else "",
            "to_int": lambda v: int(float(v)) if v else 0,
            "to_float": lambda v: float(v) if v else 0.0,
            "to_bool": lambda v: bool(v) if v is not None else False,
            # Null handling
            "default_empty_string": lambda v: v if v is not None else "",
            "default_zero": lambda v: v if v is not None else 0,
            "none_if_empty": lambda v: v if v else None,
        }

    def register_transformer(self, name: str, func: Callable) -> None:
        """
        Register a custom transformation function.

        Args:
            name: Name of the transformer
            func: Function that performs the transformation
        """
        if name in self.transformers:
            logger.warning(f"Overwriting existing transformer: {name}")
        self.transformers[name] = func
        logger.debug(f"Registered transformer: {name}")

    def load_custom_transformer(
        self, module_path: str, function_name: str, alias: Optional[str] = None
    ) -> None:
        """
        Load a custom transformer function from a Python module.

        Args:
            module_path: Import path for the module
            function_name: Name of the function in the module
            alias: Optional alternative name to register the transformer under
        """
        try:
            module = importlib.import_module(module_path)
            func = getattr(module, function_name)

            # Register with the provided alias or the original function name
            name = alias or function_name
            self.register_transformer(name, func)
            logger.info(
                f"Loaded custom transformer from {module_path}.{function_name} as {name}"
            )

        except (ImportError, AttributeError) as e:
            logger.error(f"Error loading custom transformer: {str(e)}")
            raise ValueError(
                f"Failed to load transformer from {module_path}.{function_name}: {str(e)}"
            )

    def add_mapping(
        self, source: str, target: str, fields: List[Dict[str, Any]]
    ) -> None:
        """
        Add a field mapping between source and target endpoints.

        Args:
            source: Source endpoint name
            target: Target endpoint name
            fields: List of field mappings (dicts with source, target, and optional transform)
        """
        # Validate that required fields are present
        for field in fields:
            if "source" not in field or "target" not in field:
                raise ValueError(
                    "Field mapping must contain 'source' and 'target' keys"
                )

        self.mappings.append({"source": source, "target": target, "fields": fields})
        logger.debug(
            f"Added mapping from {source} to {target} with {len(fields)} fields"
        )

    def get_mappings(self) -> List[Dict[str, Any]]:
        """Get all defined mappings."""
        return self.mappings

    def get_first_mapping(self) -> Optional[Dict[str, Any]]:
        """Get the first mapping if any exists."""
        return self.mappings[0] if self.mappings else None

    def get_value_from_path(self, data: Dict[str, Any], path: str) -> Any:
        """
        Extract a value from nested dictionary using dot notation.

        Args:
            data: Source data dictionary
            path: Path to the value using dot notation (e.g., "user.address.city")

        Returns:
            The value at the specified path or None if not found
        """
        if not path:
            return data

        # Handle array indexing in path (e.g., "items[0].name")
        parts: List[Union[str, int]] = []
        current_part = ""
        i = 0
        while i < len(path):
            if path[i] == "[":
                if current_part:
                    parts.append(current_part)
                    current_part = ""

                # Extract the array index
                i += 1
                index_str = ""
                while i < len(path) and path[i] != "]":
                    index_str += path[i]
                    i += 1

                # Add the index as a separate part
                if index_str.isdigit():
                    parts.append(int(index_str))
                i += 1  # Skip the closing bracket
            elif path[i] == ".":
                if current_part:
                    parts.append(current_part)
                    current_part = ""
                i += 1
            else:
                current_part += path[i]
                i += 1

        if current_part:
            parts.append(current_part)

        # Navigate through the path
        current: Any = data
        for part in parts:
            if isinstance(current, dict) and isinstance(part, str):
                if part in current:
                    current = current[part]
                else:
                    return None
            elif isinstance(current, list) and isinstance(part, int):
                if 0 <= part < len(current):
                    current = current[part]
                else:
                    return None
            else:
                return None

        return current

    def set_value_at_path(self, data: Dict[str, Any], path: str, value: Any) -> None:
        """
        Set a value in a nested dictionary using dot notation.

        Args:
            data: Target data dictionary
            path: Path where to set the value using dot notation
            value: Value to set
        """
        if not path:
            return

        parts = path.split(".")

        # Navigate to the parent of the leaf node
        current = data
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                current[part] = {}
            current = current[part]

        # Set the value at the leaf node
        current[parts[-1]] = value

    def apply_transform(
        self,
        value: Any,
        transform: Union[str, List[str], Dict[str, Any]],
        params: Dict[str, Any] = None,
    ) -> Any:
        """
        Apply a transformation to a value.

        Args:
            value: The value to transform
            transform: The transformation to apply (string name or list of transforms)
            params: Optional parameters for the transformer

        Returns:
            Transformed value
        """
        # Handle None values
        if value is None:
            # Special case transformers that handle None
            if transform == "default_empty_string":
                return ""
            elif transform == "default_zero":
                return 0
            else:
                return None

        # Handle empty params
        if params is None:
            params = {}

        # Handle list of transformations
        if isinstance(transform, list):
            result = value
            for t in transform:
                result = self.apply_transform(result, t)
            return result

        # Handle transformation with parameters
        if isinstance(transform, dict):
            name = transform.get("name")
            transform_params = transform.get("params", {})

            if not name or name not in self.transformers:
                logger.warning(f"Unknown transformer: {name}")
                return value

            return self.transformers[name](value, **transform_params)

        # Simple string transformer name
        if transform not in self.transformers:
            logger.warning(f"Unknown transformer: {transform}")
            return value

        # Special handling for list inputs with certain transforms
        if isinstance(value, list) and transform in ["lowercase", "uppercase", "strip"]:
            return [
                self.transformers[transform](item) if isinstance(item, str) else item
                for item in value
            ]

        # Apply the transformation with parameters if provided
        if params:
            return self.transformers[transform](value, **params)
        else:
            return self.transformers[transform](value)

    def map_data(
        self,
        source_endpoint: str,
        target_endpoint: str,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Map data from source format to target format.

        Args:
            source_endpoint: Source endpoint name
            target_endpoint: Target endpoint name
            data: Data to map

        Returns:
            Mapped data in target format
        """
        # Find the appropriate mapping
        mapping = None
        for m in self.mappings:
            if m["source"] == source_endpoint and m["target"] == target_endpoint:
                mapping = m
                break

        if not mapping:
            logger.warning(
                f"No mapping found for {source_endpoint} to {target_endpoint}"
            )
            return data

        logger.debug(f"Mapping data using {len(mapping['fields'])} field mappings")

        # Handle list of items
        if isinstance(data, list):
            return [self._map_item(item, mapping["fields"]) for item in data]

        # Handle single item
        return self._map_item(data, mapping["fields"])

    def _map_item(
        self, item: Dict[str, Any], fields: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Map a single data item according to field mappings.

        Args:
            item: Source data item
            fields: Field mapping configurations

        Returns:
            Mapped data item
        """
        result: Dict[str, Any] = {}

        for field in fields:
            source_path = field["source"]
            target_path = field["target"]

            # Get source value
            source_value = self.get_value_from_path(item, source_path)

            # Apply transformation if specified
            if "transform" in field and field["transform"]:
                transform = field["transform"]
                if isinstance(transform, str):
                    # Single transformation
                    source_value = self.apply_transform(source_value, transform)
                elif isinstance(transform, list):
                    # Multiple transformations in sequence
                    for t in transform:
                        source_value = self.apply_transform(source_value, t)
                else:
                    logger.warning(f"Unknown transform format: {transform}")

            # Check conditions if specified
            if "condition" in field:
                condition = field["condition"]
                if condition.get("field"):
                    condition_value = self.get_value_from_path(item, condition["field"])
                    operator = condition.get("operator", "eq")
                    compare_value = condition.get("value")

                    skip = False
                    if operator == "eq" and condition_value != compare_value:
                        skip = True
                    elif operator == "ne" and condition_value == compare_value:
                        skip = True
                    elif operator == "gt" and not (condition_value > compare_value):
                        skip = True
                    elif operator == "lt" and not (condition_value < compare_value):
                        skip = True
                    elif operator == "exists" and condition_value is None:
                        skip = True
                    elif operator == "not_exists" and condition_value is not None:
                        skip = True

                    if skip:
                        continue

            # Set value in result
            if source_value is not None or field.get("include_nulls", False):
                self.set_value_at_path(result, target_path, source_value)

        return result

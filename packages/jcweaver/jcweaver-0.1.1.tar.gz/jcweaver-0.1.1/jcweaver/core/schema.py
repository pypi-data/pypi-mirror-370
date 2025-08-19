
from typing import Dict, Any


class SchemaValidationError(Exception):
    pass


def validate_input_schema(data: dict, schema: Dict[str, Any]) -> dict:
    if not isinstance(data, dict):
        raise SchemaValidationError("Input must be a dictionary")

    validated = {}
    for key, expected_type in schema.items():
        if key not in data:
            raise SchemaValidationError(f"Missing required field: {key}")
        if not isinstance(data[key], expected_type):
            raise SchemaValidationError(
                f"Field '{key}' should be {expected_type.__name__}, got {type(data[key]).__name__}"
            )
        validated[key] = data[key]
    return validated

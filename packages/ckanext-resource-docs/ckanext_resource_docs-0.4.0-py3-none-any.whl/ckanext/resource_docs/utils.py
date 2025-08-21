from typing import Any

import jsonschema


def validate_json_with_schema(data: list[Any] | dict[str, Any], schema: dict[str, Any]) -> str | None:
    """Validate JSON data against a given schema.

    Args:
        data: The JSON data to validate.
        schema: The JSON schema to validate against.

    Returns:
        bool: True if the data is valid, False otherwise.
    """
    validator = jsonschema.Draft202012Validator(schema)

    try:
        return validator.validate(data)
    except jsonschema.ValidationError as e:
        return e.message

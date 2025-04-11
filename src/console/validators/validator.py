from typing import Any, TypeVar

import jsonschema

T = TypeVar('T')


def validate[T](config: Any, schema: Any) -> T:
    """
    Validates the given configuration against the schema.

    :param config: The configuration to validate.
    :return: The validated configuration.
    :raises ValueError: If the configuration is invalid.
    """
    try:
        jsonschema.validate(instance=config, schema=schema)
    except jsonschema.ValidationError as e:
        raise ValueError(f"Invalid config: {e.message}")

    return config  # Return as-is, assuming it's already in the correct format

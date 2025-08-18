from datetime import date, datetime, time
from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union

from pydantic import BaseModel, Field, create_model


def json_schema_to_model(
    json_schema: Dict[str, Any],
    definitions: Optional[Dict[str, Any]] = None,
) -> Type[BaseModel]:
    """
    Converts a JSON schema to a Pydantic BaseModel class.

    Args:
        json_schema: The JSON schema to convert.
        definitions: A dictionary of defined schemas, often found in the "$defs" property.

    Returns:
        A Pydantic BaseModel class.

    """

    model_name = json_schema.get("title")
    field_definitions = {
        name: json_schema_to_pydantic_field(
            name,
            prop,
            json_schema.get("required", []),
            definitions,
        )
        for name, prop in json_schema.get("properties", {}).items()
    }
    return create_model(model_name, **field_definitions)


def json_schema_to_pydantic_field(
    name: str,
    json_schema: Dict[str, Any],
    required: List[str],
    definitions: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Converts a JSON schema property to a Pydantic field definition.

    Args:
        name: The field name.
        json_schema: The JSON schema property.
        required: A list of required field names.
        definitions: A dictionary of defined schemas, often found in the "$defs" property.

    Returns:
        A Pydantic field definition.

    """

    type_ = json_schema_to_pydantic_type(json_schema, definitions)
    description = json_schema.get("description")
    examples = json_schema.get("examples")
    min_length = json_schema.get("minLength")
    max_length = json_schema.get("maxLength")
    minimum = json_schema.get("minimum")
    maximum = json_schema.get("maximum")
    exclusive_minimum = json_schema.get("exclusiveMinimum")
    exclusive_maximum = json_schema.get("exclusiveMaximum")
    pattern = json_schema.get("pattern")

    # Handle optional fields (including 'anyOf' with 'null')
    if name not in required or (
        "anyOf" in json_schema
        and any(item.get("type") == "null" for item in json_schema.get("anyOf", []))
    ):
        type_ = Optional[type_]

    return (
        type_,
        Field(
            description=description,
            examples=examples,
            min_length=min_length,
            max_length=max_length,
            ge=minimum,
            le=maximum,
            gt=exclusive_minimum,
            lt=exclusive_maximum,
            pattern=pattern,
            default=... if name in required else None,
        ),
    )


def json_schema_to_pydantic_type(
    json_schema: Dict[str, Any],
    definitions: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Converts a JSON schema type to a Pydantic type.

    Args:
        json_schema: The JSON schema to convert.
        definitions: A dictionary of defined schemas, often found in the "$defs" property.

    Returns:
        A Pydantic type.

    """

    type_ = json_schema.get("type")

    if type_ == "string":
        format_ = json_schema.get("format")
        if format_ == "date":
            return date
        if format_ == "time":
            return time
        if format_ == "date-time":
            return datetime
        if "enum" in json_schema:
            return Enum(
                json_schema.get("title", "EnumType"),
                {member: member for member in json_schema["enum"]},
            )
        return str
    if type_ == "integer":
        return int
    if type_ == "number":
        return float
    if type_ == "boolean":
        return bool
    if type_ == "array":
        items_schema = json_schema.get("items")
        if items_schema:
            item_type = json_schema_to_pydantic_type(items_schema, definitions)
            return List[item_type]
        return List
    if type_ == "object":
        # Handle nested models.
        properties = json_schema.get("properties")
        if properties:
            return json_schema_to_model(json_schema, definitions)
        return Dict
    if type_ == "null":
        return None
    if "$ref" in json_schema:
        # Handle references to nested schemas
        ref_path = json_schema["$ref"].split("/")
        ref_name = ref_path[-1]
        if definitions:
            ref_schema = definitions.get(ref_name)
            if ref_schema:
                return json_schema_to_pydantic_type(ref_schema, definitions)
        raise ValueError(f"Could not resolve reference: {json_schema['$ref']}")
    if "anyOf" in json_schema:
        # Handle 'anyOf' with 'null' for optional fields
        types = [
            json_schema_to_pydantic_type(item, definitions)
            for item in json_schema["anyOf"]
        ]
        if any(t is None for t in types):  # If 'null' is present in anyOf
            types = [t for t in types if t is not None]  # Remove 'null' from the list
            if len(types) == 1:
                return Optional[types[0]]  # If only one non-null type, use Optional
            return Union[types]  # If multiple non-null types, use Union
        # If 'null' is not present, return the union of all types
        return Union[types]
    raise ValueError(f"Unsupported JSON schema type: {type_}")

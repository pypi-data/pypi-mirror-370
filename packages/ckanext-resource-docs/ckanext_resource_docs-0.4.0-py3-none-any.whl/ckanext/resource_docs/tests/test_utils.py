from typing import Any

from ckanext.resource_docs.utils import validate_json_with_schema


class TestValidateJsonWithSchema:
    """Tests for validate_json_with_schema function."""

    def test_valid_data_with_simple_schema(self):
        assert (
            validate_json_with_schema(
                {"name": "John Doe", "age": 30},
                {
                    "type": "object",
                    "properties": {"name": {"type": "string"}, "age": {"type": "number"}},
                    "required": ["name"],
                },
            )
            is None
        )

    def test_invalid_data_with_simple_schema(self):
        assert (
            validate_json_with_schema(
                {"age": 30},
                {
                    "type": "object",
                    "properties": {"name": {"type": "string"}, "age": {"type": "number"}},
                    "required": ["name"],
                },
            )
            == "'name' is a required property"
        )

    def test_valid_array_data(self):
        assert (
            validate_json_with_schema(
                [{"id": 1, "title": "First item"}, {"id": 2, "title": "Second item"}],
                {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"id": {"type": "integer"}, "title": {"type": "string"}},
                        "required": ["id", "title"],
                    },
                },
            )
            is None
        )

    def test_invalid_array_data(self):
        assert (
            validate_json_with_schema(
                [
                    {"id": 1, "title": "First item"},
                    {"id": 2},  # Missing title
                ],
                {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"id": {"type": "integer"}, "title": {"type": "string"}},
                        "required": ["id", "title"],
                    },
                },
            )
            == "'title' is a required property"
        )

    def test_type_mismatch(self):
        assert (
            validate_json_with_schema(
                {
                    "name": "John Doe",
                    "age": "thirty",  # Should be integer
                    "email": "john@example.com",
                },
                {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "integer"},
                        "email": {"type": "string", "format": "email"},
                    },
                },
            )
            == "'thirty' is not of type 'integer'"
        )

    def test_nested_object_validation(self):
        assert (
            validate_json_with_schema(
                {"user": {"name": "Jane Doe", "profile": {"bio": "Software developer", "age": 25}}},
                {
                    "type": "object",
                    "properties": {
                        "user": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "profile": {
                                    "type": "object",
                                    "properties": {"bio": {"type": "string"}, "age": {"type": "integer"}},
                                    "required": ["bio"],
                                },
                            },
                            "required": ["name", "profile"],
                        }
                    },
                    "required": ["user"],
                },
            )
            is None
        )

    def test_invalid_nested_object(self):
        assert (
            validate_json_with_schema(
                {
                    "user": {
                        "name": "Jane Doe",
                        "profile": {
                            "age": 25  # Missing required 'bio' field
                        },
                    }
                },
                {
                    "type": "object",
                    "properties": {
                        "user": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "profile": {
                                    "type": "object",
                                    "properties": {"bio": {"type": "string"}, "age": {"type": "integer"}},
                                    "required": ["bio"],
                                },
                            },
                            "required": ["name", "profile"],
                        }
                    },
                    "required": ["user"],
                },
            )
            == "'bio' is a required property"
        )

    def test_additional_properties_allowed(self):
        assert (
            validate_json_with_schema(
                {"name": "John Doe", "extra_field": "This is allowed"},
                {"type": "object", "properties": {"name": {"type": "string"}}, "additionalProperties": True},
            )
            is None
        )

    def test_additional_properties_not_allowed(self):
        assert (
            validate_json_with_schema(
                {"name": "John Doe", "extra_field": "This should not be allowed"},
                {"type": "object", "properties": {"name": {"type": "string"}}, "additionalProperties": False},
            )
            == "Additional properties are not allowed ('extra_field' was unexpected)"
        )

    def test_numeric_constraints(self):
        assert (
            validate_json_with_schema(
                {"age": 25, "score": 85.5},
                {
                    "type": "object",
                    "properties": {
                        "age": {"type": "integer", "minimum": 0, "maximum": 150},
                        "score": {"type": "number", "minimum": 0.0, "maximum": 100.0},
                    },
                },
            )
            is None
        )

    def test_invalid_numeric_constraints(self):
        assert (
            validate_json_with_schema(
                {"age": 200},
                {"type": "object", "properties": {"age": {"type": "integer", "minimum": 0, "maximum": 150}}},
            )
            == "200 is greater than the maximum of 150"
        )

    def test_string_length_constraints(self):
        assert (
            validate_json_with_schema(
                {"username": "john_doe"},
                {"type": "object", "properties": {"username": {"type": "string", "minLength": 3, "maxLength": 20}}},
            )
            is None
        )

    def test_invalid_string_length(self):
        assert (
            validate_json_with_schema(
                {"username": "ab"},
                {"type": "object", "properties": {"username": {"type": "string", "minLength": 3, "maxLength": 20}}},
            )
            == "'ab' is too short"
        )

    def test_enum_validation(self):
        assert (
            validate_json_with_schema(
                {"status": "active"},
                {
                    "type": "object",
                    "properties": {"status": {"type": "string", "enum": ["active", "inactive", "pending"]}},
                },
            )
            is None
        )

    def test_invalid_enum_value(self):
        assert (
            validate_json_with_schema(
                {"status": "unknown"},
                {
                    "type": "object",
                    "properties": {"status": {"type": "string", "enum": ["active", "inactive", "pending"]}},
                },
            )
            == "'unknown' is not one of ['active', 'inactive', 'pending']"
        )

    def test_empty_data_with_empty_schema(self):
        assert validate_json_with_schema({}, {}) is None

    def test_null_values(self):
        assert (
            validate_json_with_schema(
                {"name": None, "age": 30},
                {"type": "object", "properties": {"name": {"type": ["string", "null"]}, "age": {"type": "integer"}}},
            )
            is None
        )

    def test_complex_real_world_schema(self):
        schema: dict[str, Any] = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {
                "dataset": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "minLength": 1},
                        "description": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}, "uniqueItems": True},
                        "resources": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "format": {"type": "string", "enum": ["CSV", "JSON", "XML"]},
                                    "size": {"type": "integer", "minimum": 0},
                                },
                                "required": ["name", "format"],
                            },
                        },
                    },
                    "required": ["title", "resources"],
                }
            },
            "required": ["dataset"],
        }
        data: dict[str, Any] = {
            "dataset": {
                "title": "Sample Dataset",
                "description": "A sample dataset for testing",
                "tags": ["test", "sample", "data"],
                "resources": [
                    {"name": "data.csv", "format": "CSV", "size": 1024},
                    {"name": "metadata.json", "format": "JSON", "size": 256},
                ],
            }
        }
        assert validate_json_with_schema(data, schema) is None

    def test_schema_draft_07(self):
        assert (
            validate_json_with_schema(
                {"name": "Alice", "age": 30},
                {
                    "$schema": "https://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "integer", "minimum": 0},
                    },
                    "required": ["name"],
                },
            )
            is None
        )

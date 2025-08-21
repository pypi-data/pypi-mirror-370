from ckan import types
from ckan.logic.schema import validator_args


@validator_args
def resource_docs_override(
    not_empty: types.Validator,
    unicode_safe: types.Validator,
    resource_id_exists: types.Validator,
    convert_to_json_if_string: types.Validator,
    ignore_missing: types.Validator,
) -> types.Schema:
    """Schema for creating or updating resource documentation."""
    return {
        "resource_id": [not_empty, unicode_safe, resource_id_exists],
        "docs": [not_empty, unicode_safe, convert_to_json_if_string],
        "validation_schema": [ignore_missing, convert_to_json_if_string],
    }


@validator_args
def resource_docs_show(
    not_empty: types.Validator, unicode_safe: types.Validator, resource_id_exists: types.Validator
) -> types.Schema:
    """Schema for showing resource documentation."""
    return {"resource_id": [not_empty, unicode_safe, resource_id_exists]}


@validator_args
def resource_docs_delete(
    not_empty: types.Validator, unicode_safe: types.Validator, resource_id_exists: types.Validator
) -> types.Schema:
    """Schema for deleting resource documentation."""
    return {"resource_id": [not_empty, unicode_safe, resource_id_exists]}

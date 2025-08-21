from ckan import types
from ckan.logic import validate
from ckan.plugins import toolkit as tk

from ckanext.resource_docs.config import ExtConfig
from ckanext.resource_docs.logic import schema
from ckanext.resource_docs.model import ResourceDocs
from ckanext.resource_docs.utils import validate_json_with_schema


@validate(schema.resource_docs_override)
def resource_docs_override(context: types.Context, data_dict: types.DataDict) -> types.DataDict:
    """Create or update resource documentation.

    Args:
        context: CKAN context
        data_dict: Dictionary containing:
            - resource_id: ID of the resource
            - docs: Documentation content
            - validation_schema: Optional validation schema for the docs

    Returns:
        Dictionary representation of the resource documentation
    """
    tk.check_access("resource_docs_manage", context, data_dict)

    existing_docs = ResourceDocs.get_by_resource_id(data_dict["resource_id"])

    if "validation_schema" in data_dict:
        validation_schema = data_dict["validation_schema"]
    else:
        validation_schema = existing_docs.validation_schema if existing_docs and existing_docs.validation_schema else {}  # type: ignore

    error = validate_json_with_schema(data_dict["docs"], validation_schema)

    if error:
        raise tk.ValidationError(error)

    if existing_docs:
        resource_docs = existing_docs.update(data_dict["docs"], validation_schema)
    else:
        resource_docs = ResourceDocs.create(data_dict["resource_id"], data_dict["docs"], validation_schema)

    return resource_docs.dictize(context)


@validate(schema.resource_docs_delete)
def resource_docs_delete(context: types.Context, data_dict: types.DataDict) -> types.DataDict:
    """Delete resource documentation.

    Args:
        context: CKAN context
        data_dict: Dictionary containing:
            - resource_id: ID of the resource

    Returns:
        Dictionary with success message
    """
    tk.check_access("resource_docs_manage", context, data_dict)

    resource_id = data_dict["resource_id"]

    if resource_docs := ResourceDocs.get_by_resource_id(resource_id):
        resource_docs.delete()
        return {"success": True, "message": tk._("Resource documentation deleted successfully")}

    raise tk.ObjectNotFound(f"Resource documentation for resource {resource_id} not found")  # noqa: TRY003


@validate(schema.resource_docs_show)
@tk.side_effect_free
def resource_docs_show(context: types.Context, data_dict: types.DataDict) -> types.DataDict:
    """Show resource documentation.

    Args:
        context: CKAN context
        data_dict: Dictionary containing:
            - resource_id: ID of the resource

    Returns:
        Dictionary representation of the resource documentation
    """
    tk.check_access("resource_docs_show", context, data_dict)

    resource_id = data_dict["resource_id"]
    resource_docs = ResourceDocs.get_by_resource_id(resource_id)

    if not resource_docs:
        raise tk.ObjectNotFound(f"Resource documentation for resource {resource_id} not found")  # noqa: TRY003

    return resource_docs.dictize(context)


@tk.side_effect_free
@tk.chained_action
def resource_show(next: types.Action, context: types.Context, data_dict: types.DataDict) -> types.DataDict:
    """Append resource documentation to resource dict if configured."""
    result = next(context, data_dict)

    if not ExtConfig.append_docs_to_api() or context.get("for_update"):
        return result

    if resource_docs := ResourceDocs.get_by_resource_id(result.get("id", "")):
        result[ExtConfig.get_api_field_name()] = resource_docs.docs

    return result


@tk.side_effect_free
@tk.chained_action
def package_show(next: types.Action, context: types.Context, data_dict: types.DataDict) -> types.DataDict:
    """Append resource documentation to package dict if configured."""
    result = next(context, data_dict)

    if not ExtConfig.append_docs_to_api() or context.get("for_update"):
        return result

    resource_ids = [resource.get("id", "") for resource in result.get("resources", [])]
    # get all the resources docs at once to avoid multiple DB calls
    resources_docs = ResourceDocs.get_by_resources_ids(resource_ids)

    for resource in result.get("resources", []):
        if resource_docs := resources_docs.get(resource.get("id", "")):
            resource[ExtConfig.get_api_field_name()] = resource_docs.docs

    return result

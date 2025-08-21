import ckan.plugins.toolkit as tk
from ckan import model, types


def resource_docs_manage(context: types.Context, data_dict: types.DataDict):
    """Check if the user has permission to manage resource documentation."""
    resource = model.Resource.get(data_dict.get("resource_id", ""))

    if not resource:
        raise tk.ObjectNotFound("Resource not found")  # noqa: TRY003

    return {"success": tk.check_access("package_update", context, {"id": resource.package_id})}


@tk.auth_allow_anonymous_access
def resource_docs_show(context: types.Context, data_dict: types.DataDict):
    """Check if the user has permission to view resource documentation."""
    resource = model.Resource.get(data_dict.get("resource_id", ""))

    if not resource:
        raise tk.ObjectNotFound("Resource not found")  # noqa: TRY003

    return {"success": tk.check_access("package_show", context, {"id": resource.package_id})}

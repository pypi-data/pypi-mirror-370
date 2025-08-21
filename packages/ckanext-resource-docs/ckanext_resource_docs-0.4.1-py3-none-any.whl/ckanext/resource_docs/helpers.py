import secrets
import string
from typing import Any

import ckan.plugins.toolkit as tk

from ckanext.resource_docs.config import ExtConfig

JSONType = dict[str, Any] | list[Any] | str | int | float | bool


def show_resource_docs_view() -> bool:
    """Check if the view should be shown."""
    return ExtConfig.show_resource_docs_view()


def fetch_resource_docs_data(resource: dict[str, Any]) -> JSONType:
    """Fetch resource docs data."""
    field_name = ExtConfig.get_api_field_name()
    data = resource.get(field_name)

    if data is not None:
        return data

    try:
        data = tk.get_action("resource_docs_show")({}, {"resource_id": resource["id"]})
    except tk.ObjectNotFound:
        return {}

    return data


def detect_view_type(data: JSONType) -> str:
    """Detect the view type based on the data structure."""
    if not data:
        return "scalar"

    if isinstance(data, dict):
        return "kv-table"

    if isinstance(data, list):
        if all(isinstance(item, dict) for item in data):
            return "list-table"

        return "sequence"

    return "scalar"


def generate_unique_element_id(length: int = 12) -> str:
    """Generate a unique ID for an HTML element."""
    letters = string.ascii_lowercase
    alnum = letters + string.digits + "-_"
    unique_str = "".join(secrets.choice(alnum) for _ in range(length - 1))
    return f"id_{secrets.choice(letters)}{unique_str}"


def get_column_names(data: list[dict[str, Any]]) -> list[str]:
    """Get unique column names from a list of dictionaries."""
    if not data:
        return []

    column_names = set()

    for item in data:
        column_names.update(item.keys())

    return sorted(column_names)

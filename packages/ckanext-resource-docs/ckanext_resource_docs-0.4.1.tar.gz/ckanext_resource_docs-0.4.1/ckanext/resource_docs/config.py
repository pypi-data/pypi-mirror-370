import ckan.plugins.toolkit as tk

CONF_APPEND_TO_API = "ckanext.resource_docs.append_docs_to_resource_api"
CONF_API_FIELD_NAME = "ckanext.resource_docs.api_field_name"
CONF_SHOW_VIEW = "ckanext.resource_docs.show_view"


class ExtConfig:
    """Configuration class for resource documentation extension."""

    @staticmethod
    def append_docs_to_api() -> bool:
        """Check if resource documentation should be appended to the resource API."""
        return tk.config[CONF_APPEND_TO_API]

    @staticmethod
    def get_api_field_name() -> str:
        """Get the field name for resource documentation in the API."""
        return tk.config[CONF_API_FIELD_NAME]

    @staticmethod
    def show_resource_docs_view() -> bool:
        """Determine if the resource documentation view should be shown."""
        return tk.config[CONF_SHOW_VIEW]

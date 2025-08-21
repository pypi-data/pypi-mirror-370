from typing import Any, cast

from ckan import model, types
from ckan import plugins as p
from ckan.common import CKANConfig
from ckan.plugins import toolkit as tk

from ckanext.resource_docs.config import ExtConfig
from ckanext.resource_docs.model import ResourceDocs


@tk.blanket.actions
@tk.blanket.auth_functions
@tk.blanket.blueprints
@tk.blanket.config_declarations
@tk.blanket.helpers
class ResourceDocsPlugin(p.SingletonPlugin):
    """Extension entry point."""

    p.implements(p.IConfigurer)
    p.implements(p.IResourceController, inherit=True)
    p.implements(p.IPackageController, inherit=True)

    # IConfigurer

    def update_config(self, config_: CKANConfig):
        """Update the CKAN configuration."""
        tk.add_template_directory(config_, "templates")
        tk.add_resource("assets", "resource_docs")

    # IResourceController

    def before_resource_create(self, context: types.Context, resource: dict[str, Any]) -> None:
        """Pop out the resource_docs field."""
        resource.pop(ExtConfig.get_api_field_name(), None)

    def before_resource_update(self, context: types.Context, current: dict[str, Any], resource: dict[str, Any]) -> None:
        """Pop out the resource_docs field."""
        resource.pop(ExtConfig.get_api_field_name(), None)

    def before_resource_delete(self, context: types.Context, resource: dict[str, Any], _: list[dict[str, Any]]) -> None:
        """Store resource ID to delete resource documentation later."""
        context["_resource_to_delete"] = resource["id"]  # type: ignore

    def after_resource_delete(self, context: types.Context, resources: list[dict[str, Any]]) -> None:
        """Delete resource documentation when a resource is deleted."""
        if resource_docs := ResourceDocs.get_by_resource_id(context.get("_resource_to_delete", "")):
            resource_docs.delete()

    # IPackageController

    def delete(self, package: "model.Package") -> None:
        """Drop resources documentation when a package is deleted."""
        for resource in package.resources:
            resource_docs = cast(ResourceDocs, getattr(resource, "resource_docs", None))

            if not resource_docs:
                continue

            resource_docs.delete()

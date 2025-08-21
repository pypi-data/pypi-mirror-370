from flask import Blueprint
from flask.views import MethodView

import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan import types

from ckanext.resource_docs.interfaces import IResourceDocs

bp = Blueprint("resource_docs", __name__)


class ResourceDocsEditView(MethodView):
    """View for editing resource documentation."""

    def get(self, package_id: str, resource_id: str) -> str:
        """Render the edit page for resource documentation."""
        try:
            tk.check_access(
                "resource_docs_manage",
                context=types.Context(user=tk.current_user.name),
                data_dict={"resource_id": resource_id},
            )

            pkg_dict = tk.get_action("package_show")({}, {"id": package_id})
            resource = tk.get_action("resource_show")({}, {"id": resource_id})

        except (tk.ObjectNotFound, tk.NotAuthorized):
            return tk.abort(404, tk._("Resource not found"))

        try:
            docs = tk.get_action("resource_docs_show")({}, {"resource_id": resource_id})
        except tk.ObjectNotFound:
            docs = None

            for plugin in p.PluginImplementations(IResourceDocs):
                docs = plugin.prepopulate_resource_docs(resource)

                if docs:
                    break

        return tk.render(
            "resource_docs/edit.html", {"docs_prepopulate": docs or "{}", "pkg_dict": pkg_dict, "resource": resource}
        )


bp.add_url_rule("/dataset/<package_id>/resource_docs/<resource_id>", view_func=ResourceDocsEditView.as_view("edit"))

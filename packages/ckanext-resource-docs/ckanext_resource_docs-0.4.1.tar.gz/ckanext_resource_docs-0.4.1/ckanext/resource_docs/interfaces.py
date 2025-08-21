from __future__ import annotations

from typing import Any

from ckan.plugins.interfaces import Interface


class IResourceDocs(Interface):
    """Interface for resource documentation."""

    def prepopulate_resource_docs(self, resource: dict[str, Any]) -> str:
        """Generate default content for a resource's documentation.

        This method is called when a user opens a new, empty resource documentation.
        Implementations can use the provided resource metadata to generate
        meaningful starter content, such as a DataStore Data Dictionary or
        example records.

        Args:
            resource: The resource data dictionary with its metadata.

        Returns:
            str: A JSON-formatted string containing the prepopulated documentation.
                 Returning an empty string indicates no default content.
        """
        return ""

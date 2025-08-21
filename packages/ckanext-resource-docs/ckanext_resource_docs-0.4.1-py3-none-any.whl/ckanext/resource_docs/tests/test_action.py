from collections.abc import Callable
from typing import Any

import pytest

import ckan.plugins.toolkit as tk
from ckan import types
from ckan.tests.helpers import call_action  # pyright: ignore[reportUnknownVariableType]

import ckanext.resource_docs.config as config
from ckanext.resource_docs.model import ResourceDocs


@pytest.mark.usefixtures("with_plugins", "reset_db_once")
class TestResourceDocsOverride:
    """Test resource_docs_override action."""

    def test_create_new_resource_docs(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test creating new resource documentation."""
        docs = {"documentation": "xxx"}

        result = call_action(
            "resource_docs_override", types.Context(user=sysadmin["name"]), resource_id=resource["id"], docs=docs
        )

        assert result["resource_id"] == resource["id"]
        assert result["docs"] == docs
        assert "id" in result
        assert "modified_at" in result

    def test_update_existing_resource_docs(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test updating existing resource documentation."""
        docs = {"documentation": "xxx"}
        updated_docs = {"documentation": "This is an updated test documentation"}

        call_action(
            "resource_docs_override",
            types.Context(user=sysadmin["name"]),
            resource_id=resource["id"],
            docs=docs,
        )

        # Update the documentation
        result = call_action(
            "resource_docs_override",
            types.Context(user=sysadmin["name"]),
            resource_id=resource["id"],
            docs=updated_docs,
        )

        assert result["resource_id"] == resource["id"]
        assert result["docs"] == updated_docs

        # Verify only one record exists and it's updated
        docs = ResourceDocs.get_by_resource_id(resource["id"])
        assert docs is not None
        assert docs.docs == updated_docs

    def test_resource_does_not_exist(self, sysadmin: dict[str, Any]):
        """Test creating docs for non-existent resource."""
        with pytest.raises(tk.ValidationError, match="Not found: Resource"):
            call_action("resource_docs_override", types.Context(user=sysadmin["name"]), resource_id="xxx")

    def test_missing_resource_id(self, sysadmin: dict[str, Any]):
        """Test action with missing resource_id parameter."""
        with pytest.raises(tk.ValidationError):
            call_action("resource_docs_override", types.Context(user=sysadmin["name"]))

    def test_missing_docs(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test action with missing docs parameter."""
        with pytest.raises(tk.ValidationError):
            call_action("resource_docs_override", types.Context(user=sysadmin["name"]), resource_id=resource["id"])

    def test_empty_docs(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test action with empty docs."""
        with pytest.raises(tk.ValidationError):
            call_action(
                "resource_docs_override", types.Context(user=sysadmin["name"]), resource_id=resource["id"], docs=""
            )

    def test_validation_schema_can_be_empty(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test action with empty validation schema."""
        call_action(
            "resource_docs_override",
            types.Context(user=sysadmin["name"]),
            resource_id=resource["id"],
            docs={"documentation": "Test"},
            validation_schema={},
        )

    def test_validation_error(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test action with invalid docs that do not match validation schema."""
        validation_schema: dict[str, Any] = {
            "type": "object",
            "properties": {
                "documentation": {"type": "string"},
                "version": {"type": "number"},
            },
            "required": ["documentation", "version"],
        }

        with pytest.raises(tk.ValidationError, match="'version' is a required property"):
            call_action(
                "resource_docs_override",
                types.Context(user=sysadmin["name"]),
                resource_id=resource["id"],
                docs={"documentation": "Test"},
                validation_schema=validation_schema,
            )

    def test_use_existing_validation_schema(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test using existing validation schema when updating docs."""
        validation_schema: dict[str, Any] = {
            "type": "object",
            "properties": {
                "documentation": {"type": "string"},
                "version": {"type": "number"},
            },
            "required": ["documentation", "version"],
        }

        # Create initial docs with validation schema
        call_action(
            "resource_docs_override",
            types.Context(user=sysadmin["name"]),
            resource_id=resource["id"],
            docs={"documentation": "hello world", "version": 1.0},
            validation_schema=validation_schema,
        )

        # Update without providing validation schema
        updated_docs: dict[str, Any] = {"documentation": "Updated documentation", "version": 1.0}
        result = call_action(
            "resource_docs_override",
            types.Context(user=sysadmin["name"]),
            resource_id=resource["id"],
            docs=updated_docs,
        )

        assert result["docs"] == updated_docs
        assert result["validation_schema"] == validation_schema

    def test_override_to_empty_schema(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test overriding existing docs with empty schema."""
        validation_schema: dict[str, Any] = {
            "type": "object",
            "properties": {
                "documentation": {"type": "string"},
                "version": {"type": "number"},
            },
            "required": ["documentation", "version"],
        }

        # Create initial docs with validation schema
        call_action(
            "resource_docs_override",
            types.Context(user=sysadmin["name"]),
            resource_id=resource["id"],
            docs={"documentation": "hello world", "version": 1.0},
            validation_schema=validation_schema,
        )

        # Update with empty validation schema
        assert call_action(
            "resource_docs_override",
            types.Context(user=sysadmin["name"]),
            resource_id=resource["id"],
            docs={"xxx": "yyy"},
            validation_schema={},
        )


@pytest.mark.usefixtures("with_plugins", "reset_db_once")
class TestResourceDocsShow:
    """Test resource_docs_show action."""

    def test_show_existing_resource_docs(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test showing existing resource documentation."""
        docs = {"documentation": "xxx"}

        created_result = call_action(
            "resource_docs_override", types.Context(user=sysadmin["name"]), resource_id=resource["id"], docs=docs
        )

        result = call_action("resource_docs_show", types.Context(user=sysadmin["name"]), resource_id=resource["id"])

        assert result["id"] == created_result["id"]
        assert result["resource_id"] == resource["id"]
        assert result["docs"] == docs
        assert result["modified_at"].replace("+00:00", "") == created_result["modified_at"].replace("+00:00", "")

    def test_show_non_existent_resource_docs(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test showing documentation for resource without docs."""
        with pytest.raises(tk.ObjectNotFound):
            call_action("resource_docs_show", types.Context(user=sysadmin["name"]), resource_id=resource["id"])

    def test_show_with_non_existent_resource(self, sysadmin: dict[str, Any]):
        """Test showing docs for non-existent resource."""
        with pytest.raises(tk.ValidationError, match="Not found: Resource"):
            call_action("resource_docs_show", types.Context(user=sysadmin["name"]), resource_id="xxx")

    def test_missing_resource_id(self, sysadmin: dict[str, Any]):
        """Test action with missing resource_id parameter."""
        with pytest.raises(tk.ValidationError):
            call_action("resource_docs_show", types.Context(user=sysadmin["name"]))


@pytest.mark.usefixtures("with_plugins", "reset_db_once")
class TestResourceDocsDelete:
    """Test resource_docs_delete action."""

    def test_delete_existing_resource_docs(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test deleting existing resource documentation."""
        docs = {"documentation": "xxx"}

        # Create documentation first
        call_action(
            "resource_docs_override", types.Context(user=sysadmin["name"]), resource_id=resource["id"], docs=docs
        )

        # Verify it exists
        assert ResourceDocs.get_by_resource_id(resource["id"]) is not None

        # Delete the documentation
        result = call_action(
            "resource_docs_delete",
            types.Context(user=sysadmin["name"]),
            resource_id=resource["id"],
        )

        assert result["success"] is True
        assert "message" in result

        assert ResourceDocs.get_by_resource_id(resource["id"]) is None

    def test_delete_non_existent_resource_docs(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test deleting documentation for resource without docs."""
        with pytest.raises(tk.ObjectNotFound):
            call_action("resource_docs_delete", types.Context(user=sysadmin["name"]), resource_id=resource["id"])

    def test_delete_with_non_existent_resource(self, sysadmin: dict[str, Any]):
        """Test deleting docs for non-existent resource."""
        with pytest.raises(tk.ValidationError, match="Not found: Resource"):
            call_action("resource_docs_delete", types.Context(user=sysadmin["name"]), resource_id="xxx")

    def test_missing_resource_id(self, sysadmin: dict[str, Any]):
        """Test action with missing resource_id parameter."""
        with pytest.raises(tk.ValidationError):
            call_action("resource_docs_delete", types.Context(user=sysadmin["name"]))


@pytest.mark.usefixtures("with_plugins", "reset_db_once")
class TestResourceDocsIntegration:
    """Integration tests for resource docs actions."""

    def test_full_lifecycle(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test complete lifecycle: create, show, update, delete."""
        docs = {"documentation": "xxx"}
        updated_docs = {"documentation": "This is an updated test documentation"}

        # 1. Create documentation
        create_result = call_action(
            "resource_docs_override", types.Context(user=sysadmin["name"]), resource_id=resource["id"], docs=docs
        )
        assert create_result["docs"] == docs

        # 2. Show documentation
        show_result = call_action(
            "resource_docs_show",
            types.Context(user=sysadmin["name"]),
            resource_id=resource["id"],
        )
        assert show_result["docs"] == docs
        assert show_result["id"] == create_result["id"]

        # 3. Update documentation
        update_result = call_action(
            "resource_docs_override",
            types.Context(user=sysadmin["name"]),
            resource_id=resource["id"],
            docs=updated_docs,
        )
        assert update_result["docs"] == updated_docs
        assert update_result["id"] == create_result["id"]  # Same ID, updated record

        # 4. Show updated documentation
        show_updated_result = call_action(
            "resource_docs_show", types.Context(user=sysadmin["name"]), resource_id=resource["id"]
        )
        assert show_updated_result["docs"] == updated_docs

        # 5. Delete documentation
        delete_result = call_action(
            "resource_docs_delete", types.Context(user=sysadmin["name"]), resource_id=resource["id"]
        )
        assert delete_result["success"] is True

        # 6. Verify documentation is gone
        with pytest.raises(tk.ObjectNotFound):
            call_action("resource_docs_show", types.Context(user=sysadmin["name"]), resource_id=resource["id"])

    def test_multiple_resources_isolation(
        self, resource_factory: Callable[..., dict[str, Any]], sysadmin: dict[str, Any]
    ):
        """Test that documentation for different resources is isolated."""
        resource = resource_factory()
        resource2 = resource_factory()

        docs1 = {"documentation": "Documentation for resource 1"}
        docs2 = {"documentation": "Documentation for resource 2"}

        # Create docs for both resources
        result1 = call_action(
            "resource_docs_override", types.Context(user=sysadmin["name"]), resource_id=resource["id"], docs=docs1
        )
        assert result1["docs"] == docs1

        result2 = call_action(
            "resource_docs_override", types.Context(user=sysadmin["name"]), resource_id=resource2["id"], docs=docs2
        )
        assert result2["docs"] == docs2

        # Delete one and verify the other still exists
        call_action("resource_docs_delete", types.Context(user=sysadmin["name"]), resource_id=resource["id"])

        # Resource 1 docs should be gone
        with pytest.raises(tk.ObjectNotFound):
            call_action("resource_docs_show", types.Context(user=sysadmin["name"]), resource_id=resource["id"])

        # Resource 2 docs should still exist
        docs2_after_delete = call_action(
            "resource_docs_show", types.Context(user=sysadmin["name"]), resource_id=resource2["id"]
        )
        assert docs2_after_delete["docs"] == docs2


@pytest.mark.usefixtures("with_plugins", "reset_db_once")
class TestResourceDelete:
    """Test resource deletion and its impact on resource documentation."""

    def test_drop_docs_on_resource_delete(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test deleting a resource with existing documentation."""
        call_action(
            "resource_docs_override",
            types.Context(user=sysadmin["name"]),
            resource_id=resource["id"],
            docs={"documentation": "xxx"},
        )

        assert ResourceDocs.get_by_resource_id(resource["id"]) is not None

        call_action("resource_delete", types.Context(user=sysadmin["name"]), id=resource["id"])

        assert ResourceDocs.get_by_resource_id(resource["id"]) is None

    def test_drop_docs_on_package_delete(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test deleting a package with resources and their documentation."""
        call_action(
            "resource_docs_override",
            types.Context(user=sysadmin["name"]),
            resource_id=resource["id"],
            docs={"documentation": "xxx"},
        )

        assert ResourceDocs.get_by_resource_id(resource["id"]) is not None

        call_action("package_delete", types.Context(user=sysadmin["name"]), id=resource["package_id"])

        assert ResourceDocs.get_by_resource_id(resource["id"]) is None


@pytest.mark.usefixtures("with_plugins", "reset_db_once")
class TestAppendResourceDocsToAPI:
    """Test appending resource documentation to API response."""

    def test_not_appended_by_default(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test that resource_docs are not appended by default."""
        call_action(
            "resource_docs_override",
            types.Context(user=sysadmin["name"]),
            resource_id=resource["id"],
            docs={"documentation": "xxx"},
        )

        result = call_action("resource_show", types.Context(user=sysadmin["name"]), id=resource["id"])

        assert "resource_docs" not in result

    @pytest.mark.ckan_config(config.CONF_APPEND_TO_API, True)
    def test_append_docs_to_resource_show(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test appending docs to resource_show action."""
        docs = {"documentation": "xxx"}

        call_action(
            "resource_docs_override", types.Context(user=sysadmin["name"]), resource_id=resource["id"], docs=docs
        )

        result = call_action("resource_show", types.Context(user=sysadmin["name"]), id=resource["id"])

        assert "resource_docs" in result
        assert result["resource_docs"] == docs

    @pytest.mark.ckan_config(config.CONF_APPEND_TO_API, True)
    def test_append_docs_to_package_show(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test appending docs to package_show action."""
        docs = {"documentation": "xxx"}

        call_action(
            "resource_docs_override", types.Context(user=sysadmin["name"]), resource_id=resource["id"], docs=docs
        )

        result = call_action("package_show", types.Context(user=sysadmin["name"]), id=resource["package_id"])

        assert "resource_docs" in result["resources"][0]
        assert result["resources"][0]["resource_docs"] == docs

    @pytest.mark.ckan_config(config.CONF_APPEND_TO_API, True)
    @pytest.mark.usefixtures("clean_index")
    def test_dont_append_docs_to_package_search(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test not appending docs to package_search action."""
        docs = {"documentation": "xxx"}

        call_action(
            "resource_docs_override", types.Context(user=sysadmin["name"]), resource_id=resource["id"], docs=docs
        )

        result = call_action("package_search", types.Context(user=sysadmin["name"]), q="")

        package = result["results"][0]

        assert "resource_docs" not in package["resources"][0]

    @pytest.mark.ckan_config(config.CONF_APPEND_TO_API, True)
    @pytest.mark.ckan_config(config.CONF_API_FIELD_NAME, "custom_docs")
    def test_append_with_custom_field_name(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test appending docs with custom field name."""
        docs = {"documentation": "xxx"}

        call_action(
            "resource_docs_override", types.Context(user=sysadmin["name"]), resource_id=resource["id"], docs=docs
        )

        result = call_action(
            "resource_show",
            types.Context(user=sysadmin["name"]),
            id=resource["id"],
            append_resource_docs_field="custom_docs",
        )

        assert "custom_docs" in result
        assert result["custom_docs"] == docs


@pytest.mark.usefixtures("with_plugins", "reset_db_once")
class TestResourceCreate:
    """Test resource creation and its impact on resource documentation."""

    @pytest.mark.ckan_config(config.CONF_APPEND_TO_API, True)
    def test_resource_create_when_another_resource_with_appended_rdocs_exists(
        self, sysadmin: dict[str, Any], resource_factory: Callable[..., dict[str, Any]]
    ):
        """Test creating a resource with documentation."""
        resource = resource_factory()

        call_action(
            "resource_docs_override",
            types.Context(user=sysadmin["name"]),
            resource_id=resource["id"],
            docs={"test": "xxx"},
        )

        assert resource_factory()

        assert call_action("package_update", id=resource["package_id"], notes="xxx")

    def test_resource_create_with_resource_docs_field(self, resource_factory: Callable[..., dict[str, Any]]):
        """Test the resource_docs field won't be added to the resource during creation."""
        field_name = config.ExtConfig.get_api_field_name()
        resource = resource_factory(**{field_name: {"test": "xxx"}})

        assert field_name not in resource


@pytest.mark.usefixtures("with_plugins", "reset_db_once")
class TestResourceUpdate:
    """Test resource update and its impact on resource documentation."""

    def test_resource_update_with_resource_docs_field(self, sysadmin: dict[str, Any], resource: dict[str, Any]):
        """Test the resource_docs field won't be added to the resource during update."""
        field_name = config.ExtConfig.get_api_field_name()

        result = call_action(
            "resource_patch", types.Context(user=sysadmin["name"]), id=resource["id"], **{field_name: {"test": "xxx"}}
        )

        assert field_name not in result

from collections.abc import Callable
from typing import Any

import pytest

import ckan.plugins.toolkit as tk
from ckan import types
from ckan.tests.helpers import call_auth  # pyright: ignore[reportUnknownVariableType]


@pytest.mark.usefixtures("with_plugins", "reset_db_once")
class TestResourceDocsManageAuth:
    """Tests for resource_docs_manage auth function."""

    def test_anon_user_cannot_manage_resource_docs(self, resource: dict[str, Any]):
        """Anonymous users cannot manage resource documentation."""
        with pytest.raises(tk.NotAuthorized):
            call_auth("resource_docs_manage", context=types.Context(user=""), resource_id=resource["id"])

    def test_regular_user_cannot_manage_others_resource_docs(self, resource: dict[str, Any], user: dict[str, Any]):
        """Regular users cannot manage resource docs they don't own."""
        with pytest.raises(tk.NotAuthorized):
            call_auth("resource_docs_manage", context=types.Context(user=user["name"]), resource_id=resource["id"])

    def test_nonexistent_resource(self, user: dict[str, Any]):
        """Managing docs for non-existent resource should fail."""
        with pytest.raises(tk.ObjectNotFound):
            call_auth("resource_docs_manage", context=types.Context(user=user["name"]), id="xxx")

    @pytest.mark.parametrize(
        ("org_role", "expected_success"),
        [("member", False), ("editor", True), ("admin", True)],
    )
    def test_organization_role_permissions(
        self,
        user: dict[str, Any],
        organization_factory: Callable[..., dict[str, Any]],
        dataset_factory: Callable[..., dict[str, Any]],
        org_role: str,
        expected_success: bool,
    ):
        """Test different organization roles and their permissions."""
        organization = organization_factory(users=[{"name": user["name"], "capacity": org_role}])
        dataset = dataset_factory(owner_org=organization["id"], resources=[{"name": "test_resource"}])
        resource = dataset["resources"][0]

        if expected_success:
            assert call_auth(
                "resource_docs_manage", context=types.Context(user=user["name"]), resource_id=resource["id"]
            )
        else:
            with pytest.raises(tk.NotAuthorized):
                call_auth("resource_docs_manage", context=types.Context(user=user["name"]), resource_id=resource["id"])

    def test_sysadmin_can_manage_any_resource_docs(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Sysadmins can manage any resource documentation."""
        assert call_auth(
            "resource_docs_manage", context=types.Context(user=sysadmin["name"]), resource_id=resource["id"]
        )


@pytest.mark.usefixtures("with_plugins", "reset_db_once")
class TestResourceDocsShowAuth:
    """Tests for resource_docs_show auth function."""

    def test_anon_user_can_view_public_resource_docs(self, resource: dict[str, Any]):
        """Anonymous users can view docs for public resources."""
        assert call_auth("resource_docs_show", context=types.Context(user=""), resource_id=resource["id"])

    def test_regular_user_can_view_public_resource_docs(self, resource: dict[str, Any], user: dict[str, Any]):
        """Regular users can view docs for public resources."""
        assert call_auth("resource_docs_show", context=types.Context(user=user["name"]), resource_id=resource["id"])

    def test_anon_user_cannot_view_private_resource_docs(self, dataset_factory: Callable[..., dict[str, Any]]):
        """Anonymous users cannot view docs for private resources."""
        dataset = dataset_factory(private=True, resources=[{"name": "test_resource"}])
        resource = dataset["resources"][0]

        with pytest.raises(tk.NotAuthorized):
            call_auth("resource_docs_show", context=types.Context(user=""), resource_id=resource["id"])

    def test_unauthorized_user_cannot_view_private_resource_docs(
        self, dataset_factory: Callable[..., dict[str, Any]], user: dict[str, Any]
    ):
        """Unauthorized users cannot view docs for private resources."""
        # Create private dataset not owned by user
        dataset = dataset_factory(private=True, resources=[{"name": "test_resource"}])
        resource = dataset["resources"][0]

        with pytest.raises(tk.NotAuthorized):
            call_auth("resource_docs_show", context=types.Context(user=user["name"]), resource_id=resource["id"])

    @pytest.mark.parametrize(
        ("org_role", "expected_success"),
        [("member", False), ("editor", True), ("admin", True)],
    )
    def test_organization_role_permissions(
        self,
        user: dict[str, Any],
        organization_factory: Callable[..., dict[str, Any]],
        dataset_factory: Callable[..., dict[str, Any]],
        org_role: str,
        expected_success: bool,
    ):
        """Organization members can view docs for private resources in their org."""
        # Create organization
        organization: dict[str, Any] = organization_factory(users=[{"name": user["name"], "capacity": org_role}])

        # Create private dataset in the organization
        dataset = dataset_factory(owner_org=organization["id"], private=True, resources=[{"name": "test_resource"}])
        resource = dataset["resources"][0]

        assert call_auth("resource_docs_show", context=types.Context(user=user["name"]), resource_id=resource["id"])

    def test_sysadmin_can_view_any_resource_docs(
        self, dataset_factory: Callable[..., dict[str, Any]], sysadmin: dict[str, Any]
    ):
        """Sysadmins can view docs for any resource, including private ones."""
        # Create private dataset
        dataset = dataset_factory(private=True, resources=[{"name": "test_resource"}])
        resource = dataset["resources"][0]

        assert call_auth("resource_docs_show", context=types.Context(user=sysadmin["name"]), resource_id=resource["id"])

    def test_nonexistent_resource(self, user: dict[str, Any]):
        """Viewing docs for non-existent resource should fail."""
        with pytest.raises(tk.ObjectNotFound):
            call_auth("resource_docs_show", context=types.Context(user=user["name"]), id="non-existent-resource-id")


@pytest.mark.usefixtures("with_plugins", "reset_db_once")
class TestResourceDocsAuthIntegration:
    """Integration tests for auth functions."""

    def test_show_more_permissive_than_manage(self, user: dict[str, Any], resource: dict[str, Any]):
        """Show permissions should be more permissive than manage permissions."""
        # User cannot manage others' resources
        with pytest.raises(tk.NotAuthorized):
            call_auth("resource_docs_manage", context=types.Context(user=user["name"]), resource_id=resource["id"])

        # But can view public resources
        assert call_auth("resource_docs_show", context=types.Context(user=user["name"]), resource_id=resource["id"])

    def test_auth_functions_handle_missing_resource_id(self, user: dict[str, Any]):
        """Auth functions should handle missing resource_id gracefully."""
        # Test with empty data_dict
        with pytest.raises(tk.ObjectNotFound):
            call_auth("resource_docs_manage", context=types.Context(user=user["name"]))

        with pytest.raises(tk.ObjectNotFound):
            call_auth("resource_docs_show", context=types.Context(user=user["name"]))

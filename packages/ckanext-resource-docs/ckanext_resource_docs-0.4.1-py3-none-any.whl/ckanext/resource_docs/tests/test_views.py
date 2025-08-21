from collections.abc import Callable
from typing import Any

import pytest

from ckan.tests import helpers
from ckan.tests.helpers import CKANTestApp


@pytest.mark.usefixtures("with_plugins", "reset_db_once")
class TestResourceDocsEditView:
    """Tests for ResourceDocsEditView."""

    def test_sysadmin_can_access_the_page(self, app: CKANTestApp, resource: dict[str, Any], sysadmin: dict[str, Any]):
        helpers.call_action("resource_docs_override", resource_id=resource["id"], docs={"documentation": "xxx"})

        response: Any = app.get(
            f"/dataset/{resource['package_id']}/resource_docs/{resource['id']}",
            headers={"Authorization": sysadmin["token"]},
        )

        assert response.status_code == 200

    def test_regular_user_cant_access_the_page(self, app: CKANTestApp, resource: dict[str, Any], user: dict[str, Any]):
        helpers.call_action("resource_docs_override", resource_id=resource["id"], docs={"documentation": "xxx"})

        response: Any = app.get(
            f"/dataset/{resource['package_id']}/resource_docs/{resource['id']}",
            headers={"Authorization": user["token"]},
        )

        assert response.status_code == 404

    def test_anon_user_cant_access_the_page(self, app: CKANTestApp, resource: dict[str, Any]):
        helpers.call_action("resource_docs_override", resource_id=resource["id"], docs={"documentation": "xxx"})

        response: Any = app.get(
            f"/dataset/{resource['package_id']}/resource_docs/{resource['id']}",
            headers={"Authorization": ""},
        )

        assert response.status_code == 404

    def test_resource_doesnt_exist(self, app: CKANTestApp, sysadmin: dict[str, Any]):
        response: Any = app.get(
            "/dataset/xxx/resource_docs/does-not-exist",
            headers={"Authorization": sysadmin["token"]},
        )

        assert response.status_code == 404

    @pytest.mark.parametrize(
        ("org_role", "expected_success"),
        [("member", False), ("editor", True), ("admin", True)],
    )
    def test_organization_member_access(
        self,
        app: CKANTestApp,
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

        response: Any = app.get(
            f"/dataset/{resource['package_id']}/resource_docs/{resource['id']}",
            headers={"Authorization": user["token"]},
        )

        assert response.status_code == 200 if expected_success else 404

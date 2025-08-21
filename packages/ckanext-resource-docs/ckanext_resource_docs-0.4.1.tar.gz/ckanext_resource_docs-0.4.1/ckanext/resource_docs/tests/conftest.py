from collections.abc import Callable
from typing import Any

import factory
import pytest
from pytest_factoryboy import register

from ckan.plugins import load_all
from ckan.tests import factories


@pytest.fixture(scope="session")
def reset_db_once(reset_db: Callable[..., Any], migrate_db_for: Callable[..., Any]) -> None:
    """Internal fixture that cleans DB only the first time it's used."""
    load_all()
    reset_db()

    migrate_db_for("resource_docs")


@register(_name="dataset")
class DatasetFactory(factories.Dataset):
    """Factory for creating datasets."""

    private = False
    owner_org = factory.LazyFunction(lambda: factories.Organization().get("id"))  # type: ignore


@register(_name="resource")
class ResourceFactory(factories.Resource):
    """Factory for creating resources."""

    package_id = factory.LazyFunction(lambda: DatasetFactory()["id"])  # type: ignore


@register(_name="sysadmin")
class SysadminFactory(factories.SysadminWithToken):
    """Factory for creating a sysadmin user with a token."""


@register(_name="user")
class UserFactory(factories.UserWithToken):
    """Factory for creating a regular user with a token."""

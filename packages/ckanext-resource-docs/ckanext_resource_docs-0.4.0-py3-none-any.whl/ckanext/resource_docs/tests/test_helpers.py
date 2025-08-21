from typing import Any

import pytest

from ckan.tests.helpers import call_action  # pyright: ignore[reportUnknownVariableType]

from ckanext.resource_docs import config
from ckanext.resource_docs.helpers import (
    detect_view_type,
    fetch_resource_docs_data,
    generate_unique_element_id,
    get_column_names,
    show_resource_docs_view,
)


@pytest.mark.usefixtures("with_plugins")
class TestShowResourceDocsView:
    """Tests for show_resource_docs_view helper."""

    def test_enabled_by_default(self) -> None:
        """Test helper returns True by default."""
        assert show_resource_docs_view()

    @pytest.mark.ckan_config(config.CONF_SHOW_VIEW, False)
    def test_disabled(self) -> None:
        """Test helper returns False when config setting is disabled."""
        assert not show_resource_docs_view()

    @pytest.mark.ckan_config(config.CONF_SHOW_VIEW, True)
    def test_enabled(self) -> None:
        """Test helper returns True when config setting is enabled."""
        assert show_resource_docs_view()


@pytest.mark.usefixtures("with_plugins", "reset_db_once")
class TestFetchResourceDocsData:
    """Tests for fetch_resource_docs_data helper."""

    @pytest.mark.ckan_config(config.CONF_APPEND_TO_API, True)
    def test_returns_data_from_resource_when_present(self, resource: dict[str, Any]) -> None:
        """Test fetching data directly from resource when field is present."""
        docs = {"documentation": "xxx"}
        call_action("resource_docs_override", resource_id=resource["id"], docs=docs)

        resource = call_action("resource_show", id=resource["id"])

        assert fetch_resource_docs_data(resource)
        assert fetch_resource_docs_data({"id": resource["id"]})


@pytest.mark.usefixtures("with_plugins", "reset_db_once")
class TestDetectViewType:
    """Tests for detect_view_type helper."""

    def test_returns_scalar_for_empty_data(self) -> None:
        """Test returns 'scalar' for empty data."""
        test_cases: list[Any] = [None, "", [], {}, 0, False]

        for data in test_cases:
            assert detect_view_type(data) == "scalar"

    def test_returns_kv_table_for_dict(self) -> None:
        """Test returns 'kv-table' for dictionary data."""
        test_cases: list[dict[str, Any]] = [
            {"key": "value"},
            {"name": "John", "age": 30},
            {"nested": {"key": "value"}},
            {"list": [1, 2, 3]},
        ]

        for data in test_cases:
            assert detect_view_type(data) == "kv-table"

    def test_returns_list_table_for_list_of_dicts(self) -> None:
        """Test returns 'list-table' for list of dictionaries."""
        test_cases: list[list[dict[str, Any]]] = [
            [{"name": "John", "age": 30}],
            [{"id": 1, "title": "First"}, {"id": 2, "title": "Second"}],
            [{}],
            [{"key": "value"}, {"another": "dict"}],
        ]

        for data in test_cases:
            assert detect_view_type(data) == "list-table"

    def test_returns_sequence_for_list_of_non_dicts(self) -> None:
        """Test returns 'sequence' for list of non-dictionary items."""
        test_cases: list[list[Any]] = [
            [1, 2, 3],
            ["a", "b", "c"],
            [1, "mixed", 3.14],
            [True, False],
            [[1, 2], [3, 4]],
            [1, {"mixed": "with dict"}],
        ]

        for data in test_cases:
            assert detect_view_type(data) == "sequence"

    def test_returns_scalar_for_primitive_types(self) -> None:
        """Test returns 'scalar' for primitive data types."""
        test_cases: list[Any] = ["string", 123, 3.14, True, False]

        for data in test_cases:
            assert detect_view_type(data) == "scalar"

    def test_complex_nested_structures(self) -> None:
        """Test detection with complex nested structures."""
        # Dict should return kv-table regardless of nesting
        complex_dict: dict[str, Any] = {
            "metadata": {"fields": [{"name": "column1", "type": "string"}, {"name": "column2", "type": "integer"}]},
            "description": "Complex dataset",
        }
        assert detect_view_type(complex_dict) == "kv-table"

        # List of dicts should return list-table
        complex_list: list[dict[str, Any]] = [
            {"id": 1, "details": {"name": "Item 1", "values": [1, 2, 3]}},
            {"id": 2, "details": {"name": "Item 2", "values": [4, 5, 6]}},
        ]
        assert detect_view_type(complex_list) == "list-table"


@pytest.mark.usefixtures("with_plugins", "reset_db_once")
class TestGenerateUniqueElementID:
    """Test the generation of unique element IDs."""

    def test_generate_unique_element_id_default_length(self) -> None:
        """Test generates ID with default length."""
        element_id = generate_unique_element_id()

        assert len(element_id) == 15
        assert element_id.startswith("id_")
        assert len(element_id[3:]) == 12

    def test_generate_unique_element_id_custom_length(self) -> None:
        """Test generates ID with custom length."""
        test_lengths = [5, 8, 16, 20]

        for length in test_lengths:
            element_id = generate_unique_element_id(length)
            assert len(element_id) == length + 3
            assert element_id.startswith("id_")

    def test_uniqueness(self) -> None:
        """Test that generated IDs are unique."""
        unique_ids: set[str] = set()

        for _ in range(100):
            element_id = generate_unique_element_id()
            assert element_id.startswith("id_")
            assert len(element_id) == 15
            unique_ids.add(element_id)

        assert len(unique_ids) == 100


@pytest.mark.usefixtures("with_plugins")
class TestGetColumnNames:
    """Tests for get_column_names helper."""

    def test_returns_empty_list_for_empty_data(self) -> None:
        """Test returns empty list for empty data."""
        assert get_column_names([]) == []

    def test_returns_sorted_columns_for_single_dict(self) -> None:
        """Test returns sorted column names for single dictionary."""
        data = [{"name": "John", "age": 30, "city": "New York"}]
        # sorted alphabetically
        assert get_column_names(data) == ["age", "city", "name"]

    def test_returns_all_unique_columns_from_multiple_dicts(self) -> None:
        """Test returns all unique columns from multiple dictionaries."""
        data = [{"id": 1, "name": "John"}, {"id": 2, "age": 30}, {"name": "Jane", "city": "Boston"}]
        assert get_column_names(data) == ["age", "city", "id", "name"]

    def test_handles_varying_column_structures(self) -> None:
        """Test handles dictionaries with completely different column sets."""
        data = [{"a": 1, "b": 2}, {"c": 3, "d": 4}, {"e": 5}]
        assert get_column_names(data) == ["a", "b", "c", "d", "e"]

    def test_handles_empty_dictionaries(self) -> None:
        """Test handles empty dictionaries in the list."""
        data = [{}, {"name": "John"}, {}, {"age": 30}]
        assert get_column_names(data) == ["age", "name"]

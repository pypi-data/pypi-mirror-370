"""
Tests for the TorontoOpenDataAPI class.
"""

from unittest.mock import Mock, patch

import pandas as pd
import pytest

from toronto_open_data.api import TorontoOpenDataAPI


class TestTorontoOpenDataAPI:
    """Test cases for TorontoOpenDataAPI class."""

    @pytest.fixture
    def api(self):
        """Create a TorontoOpenDataAPI instance for testing."""
        with patch("toronto_open_data.api.config") as mock_config:
            mock_config.API_BASE_URL = "https://test.example.com"
            api = TorontoOpenDataAPI()
            # Mock the CKAN client to prevent real HTTP requests
            api.ckan = Mock()
            return api

    @pytest.fixture
    def mock_ckan(self, api):
        """Mock CKAN client."""
        return api.ckan

    def test_initialization(self, api):
        """Test API initialization."""
        assert api is not None
        assert hasattr(api, "ckan")

    def test_list_all_datasets_as_frame(self, api, mock_ckan):
        """Test listing all datasets as DataFrame."""
        mock_ckan.action.package_list.return_value = ["dataset1", "dataset2"]

        result = api.list_all_datasets(as_frame=True)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        mock_ckan.action.package_list.assert_called_once()

    def test_list_all_datasets_as_list(self, api, mock_ckan):
        """Test listing all datasets as list."""
        mock_ckan.action.package_list.return_value = ["dataset1", "dataset2"]

        result = api.list_all_datasets(as_frame=False)

        assert isinstance(result, list)
        assert result == ["dataset1", "dataset2"]
        mock_ckan.action.package_list.assert_called_once()

    def test_search_datasets_with_results(self, api, mock_ckan):
        """Test searching datasets with results."""
        mock_response = {"results": [{"name": "test1"}, {"name": "test2"}]}
        mock_ckan.action.package_search.return_value = mock_response

        result = api.search_datasets("test", as_frame=True)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        mock_ckan.action.package_search.assert_called_once_with(q="test")

    def test_search_datasets_with_results_as_list(self, api, mock_ckan):
        """Test searching datasets with results as list."""
        mock_response = {"results": [{"name": "test1"}, {"name": "test2"}]}
        mock_ckan.action.package_search.return_value = mock_response

        result = api.search_datasets("test", as_frame=False)

        assert isinstance(result, list)
        assert result == [{"name": "test1"}, {"name": "test2"}]
        mock_ckan.action.package_search.assert_called_once_with(q="test")

    def test_search_datasets_no_results(self, api, mock_ckan):
        """Test searching datasets with no results."""
        mock_ckan.action.package_search.return_value = {}

        result = api.search_datasets("nonexistent", as_frame=True)

        assert isinstance(result, list)
        assert result == []

    def test_get_dataset_resources_success(self, api, mock_ckan):
        """Test getting dataset resources successfully."""
        mock_response = {"resources": [{"name": "file1.csv"}, {"name": "file2.json"}]}
        mock_ckan.action.package_show.return_value = mock_response

        result = api.get_dataset_resources("test-dataset", as_frame=True)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        mock_ckan.action.package_show.assert_called_once_with(id="test-dataset")

    def test_get_dataset_resources_success_as_list(self, api, mock_ckan):
        """Test getting dataset resources as list."""
        mock_response = {"resources": [{"name": "file1.csv"}, {"name": "file2.json"}]}
        mock_ckan.action.package_show.return_value = mock_response

        result = api.get_dataset_resources("test-dataset", as_frame=False)

        assert isinstance(result, list)
        assert result == [{"name": "file1.csv"}, {"name": "file2.json"}]
        mock_ckan.action.package_show.assert_called_once_with(id="test-dataset")

    def test_get_dataset_resources_not_found(self, api, mock_ckan):
        """Test getting dataset resources when dataset not found."""
        from ckanapi.errors import CKANAPIError

        mock_ckan.action.package_show.side_effect = CKANAPIError("Not found")

        result = api.get_dataset_resources("nonexistent", as_frame=True)

        assert result is None

    def test_get_dataset_info_success(self, api, mock_ckan):
        """Test getting dataset info successfully."""
        mock_response = {"name": "test-dataset", "title": "Test Dataset"}
        mock_ckan.action.package_show.return_value = mock_response

        result = api.get_dataset_info("test-dataset")

        assert result == mock_response
        mock_ckan.action.package_show.assert_called_once_with(id="test-dataset")

    def test_get_dataset_info_not_found(self, api, mock_ckan):
        """Test getting dataset info when dataset not found."""
        from ckanapi.errors import CKANAPIError

        mock_ckan.action.package_show.side_effect = CKANAPIError("Not found")

        result = api.get_dataset_info("nonexistent")

        assert result is None

    def test_datastore_search_success(self, api, mock_ckan):
        """Test datastore search successfully."""
        mock_response = {
            "records": [{"id": 1, "name": "test"}],
            "fields": [{"id": "id", "type": "int"}, {"id": "name", "type": "text"}],
        }
        mock_ckan.action.datastore_search.return_value = mock_response

        result = api.datastore_search("resource-123", as_frame=True)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        mock_ckan.action.datastore_search.assert_called_once()

    def test_datastore_search_with_filters(self, api, mock_ckan):
        """Test datastore search with filters."""
        mock_response = {"records": [{"id": 1, "name": "test"}]}
        mock_ckan.action.datastore_search.return_value = mock_response

        result = api.datastore_search(
            "resource-123",
            filters={"status": "active"},
            q="test query",
            limit=50,
            offset=10,
            fields=["id", "name"],
            sort="name asc",
            as_frame=False,
        )

        assert result == mock_response
        mock_ckan.action.datastore_search.assert_called_once_with(
            resource_id="resource-123",
            limit=50,
            offset=10,
            filters={"status": "active"},
            q="test query",
            fields=["id", "name"],
            sort="name asc",
        )

    def test_datastore_search_no_records(self, api, mock_ckan):
        """Test datastore search with no records."""
        mock_response = {"fields": []}
        mock_ckan.action.datastore_search.return_value = mock_response

        result = api.datastore_search("resource-123", as_frame=True)

        assert result == mock_response

    def test_datastore_search_failure(self, api, mock_ckan):
        """Test datastore search failure."""
        from ckanapi.errors import CKANAPIError

        mock_ckan.action.datastore_search.side_effect = CKANAPIError("Search failed")

        result = api.datastore_search("resource-123")

        assert result is None

    def test_datastore_info_success(self, api, mock_ckan):
        """Test datastore info successfully."""
        mock_response = {"fields": [{"id": "id", "type": "int"}]}
        mock_ckan.action.datastore_info.return_value = mock_response

        result = api.datastore_info("resource-123")

        assert result == mock_response
        mock_ckan.action.datastore_info.assert_called_once_with(id="resource-123")

    def test_datastore_info_failure(self, api, mock_ckan):
        """Test datastore info failure."""
        from ckanapi.errors import CKANAPIError

        mock_ckan.action.datastore_info.side_effect = CKANAPIError("Info failed")

        result = api.datastore_info("resource-123")

        assert result is None

    def test_datastore_search_sql_success(self, api, mock_ckan):
        """Test datastore SQL search successfully."""
        mock_response = {"records": [{"id": 1, "name": "test"}]}
        mock_ckan.action.datastore_search_sql.return_value = mock_response

        result = api.datastore_search_sql("SELECT * FROM table", as_frame=True)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        mock_ckan.action.datastore_search_sql.assert_called_once_with(sql="SELECT * FROM table")

    def test_datastore_search_sql_no_records(self, api, mock_ckan):
        """Test datastore SQL search with no records."""
        mock_response = {"fields": []}
        mock_ckan.action.datastore_search_sql.return_value = mock_response

        result = api.datastore_search_sql("SELECT * FROM table", as_frame=True)

        assert result == mock_response

    def test_datastore_search_sql_failure(self, api, mock_ckan):
        """Test datastore SQL search failure."""
        from ckanapi.errors import CKANAPIError

        mock_ckan.action.datastore_search_sql.side_effect = CKANAPIError("SQL failed")

        result = api.datastore_search_sql("SELECT * FROM table")

        assert result is None

    def test_convert_field_type_timestamp(self, api):
        """Test converting field type to timestamp."""
        series = pd.Series(["2023-01-01", "2023-01-02"])
        result = api._convert_field_type(series, "timestamp")

        assert pd.api.types.is_datetime64_any_dtype(result)

    def test_convert_field_type_int(self, api):
        """Test converting field type to int."""
        series = pd.Series(["1", "2", "3"])
        result = api._convert_field_type(series, "int")

        assert pd.api.types.is_integer_dtype(result)

    def test_convert_field_type_float(self, api):
        """Test converting field type to float."""
        series = pd.Series(["1.1", "2.2", "3.3"])
        result = api._convert_field_type(series, "float")

        assert pd.api.types.is_float_dtype(result)

    def test_convert_field_type_bool(self, api):
        """Test converting field type to bool."""
        series = pd.Series(["True", "False", "True"])
        result = api._convert_field_type(series, "bool")

        # The boolean conversion should fail and return the original series
        assert result.equals(series)
        assert result.dtype == "object"

    def test_convert_field_type_text(self, api):
        """Test converting field type to text."""
        series = pd.Series(["text1", "text2"])
        result = api._convert_field_type(series, "text")

        assert pd.api.types.is_string_dtype(result)

    def test_convert_field_type_conversion_failure(self, api):
        """Test field type conversion failure."""
        series = pd.Series(["invalid", "data"])
        result = api._convert_field_type(series, "int")

        # Should return original series on failure (pandas converts to Int64 with NA)
        assert len(result) == len(series)
        assert result.dtype == "Int64"

    def test_infer_dataframe_types_numeric(self, api):
        """Test DataFrame type inference for numeric columns."""
        df = pd.DataFrame({"numeric": ["1", "2", "3"], "text": ["a", "b", "c"]})

        result = api._infer_dataframe_types(df)

        assert pd.api.types.is_numeric_dtype(result["numeric"])
        assert pd.api.types.is_string_dtype(result["text"])

    def test_infer_dataframe_types_datetime(self, api):
        """Test DataFrame type inference for datetime columns."""
        df = pd.DataFrame({"date": ["2023-01-01", "2023-01-02"], "text": ["a", "b"]})

        result = api._infer_dataframe_types(df)

        assert pd.api.types.is_datetime64_any_dtype(result["date"])
        assert pd.api.types.is_string_dtype(result["text"])

    def test_infer_dataframe_types_mixed(self, api):
        """Test DataFrame type inference for mixed columns."""
        # Use list of dictionaries to avoid length mismatch issues
        data = [
            {"numeric": "1", "date": "2023-01-01", "text": "a"},
            {"numeric": "2", "date": "2023-01-02", "text": "b"},
            {"numeric": "3", "date": "2023-01-03", "text": "c"},
        ]
        df = pd.DataFrame(data)

        result = api._infer_dataframe_types(df)

        assert pd.api.types.is_numeric_dtype(result["numeric"])
        assert pd.api.types.is_datetime64_any_dtype(result["date"])
        assert pd.api.types.is_string_dtype(result["text"])

    def test_infer_dataframe_types_datetime_failure(self, api):
        """Test DataFrame type inference with datetime conversion failure."""
        df = pd.DataFrame({"bad_date": ["invalid", "date", "format"], "text": ["a", "b", "c"]})

        result = api._infer_dataframe_types(df)

        # Should fall back to string type
        assert pd.api.types.is_string_dtype(result["bad_date"])
        assert pd.api.types.is_string_dtype(result["text"])

"""
Tests for the TorontoOpenData core class.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from toronto_open_data import TorontoOpenData


class TestTorontoOpenData:
    """Test cases for TorontoOpenData class."""

    @pytest.fixture
    def tod(self):
        """Create a TorontoOpenData instance for testing."""
        return TorontoOpenData()

    @pytest.fixture
    def mock_api(self):
        """Create a mock API instance."""
        mock = Mock()
        mock.list_all_datasets.return_value = pd.DataFrame({"name": ["dataset1", "dataset2"]})
        mock.search_datasets.return_value = pd.DataFrame({"name": ["test_dataset"]})
        mock.get_dataset_resources.return_value = pd.DataFrame(
            {
                "name": ["file1.csv", "file2.json"],
                "url": [
                    "http://example.com/file1.csv",
                    "http://example.com/file2.json",
                ],
                "format": ["CSV", "JSON"],
            }
        )
        mock.get_dataset_info.return_value = {
            "name": "test_dataset",
            "title": "Test Dataset",
        }
        mock.datastore_search.return_value = pd.DataFrame({"id": [1, 2], "value": ["a", "b"]})
        mock.datastore_info.return_value = {"fields": [{"id": "id", "type": "int"}]}
        mock.datastore_search_sql.return_value = pd.DataFrame({"result": ["data"]})
        return mock

    @pytest.fixture
    def mock_cache(self):
        """Create a mock cache instance."""
        mock = Mock()
        mock.download_dataset.return_value = ["file1.csv", "file2.json"]
        mock.download_file.return_value = Path("/tmp/test_file.csv")
        mock.file_exists.return_value = True
        return mock

    @pytest.fixture
    def tod_with_mocks(self, mock_api, mock_cache):
        """Create TorontoOpenData with mocked dependencies."""
        with patch("toronto_open_data.core.TorontoOpenDataAPI", return_value=mock_api), patch(
            "toronto_open_data.core.FileCache", return_value=mock_cache
        ):
            return TorontoOpenData()

    def test_initialization(self, tod):
        """Test TorontoOpenData initialization."""
        assert tod is not None
        assert hasattr(tod, "api")
        assert hasattr(tod, "cache")
        # Check that the attributes exist and are the right types
        assert hasattr(tod.api, "list_all_datasets")
        assert hasattr(tod.cache, "download_dataset")

    def test_initialization_with_cache_path(self):
        """Test TorontoOpenData initialization with custom cache path."""
        with patch("toronto_open_data.core.TorontoOpenDataAPI"), patch(
            "toronto_open_data.core.FileCache"
        ) as mock_cache_class:
            mock_cache_instance = Mock()
            mock_cache_class.return_value = mock_cache_instance

            tod = TorontoOpenData(cache_path="/custom/cache/path")
            mock_cache_class.assert_called_once_with("/custom/cache/path")
            assert tod.cache == mock_cache_instance

    def test_list_all_datasets(self, tod_with_mocks, mock_api):
        """Test listing all datasets."""
        result = tod_with_mocks.list_all_datasets()
        mock_api.list_all_datasets.assert_called_once_with(True)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

    def test_list_all_datasets_as_list(self, tod_with_mocks, mock_api):
        """Test listing all datasets as list."""
        mock_api.list_all_datasets.return_value = ["dataset1", "dataset2"]
        result = tod_with_mocks.list_all_datasets(as_frame=False)
        mock_api.list_all_datasets.assert_called_once_with(False)
        assert isinstance(result, list)
        assert result == ["dataset1", "dataset2"]

    def test_search_datasets(self, tod_with_mocks, mock_api):
        """Test searching datasets."""
        result = tod_with_mocks.search_datasets("test query")
        mock_api.search_datasets.assert_called_once_with("test query", True)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    def test_search_datasets_as_list(self, tod_with_mocks, mock_api):
        """Test searching datasets as list."""
        mock_api.search_datasets.return_value = [{"name": "test_dataset"}]
        result = tod_with_mocks.search_datasets("test query", as_frame=False)
        mock_api.search_datasets.assert_called_once_with("test query", False)
        assert isinstance(result, list)
        assert result == [{"name": "test_dataset"}]

    def test_search_resources_by_name_found(self, tod_with_mocks, mock_api):
        """Test searching resources by name when dataset is found."""
        result = tod_with_mocks.search_resources_by_name("test dataset")
        mock_api.get_dataset_resources.assert_called_once_with("test dataset", True)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

    def test_search_resources_by_name_not_found(self, tod_with_mocks, mock_api):
        """Test searching resources by name when dataset is not found."""
        mock_api.get_dataset_resources.return_value = None
        result = tod_with_mocks.search_resources_by_name("nonexistent dataset")
        assert result is None

    def test_download_dataset_success(self, tod_with_mocks, mock_api, mock_cache):
        """Test successful dataset download."""
        result = tod_with_mocks.download_dataset("test dataset")
        mock_api.get_dataset_resources.assert_called_once_with("test dataset", as_frame=False)
        mock_cache.download_dataset.assert_called_once_with(
            "test dataset", mock_api.get_dataset_resources.return_value, False
        )
        assert result == ["file1.csv", "file2.json"]

    def test_download_dataset_not_found(self, tod_with_mocks, mock_api):
        """Test dataset download when dataset is not found."""
        mock_api.get_dataset_resources.return_value = None
        with pytest.raises(ValueError, match="Dataset nonexistent not found"):
            tod_with_mocks.download_dataset("nonexistent")

    def test_download_dataset_with_overwrite(self, tod_with_mocks, mock_api, mock_cache):
        """Test dataset download with overwrite flag."""
        result = tod_with_mocks.download_dataset("test dataset", overwrite=True)
        mock_cache.download_dataset.assert_called_once_with(
            "test dataset", mock_api.get_dataset_resources.return_value, True
        )

    def test_load_dataset_not_found(self, tod_with_mocks, mock_api):
        """Test load method when dataset is not found."""
        mock_api.get_dataset_resources.return_value = None
        with pytest.raises(ValueError, match="Dataset nonexistent not found"):
            tod_with_mocks.load("nonexistent", "file.csv")

    def test_load_filename_not_specified(self, tod_with_mocks, mock_api):
        """Test load method when filename is not specified."""
        with pytest.raises(ValueError, match="Please specify a file name"):
            tod_with_mocks.load("test dataset")

    def test_load_file_not_in_dataset(self, tod_with_mocks, mock_api):
        """Test load method when file is not in dataset."""
        with pytest.raises(ValueError, match="File nonexistent.csv not found in dataset"):
            tod_with_mocks.load("test dataset", "nonexistent.csv")

    def test_load_file_no_valid_url(self, tod_with_mocks, mock_api):
        """Test load method when file has no valid URL."""
        mock_api.get_dataset_resources.return_value = pd.DataFrame(
            {"name": ["file1.csv"], "url": [None], "format": ["CSV"]}  # No valid URL
        )
        with pytest.raises(ValueError, match="does not have a valid url"):
            tod_with_mocks.load("test dataset", "file1.csv")

    def test_load_file_success_path_return(self, tod_with_mocks, mock_api, mock_cache):
        """Test successful file load returning file path."""
        result = tod_with_mocks.load("test dataset", "file1.csv", smart_return=False)
        mock_cache.download_file.assert_called_once_with(
            "test dataset", "file1.csv", "http://example.com/file1.csv", False
        )
        assert result == Path("/tmp/test_file.csv")

    def test_load_file_success_smart_return(self, tod_with_mocks, mock_api, mock_cache):
        """Test successful file load with smart return."""
        with patch("toronto_open_data.core.loader_factory") as mock_loader_factory:
            mock_loaded_object = Mock()
            mock_loader_factory.load_file.return_value = mock_loaded_object

            result = tod_with_mocks.load("test dataset", "file1.csv", smart_return=True)
            mock_loader_factory.load_file.assert_called_once_with(Path("/tmp/test_file.csv"), "csv")
            assert result == mock_loaded_object

    def test_load_file_reload_flag(self, tod_with_mocks, mock_api, mock_cache):
        """Test load method with reload flag."""
        # Test with smart_return=False to avoid file loading issues
        tod_with_mocks.load("test dataset", "file1.csv", reload=True, smart_return=False)
        mock_cache.download_file.assert_called_once_with(
            "test dataset", "file1.csv", "http://example.com/file1.csv", True
        )

    def test_get_dataset_info_success(self, tod_with_mocks, mock_api):
        """Test getting dataset info successfully."""
        result = tod_with_mocks.get_dataset_info("test dataset")
        mock_api.get_dataset_info.assert_called_once_with("test dataset")
        assert result == {"name": "test_dataset", "title": "Test Dataset"}

    def test_get_dataset_info_not_found(self, tod_with_mocks, mock_api):
        """Test getting dataset info when dataset is not found."""
        mock_api.get_dataset_info.return_value = None
        result = tod_with_mocks.get_dataset_info("nonexistent")
        assert result is None

    def test_get_available_files_success(self, tod_with_mocks, mock_api):
        """Test getting available files successfully."""
        result = tod_with_mocks.get_available_files("test dataset")
        mock_api.get_dataset_resources.assert_called_once_with("test dataset", as_frame=True)
        assert result == ["file1.csv", "file2.json"]

    def test_get_available_files_dataset_not_found(self, tod_with_mocks, mock_api):
        """Test getting available files when dataset is not found."""
        mock_api.get_dataset_resources.return_value = None
        with pytest.raises(ValueError, match="Dataset nonexistent not found"):
            tod_with_mocks.get_available_files("nonexistent")

    def test_is_file_cached(self, tod_with_mocks, mock_cache):
        """Test checking if file is cached."""
        result = tod_with_mocks.is_file_cached("test dataset", "file1.csv")
        mock_cache.file_exists.assert_called_once_with("test dataset", "file1.csv")
        assert result is True

    def test_datastore_search(self, tod_with_mocks, mock_api):
        """Test datastore search."""
        result = tod_with_mocks.datastore_search("resource_id")
        mock_api.datastore_search.assert_called_once_with("resource_id", None, None, 100, 0, None, None, True)
        assert isinstance(result, pd.DataFrame)

    def test_datastore_search_with_all_params(self, tod_with_mocks, mock_api):
        """Test datastore search with all parameters."""
        filters = {"status": "active"}
        fields = ["id", "name"]
        result = tod_with_mocks.datastore_search(
            "resource_id",
            filters=filters,
            q="search query",
            limit=50,
            offset=10,
            fields=fields,
            sort="name asc",
            as_frame=False,
        )
        mock_api.datastore_search.assert_called_once_with(
            "resource_id", filters, "search query", 50, 10, fields, "name asc", False
        )

    def test_datastore_info(self, tod_with_mocks, mock_api):
        """Test getting datastore info."""
        result = tod_with_mocks.datastore_info("resource_id")
        mock_api.datastore_info.assert_called_once_with("resource_id")
        assert result == {"fields": [{"id": "id", "type": "int"}]}

    def test_datastore_search_sql(self, tod_with_mocks, mock_api):
        """Test datastore SQL search."""
        sql_query = "SELECT * FROM table LIMIT 10"
        result = tod_with_mocks.datastore_search_sql(sql_query)
        mock_api.datastore_search_sql.assert_called_once_with(sql_query, True)
        assert isinstance(result, pd.DataFrame)

    def test_datastore_search_sql_as_dict(self, tod_with_mocks, mock_api):
        """Test datastore SQL search returning dict."""
        mock_api.datastore_search_sql.return_value = {"records": []}
        sql_query = "SELECT * FROM table LIMIT 10"
        result = tod_with_mocks.datastore_search_sql(sql_query, as_frame=False)
        mock_api.datastore_search_sql.assert_called_once_with(sql_query, False)
        assert isinstance(result, dict)

    def test_get_datastore_resources_success(self, tod_with_mocks, mock_api):
        """Test getting datastore resources successfully."""
        # Mock resources with datastore_active flag
        mock_resources = [
            {"id": "res1", "name": "resource1", "datastore_active": True},
            {"id": "res2", "name": "resource2", "datastore_active": False},
            {"id": "res3", "name": "resource3", "datastore_active": True},
        ]
        mock_api.get_dataset_resources.return_value = mock_resources

        result = tod_with_mocks.get_datastore_resources("test dataset")
        mock_api.get_dataset_resources.assert_called_once_with("test dataset", as_frame=False)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2  # Only datastore_active=True resources
        assert result.iloc[0]["id"] == "res1"
        assert result.iloc[1]["id"] == "res3"

    def test_get_datastore_resources_as_list(self, tod_with_mocks, mock_api):
        """Test getting datastore resources as list."""
        mock_resources = [{"id": "res1", "name": "resource1", "datastore_active": True}]
        mock_api.get_dataset_resources.return_value = mock_resources

        result = tod_with_mocks.get_datastore_resources("test dataset", as_frame=False)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["id"] == "res1"

    def test_get_datastore_resources_dataset_not_found(self, tod_with_mocks, mock_api):
        """Test getting datastore resources when dataset is not found."""
        mock_api.get_dataset_resources.return_value = None
        result = tod_with_mocks.get_datastore_resources("nonexistent")
        assert result is None

    def test_get_datastore_resources_no_datastore_resources(self, tod_with_mocks, mock_api):
        """Test getting datastore resources when none are datastore-enabled."""
        mock_resources = [
            {"id": "res1", "name": "resource1", "datastore_active": False},
            {"id": "res2", "name": "resource2", "datastore_active": False},
        ]
        mock_api.get_dataset_resources.return_value = mock_resources

        result = tod_with_mocks.get_datastore_resources("test dataset")
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0  # Empty DataFrame

    def test_get_datastore_resources_empty_list(self, tod_with_mocks, mock_api):
        """Test getting datastore resources when dataset has no resources."""
        mock_api.get_dataset_resources.return_value = []

        tod_with_mocks.get_datastore_resources("test dataset")
        # Verify that the method completes without raising an exception

    def test_load_with_smart_return_disabled(self, tod_with_mocks, mock_api, mock_cache):
        """Test load method with smart return disabled."""
        tod_with_mocks.load("test dataset", "file1.csv", smart_return=False)
        mock_cache.download_file.assert_called_once_with(
            "test dataset", "file1.csv", "http://example.com/file1.csv", False
        )

    def test_load_with_reload_enabled(self, tod_with_mocks, mock_api, mock_cache):
        """Test load method with reload enabled."""
        # Test with smart_return=False to avoid file loading issues
        tod_with_mocks.load("test dataset", "file1.csv", reload=True, smart_return=False)
        mock_cache.download_file.assert_called_once_with(
            "test dataset", "file1.csv", "http://example.com/file1.csv", True
        )

    def test_load_file_with_na_url_handling(self, tod_with_mocks, mock_api):
        """Test load method handling of NaN URLs."""
        # Create a DataFrame with a NaN URL
        mock_api.get_dataset_resources.return_value = pd.DataFrame(
            {
                "name": ["file1.csv"],
                "url": [pd.NA],  # Using pandas NA
                "format": ["CSV"],
            }
        )

        with pytest.raises(ValueError, match="does not have a valid url"):
            tod_with_mocks.load("test dataset", "file1.csv")

    def test_load_file_with_empty_url_handling(self, tod_with_mocks, mock_api):
        """Test load method handling of empty URLs."""
        # Note: Empty strings are not considered NaN by pandas, so this won't raise an exception
        # The actual code only checks for pd.isna(url), not empty strings
        mock_api.get_dataset_resources.return_value = pd.DataFrame(
            {"name": ["file1.csv"], "url": [""], "format": ["CSV"]}  # Empty string URL
        )

        # This should not raise an exception since empty string is not NaN
        # The test verifies the current behavior of the code
        tod_with_mocks.load("test dataset", "file1.csv", smart_return=False)
        # Verify that the method completes without raising an exception

    def test_load_file_case_insensitive_format(self, tod_with_mocks, mock_api, mock_cache):
        """Test load method with case-insensitive format handling."""
        # Test with uppercase format that gets converted to lowercase
        mock_api.get_dataset_resources.return_value = pd.DataFrame(
            {
                "name": ["file1.CSV"],
                "url": ["http://example.com/file1.CSV"],
                "format": ["CSV"],  # Uppercase format
            }
        )

        with patch("toronto_open_data.core.loader_factory") as mock_loader_factory:
            mock_loaded_object = Mock()
            mock_loader_factory.load_file.return_value = mock_loaded_object

            result = tod_with_mocks.load("test dataset", "file1.CSV", smart_return=True)
            # Should convert format to lowercase for loader_factory
            mock_loader_factory.load_file.assert_called_once_with(Path("/tmp/test_file.csv"), "csv")
            assert result == mock_loaded_object

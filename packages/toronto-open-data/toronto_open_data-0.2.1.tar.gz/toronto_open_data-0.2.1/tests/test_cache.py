import os
import shutil
import tempfile
from unittest.mock import Mock, patch

import pytest

from toronto_open_data.cache import FileCache


class TestFileCache:
    """Test cases for FileCache class."""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create a temporary cache directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def file_cache(self, temp_cache_dir):
        """Create a FileCache instance for testing."""
        return FileCache(temp_cache_dir)

    def test_cache_initialization(self, file_cache, temp_cache_dir):
        """Test FileCache initialization."""
        assert str(file_cache.cache_path) == temp_cache_dir
        assert os.path.exists(temp_cache_dir)

    def test_download_dataset(self, file_cache):
        """Test downloading a dataset."""
        # Mock resources
        resources = [
            {
                "name": "test.csv",
                "url": "http://example.com/test.csv",
                "url_type": "upload",
            }
        ]

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.iter_content.return_value = [b"test content"]
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = file_cache.download_dataset("test_dataset", resources)
            assert len(result) == 1
            assert "test.csv" in result

    def test_download_file(self, file_cache):
        """Test downloading a single file."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.iter_content.return_value = [b"test content"]
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = file_cache.download_file("test_dataset", "test.csv", "http://example.com/test.csv")
            assert result.exists()

    def test_get_file_path(self, file_cache):
        """Test getting file path."""
        result = file_cache.get_file_path("test_dataset", "test.csv")
        expected_path = file_cache.cache_path / "test_dataset" / "test.csv"
        assert result == expected_path

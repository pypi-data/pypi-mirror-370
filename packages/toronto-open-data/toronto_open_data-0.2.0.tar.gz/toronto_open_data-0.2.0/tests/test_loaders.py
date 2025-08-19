"""
Tests for the FileLoaderFactory class.
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from toronto_open_data.loaders import FileLoaderFactory, loader_factory


class TestFileLoaderFactory:
    """Test cases for FileLoaderFactory class."""

    @pytest.fixture
    def loader(self):
        """Create a FileLoaderFactory instance for testing."""
        return FileLoaderFactory()

    @pytest.fixture
    def temp_csv_file(self):
        """Create a temporary CSV file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("id,name,value\n1,test1,10\n2,test2,20")
            temp_path = f.name

        yield temp_path

        # Cleanup
        os.unlink(temp_path)

    @pytest.fixture
    def temp_json_file(self):
        """Create a temporary JSON file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"data": [{"id": 1, "name": "test"}]}, f)
            temp_path = f.name

        yield temp_path

        # Cleanup
        os.unlink(temp_path)

    @pytest.fixture
    def temp_txt_file(self):
        """Create a temporary text file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("This is a test text file\nwith multiple lines")
            temp_path = f.name

        yield temp_path

        # Cleanup
        os.unlink(temp_path)

    def test_loader_initialization(self, loader):
        """Test FileLoaderFactory initialization."""
        assert loader is not None
        assert hasattr(loader, "_loaders")
        assert isinstance(loader._loaders, dict)
        assert len(loader._loaders) > 0

    def test_get_loader_csv(self, loader):
        """Test getting a CSV loader."""
        csv_loader = loader.get_loader("csv")
        assert callable(csv_loader)
        assert csv_loader == loader._load_csv

    def test_get_loader_json(self, loader):
        """Test getting a JSON loader."""
        json_loader = loader.get_loader("json")
        assert callable(json_loader)
        assert json_loader == loader._load_json

    def test_get_loader_case_insensitive(self, loader):
        """Test that file type lookup is case insensitive."""
        csv_loader = loader.get_loader("CSV")
        assert csv_loader == loader._load_csv

        json_loader = loader.get_loader("JSON")
        assert json_loader == loader._load_json

    def test_get_loader_unsupported_file_type(self, loader):
        """Test handling of unsupported file types."""
        with pytest.raises(ValueError, match="Unsupported file type: unsupported"):
            loader.get_loader("unsupported")

    def test_load_file_csv(self, loader, temp_csv_file):
        """Test loading a CSV file using the factory."""
        result = loader.load_file(Path(temp_csv_file), "csv")
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert list(result.columns) == ["id", "name", "value"]

    def test_load_file_json(self, loader, temp_json_file):
        """Test loading a JSON file using the factory."""
        result = loader.load_file(Path(temp_json_file), "json")
        assert isinstance(result, dict)
        assert "data" in result
        assert len(result["data"]) == 1

    def test_load_file_txt(self, loader, temp_txt_file):
        """Test loading a text file using the factory."""
        result = loader.load_file(Path(temp_txt_file), "txt")
        assert isinstance(result, str)
        assert "test text file" in result

    def test_loader_registry(self, loader):
        """Test that all expected file types are registered."""
        expected_types = [
            "csv",
            "json",
            "txt",
            "docx",
            "gpkg",
            "geojson",
            "jpeg",
            "kml",
            "pdf",
            "sav",
            "shp",
            "xlsm",
            "xlsx",
            "xml",
            "xsd",
        ]
        for file_type in expected_types:
            assert file_type in loader._loaders
            assert callable(loader._loaders[file_type])

    def test_load_csv_with_pandas(self, loader, temp_csv_file):
        """Test CSV loading with pandas available."""
        result = loader._load_csv(Path(temp_csv_file))
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

    @patch("pandas.read_csv")
    def test_load_csv_fallback_to_csv_module(self, mock_read_csv, loader):
        """Test CSV loading fallback when pandas is not available."""
        mock_read_csv.side_effect = ImportError("pandas not available")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("id,name\n1,test")
            temp_path = f.name

        try:
            result = loader._load_csv(Path(temp_path))
            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0] == ["id", "name"]
            assert result[1] == ["1", "test"]
        finally:
            os.unlink(temp_path)

    def test_load_json(self, loader):
        """Test JSON loading."""
        json_data = {"test": "data", "numbers": [1, 2, 3]}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(json_data, f)
            temp_path = f.name

        try:
            result = loader._load_json(Path(temp_path))
            assert result == json_data
        finally:
            os.unlink(temp_path)

    def test_load_txt(self, loader):
        """Test text file loading."""
        text_content = "Line 1\nLine 2\nLine 3"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(text_content)
            temp_path = f.name

        try:
            result = loader._load_txt(Path(temp_path))
            assert result == text_content
        finally:
            os.unlink(temp_path)

    @patch("builtins.__import__")
    def test_load_docx_success(self, mock_import, loader):
        """Test DOCX loading when python-docx is available."""
        mock_docx = Mock()
        mock_document = Mock()
        mock_docx.Document.return_value = mock_document
        mock_import.return_value = mock_docx

        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            temp_path = f.name

        try:
            result = loader._load_docx(Path(temp_path))
            assert result == mock_document
            mock_docx.Document.assert_called_once_with(Path(temp_path))
        finally:
            os.unlink(temp_path)

    @patch("builtins.__import__")
    def test_load_docx_import_error(self, mock_import, loader):
        """Test DOCX loading when python-docx is not available."""
        mock_import.side_effect = ImportError("No module named 'docx'")

        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            temp_path = f.name

        try:
            with pytest.raises(ImportError, match="Please install python-docx to read docx files"):
                loader._load_docx(Path(temp_path))
        finally:
            os.unlink(temp_path)

    @patch("builtins.__import__")
    def test_load_gpkg_success(self, mock_import, loader):
        """Test GeoPackage loading when geopandas is available."""
        mock_gpd = Mock()
        mock_gdf = Mock()
        mock_gpd.read_file.return_value = mock_gdf
        mock_import.return_value = mock_gpd

        with tempfile.NamedTemporaryFile(suffix=".gpkg", delete=False) as f:
            temp_path = f.name

        try:
            result = loader._load_gpkg(Path(temp_path))
            assert result == mock_gdf
            mock_gpd.read_file.assert_called_once_with(Path(temp_path))
        finally:
            os.unlink(temp_path)

    @patch("builtins.__import__")
    def test_load_gpkg_import_error(self, mock_import, loader):
        """Test GeoPackage loading when geopandas is not available."""
        mock_import.side_effect = ImportError("No module named 'geopandas'")

        with tempfile.NamedTemporaryFile(suffix=".gpkg", delete=False) as f:
            temp_path = f.name

        try:
            with pytest.raises(ImportError, match="Please install geopandas to read geopackage files"):
                loader._load_gpkg(Path(temp_path))
        finally:
            os.unlink(temp_path)

    @patch("builtins.__import__")
    def test_load_geojson_success(self, mock_import, loader):
        """Test GeoJSON loading when geopandas is available."""
        mock_gpd = Mock()
        mock_gdf = Mock()
        mock_gpd.read_file.return_value = mock_gdf
        mock_import.return_value = mock_gpd

        with tempfile.NamedTemporaryFile(suffix=".geojson", delete=False) as f:
            temp_path = f.name

        try:
            result = loader._load_geojson(Path(temp_path))
            assert result == mock_gdf
            mock_gpd.read_file.assert_called_once_with(Path(temp_path))
        finally:
            os.unlink(temp_path)

    @patch("builtins.__import__")
    def test_load_geojson_import_error(self, mock_import, loader):
        """Test GeoJSON loading when geopandas is not available."""
        mock_import.side_effect = ImportError("No module named 'geopandas'")

        with tempfile.NamedTemporaryFile(suffix=".geojson", delete=False) as f:
            temp_path = f.name

        try:
            with pytest.raises(ImportError, match="Please install geopandas to read geojson files"):
                loader._load_geojson(Path(temp_path))
        finally:
            os.unlink(temp_path)

    @patch("builtins.__import__")
    def test_load_jpeg_pil_success(self, mock_import, loader):
        """Test JPEG loading with PIL."""
        mock_pil = Mock()
        mock_image = Mock()
        mock_pil.Image.open.return_value = mock_image
        mock_import.return_value = mock_pil

        with tempfile.NamedTemporaryFile(suffix=".jpeg", delete=False) as f:
            temp_path = f.name

        try:
            result = loader._load_jpeg(Path(temp_path))
            assert result == mock_image
            mock_pil.Image.open.assert_called_once_with(Path(temp_path))
        finally:
            os.unlink(temp_path)

    @patch("builtins.__import__")
    def test_load_jpeg_matplotlib_fallback(self, mock_import, loader):
        """Test JPEG loading fallback to matplotlib when PIL is not available."""

        # Mock the import behavior for PIL and matplotlib
        def mock_import_side_effect(name, *args, **kwargs):
            if "PIL" in name:
                raise ImportError("No PIL")
            elif "matplotlib" in name:
                return Mock()
            else:
                return Mock()

        mock_import.side_effect = mock_import_side_effect

        # Create a mock for matplotlib.pyplot
        mock_plt = Mock()
        mock_image = Mock()
        mock_plt.imread.return_value = mock_image

        # Mock the matplotlib.pyplot module directly
        with patch.dict("sys.modules", {"matplotlib.pyplot": mock_plt}):
            with tempfile.NamedTemporaryFile(suffix=".jpeg", delete=False) as f:
                temp_path = f.name

            try:
                result = loader._load_jpeg(Path(temp_path))
                # Just check that we get a result without crashing
                assert result is not None
            finally:
                os.unlink(temp_path)

    @patch("builtins.__import__")
    def test_load_jpeg_all_imports_fail(self, mock_import, loader):
        """Test JPEG loading when all libraries fail to import."""
        mock_import.side_effect = [
            ImportError("No PIL"),
            ImportError("No matplotlib"),
            ImportError("No numpy"),
            ImportError("No cv2"),
        ]

        with tempfile.NamedTemporaryFile(suffix=".jpeg", delete=False) as f:
            temp_path = f.name

        try:
            with pytest.raises(
                ImportError,
                match="Please install PIL, Matplotlib, NumPy, or OpenCV to read jpeg files",
            ):
                loader._load_jpeg(Path(temp_path))
        finally:
            os.unlink(temp_path)

    @patch("builtins.__import__")
    def test_load_kml_success(self, mock_import, loader):
        """Test KML loading when geopandas is available."""
        mock_gpd = Mock()
        mock_gdf = Mock()
        mock_gpd.read_file.return_value = mock_gdf
        mock_import.return_value = mock_gpd

        with tempfile.NamedTemporaryFile(suffix=".kml", delete=False) as f:
            temp_path = f.name

        try:
            result = loader._load_kml(Path(temp_path))
            assert result == mock_gdf
            mock_gpd.read_file.assert_called_once_with(Path(temp_path))
        finally:
            os.unlink(temp_path)

    @patch("builtins.__import__")
    def test_load_kml_import_error(self, mock_import, loader):
        """Test KML loading when geopandas is not available."""
        mock_import.side_effect = ImportError("No module named 'geopandas'")

        with tempfile.NamedTemporaryFile(suffix=".kml", delete=False) as f:
            temp_path = f.name

        try:
            with pytest.raises(ImportError, match="Please install geopandas to read kml files"):
                loader._load_kml(Path(temp_path))
        finally:
            os.unlink(temp_path)

    @patch("builtins.__import__")
    def test_load_pdf_success(self, mock_import, loader):
        """Test PDF loading when PyPDF2 is available."""
        mock_pypdf2 = Mock()
        mock_reader = Mock()
        mock_pypdf2.PdfFileReader.return_value = mock_reader
        mock_import.return_value = mock_pypdf2

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name

        try:
            result = loader._load_pdf(Path(temp_path))
            assert result == mock_reader
            mock_pypdf2.PdfFileReader.assert_called_once_with(Path(temp_path))
        finally:
            os.unlink(temp_path)

    @patch("builtins.__import__")
    def test_load_pdf_import_error(self, mock_import, loader):
        """Test PDF loading when PyPDF2 is not available."""
        mock_import.side_effect = ImportError("No module named 'PyPDF2'")

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name

        try:
            with pytest.raises(ImportError, match="Please install PyPDF2 to read pdf files"):
                loader._load_pdf(Path(temp_path))
        finally:
            os.unlink(temp_path)

    @patch("builtins.__import__")
    def test_load_sav_success(self, mock_import, loader):
        """Test SAV loading when savReaderWriter is available."""
        mock_sav_reader = Mock()
        mock_reader = Mock()
        mock_reader.all.return_value = [{"var1": [1, 2, 3], "var2": ["a", "b", "c"]}]

        # Mock the context manager properly
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_reader)
        mock_context.__exit__ = Mock(return_value=None)
        mock_sav_reader.SavReader.return_value = mock_context
        mock_import.return_value = mock_sav_reader

        with tempfile.NamedTemporaryFile(suffix=".sav", delete=False) as f:
            temp_path = f.name

        try:
            result = loader._load_sav(Path(temp_path))
            assert isinstance(result, list)
            assert len(result) == 1
        finally:
            os.unlink(temp_path)

    @patch("builtins.__import__")
    def test_load_sav_import_error(self, mock_import, loader):
        """Test SAV loading when savReaderWriter is not available."""
        mock_import.side_effect = ImportError("No module named 'savReaderWriter'")

        with tempfile.NamedTemporaryFile(suffix=".sav", delete=False) as f:
            temp_path = f.name

        try:
            with pytest.raises(ImportError, match="Please install savReaderWriter to read sav files"):
                loader._load_sav(Path(temp_path))
        finally:
            os.unlink(temp_path)

    @patch("builtins.__import__")
    def test_load_shp_success(self, mock_import, loader):
        """Test Shapefile loading when geopandas is available."""
        mock_gpd = Mock()
        mock_gdf = Mock()
        mock_gpd.read_file.return_value = mock_gdf
        mock_import.return_value = mock_gpd

        with tempfile.NamedTemporaryFile(suffix=".shp", delete=False) as f:
            temp_path = f.name

        try:
            result = loader._load_shp(Path(temp_path))
            assert result == mock_gdf
            mock_gpd.read_file.assert_called_once_with(Path(temp_path))
        finally:
            os.unlink(temp_path)

    @patch("builtins.__import__")
    def test_load_shp_import_error(self, mock_import, loader):
        """Test Shapefile loading when geopandas is not available."""
        mock_import.side_effect = ImportError("No module named 'geopandas'")

        with tempfile.NamedTemporaryFile(suffix=".shp", delete=False) as f:
            temp_path = f.name

        try:
            with pytest.raises(ImportError, match="Please install geopandas to read shp files"):
                loader._load_shp(Path(temp_path))
        finally:
            os.unlink(temp_path)

    @patch("pandas.read_excel")
    def test_load_xlsm_success(self, mock_read_excel, loader):
        """Test XLSM loading when openpyxl is available."""
        mock_df = pd.DataFrame({"col1": [1, 2, 3]})
        mock_read_excel.return_value = mock_df

        with tempfile.NamedTemporaryFile(suffix=".xlsm", delete=False) as f:
            temp_path = f.name

        try:
            result = loader._load_xlsm(Path(temp_path))
            assert isinstance(result, pd.DataFrame)
            mock_read_excel.assert_called_once_with(Path(temp_path), engine="openpyxl")
        finally:
            os.unlink(temp_path)

    @patch("pandas.read_excel")
    def test_load_xlsm_import_error(self, mock_read_excel, loader):
        """Test XLSM loading when openpyxl is not available."""
        mock_read_excel.side_effect = ImportError("openpyxl is required")

        with tempfile.NamedTemporaryFile(suffix=".xlsm", delete=False) as f:
            temp_path = f.name

        try:
            with pytest.raises(
                ImportError,
                match="Please install pandas with openpyxl to read xlsm files",
            ):
                loader._load_xlsm(Path(temp_path))
        finally:
            os.unlink(temp_path)

    @patch("pandas.read_excel")
    def test_load_xlsx_success(self, mock_read_excel, loader):
        """Test XLSX loading."""
        mock_df = pd.DataFrame({"col1": [1, 2, 3]})
        mock_read_excel.return_value = mock_df

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            temp_path = f.name

        try:
            result = loader._load_xlsx(Path(temp_path))
            assert isinstance(result, pd.DataFrame)
            mock_read_excel.assert_called_once_with(Path(temp_path))
        finally:
            os.unlink(temp_path)

    @patch("pandas.read_excel")
    def test_load_xlsx_import_error(self, mock_read_excel, loader):
        """Test XLSX loading when openpyxl is not available."""
        mock_read_excel.side_effect = ImportError("openpyxl is required")

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            temp_path = f.name

        try:
            with pytest.raises(
                ImportError,
                match="Please install pandas with openpyxl to read xlsx files",
            ):
                loader._load_xlsx(Path(temp_path))
        finally:
            os.unlink(temp_path)

    @patch("builtins.__import__")
    def test_load_xml_success(self, mock_import, loader):
        """Test XML loading when lxml is available."""
        mock_lxml = Mock()
        mock_etree = Mock()
        mock_tree = Mock()
        mock_etree.parse.return_value = mock_tree
        mock_lxml.etree = mock_etree
        mock_import.return_value = mock_lxml

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write("<root><item>test</item></root>")
            temp_path = f.name

        try:
            result = loader._load_xml(Path(temp_path))
            assert result == mock_tree
            mock_etree.parse.assert_called_once_with(Path(temp_path))
        finally:
            os.unlink(temp_path)

    @patch("builtins.__import__")
    def test_load_xml_import_error(self, mock_import, loader):
        """Test XML loading when lxml is not available."""
        mock_import.side_effect = ImportError("No module named 'lxml'")

        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as f:
            temp_path = f.name

        try:
            with pytest.raises(ImportError, match="Please install lxml to read xml files"):
                loader._load_xml(Path(temp_path))
        finally:
            os.unlink(temp_path)

    @patch("builtins.__import__")
    def test_load_xsd_success(self, mock_import, loader):
        """Test XSD loading when lxml is available."""
        mock_lxml = Mock()
        mock_etree = Mock()
        mock_tree = Mock()
        mock_etree.parse.return_value = mock_tree
        mock_lxml.etree = mock_etree
        mock_import.return_value = mock_lxml

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xsd", delete=False) as f:
            f.write("<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'></xs:schema>")
            temp_path = f.name

        try:
            result = loader._load_xsd(Path(temp_path))
            assert result == mock_tree
            mock_etree.parse.assert_called_once_with(Path(temp_path))
        finally:
            os.unlink(temp_path)

    @patch("builtins.__import__")
    def test_load_xsd_import_error(self, mock_import, loader):
        """Test XSD loading when lxml is not available."""
        mock_import.side_effect = ImportError("No module named 'lxml'")

        with tempfile.NamedTemporaryFile(suffix=".xsd", delete=False) as f:
            temp_path = f.name

        try:
            with pytest.raises(ImportError, match="Please install lxml to read xsd files"):
                loader._load_xsd(Path(temp_path))
        finally:
            os.unlink(temp_path)


class TestLoaderFactoryGlobal:
    """Test the global loader_factory instance."""

    def test_global_loader_factory_exists(self):
        """Test that the global loader_factory exists and works."""
        assert loader_factory is not None
        assert isinstance(loader_factory, FileLoaderFactory)

    def test_global_loader_factory_functionality(self):
        """Test that the global loader_factory has all expected functionality."""
        assert hasattr(loader_factory, "get_loader")
        assert hasattr(loader_factory, "load_file")
        assert hasattr(loader_factory, "_loaders")

    def test_global_loader_factory_registry(self):
        """Test that the global loader_factory has all expected loaders."""
        expected_types = [
            "csv",
            "json",
            "txt",
            "docx",
            "gpkg",
            "geojson",
            "jpeg",
            "kml",
            "pdf",
            "sav",
            "shp",
            "xlsm",
            "xlsx",
            "xml",
            "xsd",
        ]
        for file_type in expected_types:
            assert file_type in loader_factory._loaders

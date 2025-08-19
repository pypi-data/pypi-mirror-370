"""
Core module containing the main TorontoOpenData class.
"""

from pathlib import Path
from typing import Any, List, Optional, Union

import pandas as pd

try:
    from .api import TorontoOpenDataAPI
    from .cache import FileCache
    from .config import config
    from .loaders import loader_factory
except ImportError:
    from api import TorontoOpenDataAPI
    from config import config
    from loaders import loader_factory

    from cache import FileCache


class TorontoOpenData:
    """
    Main class for interacting with Toronto Open Data portal.

    This class provides a high-level interface for listing, searching,
    downloading, and loading datasets from Toronto's open data portal.
    """

    def __init__(self, cache_path: Optional[str] = None):
        """
        Initialize the Toronto Open Data client.

        Args:
            cache_path: Directory where downloaded files will be stored
        """
        self.api = TorontoOpenDataAPI()
        self.cache = FileCache(cache_path)

    def list_all_datasets(self, as_frame: bool = True) -> Union[List[str], pd.DataFrame]:
        """
        List all available datasets.

        Args:
            as_frame: Whether to return the result as a Pandas DataFrame

        Returns:
            List of datasets as DataFrame or list
        """
        return self.api.list_all_datasets(as_frame)

    def search_datasets(self, query: str, as_frame: bool = True) -> Union[List[dict], pd.DataFrame]:
        """
        Search datasets by keyword.

        Args:
            query: Keyword to search for
            as_frame: Whether to return the result as a Pandas DataFrame

        Returns:
            List of datasets that match the query
        """
        return self.api.search_datasets(query, as_frame)

    def search_resources_by_name(self, name: str, as_frame: bool = True) -> Optional[Union[List[dict], pd.DataFrame]]:
        """
        Get resources for a specific dataset by name.

        Args:
            name: Name of the dataset to retrieve
            as_frame: Whether to return the result as a Pandas DataFrame

        Returns:
            Dataset resources as DataFrame or list, or None if not found
        """
        return self.api.get_dataset_resources(name, as_frame)

    def download_dataset(self, name: str, overwrite: bool = False) -> List[str]:
        """
        Download all resources for a dataset.

        Args:
            name: Name of the dataset to download
            overwrite: Whether to overwrite existing files

        Returns:
            List of downloaded resource names
        """
        resources = self.api.get_dataset_resources(name, as_frame=False)
        if resources is None:
            raise ValueError(f"Dataset {name} not found")

        return self.cache.download_dataset(name, resources, overwrite)

    def load(
        self,
        name: str,
        filename: Optional[str] = None,
        reload: bool = False,
        smart_return: bool = True,
    ) -> Union[Path, Any]:
        """
        Load a file from a specified dataset.

        Args:
            name: Name of the dataset to load from
            filename: Name of the file to load
            reload: Whether to download the file again even if it exists
            smart_return: Whether to attempt returning a loaded object instead of a file path

        Returns:
            File path or loaded object

        Raises:
            ValueError: If dataset or file not found, or file has no valid URL
        """
        # Get dataset resources
        dataset = self.api.get_dataset_resources(name, as_frame=True)
        if dataset is None:
            raise ValueError(f"Dataset {name} not found")

        # If filename not specified, show available options
        if filename is None:
            available_files = dataset["name"].values
            raise ValueError(f"Please specify a file name from the following options:\n" f"{available_files}")

        # Verify file exists in dataset
        if filename not in dataset["name"].values:
            available_files = dataset["name"].values
            raise ValueError(f"File {filename} not found in dataset {name} with options:\n" f"{available_files}")

        # Get file URL and verify it's valid
        file_info = dataset[dataset["name"] == filename].iloc[0]
        url = file_info["url"]
        if pd.isna(url):
            raise ValueError(f"File {filename} in dataset {name} does not have a valid url")

        # Get file type for smart return
        file_type = file_info["format"].lower()

        # Download file if needed
        file_path = self.cache.download_file(name, filename, url, reload)

        # Return loaded object or file path
        if smart_return and file_type in config.SMART_RETURN_FILETYPES:
            return loader_factory.load_file(file_path, file_type)

        return file_path

    def get_dataset_info(self, name: str) -> Optional[dict]:
        """
        Get complete information about a dataset.

        Args:
            name: Name of the dataset

        Returns:
            Complete dataset information or None if not found
        """
        return self.api.get_dataset_info(name)

    def get_available_files(self, name: str) -> List[str]:
        """
        Get list of available files for a dataset.

        Args:
            name: Name of the dataset

        Returns:
            List of available file names

        Raises:
            ValueError: If dataset not found
        """
        dataset = self.api.get_dataset_resources(name, as_frame=True)
        if dataset is None:
            raise ValueError(f"Dataset {name} not found")

        return dataset["name"].values.tolist()

    def is_file_cached(self, name: str, filename: str) -> bool:
        """
        Check if a file is already cached.

        Args:
            name: Name of the dataset
            filename: Name of the file

        Returns:
            True if file is cached, False otherwise
        """
        return self.cache.file_exists(name, filename)

    def datastore_search(
        self,
        resource_id: str,
        filters: Optional[dict] = None,
        q: Optional[str] = None,
        limit: Optional[int] = 100,
        offset: Optional[int] = 0,
        fields: Optional[List[str]] = None,
        sort: Optional[str] = None,
        as_frame: bool = True,
    ) -> Optional[Union[dict, pd.DataFrame]]:
        """
        Search records in a datastore resource with type-enforced results.

        This method provides access to CKAN's datastore API, allowing you to query
        structured data directly without downloading files. Results are returned
        with proper data types (dates as dates, numbers as numbers, etc.).

        Args:
            resource_id: ID of the datastore resource (found in resource metadata)
            filters: Dictionary of field filters (e.g., {'status': 'active', 'year': 2023})
            q: Full-text search query across all fields
            limit: Maximum number of records to return (default: 100, max: 32000)
            offset: Number of records to skip (useful for pagination)
            fields: List of specific fields to return (if None, returns all fields)
            sort: Sort order (e.g., 'date_field asc' or 'name_field desc')
            as_frame: Whether to return as DataFrame with proper types (default: True)

        Returns:
            DataFrame with properly typed data or raw dict, or None if resource not found

        Example:
            # Basic search
            data = tod.datastore_search('resource-id-here')

            # Filtered search
            data = tod.datastore_search('resource-id-here',
                                      filters={'status': 'active'},
                                      limit=50)

            # Search with sorting
            data = tod.datastore_search('resource-id-here',
                                      sort='date_created desc',
                                      limit=10)
        """
        return self.api.datastore_search(resource_id, filters, q, limit, offset, fields, sort, as_frame)

    def datastore_info(self, resource_id: str) -> Optional[dict]:
        """
        Get metadata information about a datastore resource.

        This method returns detailed information about the structure of a datastore
        resource, including field names, types, and descriptions.

        Args:
            resource_id: ID of the datastore resource

        Returns:
            Dictionary containing resource metadata including field information,
            or None if resource not found

        Example:
            info = tod.datastore_info('resource-id-here')
            if info:
                print("Fields available:")
                for field in info['fields']:
                    label = field.get('info', {}).get('label', 'No description')
                    print(f"- {field['id']}: {field.get('type', 'unknown')} - {label}")
        """
        return self.api.datastore_info(resource_id)

    def datastore_search_sql(self, sql: str, as_frame: bool = True) -> Optional[Union[dict, pd.DataFrame]]:
        """
        Execute SQL query on datastore with type-enforced results.

        This method allows you to run custom SQL queries against the datastore,
        providing maximum flexibility for data analysis.

        Args:
            sql: SQL query to execute (must be read-only)
            as_frame: Whether to return as DataFrame with proper types (default: True)

        Returns:
            DataFrame with properly typed data or raw dict, or None if query fails

        Example:
            # Custom SQL query
            data = tod.datastore_search_sql('''
                SELECT field1, field2, COUNT(*) as count
                FROM "resource-id-here"
                WHERE field1 > 100
                GROUP BY field1, field2
                ORDER BY count DESC
                LIMIT 10
            ''')
        """
        return self.api.datastore_search_sql(sql, as_frame)

    def get_datastore_resources(self, name: str, as_frame: bool = True) -> Optional[Union[List[dict], pd.DataFrame]]:
        """
        Get only datastore-enabled resources for a dataset.

        This is a convenience method that filters dataset resources to return only
        those that have datastore functionality enabled.

        Args:
            name: Name of the dataset
            as_frame: Whether to return the result as a Pandas DataFrame

        Returns:
            List of datastore-enabled resources or None if dataset not found

        Example:
            datastore_resources = tod.get_datastore_resources('dataset-name')
            if datastore_resources is not None:
                for resource in datastore_resources:
                    print(f"Resource: {resource['name']} (ID: {resource['id']})")
        """
        resources = self.api.get_dataset_resources(name, as_frame=False)
        if resources is None:
            return None

        # Filter for datastore-enabled resources
        datastore_resources = [r for r in resources if r.get("datastore_active", False)]

        if as_frame:
            return pd.DataFrame(datastore_resources) if datastore_resources else pd.DataFrame()
        return datastore_resources

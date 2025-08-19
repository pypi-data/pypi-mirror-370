"""
API module for interacting with Toronto Open Data CKAN portal.
"""

import logging
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from ckanapi import RemoteCKAN
from ckanapi.errors import CKANAPIError

try:
    from .config import config
except ImportError:
    from config import config


class TorontoOpenDataAPI:
    """Handles all API interactions with Toronto Open Data portal."""

    def __init__(self):
        """
        Initialize the API client.
        """
        self.ckan = RemoteCKAN(config.API_BASE_URL)

    def list_all_datasets(self, as_frame: bool = True) -> Union[List[str], pd.DataFrame]:
        """
        List all available datasets.

        Args:
            as_frame: Whether to return the result as a Pandas DataFrame

        Returns:
            List of datasets as DataFrame or list
        """
        result = self.ckan.action.package_list()

        if as_frame:
            return pd.DataFrame(result)
        return result

    def search_datasets(self, query: str, as_frame: bool = True) -> Union[List[Dict], pd.DataFrame]:
        """
        Search datasets by keyword.

        Args:
            query: Keyword to search for
            as_frame: Whether to return the result as a Pandas DataFrame

        Returns:
            List of datasets that match the query
        """
        result = self.ckan.action.package_search(q=query)

        if "results" in result:
            if as_frame:
                return pd.DataFrame(result["results"])
            return result["results"]
        return []

    def get_dataset_resources(self, name: str, as_frame: bool = True) -> Optional[Union[List[Dict], pd.DataFrame]]:
        """
        Get resources for a specific dataset.

        Args:
            name: Name of the dataset to retrieve
            as_frame: Whether to return the result as a Pandas DataFrame

        Returns:
            Dataset resources as DataFrame or list, or None if not found
        """
        try:
            result = self.ckan.action.package_show(id=name)["resources"]
        except CKANAPIError:
            return None

        if as_frame:
            return pd.DataFrame(result)
        return result

    def get_dataset_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get complete dataset information.

        Args:
            name: Name of the dataset to retrieve

        Returns:
            Complete dataset information or None if not found
        """
        try:
            return self.ckan.action.package_show(id=name)
        except CKANAPIError:
            return None

    def datastore_search(
        self,
        resource_id: str,
        filters: Optional[Dict[str, Any]] = None,
        q: Optional[str] = None,
        limit: Optional[int] = 100,
        offset: Optional[int] = 0,
        fields: Optional[List[str]] = None,
        sort: Optional[str] = None,
        as_frame: bool = True,
    ) -> Optional[Union[Dict[str, Any], pd.DataFrame]]:
        """
        Search records in a datastore resource with type-enforced results.

        Args:
            resource_id: ID of the datastore resource
            filters: Dictionary of field filters (e.g., {'field': 'value'})
            q: Full-text search query
            limit: Maximum number of records to return (default: 100, max: 32000)
            offset: Number of records to skip (for pagination)
            fields: List of fields to return (if None, returns all fields)
            sort: Sort order (e.g., 'field_name asc' or 'field_name desc')
            as_frame: Whether to return the result as a Pandas DataFrame with proper types

        Returns:
            Search results as DataFrame with proper types or raw dict, or None if resource not found
        """
        try:
            # Build search parameters
            search_params = {
                "resource_id": resource_id,
                "limit": limit,
                "offset": offset,
            }

            if filters:
                search_params["filters"] = filters
            if q:
                search_params["q"] = q
            if fields:
                search_params["fields"] = fields
            if sort:
                search_params["sort"] = sort

            result = self.ckan.action.datastore_search(**search_params)

            if as_frame and "records" in result:
                # Convert to DataFrame with proper types based on field info
                df = pd.DataFrame(result["records"])

                # Apply type conversions based on field metadata
                if "fields" in result:
                    for field in result["fields"]:
                        field_name = field["id"]
                        field_type = field.get("type", "text")

                        if field_name in df.columns:
                            df[field_name] = self._convert_field_type(df[field_name], field_type)

                return df

            return result

        except CKANAPIError:
            return None

    def datastore_info(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata information about a datastore resource including field types and descriptions.

        Args:
            resource_id: ID of the datastore resource

        Returns:
            Resource metadata including field information or None if resource not found
        """
        try:
            return self.ckan.action.datastore_info(id=resource_id)
        except CKANAPIError:
            return None

    def datastore_search_sql(self, sql: str, as_frame: bool = True) -> Optional[Union[Dict[str, Any], pd.DataFrame]]:
        """
        Execute SQL query on datastore with type-enforced results.

        Args:
            sql: SQL query to execute
            as_frame: Whether to return the result as a Pandas DataFrame with proper types

        Returns:
            Query results as DataFrame with proper types or raw dict, or None if query fails
        """
        try:
            result = self.ckan.action.datastore_search_sql(sql=sql)

            if as_frame and "records" in result:
                df = pd.DataFrame(result["records"])

                # Apply basic type inference since SQL results may not have field metadata
                df = self._infer_dataframe_types(df)

                return df

            return result

        except CKANAPIError:
            return None

    def _convert_field_type(self, series: pd.Series, field_type: str) -> pd.Series:
        """
        Convert a pandas Series to the appropriate type based on CKAN field type.

        Args:
            series: Pandas Series to convert
            field_type: CKAN field type

        Returns:
            Converted series with appropriate dtype
        """
        try:
            if field_type in ["timestamp", "date"]:
                return pd.to_datetime(series, errors="coerce")
            elif field_type in ["int", "int4", "integer"]:
                return pd.to_numeric(series, errors="coerce").astype("Int64")
            elif field_type in ["float", "float8", "numeric"]:
                return pd.to_numeric(series, errors="coerce")
            elif field_type == "bool":
                return series.astype("boolean")
            else:  # text, string, or other types
                return series.astype("string")
        except Exception:
            # If conversion fails, return original series
            return series

    def _infer_dataframe_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Infer and convert appropriate types for a DataFrame.

        Args:
            df: DataFrame to process

        Returns:
            DataFrame with inferred types
        """
        for col in df.columns:
            # Try to convert to numeric first
            numeric_series = pd.to_numeric(df[col], errors="coerce")
            if not numeric_series.isna().all():
                df[col] = numeric_series
                continue

            # Try to convert to datetime
            try:
                datetime_series = pd.to_datetime(df[col], errors="coerce")
                if not datetime_series.isna().all():
                    df[col] = datetime_series
                    continue
            except Exception as e:
                logging.exception("Failed to convert column '%s' to datetime: %s", col, e)

            # Default to string type
            df[col] = df[col].astype("string")
        return df

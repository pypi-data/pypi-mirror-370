#!/usr/bin/env python3
"""
Comprehensive examples demonstrating ALL functionality mentioned in the README.

This script covers:
- Basic dataset operations
- Datastore API features
- Smart return file types
- Error handling
- Performance tips
"""

import sys
from pathlib import Path

# Add the package to the path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from toronto_open_data import TorontoOpenData
except ImportError:
    print("❌ Could not import toronto_open_data. Make sure the package is installed.")
    sys.exit(1)


def basic_dataset_operations():
    """Demonstrate basic dataset operations from README."""
    print("🚀 Basic Dataset Operations")
    print("=" * 50)

    tod = TorontoOpenData()

    # 1. List all datasets
    print("\n1. Listing all available datasets...")
    try:
        datasets = tod.list_all_datasets(as_frame=False)
        print(f"📊 Found {len(datasets)} total datasets")
        print("First 3 datasets:")
        for i, name in enumerate(datasets[:3]):
            print(f"   {i+1}. {name}")
    except Exception as e:
        print(f"❌ Error listing datasets: {e}")

    # 2. Search datasets by keyword
    print("\n2. Searching for 'parks' datasets...")
    try:
        parks_datasets = tod.search_datasets("parks", as_frame=False)
        print(f"🌳 Found {len(parks_datasets)} parks-related datasets")
        if parks_datasets:
            print("Parks datasets:")
            for i, name in enumerate(parks_datasets[:3]):
                print(f"   {i+1}. {name}")
    except Exception as e:
        print(f"❌ Error searching parks datasets: {e}")

    # 3. Get dataset by name
    print("\n3. Getting dataset by name...")
    try:
        # Try to find a real dataset
        if parks_datasets:
            dataset_name = parks_datasets[0]
            resources = tod.search_resources_by_name(dataset_name, as_frame=False)
            if resources:
                print(f"✅ Found resources for '{dataset_name}': {len(resources)} resources")
            else:
                print(f"❌ No resources found for '{dataset_name}'")
        else:
            print("❌ No parks datasets found to test with")
    except Exception as e:
        print(f"❌ Error getting dataset resources: {e}")

    return tod


def download_and_load_examples():
    """Demonstrate download and load functionality."""
    print("\n📥 Download and Load Examples")
    print("=" * 50)

    tod = TorontoOpenData()

    # Search for a dataset with downloadable files
    print("Searching for datasets with downloadable files...")
    try:
        # Look for CSV datasets specifically
        csv_datasets = tod.search_datasets("csv", as_frame=False)
        if csv_datasets:
            dataset_name = csv_datasets[0]
            print(f"Working with dataset: {dataset_name}")

            # Get available files
            files = tod.get_available_files(dataset_name)
            print(f"Available files: {files}")

            if files:
                # Download the dataset
                print(f"\nDownloading {dataset_name}...")
                try:
                    downloaded = tod.download_dataset(dataset_name, overwrite=False)
                    print(f"✅ Downloaded: {downloaded}")

                    # Try to load a file
                    first_file = files[0]
                    print(f"\nLoading file: {first_file}")

                    # Load with smart return disabled (get file path)
                    file_path = tod.load(dataset_name, first_file, smart_return=False)
                    print(f"📁 File path: {file_path}")

                    # Load with smart return enabled (attempt to parse)
                    try:
                        data = tod.load(dataset_name, first_file, smart_return=True)
                        if hasattr(data, "head"):  # DataFrame
                            print(f"✅ Loaded as DataFrame: {data.shape}")
                            print("First few rows:")
                            print(data.head())
                        else:
                            print(f"✅ Loaded as: {type(data).__name__}")
                    except Exception as e:
                        print(f"⚠️  Smart return failed: {e}")
                        print("This is normal for some file types")

                except Exception as e:
                    print(f"❌ Error downloading: {e}")
            else:
                print("❌ No downloadable files found")
        else:
            print("❌ No CSV datasets found")

    except Exception as e:
        print(f"❌ Error in download/load examples: {e}")


def datastore_api_examples():
    """Demonstrate datastore API functionality."""
    print("\n🗄️  Datastore API Examples")
    print("=" * 50)

    tod = TorontoOpenData()

    # Search for datasets that might have datastore resources
    print("Searching for datasets with datastore resources...")
    try:
        # Look for datasets that might have structured data
        structured_datasets = tod.search_datasets("data", as_frame=False)

        if structured_datasets:
            for dataset_name in structured_datasets[:3]:
                print(f"\nChecking dataset: {dataset_name}")

                try:
                    # Check if this dataset has datastore resources
                    datastore_resources = tod.get_datastore_resources(dataset_name, as_frame=False)

                    if datastore_resources:
                        print(f"✅ Found {len(datastore_resources)} datastore resources")

                        # Get info about the first resource
                        first_resource = datastore_resources[0]
                        resource_id = first_resource["id"]
                        print(f"Resource: {first_resource['name']} (ID: {resource_id})")

                        # Get metadata about the resource
                        try:
                            info = tod.datastore_info(resource_id)
                            print(f"📋 Resource info: {len(info.get('fields', []))} fields")

                            # Show field information
                            for field in info.get("fields", [])[:3]:  # Show first 3 fields
                                field_id = field.get("id", "Unknown")
                                field_type = field.get("type", "Unknown")
                                field_label = field.get("info", {}).get("label", "No description")
                                print(f"   - {field_id}: {field_type} - {field_label}")

                            # Try a basic search
                            print("\n🔍 Trying basic datastore search...")
                            try:
                                search_results = tod.datastore_search(resource_id, limit=5)
                                if hasattr(search_results, "shape"):
                                    print(f"✅ Search successful: {search_results.shape}")
                                    print("First few results:")
                                    print(search_results.head())
                                else:
                                    print(f"✅ Search successful: {type(search_results)}")
                            except Exception as e:
                                print(f"⚠️  Basic search failed: {e}")

                            # Try SQL query if supported
                            print("\n🔍 Trying SQL query...")
                            try:
                                sql_results = tod.datastore_search_sql(f'SELECT * FROM "{resource_id}" LIMIT 3')
                                if hasattr(sql_results, "shape"):
                                    print(f"✅ SQL query successful: {sql_results.shape}")
                                    print("SQL results:")
                                    print(sql_results.head())
                                else:
                                    print(f"✅ SQL query successful: {type(sql_results)}")
                            except Exception as e:
                                print(f"⚠️  SQL query failed: {e}")

                        except Exception as e:
                            print(f"❌ Error getting resource info: {e}")

                        # Only test with first resource to avoid overwhelming output
                        break
                    else:
                        print("❌ No datastore resources found")

                except Exception as e:
                    print(f"❌ Error checking dataset: {e}")
                    continue
        else:
            print("❌ No structured datasets found")

    except Exception as e:
        print(f"❌ Error in datastore examples: {e}")


def smart_return_file_types():
    """Demonstrate smart return for different file types."""
    print("\n🎯 Smart Return File Types Examples")
    print("=" * 50)

    print("The package supports smart return for these file types:")
    supported_types = [
        "csv",
        "docx",
        "gpkg",
        "geojson",
        "jpeg",
        "json",
        "kml",
        "pdf",
        "sav",
        "shp",
        "txt",
        "xlsm",
        "xlsx",
        "xml",
        "xsd",
    ]

    for i, file_type in enumerate(supported_types, 1):
        print(f"   {i:2d}. {file_type}")

    print("\n💡 Smart return automatically:")
    print("   - Parses CSV files into pandas DataFrames")
    print("   - Loads JSON files as Python objects")
    print("   - Converts Excel files to DataFrames")
    print("   - Handles geographic files (GeoJSON, KML, Shapefiles)")
    print("   - Processes various document formats")

    # Try to find and test some supported file types
    tod = TorontoOpenData()

    print("\n🔍 Testing smart return with real files...")

    # Test CSV files
    try:
        csv_datasets = tod.search_datasets("csv", as_frame=False)
        if csv_datasets:
            dataset_name = csv_datasets[0]
            files = tod.get_available_files(dataset_name)
            if files:
                csv_file = next((f for f in files if f.lower().endswith(".csv")), None)
                if csv_file:
                    print(f"\nTesting CSV smart return with: {csv_file}")
                    try:
                        data = tod.load(dataset_name, csv_file, smart_return=True)
                        if hasattr(data, "head"):
                            print(f"✅ CSV loaded as DataFrame: {data.shape}")
                        else:
                            print(f"✅ CSV loaded as: {type(data).__name__}")
                    except Exception as e:
                        print(f"⚠️  CSV smart return failed: {e}")
    except Exception as e:
        print(f"❌ Error testing CSV: {e}")

    # Test JSON files
    try:
        json_datasets = tod.search_datasets("json", as_frame=False)
        if json_datasets:
            dataset_name = json_datasets[0]
            files = tod.get_available_files(dataset_name)
            if files:
                json_file = next((f for f in files if f.lower().endswith(".json")), None)
                if json_file:
                    print(f"\nTesting JSON smart return with: {json_file}")
                    try:
                        data = tod.load(dataset_name, json_file, smart_return=True)
                        print(f"✅ JSON loaded as: {type(data).__name__}")
                    except Exception as e:
                        print(f"⚠️  JSON smart return failed: {e}")
    except Exception as e:
        print(f"❌ Error testing JSON: {e}")


def error_handling_examples():
    """Demonstrate error handling and edge cases."""
    print("\n⚠️  Error Handling Examples")
    print("=" * 50)

    tod = TorontoOpenData()

    # Test with non-existent dataset
    print("1. Testing with non-existent dataset...")
    try:
        result = tod.search_resources_by_name("this-dataset-does-not-exist")
        if result is None:
            print("✅ Correctly returned None for non-existent dataset")
        else:
            print(f"❌ Unexpected result: {result}")
    except Exception as e:
        print(f"✅ Correctly caught error: {e}")

    # Test with non-existent file
    print("\n2. Testing with non-existent file...")
    try:
        # Get a real dataset first
        datasets = tod.list_all_datasets(as_frame=False)
        if datasets:
            dataset_name = datasets[0]
            result = tod.load(dataset_name, "non-existent-file.csv")
            print(f"❌ Unexpected success: {result}")
        else:
            print("❌ No datasets available for testing")
    except Exception as e:
        print(f"✅ Correctly caught error: {e}")

    # Test cache status
    print("\n3. Testing cache status...")
    try:
        datasets = tod.list_all_datasets(as_frame=False)
        if datasets:
            dataset_name = datasets[0]
            files = tod.get_available_files(dataset_name)
            if files:
                first_file = files[0]
                is_cached = tod.is_file_cached(dataset_name, first_file)
                print(f"📁 File '{first_file}' is {'✅ cached' if is_cached else '❌ not cached'}")
            else:
                print("❌ No files available for cache testing")
        else:
            print("❌ No datasets available for cache testing")
    except Exception as e:
        print(f"❌ Error checking cache: {e}")


def performance_tips():
    """Show performance tips and best practices."""
    print("\n⚡ Performance Tips and Best Practices")
    print("=" * 50)

    print("💡 Performance Tips:")
    print("   1. Use caching - files are cached locally after first download")
    print("   2. Use datastore API for large datasets instead of downloading")
    print("   3. Use filters in datastore_search to limit data transfer")
    print("   4. Set smart_return=False if you only need file paths")
    print("   5. Use overwrite=False to avoid re-downloading existing files")

    print("\n🔧 Best Practices:")
    print("   1. Always handle exceptions gracefully")
    print("   2. Check if files exist before attempting to load")
    print("   3. Use appropriate data types (as_frame=True/False)")
    print("   4. Leverage datastore API for real-time data")
    print("   5. Monitor cache directory size for large datasets")

    print("\n📊 Datastore vs File Download:")
    print("   File Download (load()):")
    print("     - Static files, client-side filtering")
    print("     - Good for one-time analysis")
    print("     - Higher network usage")
    print("   Datastore API:")
    print("     - Real-time data, server-side filtering")
    print("     - Good for dynamic queries")
    print("     - Lower network usage")


def main():
    """Run all comprehensive examples."""
    print("Toronto Open Data Package - Comprehensive Feature Examples")
    print("=" * 70)

    try:
        # Run all example sections
        basic_dataset_operations()
        download_and_load_examples()
        datastore_api_examples()
        smart_return_file_types()
        error_handling_examples()
        performance_tips()

        print("\n" + "=" * 70)
        print("🎉 All examples completed successfully!")
        print("\n💡 Key Takeaways:")
        print("   - The package provides both basic and advanced data access")
        print("   - Datastore API offers real-time, filtered data access")
        print("   - Smart return automatically handles various file formats")
        print("   - Robust error handling for production use")
        print("   - Caching improves performance for repeated access")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("This might be due to network issues or API changes")


if __name__ == "__main__":
    main()

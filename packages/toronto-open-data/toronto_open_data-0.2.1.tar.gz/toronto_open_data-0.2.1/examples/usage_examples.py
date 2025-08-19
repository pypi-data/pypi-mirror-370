#!/usr/bin/env python3
"""
Comprehensive examples for Toronto Open Data Package.

This script demonstrates various usage patterns and features.
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


def main():
    """Main example function demonstrating package usage."""
    print("🚀 Toronto Open Data Package Examples")
    print("=" * 50)

    # Initialize the client
    print("\n1. Initializing Toronto Open Data client...")
    tod = TorontoOpenData()
    print(f"✅ Client initialized with cache directory: {tod.cache.cache_dir}")

    # Example 1: List all available datasets
    print("\n2. Listing all available datasets...")
    try:
        datasets = tod.list_all_datasets(as_frame=False)  # Get as list
        print(f"📊 Found {len(datasets)} total datasets")
        print("First 5 datasets:")
        for i, name in enumerate(datasets[:5]):
            print(f"   {i+1}. {name}")
    except Exception as e:
        print(f"❌ Error listing datasets: {e}")

    # Example 2: Search for specific datasets
    print("\n3. Searching for datasets containing 'population'...")
    try:
        population_datasets = tod.search_datasets("population", as_frame=False)  # Get as list
        print(f"🔍 Found {len(population_datasets)} population-related datasets")
        if len(population_datasets) > 0:
            print("Population datasets:")
            for i, name in enumerate(population_datasets[:3]):
                print(f"   {i+1}. {name}")
    except Exception as e:
        print(f"❌ Error searching datasets: {e}")

    # Example 3: Get information about a specific dataset
    print("\n4. Getting information about 'Toronto Population Health Status Indicators'...")
    try:
        dataset_info = tod.get_dataset_info("toronto-population-health-status-indicators")
        if dataset_info:
            print(f"📋 Dataset: {dataset_info['title']}")
            print(f"   Description: {dataset_info['description'][:200]}...")
            print(f"   Organization: {dataset_info.get('organization', {}).get('title', 'N/A')}")
            print(f"   Last Updated: {dataset_info.get('metadata_modified', 'N/A')}")
        else:
            print("❌ Dataset not found")
    except Exception as e:
        print(f"❌ Error getting dataset info: {e}")

    # Example 4: List available files in a dataset
    print("\n5. Listing available files in 'Toronto Population Health Status Indicators'...")
    try:
        files = tod.get_available_files("toronto-population-health-status-indicators")
        print(f"📁 Available files: {files}")
    except Exception as e:
        print(f"❌ Error getting available files: {e}")

    # Example 5: Download a dataset
    print("\n6. Downloading 'Toronto Population Health Status Indicators' dataset...")
    try:
        downloaded_files = tod.download_dataset("toronto-population-health-status-indicators", overwrite=False)
        print(f"⬇️  Downloaded {len(downloaded_files)} files:")
        for file in downloaded_files:
            print(f"   - {file}")
    except Exception as e:
        print(f"❌ Error downloading dataset: {e}")

    # Example 6: Load and work with data
    print("\n7. Loading data from the downloaded dataset...")
    try:
        # Try to load the first available file
        files = tod.get_available_files("toronto-population-health-status-indicators")
        if files:
            first_file = files[0]
            print(f"📖 Loading file: {first_file}")

            # Load with smart return (attempts to parse the file)
            data = tod.load("toronto-population-health-status-indicators", first_file, smart_return=True)

            if hasattr(data, "head"):  # It's a DataFrame
                print(f"✅ Loaded as DataFrame with shape: {data.shape}")
                print("First few rows:")
                print(data.head())
                print(f"\nColumns: {list(data.columns)}")
            else:
                print(f"✅ Loaded as: {type(data).__name__}")
                print(f"Content: {data}")
        else:
            print("❌ No files available to load")
    except Exception as e:
        print(f"❌ Error loading data: {e}")

    # Example 7: Search for datasets with specific criteria
    print("\n8. Searching for datasets with 'health' in the name...")
    try:
        health_datasets = tod.search_datasets("health", as_frame=False)  # Get as list
        print(f"🏥 Found {len(health_datasets)} health-related datasets")
        if len(health_datasets) > 0:
            print("Health datasets:")
            for i, name in enumerate(health_datasets[:3]):
                print(f"   {i+1}. {name}")
    except Exception as e:
        print(f"❌ Error searching health datasets: {e}")

    # Example 8: Check if files are cached
    print("\n9. Checking cache status...")
    try:
        files = tod.get_available_files("toronto-population-health-status-indicators")
        if files:
            first_file = files[0]
            is_cached = tod.is_file_cached("toronto-population-health-status-indicators", first_file)
            print(f"📁 File '{first_file}' is {'✅ cached' if is_cached else '❌ not cached'}")
    except Exception as e:
        print(f"❌ Error checking cache: {e}")

    # Example 9: Try to load a non-existent dataset (error handling)
    print("\n10. Testing error handling with non-existent dataset...")
    try:
        result = tod.search_resources_by_name("this-dataset-does-not-exist")
        if result is None:
            print("✅ Correctly returned None for non-existent dataset")
        else:
            print(f"❌ Unexpected result: {result}")
    except Exception as e:
        print(f"✅ Correctly caught error: {e}")

    print("\n" + "=" * 50)
    print("🎉 Examples completed!")
    print("\n💡 Tips:")
    print("   - Use 'as_frame=True' to get pandas DataFrames")
    print("   - Use 'smart_return=True' to automatically parse files")
    print("   - Check cache status before downloading")
    print("   - Handle exceptions for robust applications")
    print("   - Use search functions to discover relevant datasets")


if __name__ == "__main__":
    main()

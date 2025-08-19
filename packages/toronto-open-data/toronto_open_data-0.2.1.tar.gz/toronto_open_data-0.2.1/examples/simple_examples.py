#!/usr/bin/env python3
"""
Simple examples for Toronto Open Data Package.

This script demonstrates basic usage patterns.
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


def basic_usage():
    """Show basic package usage."""
    print("🚀 Basic Toronto Open Data Usage")
    print("=" * 40)

    # Initialize
    tod = TorontoOpenData()

    # List datasets
    print("\n📊 Available datasets:")
    datasets = tod.list_all_datasets(as_frame=False)  # Get as list
    print(f"Total: {len(datasets)} datasets")

    # Show first few
    for i, name in enumerate(datasets[:3]):
        print(f"  {i+1}. {name}")

    return tod


def search_and_download():
    """Show how to search and download datasets."""
    print("\n🔍 Search and Download Example")
    print("=" * 40)

    tod = TorontoOpenData()

    # Search for population data
    print("Searching for 'population' datasets...")
    results = tod.search_datasets("population", as_frame=False)  # Get as list
    print(f"Found {len(results)} results")

    if len(results) > 0:
        # Get the first result - extract the name if it's a dict
        first_result = results[0]
        if isinstance(first_result, dict):
            dataset_name = first_result.get("name", str(first_result))
        else:
            dataset_name = first_result

        print(f"\nWorking with: {dataset_name}")

        # List available files
        files = tod.get_available_files(dataset_name)
        print(f"Available files: {files}")

        if files:
            # Download the dataset
            print(f"\nDownloading {dataset_name}...")
            try:
                downloaded = tod.download_dataset(dataset_name)
                print(f"✅ Downloaded: {downloaded}")

                return dataset_name, files[0]
            except Exception as e:
                print(f"❌ Error downloading: {e}")
                return None, None
        else:
            print("❌ No downloadable files found")
            return None, None
    else:
        print("❌ No population datasets found")
        return None, None


def load_and_analyze(dataset_name, filename):
    """Show how to load and analyze data."""
    if not dataset_name or not filename:
        print("❌ No dataset to load")
        return

    print("\n📖 Loading and Analyzing Data")
    print("=" * 40)

    tod = TorontoOpenData()

    try:
        # Load the data with smart return
        print(f"Loading {filename} from {dataset_name}...")
        data = tod.load(dataset_name, filename, smart_return=True)

        if hasattr(data, "head"):  # DataFrame
            print(f"✅ Loaded as DataFrame: {data.shape}")
            print("\nFirst few rows:")
            print(data.head())

            print(f"\nColumns: {list(data.columns)}")
            print(f"Data types: {data.dtypes}")

            # Basic statistics
            if data.select_dtypes(include=["number"]).shape[1] > 0:
                print("\nNumeric column statistics:")
                print(data.describe())

        else:
            print(f"✅ Loaded as: {type(data).__name__}")
            print(f"Content preview: {str(data)[:200]}...")

    except Exception as e:
        print(f"❌ Error loading data: {e}")


def main():
    """Run all examples."""
    print("Toronto Open Data Package - Simple Examples")
    print("=" * 50)

    # Basic usage
    tod = basic_usage()

    # Search and download
    dataset_name, filename = search_and_download()

    # Load and analyze
    load_and_analyze(dataset_name, filename)

    print("\n🎉 Examples completed!")
    print("\n💡 Try running individual functions:")
    print("   basic_usage()")
    print("   search_and_download()")
    print("   load_and_analyze('dataset-name', 'filename')")


if __name__ == "__main__":
    main()

# Toronto Open Data Package Examples

This directory contains example scripts demonstrating how to use the `toronto-open-data` package with real Toronto Open Data.

## 📁 Files

- **`comprehensive_features.py`** - **NEW!** Complete examples covering ALL functionality from the README
- **`usage_examples.py`** - Comprehensive examples showing all package features
- **`simple_examples.py`** - Basic examples for quick start
- **`README.md`** - This file

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- `toronto-open-data` package installed
- Internet connection to access Toronto Open Data

### Installation
```bash
# Install the package
pip install toronto-open-data

# Or install in development mode
pip install -e .
```

### Running Examples

#### Start Here - Complete Feature Coverage
```bash
cd examples
python comprehensive_features.py
```

#### Simple Examples
```bash
cd examples
python simple_examples.py
```

#### Comprehensive Examples
```bash
cd examples
python usage_examples.py
```

## 📊 What the Examples Show

### Basic Usage
- Initializing the client
- Listing available datasets
- Searching for specific datasets
- Getting dataset information

### Data Operations
- Downloading datasets
- Loading data with automatic format detection
- Working with pandas DataFrames
- Handling different file types

### Advanced Features
- **Datastore API** - Real-time data access with filtering and SQL queries
- **Smart Return** - Automatic file format detection and parsing
- **Cache management** - Efficient file management and reuse
- **Error handling** - Robust error handling for production use
- **Performance optimization** - Best practices for large datasets

### Complete Feature Coverage (comprehensive_features.py)
This new file demonstrates **every single feature** mentioned in the main README:

1. **Basic Dataset Operations**
   - `list_all_datasets()`
   - `search_datasets()`
   - `search_resources_by_name()`

2. **Download and Load**
   - `download_dataset()`
   - `load()` with smart return
   - File path vs parsed object loading

3. **Datastore API (Advanced)**
   - `datastore_search()` with filters
   - `datastore_info()` for metadata
   - `datastore_search_sql()` for custom queries
   - `get_datastore_resources()` discovery

4. **Smart Return File Types**
   - All 15 supported formats (CSV, JSON, Excel, GeoJSON, etc.)
   - Automatic format detection
   - Real examples with actual files

5. **Error Handling**
   - Non-existent datasets
   - Missing files
   - Cache status checking

6. **Performance Tips**
   - Caching strategies
   - Datastore vs file download
   - Best practices

## 💡 Key Features Demonstrated

1. **Smart Data Loading** - Automatic file format detection and parsing
2. **Caching** - Efficient file management and reuse
3. **Search** - Find relevant datasets by keywords
4. **Error Handling** - Robust error handling for production use
5. **Data Analysis** - Basic pandas operations on loaded data
6. **Real-time Data** - Datastore API for live data access
7. **Advanced Queries** - SQL support for complex data operations

## 🔧 Customization

You can modify these examples to:
- Work with specific datasets you're interested in
- Add your own data analysis workflows
- Integrate with other data science tools
- Build automated data pipelines

## 📚 Learn More

- **Package Documentation**: See the main README.md
- **API Reference**: Check the source code in `toronto_open_data/`
- **Toronto Open Data Portal**: https://open.toronto.ca/

## 🐛 Troubleshooting

If you encounter issues:
1. Check your internet connection
2. Verify the package is installed correctly
3. Check the Toronto Open Data portal status
4. Review error messages for specific issues

## 🤝 Contributing

Feel free to:
- Add new examples
- Improve existing examples
- Report issues
- Suggest new features

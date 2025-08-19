# Toronto Open Data Package - Examples Summary

This document provides an overview of all available example scripts and what they demonstrate.

## 📁 Available Examples

### 1. **`comprehensive_features.py`** ⭐ **START HERE**
**Purpose**: Complete demonstration of ALL functionality mentioned in the README
**What it shows**:
- ✅ Basic dataset operations (list, search, get info)
- ✅ Download and load functionality with smart return
- ✅ **Datastore API** - Real-time data access, filtering, SQL queries
- ✅ **Smart Return** - All 15 supported file formats
- ✅ Error handling and edge cases
- ✅ Performance tips and best practices
- ✅ Cache management

**Best for**: Understanding the complete package capabilities

### 2. **`usage_examples.py`**
**Purpose**: Comprehensive examples showing all package features
**What it shows**:
- ✅ Basic usage patterns
- ✅ Data operations
- ✅ Advanced features
- ✅ Error handling
- ✅ Performance optimization

**Best for**: Learning specific use cases and patterns

### 3. **`simple_examples.py`**
**Purpose**: Basic examples for quick start
**What it shows**:
- ✅ Package initialization
- ✅ Basic dataset operations
- ✅ Simple data loading
- ✅ Error handling basics

**Best for**: Getting started quickly

## 🚀 Quick Start Guide

### Prerequisites
```bash
# Install the package
pip install toronto-open-data

# Or for development
pip install -e .
```

### Run Examples
```bash
cd examples

# Start with complete feature coverage
python comprehensive_features.py

# Then explore specific areas
python simple_examples.py
python usage_examples.py
```

## 📊 What Each Example Demonstrates

### Basic Dataset Operations
- `list_all_datasets()` - Get all available datasets
- `search_datasets(query)` - Find datasets by keyword
- `search_resources_by_name(name)` - Get specific dataset
- `get_dataset_info(name)` - Get detailed metadata

### Data Operations
- `download_dataset(name)` - Download files locally
- `load(name, filename)` - Load data with smart return
- `get_available_files(name)` - List downloadable files
- `is_file_cached(name, filename)` - Check cache status

### Advanced Features (Datastore API)
- `datastore_search()` - Real-time data with filters
- `datastore_info()` - Field metadata and descriptions
- `datastore_search_sql()` - Custom SQL queries
- `get_datastore_resources()` - Find datastore-enabled resources

### Smart Return File Types
The package automatically handles these formats:
- **Data**: CSV, JSON, Excel (XLSX, XLSM)
- **Documents**: PDF, DOCX, TXT
- **Geographic**: GeoJSON, KML, SHP, GPKG
- **Other**: XML, XSD, JPEG, SAV

## 💡 Key Learning Points

### 1. **Smart Return vs File Paths**
```python
# Get file path only
file_path = tod.load('dataset', 'file.csv', smart_return=False)

# Get parsed data automatically
data = tod.load('dataset', 'file.csv', smart_return=True)
```

### 2. **Datastore vs File Download**
```python
# Real-time, filtered data
data = tod.datastore_search('resource-id', filters={'status': 'active'})

# Static file download
data = tod.load('dataset', 'file.csv', smart_return=True)
```

### 3. **Error Handling**
```python
try:
    data = tod.load('dataset', 'file.csv')
except Exception as e:
    print(f"Error: {e}")
```

### 4. **Performance Optimization**
```python
# Use caching
tod.download_dataset('dataset', overwrite=False)

# Use datastore for large datasets
data = tod.datastore_search('resource-id', limit=100)
```

## 🔧 Customization Examples

### Working with Specific Datasets
```python
# Find transportation data
transport_datasets = tod.search_datasets('transportation')

# Get health indicators
health_data = tod.load('toronto-population-health-status-indicators', 'data.csv')
```

### Building Data Pipelines
```python
# Download multiple datasets
datasets = ['dataset1', 'dataset2', 'dataset3']
for dataset in datasets:
    files = tod.download_dataset(dataset)
    data = tod.load(dataset, files[0], smart_return=True)
    # Process data...
```

### Real-time Monitoring
```python
# Check for updates
info = tod.datastore_info('resource-id')
last_update = info.get('last_updated')

# Get latest data
data = tod.datastore_search('resource-id', limit=10)
```

## 🐛 Troubleshooting

### Common Issues
1. **Network errors**: Check internet connection
2. **File not found**: Verify dataset and filename
3. **Import errors**: Ensure package is installed correctly
4. **Memory issues**: Use datastore API for large datasets

### Debug Tips
```python
# Check what's available
datasets = tod.list_all_datasets()
files = tod.get_available_files('dataset-name')

# Test with simple operations first
try:
    tod.search_datasets('test')
except Exception as e:
    print(f"Basic operation failed: {e}")
```

## 📚 Next Steps

After running the examples:

1. **Explore the API**: Try different search terms and datasets
2. **Build workflows**: Combine multiple operations
3. **Integrate with tools**: Use with pandas, matplotlib, etc.
4. **Check documentation**: See the main README for more details
5. **Join community**: Report issues, suggest features

## 🎯 Example Use Cases

### Data Analysis
- Download CSV files and analyze with pandas
- Use datastore API for real-time insights
- Build automated reporting systems

### Research
- Access historical data
- Monitor real-time updates
- Combine multiple data sources

### Applications
- Build dashboards
- Create data pipelines
- Develop monitoring tools

---

**Start with `comprehensive_features.py` to see everything the package can do!**

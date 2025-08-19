# TorontoOpenData Python Package

## Overview

The `TorontoOpenData` package provides a Python interface to interact with the Toronto Open Data portal. It allows users to list, search, and download datasets, as well as load specific resources.

## Installation

To install the package, run:

```bash
pip install toronto-open-data
```

### Development Installation

For development and contributing:

```bash
git clone https://github.com/alexwolson/toronto-open-data.git
cd toronto-open-data
pip install -e ".[dev]"
make pre-commit  # Install pre-commit hooks
```

## Dependencies

- `pandas`
- `requests`
- `tqdm`
- `ckanapi`

## Usage

### Initialization

Initialize the `TorontoOpenData` class:

```python
from toronto_open_data import TorontoOpenData

tod = TorontoOpenData()
```

### List All Datasets

List all available datasets:

```python
datasets = tod.list_all_datasets()
```

### Search Datasets

Search datasets by keyword:

```python
search_results = tod.search_datasets('parks')
```

### Download Dataset

Download a specific dataset:

```python
tod.download_dataset('dataset_name')
```

### Load Dataset

Load a specific file from a dataset:

```python
file_path = tod.load('dataset_name', 'file_name.csv', smart_return=False)
```

Load a specific file, returning an object if supported (default behaviour):

```python
file_object = tod.load('dataset_name', 'file_name.csv', smart_return=True)
```

### Using the Datastore API (New!)

For datasets that support CKAN's datastore, you can query data directly without downloading files:

#### Basic Datastore Search

```python
# Get type-enforced data directly from the datastore
data = tod.datastore_search('resource-id-here', limit=100)
print(data.dtypes)  # Shows proper data types (dates, numbers, etc.)
```

#### Filtered Search

```python
# Search with filters and sorting
filtered_data = tod.datastore_search(
    'resource-id-here',
    filters={'status': 'active', 'year': 2023},
    sort='date_created desc',
    limit=50
)
```

#### Get Resource Metadata

```python
# Get field information and descriptions
info = tod.datastore_info('resource-id-here')
for field in info['fields']:
    print(f"{field['id']}: {field.get('type')} - {field.get('info', {}).get('label', 'No description')}")
```

#### Custom SQL Queries

```python
# Advanced querying with SQL
data = tod.datastore_search_sql('''
    SELECT category, COUNT(*) as count, AVG(value) as avg_value
    FROM "resource-id-here"
    WHERE status = 'active'
    GROUP BY category
    ORDER BY count DESC
    LIMIT 10
''')
```

#### Find Datastore Resources

```python
# Check which resources support datastore
datastore_resources = tod.get_datastore_resources('dataset-name')
for resource in datastore_resources:
    print(f"Datastore resource: {resource['name']} (ID: {resource['id']})")
```

### Datastore vs File Download

| Feature | File Download (`load()`) | Datastore API |
|---------|-------------------------|---------------|
| Data freshness | Static files | Real-time data |
| Type enforcement | Basic pandas inference | CKAN-defined types |
| Filtering | Client-side (after download) | Server-side |
| Metadata | Limited | Rich field descriptions |
| Query flexibility | None | Full SQL support |
| Network usage | Downloads entire file | Only requested data |

## Methods

### Basic Dataset Operations
- `list_all_datasets(as_frame=True)`: List all datasets.
- `search_datasets(query, as_frame=True)`: Search datasets by keyword.
- `search_resources_by_name(name, as_frame=True)`: Get dataset by name.
- `download_dataset(name, file_path='./cache/', overwrite=False)`: Download resource.
- `load(name, filename, file_path='./cache/', reload=False, smart_return=True)`: Load a file from the dataset.

### Datastore API Methods (New!)
- `datastore_search(resource_id, filters=None, q=None, limit=100, offset=0, fields=None, sort=None, as_frame=True)`: Search datastore records with type-enforced results and filtering.
- `datastore_info(resource_id)`: Get metadata about datastore resource fields, types, and descriptions.
- `datastore_search_sql(sql, as_frame=True)`: Execute SQL queries on datastore resources.
- `get_datastore_resources(name, as_frame=True)`: Get only datastore-enabled resources for a dataset.

## Smart Return File Types

The package supports smart return for the following file types:

- csv
- docx
- gpkg
- geojson
- jpeg
- json
- kml
- pdf
- sav
- shp
- txt
- xlsm
- xlsx
- xml
- xsd

## Development

### Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run linting checks
make lint
```

### Code Quality

This project uses several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pre-commit**: Automated checks

### PyPI Publishing

The package is automatically published to PyPI when you create a new release on GitHub:

1. Update the version in `pyproject.toml`
2. Commit and push your changes
3. Create a new release on GitHub (this triggers the publishing workflow)
4. The workflow runs tests and publishes automatically using Trusted Publishing

For detailed instructions, see [docs/PYPI_PUBLISHING.md](docs/PYPI_PUBLISHING.md).

### Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

MIT License

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.

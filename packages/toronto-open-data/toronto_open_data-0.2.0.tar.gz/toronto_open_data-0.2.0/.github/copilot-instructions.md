# Toronto Open Data Python Package

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Dependencies and Installation
- Install dependencies manually (package installation via pip has configuration issues):
  - `pip3 install pandas ckanapi tqdm requests`
- DO NOT attempt `pip install -e .` -- it fails due to hatchling build configuration issues with package structure
- Required Python version: >= 3.7 (tested with Python 3.12.3)

### Basic Validation
- Test all modules import correctly:
  - `python3 -c "import core; import api; import loaders; import cache; import config; print('All modules import successfully')"`
- Test basic functionality (will fail with network errors in sandboxed environments):
  - `python3 -c "import core; tod = core.TorontoOpenData(); print('Package initializes:', type(tod))"`
- Validate Python syntax for all files:
  - `python3 -m py_compile *.py && echo 'All Python files compile successfully'`

### Development Workflow
- Work directly with Python files in the repository root
- No build system required - all modules can be imported directly
- NEVER CANCEL any network operations - API calls may take 30+ seconds to timeout in restricted environments
- Use timeout of 120+ seconds for any commands that involve network operations

## Repository Structure

### Core Files
- `core.py` - Main TorontoOpenData class with public API
- `api.py` - CKAN API interaction layer (handles Toronto Open Data portal)
- `cache.py` - File download and caching operations
- `loaders.py` - File type-specific loaders (CSV, JSON, XML, etc.)
- `config.py` - Configuration settings and supported file types
- `__init__.py` - Package initialization and version info

### Configuration Files
- `pyproject.toml` - Package metadata (has hatchling configuration issues)
- `README.md` - Package documentation and usage examples
- `.gitignore` - Includes Python, JetBrains, and cache directory exclusions

## Key Features and Capabilities

### Supported File Types for Smart Loading
csv, docx, gpkg, geojson, jpeg, json, kml, pdf, sav, shp, txt, xlsm, xlsx, xml, xsd

### Main API Methods
- `list_all_datasets()` - List all available datasets
- `search_datasets(query)` - Search datasets by keyword
- `download_dataset(name)` - Download all files for a dataset
- `load(name, filename)` - Load specific file from dataset (supports smart return)
- `get_available_files(name)` - List files available in a dataset

## Testing and Validation

### No Automated Testing
- No test framework configured (no pytest, unittest, or other testing tools)
- No linting tools configured (no pylint, flake8, black, or mypy)
- No CI/CD pipeline configured (no .github/workflows)

### Manual Validation Scenarios
After making changes, ALWAYS run these validation scenarios:

1. **Basic Import Test**:
   ```bash
   python3 -c "import core; import api; import loaders; import cache; import config; print('SUCCESS: All modules import')"
   ```

2. **Package Initialization Test**:
   ```bash
   python3 -c "from core import TorontoOpenData; tod = TorontoOpenData(); print('SUCCESS: Package initializes correctly')"
   ```

3. **Configuration Test**:
   ```bash
   python3 -c "from config import config; print('Supported file types:', len(config.SMART_RETURN_FILETYPES)); print('File loaders:', len(config.FILE_TYPE_LOADERS))"
   ```

4. **File Loader Test**:
   ```bash
   python3 -c "from loaders import loader_factory; print('Loaders available:', ['csv', 'json', 'txt'])"
   ```

### Network-Dependent Functionality
- API calls to Toronto Open Data portal will FAIL in sandboxed environments
- Expected error: `NameResolutionError` or `ConnectionError` for hostname `ckan0.cf.opendata.inter.prod-toronto.ca`
- This is NORMAL and expected behavior in restricted network environments
- Do NOT attempt to fix network connectivity issues

## Common Development Tasks

### Adding New File Type Support
1. Add file extension to `config.py` SMART_RETURN_FILETYPES list
2. Add loader method mapping in `config.py` FILE_TYPE_LOADERS dict
3. Implement `_load_[filetype]` method in `loaders.py` FileLoaderFactory class
4. Test with validation scenarios above

### Modifying API Endpoints
1. Update `config.py` API_BASE_URL if needed
2. Modify methods in `api.py` TorontoOpenDataAPI class
3. Ensure error handling for network failures
4. Test with basic import and initialization scenarios

### Cache Behavior Changes
1. Modify `cache.py` FileCache class methods
2. Update default cache path in `config.py` if needed
3. Test file path generation with `get_file_path()` method
4. Validate with initialization test scenario

## Known Limitations and Workarounds

### Build System Issues
- `pip install -e .` FAILS due to hatchling configuration
- Package structure does not match expected hatchling conventions
- WORKAROUND: Install dependencies manually with `pip3 install pandas ckanapi tqdm requests`

### No Testing Infrastructure
- No automated tests exist
- WORKAROUND: Use manual validation scenarios listed above
- Always run ALL validation scenarios after making changes

### Network Dependencies
- Package requires internet access to function fully
- API calls will fail in sandboxed/restricted environments
- WORKAROUND: Focus testing on import/initialization scenarios, not live API calls

### Development Environment
- No linting or code formatting tools configured
- WORKAROUND: Use manual Python syntax validation with `python3 -m py_compile *.py`

## Performance Expectations

### Command Timing
- Dependency installation: 30-60 seconds
- Module import tests: < 5 seconds
- Python compilation checks: < 10 seconds
- Network operations: 30+ seconds timeout (will fail in restricted environments)
- NEVER CANCEL: Always wait for network operations to timeout naturally

## Example Usage Patterns

### Basic Dataset Access
```python
from core import TorontoOpenData

# Initialize (works without API key)
tod = TorontoOpenData()

# List datasets (requires network)
datasets = tod.list_all_datasets()

# Search datasets (requires network)
results = tod.search_datasets('parks')

# Download dataset (requires network)
tod.download_dataset('dataset-name')

# Load specific file (requires network for download)
data = tod.load('dataset-name', 'file.csv')
```

### Error Handling Pattern
```python
try:
    tod = TorontoOpenData()
    # Network operations will fail in sandboxed environments
    datasets = tod.list_all_datasets()
except (ConnectionError, NameResolutionError) as e:
    print(f"Expected network error in sandboxed environment: {e}")
```

Always validate changes thoroughly using the manual validation scenarios before considering work complete.

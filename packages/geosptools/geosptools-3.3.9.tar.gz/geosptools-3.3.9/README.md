# geosptools

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/geosptools.svg)](https://pypi.org/project/geosptools/)

**geosptools** is a specialised Python toolkit designed for geospatial raster data processing and analysis. Built on top of GDAL (Geospatial Data Abstraction Library), it provides robust tools for converting NetCDF files to raster formats and merging independent raster datasets. The package emphasises reliable raster processing workflows with comprehensive error handling and defensive programming practices.

## Features

- **NetCDF to Raster Conversion**:
  - Convert NetCDF files to various raster formats (GeoTIFF, JPEG, PNG, etc.)
  - Configurable resolution and coordinate reference systems
  - Batch processing with nested list support
  - Comprehensive error handling and validation

- **Raster Merging Operations**:
  - Merge independent raster files from multiple regions
  - Synchronised processing of multi-region datasets
  - Flexible output format configuration
  - NoData value handling and projection preservation

- **GDAL Integration**:
  - Professional GDAL-based processing workflows
  - Support for multiple raster formats and drivers
  - Efficient memory management and dataset handling
  - Robust error reporting and debugging capabilities

- **Defensive Programming**:
  - Automatic nested list flattening for file inputs
  - Comprehensive parameter validation
  - Enhanced error handling with detailed diagnostics
  - Type safety with modern Python annotations

## Installation

### Prerequisites

Before installing, please ensure the following dependencies are available on your system:

- **External Tools** (required for full functionality):
  - GDAL Library (system-level installation required)
  - Database server (if using database features)

- **GDAL Library** (system-level installation required):

  ```bash
  # Ubuntu/Debian
  sudo apt-get update
  sudo apt-get install gdal-bin libgdal-dev

  # macOS (using Homebrew)
  brew install gdal

  # CentOS/RHEL
  sudo yum install gdal gdal-devel
  ```

- **Required Python Libraries**:

  ```bash
  pip install gdal numpy
  ```

  Or via Anaconda (recommended for GDAL compatibility):

  ```bash
  conda install -c conda-forge gdal numpy
  ```

- **Internal Package Dependencies**:

  ```bash
  pip install paramlib
  pip install pygenutils                    # Core functionality
  pip install pygenutils[arrow]             # With arrow support (optional)
  ```

### For regular users (from PyPI)

```bash
pip install geosptools
```

### For contributors/developers (with latest Git versions)

```bash
# Install with development dependencies (includes latest Git versions)
pip install -e .[dev]

# Alternative: Use requirements-dev.txt for explicit Git dependencies
pip install -r requirements-dev.txt
pip install -e .
```

**Benefits of the new approach:**

- **Regular users**: Simple `pip install geosptools` with all dependencies included
- **Developers**: Access to latest Git versions for development and testing
- **PyPI compatibility**: All packages can be published without Git dependency issues

**If you encounter import errors:**

1. **For PyPI users**: The package should install all dependencies automatically. If you get import errors, try:

   ```bash
   pip install --upgrade geosptools
   ```

2. **For developers**: Make sure you've installed the development dependencies:

   ```bash
   pip install -e .[dev]
   ```

3. **Common issues**:
   - **Missing GDAL**: Ensure GDAL is properly installed at the system level
   - **Missing dependencies**: For regular users, all dependencies are included. For developers, use `pip install -e .[dev]`
   - **Python version**: Ensure you're using Python 3.10 or higher

### Verify Installation

To verify that your installation is working correctly:

```python
try:
    import geosptools
    from filewise.file_operations.path_utils import find_files
    from pygenutils.arrays_and_lists.data_manipulation import flatten_list
    from paramlib.global_parameters import COMMON_DELIMITER_LIST
    
    print("✅ All imports successful!")
    print(f"✅ geosptools version: {geosptools.__version__}")
    print("✅ Installation is working correctly.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 For regular users: pip install geosptools")
    print("💡 For developers: pip install -e .[dev]")
```

## Usage

### Basic Example - NetCDF to Raster Conversion

```python
from geosptools.raster_tools import nc2raster

# Convert a single NetCDF file to GeoTIFF
nc2raster(
    nc_file_list="temperature_data.nc",
    output_file_format="GTiff",
    raster_extension="tif",
    raster_resolution=300,
    nodata_value=-9999,
    crs="EPSG:4326"
)

# Batch convert multiple NetCDF files
nc_files = ["temp_2020.nc", "temp_2021.nc", "temp_2022.nc"]
nc2raster(
    nc_file_list=nc_files,
    output_file_format="GTiff",
    raster_extension="tif",
    raster_resolution=500
)
```

### Advanced Example - Nested List Processing

```python
from geosptools.raster_tools import nc2raster

# Handle complex nested file structures automatically
nested_files = [
    ["region1_temp.nc", "region1_precip.nc"],
    ["region2_temp.nc", "region2_precip.nc"],
    "global_summary.nc"
]

# Defensive programming automatically flattens nested lists
nc2raster(
    nc_file_list=nested_files,
    output_file_format="GTiff",
    raster_extension="tif",
    raster_resolution=1000,
    nodata_value=-32768,
    crs="EPSG:3857"  # Web Mercator projection
)
```

### Multi-Region Raster Merging

```python
from geosptools.raster_tools import merge_independent_rasters

# Define raster files for different regions
raster_data = {
    "north_region": [
        "north_temp_jan.tif",
        "north_temp_feb.tif",
        "north_temp_mar.tif"
    ],
    "south_region": [
        "south_temp_jan.tif",
        "south_temp_feb.tif",
        "south_temp_mar.tif"
    ],
    "central_region": [
        "central_temp_jan.tif",
        "central_temp_feb.tif",
        "central_temp_mar.tif"
    ]
}

# Merge corresponding files from each region
merge_independent_rasters(
    raster_files_dict=raster_data,
    output_file_format="GTiff",
    joint_region_name="combined",
    output_file_name_ext="tif",
    nodata_value=-9999
)
```

### Climate Data Processing Example

```python
from geosptools.raster_tools import nc2raster, merge_independent_rasters

# Step 1: Convert climate NetCDF files to rasters
climate_files = [
    "ERA5_temperature_2023.nc",
    "ERA5_precipitation_2023.nc",
    "ERA5_humidity_2023.nc"
]

nc2raster(
    nc_file_list=climate_files,
    output_file_format="GTiff",
    raster_extension="tif",
    raster_resolution=1000,
    crs="EPSG:4326"
)

# Step 2: Merge regional climate data
regional_data = {
    "europe": ["EUR_temp_2023.tif", "EUR_precip_2023.tif"],
    "asia": ["ASIA_temp_2023.tif", "ASIA_precip_2023.tif"],
    "africa": ["AFR_temp_2023.tif", "AFR_precip_2023.tif"]
}

merge_independent_rasters(
    raster_files_dict=regional_data,
    output_file_format="GTiff",
    joint_region_name="global",
    output_file_name_ext="tif"
)
```

## Project Structure

The package is organised as a focused raster processing toolkit:

```text
geosptools/
├── raster_tools.py              # Core raster processing functions
├── __init__.py                  # Package initialisation
├── CHANGELOG.md                 # Version history and changes
└── README.md                    # Package documentation
```

## Key Functions

### `nc2raster()`

**Purpose**: Convert NetCDF files to various raster formats using GDAL

**Key Features**:

- Supports single files, lists, and nested lists of NetCDF files
- Configurable output formats (GeoTIFF, JPEG, PNG, etc.)
- Customisable resolution and coordinate reference systems
- NoData value handling and projection settings
- Comprehensive error handling and progress reporting

**Parameters**:

- `nc_file_list`: NetCDF file(s) to convert (supports nested lists)
- `output_file_format`: GDAL driver name (e.g., "GTiff", "JPEG")
- `raster_extension`: Output file extension
- `raster_resolution`: Resolution for output rasters
- `nodata_value`: NoData value for raster files (optional)
- `crs`: Coordinate reference system (default: "EPSG:4326")

### `merge_independent_rasters()`

**Purpose**: Merge corresponding raster files from multiple regions into unified outputs

**Key Features**:

- Synchronised processing of multi-region datasets
- Automatic validation of input file consistency
- Preserves geospatial metadata and projections
- Flexible output naming and format configuration
- Robust error handling for GDAL operations

**Parameters**:

- `raster_files_dict`: Dictionary mapping region names to file lists
- `output_file_format`: GDAL driver for output format
- `joint_region_name`: Name for combined region in output files
- `output_file_name_ext`: Extension for output files
- `nodata_value`: NoData value handling (optional)

## Advanced Features

### Defensive Programming

- **Nested List Support**: Automatically flattens complex nested file structures
- **Parameter Validation**: Comprehensive input validation with detailed error messages
- **Type Safety**: Modern Python type annotations (PEP-604) for better IDE support
- **Error Handling**: Detailed RuntimeError and ValueError reporting for debugging

### GDAL Integration

- **Professional Workflows**: Proper dataset opening, processing, and closing
- **Memory Management**: Efficient handling of large raster datasets
- **Format Support**: Wide range of raster formats through GDAL drivers
- **Metadata Preservation**: Maintains geospatial information during processing

### Performance Optimisation

- **Batch Processing**: Efficient handling of multiple files
- **Progress Reporting**: Real-time feedback during long operations
- **Resource Management**: Proper cleanup of GDAL datasets and memory

## Supported Formats

### Input Formats

- **NetCDF** (.nc) - Primary input format for conversion
- **Various raster formats** - For merging operations (GeoTIFF, JPEG, PNG, etc.)

### Output Formats

- **GeoTIFF** (.tif) - Recommended for geospatial data
- **JPEG** (.jpg) - For visualisation and web applications
- **PNG** (.png) - For high-quality images with transparency
- **And many others** - Any format supported by GDAL drivers

## Version Information

Current version: **3.3.0**

### Recent Updates (v3.3.0)

- Enhanced defensive programming with nested list support
- Modern PEP-604 type annotations throughout
- Improved error handling and documentation
- Variable name standardisation for consistency

For detailed version history, see [CHANGELOG.md](CHANGELOG.md).

## Error Handling

The package provides comprehensive error handling:

- **RuntimeError**: For GDAL operation failures (file opening, driver issues, raster creation)
- **ValueError**: For parameter validation and input consistency checks
- **TypeError**: For incorrect parameter types

Example error scenarios:

```python
# This will raise ValueError if regions have different numbers of files
raster_data = {
    "region1": ["file1.tif", "file2.tif"],
    "region2": ["file1.tif"]  # Inconsistent length
}
merge_independent_rasters(raster_data, "GTiff", "combined", "tif")
```

## System Requirements

- **Python**: 3.8 or higher
- **GDAL**: System-level installation required (>= 2.0)
- **Operating System**: Linux, macOS, Windows (with proper GDAL setup)
- **Memory**: Sufficient RAM for processing large raster datasets

## Dependencies

### Core Dependencies

- **GDAL Python bindings**: Essential for all raster operations
- **NumPy**: For efficient array operations (indirect dependency)

### Internal Dependencies

- **pygenutils**: Utility functions and data manipulation
- **paramlib**: Parameter and configuration management

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Guidelines

- Follow existing code structure and GDAL best practices
- Add comprehensive docstrings with parameter descriptions
- Include error handling for all GDAL operations
- Test with various raster formats and coordinate systems
- Update changelog for significant changes

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **GDAL Development Team** for the foundational geospatial data processing library
- **OSGeo Community** for open-source geospatial tools and standards
- **Python Geospatial Community** for ecosystem development and best practices
- **Climate and Earth Science Communities** for driving requirements and use cases

## Contact

For any questions or suggestions, please open an issue on GitHub or contact the maintainers.

## Troubleshooting

### Common Issues

1. **GDAL Import Error**:

   ```bash
   # Ensure GDAL is properly installed
   conda install -c conda-forge gdal
   # Or check system installation
   gdalinfo --version
   ```

2. **Coordinate Reference System Issues**:
   - Verify CRS string format (e.g., "EPSG:4326")
   - Check if target CRS is supported by GDAL

3. **Memory Issues with Large Files**:
   - Process files in smaller batches
   - Monitor system memory usage during operations
   - Consider using GDAL virtual file systems for very large datasets

### Getting Help

- Check the [CHANGELOG.md](CHANGELOG.md) for recent updates
- Review function docstrings for parameter details
- Open an issue on GitHub for bugs or feature requests

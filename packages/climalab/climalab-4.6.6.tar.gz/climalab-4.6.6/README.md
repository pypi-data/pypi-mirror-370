# climalab

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/climalab.svg)](https://pypi.org/project/climalab/)

**climalab** is a Python toolkit designed to facilitate climate data analysis and manipulation, including tools for data extraction, processing, and visualisation. It leverages external tools and standards like CDO (Climate Data Operators), NCO (NetCDF operators), and CDS (Copernicus Climate Data Store) to streamline workflows for climate-related research.

## Features

- **Meteorological Tools**:
  - Comprehensive handling of meteorological variables and data
  - Unit conversions (temperature, wind speed, angles)
  - Wind direction calculations using meteorological criteria
  - Dewpoint temperature and relative humidity calculations using Magnus' formula
  - Weather software input file generation (EnergyPlus EPW format)

- **NetCDF Tools**:
  - Advanced CDO operations for netCDF file manipulation (merge, remap, statistical operations)
  - NCO tools for efficient data processing and variable modifications
  - Faulty file detection and reporting
  - Basic information extraction from netCDF files (lat/lon bounds, time information)
  - Time coordinate manipulation and correction tools

- **Supplementary Analysis Tools**:
  - Visualisation tools for maps and basic plots
  - Bias correction methods (parametric and non-parametric quantile mapping)
  - Statistical analysis and evaluation tools
  - Auxiliary functions for data processing and plotting

- **Data Analysis Project Templates**:
  - Sample project structure with configuration-based approach
  - Automated data download scripts for CORDEX, E-OBS, ERA5, and ERA5-Land datasets
  - YAML configuration files for different climate datasets
  - Standardised directory organisation for climate data projects

## Installation

### Prerequisites

Before installing, please ensure the following dependencies are available on your system:

- **External Tools** (required for full functionality):
  - CDO (Climate Data Operators) - for netCDF processing
  - NCO (NetCDF Operators) - for netCDF manipulation

### For regular users (from PyPI)

```bash
pip install climalab
```

**Note:** PyPI installation includes all core dependencies automatically. The interdependent packages (`filewise`, `pygenutils`, `paramlib`) are available as separate packages on PyPI.

### For contributors/developers (with interdependent packages)

If you're planning to contribute to the project or work with the source code, follow these setup instructions:

#### Quick Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/EusDancerDev/climalab.git
cd climalab

# Install all dependencies including Git packages
pip install -r requirements.txt

# Install in editable mode
pip install -e .
```

**Note**: The `-e` flag installs the package in "editable" mode, meaning changes to the source code are immediately reflected without reinstalling.

This will install all dependencies, including the required `filewise`, `pygenutils`, and `paramlib` packages directly from their GitHub repositories.

#### Manual Setup (Alternative)

If you prefer to set up dependencies manually:

```bash
# Clone the repository
git clone https://github.com/EusDancerDev/climalab.git
cd climalab

# Install with development dependencies (includes latest Git versions)
pip install -e .[dev]

# Alternative: Use requirements-dev.txt for explicit Git dependencies
pip install -r requirements-dev.txt
pip install -e .
```

This approach gives you the latest development versions of all interdependent packages for testing and development.

### Troubleshooting

If you encounter import errors after cloning:

1. **For regular users**: Run `pip install climalab` (all dependencies included)
2. **For developers**: Run `pip install -e .[dev]` to include development dependencies
3. **Verify Python environment**: Make sure you're using a compatible Python version (3.10+)

### Verify Installation

To verify that your installation is working correctly, you can run this quick test:

```python
# Test script to verify installation
try:
    import climalab
    from filewise.general.introspection_utils import get_type_str
    from pygenutils.strings.text_formatters import format_string
    from paramlib.global_parameters import BASIC_ARITHMETIC_OPERATORS
    
    print("✅ All imports successful!")
    print(f"✅ climalab version: {climalab.__version__}")
    print("✅ Installation is working correctly.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 For regular users: pip install climalab")
    print("💡 For developers: pip install -e .[dev]")
```

### Implementation Notes

This project implements a **dual-approach dependency management** system:

- **Production Dependencies**: Version-constrained dependencies for PyPI compatibility
- **Development Dependencies**: Git-based dependencies for latest development versions
- **Installation Methods**:
  - **Regular users**: Simple `pip install climalab` with all dependencies included
  - **Developers**: `pip install -e .[dev]` for latest Git versions and development tools
- **PyPI Compatibility**: All packages can be published without Git dependency issues
- **Development Flexibility**: Contributors get access to latest versions for testing and development

## Usage

### Basic Example - Meteorological Variables

```python
from climalab.meteorological import variables
import numpy as np

# Convert temperature from Kelvin to Celsius using angle converter for degrees
temp_kelvin = np.array([273.15, 283.15, 293.15])
# Convert wind speeds
wind_mps = 10.0
wind_kph = variables.ws_unit_converter(wind_mps, "mps_to_kph")
print(f"Wind speed: {wind_mps} m/s = {wind_kph} km/h")

# Calculate dewpoint temperature
temperature = np.array([20, 25, 30])  # °C
relative_humidity = np.array([60, 70, 80])  # %
dewpoint = variables.dewpoint_temperature(temperature, relative_humidity)
print(f"Dewpoint temperatures: {dewpoint}")
```

### Advanced Example - NetCDF Processing

```python
from climalab.netcdf_tools import cdo_tools
from climalab.netcdf_tools.detect_faulty import scan_ncfiles

# Merge multiple NetCDF files with time steps
file_list = ['temp_2000.nc', 'temp_2001.nc', 'temp_2002.nc']
cdo_tools.cdo_mergetime(
    file_list=file_list,
    variable='temperature',
    freq='daily',
    model='ERA5',
    experiment='reanalysis',
    calc_proc='mergetime',
    period='2000-2002',
    region='global',
    ext='nc'
)

# Select specific years from a dataset
cdo_tools.cdo_selyear(
    file_list=['climate_data_full.nc'],
    selyear_str='2000/2010',
    freq='monthly',
    model='CORDEX',
    experiment='historical',
    calc_proc='subset',
    region='europe',
    ext='nc'
)

# Detect faulty NetCDF files
scan_ncfiles('/path/to/netcdf/files')
```

### Bias Correction Example

```python
from climalab.supplementary_tools import auxiliary_functions
import numpy as np

# Generate sample data
obs_data = np.random.normal(25, 3, 1000)  # observed temperature data
sim_data = np.random.normal(27, 4, 1000)  # simulated temperature data

# Apply bias correction using delta method
obs_mean = np.mean(obs_data)
sim_mean = np.mean(sim_data)
corrected_data = auxiliary_functions.ba_mean(sim_data, sim_mean, obs_mean)

# Apply quantile mapping
corrected_qm = auxiliary_functions.ba_nonparametric_qm(
    sim_data, sim_data, obs_data
)
```

### Data Download Example

```python
# The data_analysis_projects_sample provides ready-to-use scripts
# for downloading climate data with configuration files:

# 1. Configure your dataset in the YAML files (config/)
# 2. Run the download scripts:
from climalab.data_analysis_projects_sample.src.data import download_era5
# download_era5.main()  # Downloads ERA5 data based on configuration
```

## Project Structure

The package is organised into several sub-packages:

```text
climalab/
├── meteorological/
│   ├── variables.py           # Unit conversions, meteorological calculations
│   └── weather_software.py    # EnergyPlus weather file generation
├── netcdf_tools/
│   ├── cdo_tools.py          # CDO operations and wrappers
│   ├── nco_tools.py          # NCO operations and wrappers
│   ├── detect_faulty.py      # NetCDF file integrity checking
│   └── extract_basics.py     # Basic information extraction
├── supplementary_tools/
│   ├── auxiliary_functions.py    # Bias correction and utility functions
│   ├── ba_*.py                   # Individual bias correction methods
│   ├── basic_*.py                # Basic plotting functions
│   ├── comparison_lineplot.py    # Comparison plotting tools
│   ├── temperature_map.py        # Temperature mapping tools
│   └── eval_original.py          # Evaluation and statistics
└── data_analysis_projects_sample/
    ├── config/                   # YAML configuration files
    │   ├── cordex_config.yaml
    │   ├── eobs_config.yaml
    │   ├── era5_config.yaml
    │   └── era5_land_config.yaml
    ├── src/data/                 # Data download scripts
    │   ├── cds_tools.py
    │   ├── download_cordex.py
    │   ├── download_eobs.py
    │   ├── download_era5.py
    │   └── download_era5_land.py
    └── data/                     # Data storage directories
        ├── raw/
        └── processed/
```

## Key Functions

### Meteorological Tools

- `angle_converter()` - Convert between degrees and radians
- `ws_unit_converter()` - Convert wind speeds between m/s and km/h
- `dewpoint_temperature()` - Calculate dewpoint using Magnus' formula
- `relative_humidity()` - Calculate relative humidity from temperature and dewpoint
- `meteorological_wind_direction()` - Calculate wind direction from u/v components

### NetCDF Tools (CDO)

- `cdo_mergetime()` - Merge files with different time steps
- `cdo_selyear()` - Select specific years from datasets
- `cdo_sellonlatbox()` - Extract geographical regions
- `cdo_remap()` - Remap data to different grids
- `cdo_periodic_statistics()` - Calculate temporal statistics

### NetCDF Tools (NCO)

- `modify_variable_units_and_values()` - Modify variable values and units
- `modify_coordinate_values_by_threshold()` - Conditional coordinate modifications
- `modify_coordinate_all_values()` - Apply operations to all coordinate values

### Bias Correction

- `ba_mean()` - Delta (mean bias) correction
- `ba_mean_and_var()` - Mean and variance correction  
- `ba_nonparametric_qm()` - Non-parametric quantile mapping
- `ba_parametric_qm()` - Parametric quantile mapping

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Climate Data Operators (CDO) team
- Copernicus Climate Data Store (CDS)
- NetCDF Operators (NCO) team
- Potsdam Institute for Climate Impact Research (sample bias correction methods)

## Contact

For any questions or suggestions, please open an issue on GitHub or contact the maintainers.

## Version

Current version: 4.5.1

For detailed changelog, see [CHANGELOG.md](CHANGELOG.md).
For versioning information, see [VERSIONING.md](VERSIONING.md).

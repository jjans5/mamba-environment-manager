# Mamba Environment Manager

A comprehensive Python tool for managing mamba/conda environments with automated reinstallation and renaming capabilities.

## Project Structure

```
├── environment_manager.py      # Main environment management tool
├── yaml_analyzer.py           # YAML file analysis and cleanup utility
├── batch_process.py           # Batch processing script
├── README.md                  # This documentation
├── requirements.txt           # Python dependencies
├── tests/                     # All test files
│   ├── test_manager.py       # Core functionality tests
│   ├── test_smart_naming.py  # Naming convention tests
│   └── ...                   # Additional test files
├── utils/                     # Utility and debug scripts
│   ├── demo_new_features.py  # Feature demonstrations
│   ├── debug_*.py           # Debug utilities
│   └── ...                   # Additional utilities
├── docs/                      # Documentation and examples
│   └── environment_manager_demo.ipynb  # Jupyter notebook demo
├── exported_environments/     # YAML exports (auto-created)
└── backup_environments/       # Operation logs (auto-created)
```

## Features

- **Export & Reinstall**: Export broken environments to YAML files and reinstall them
- **Smart Renaming**: Rename environments to lowercase with Python/R version suffixes
- **Verification**: Verify successful installation before cleanup
- **Safe Cleanup**: Remove old environments only after successful reinstall
- **Error Handling**: Comprehensive error handling and graceful recovery
- **Detailed Logging**: All operations logged to file with timestamps
- **Interactive Mode**: User-friendly interface for selective processing
- **Batch Mode**: Automated processing of all environments
- **🆕 YAML Analysis**: Analyze exported files for duplicates and conflicts
- **🆕 Smart Cleanup**: Remove duplicate YAML files intelligently
- **🆕 Jupyter Kernel Recreation**: Automatically update/create Jupyter kernels for environments

## Usage

### Interactive Mode (Recommended)
```bash
python environment_manager.py
```
This mode allows you to:
- View all environments with their current and proposed new names
- **Preview changes** before processing (no modifications made)
- Choose to process all environments or select specific ones
- **🆕 Analyze YAML files** for duplicates and conflicts (Option 4)
- **🆕 Clean up YAML files** with smart duplicate detection (Option 5)
- **🆕 Recreate Jupyter kernels** for Python/R environments (Option 6)
- See real-time progress and results
- Review smart naming decisions and conflict resolutions

### YAML Analysis (Standalone)
```bash
# Analyze YAML files for duplicates and conflicts
python yaml_analyzer.py --analyze

# Clean up duplicate files (keep newest)
python yaml_analyzer.py --cleanup-duplicates keep_newest

# Clean up multiple files per environment (keep latest)
python yaml_analyzer.py --cleanup-env-duplicates

# Remove all YAML files
python yaml_analyzer.py --cleanup-all
```

### Batch Mode (All Environments)
```bash
python batch_process.py
```
Processes all environments automatically after confirmation.

### Test Mode
```bash
python tests/test_manager.py             # Basic functionality test
python tests/test_smart_naming.py        # Test smart naming with real patterns  
python tests/test_package_detection.py   # Test package version detection
python tests/test_new_features.py        # Test new cleanup and kernel features
```
Tests the functionality without making any changes.

## Environment Naming Convention

The tool uses **intelligent naming** that handles existing version patterns gracefully and includes key package versions:

### Smart Cleaning Examples:
- `py_jjans_3.10_scanpy` → `py_jjans_scanpy_py310` ✅ (eliminates duplication)
- `py_jjans_3.7_harmony` → `py_jjans_harmony_py37` ✅ (eliminates duplication)
- `R_jjans_4.2_cistopic` → `r_jjans_cistopic_r42` (cleans and standardizes)
- `neuronchat_r405` → `neuronchat_py310` (detects existing R version, no duplication)
- `scenicplus_v102` → `scenicplus_py311` (removes version suffix)
- `scanpy_analysis` → `scanpy_analysis_scanpy19_py310` (adds detected package version)

### Advanced Features:
1. **Duplication Prevention**: Detects when versions already exist in different formats
2. **Package Version Detection**: Extracts key package versions from YAML exports
3. **Smart Package Mapping**: Recognizes package name variations (harmonypy, harmony, etc.)
4. **Intelligent Cleaning**: Removes redundant version patterns before adding standardized ones

### Naming Rules:
1. **Convert to lowercase**: `MyEnvironment` → `myenvironment`
2. **Clean existing versions**: Removes patterns like `_py3.10`, `_r4.2`, `_v102`
3. **Add package versions**: `_scanpy19`, `_harmonypy00` for key packages
4. **Add standardized language versions**: `_py310`, `_r42` format
5. **Resolve conflicts**: Adds `_v1`, `_v2` suffixes when needed
6. **Preserve meaningful names**: Keeps descriptive parts intact

### Pattern Detection:
The tool automatically detects and handles:
- **Python versions**: `py3.10`, `python3.10`, `_py310`, `py_3.10`, `_3.10`
- **R versions**: `r4.2`, `_r42`, `r_4.2`, `_r_4.2`, `r405`
- **Version suffixes**: `_v1`, `_v102`, `_version2`
- **Package versions**: From both conda and pip dependencies in YAML files

### Package Version Detection:
- Automatically scans exported YAML files for key packages
- Maps environment names to relevant packages (scanpy→scanpy, harmony→harmonypy)
- Includes up to 2 most relevant package versions to avoid overly long names
- Supports both conda (`package=version=build`) and pip (`package==version`) formats

### Conflict Resolution:
- If `myenv_py39` already exists, new environment becomes `myenv_py39_v1`
- Sequential numbering prevents overwrites
- Safe processing ensures no data loss

## Requirements

- Python 3.8+
- mamba or conda installed and available in PATH
- PyYAML
- colorama

## Installation

1. Clone or download this project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the script:
   ```bash
   python environment_manager.py
   ```

## Configuration

Copy `config_template.py` to `config.py` to customize:
- Tool preference (mamba vs conda)
- Naming conventions
- Directory locations
- Verification settings
- Logging configuration

## Logging

All operations are logged to `environment_manager.log` with:
- Timestamps for all operations
- Detailed error messages
- Success confirmations
- Command outputs when relevant

## Safety Features

- **Backup**: Environments are exported before any changes
- **Verification**: New environments are tested before old ones are removed
- **Error Recovery**: Failed operations don't affect other environments
- **User Confirmation**: Interactive prompts for destructive operations
- **Detailed Logging**: Complete audit trail of all operations

## Example Output

```
=== Processing environment: py_jjans_3.10_scanpy ===
Step 1: Exporting environment...
Successfully exported py_jjans_3.10_scanpy to exported_environments/py_jjans_3.10_scanpy_20250827_104758.yml
Cleaned base name: py_jjans_3.10_scanpy -> py_jjans_scanpy
Detected packages: scanpy=1.9, numpy=1.21
New environment name: py_jjans_scanpy_scanpy19_py310
Step 2: Creating new environment...
Successfully created environment py_jjans_scanpy_scanpy19_py310
Step 3: Verifying new environment...
Environment py_jjans_scanpy_scanpy19_py310 verified successfully
Step 4: Removing old environment...
Successfully removed environment py_jjans_3.10_scanpy
✓ Successfully processed py_jjans_3.10_scanpy -> py_jjans_scanpy_scanpy19_py310
```

## New Features (v2.0)

### YAML Analysis & Smart Cleanup
**Standalone tool**: `yaml_analyzer.py`
- **Duplicate Detection**: Finds files with identical content (ignoring names)
- **Environment Grouping**: Shows multiple exports for the same environment
- **Smart Cleanup Options**:
  ```python
  # Programmatic usage
  from yaml_analyzer import YAMLAnalyzer
  analyzer = YAMLAnalyzer()
  
  # Analyze files
  analysis = analyzer.analyze_yaml_files()
  analyzer.print_analysis_report(analysis)
  
  # Clean up duplicates (keep newest)
  analyzer.cleanup_duplicates(analysis, "keep_newest")
  
  # Clean up environment duplicates (keep latest per environment)
  analyzer.cleanup_by_environment(analysis, keep_latest=True)
  ```

**Key Benefits**:
- **Efficient**: No environment scanning required - analyzes files directly
- **Smart Detection**: Content-based duplicate detection (ignores naming differences)
- **Flexible Cleanup**: Multiple strategies for different use cases
- **Detailed Reports**: Shows file sizes, modification times, dependency counts

### Jupyter Kernel Recreation
Updates/creates Jupyter kernels for environments with Python or R:
```python
# Recreate kernels for all environments
manager.recreate_jupyter_kernels()

# Recreate kernels for specific environments
manager.recreate_jupyter_kernels(['env1', 'env2'])

# Interactive menu: Option 6
```

**Kernel Features:**
- Preserves existing kernel configurations (display name, metadata, etc.)
- Updates only the executable path to match environment location
- Supports both Python (`ipykernel`) and R (`IRkernel`) environments
- Creates kernels in user's local Jupyter directory
- Handles kernel conflicts gracefully

**Kernel Locations:**
- **User kernels**: `~/.local/share/jupyter/kernels/`
- **System kernels**: `/usr/local/share/jupyter/kernels/` (if accessible)
- **macOS**: `~/Library/Jupyter/kernels/`

## Troubleshooting

- **Mamba not found**: The tool automatically falls back to conda
- **Export fails**: Check if the environment is corrupted or has dependency conflicts
- **Import fails**: Review the exported YAML file for invalid dependencies
- **Verification fails**: The new environment may have issues but won't be removed automatically
- **Kernel creation fails**: Check if Jupyter is installed and kernel directories are writable

## Files Created

- `exported_environments/`: YAML exports of original environments
- `backup_environments/`: Installation/removal logs and additional backups
- `environment_manager.log`: Detailed operation log
- `~/.local/share/jupyter/kernels/`: Created Jupyter kernels

# Mamba Environment Manager

A comprehensive Python tool for managing mamba/conda environments with automated backup, cloning, analysis, and debugging capabilities. Now featuring an intuitive, task-oriented interface for efficient environment management.

## 🚀 Quick Start

```bash
# Interactive mode with task-oriented menu
python environment_manager.py

# Batch processing mode
python scripts/batch_process.py

# Environment cloning tool
python utils/environment_cloner.py

# Log analysis and debugging
python utils/simple_log_analyzer.py
```

## 📋 User Interface

The environment manager features a **user-centric workflow** designed around common tasks:

```
Environment Management Options:
1. [BACKUP] Backup environment (preserve original)
2. [CLONE]  Clone environment (backup + rename/recreate)
3. [UNPACK] Unpack conda-pack archive to environment
4. [ANALYZE] Analyze exported YAML files for duplicates
5. [BATCH]  Batch processing (multiple environments)
6. [DEBUG]  Debug and analyze failures
7. [KERNEL] Create Jupyter kernels
8. [DELETE] Delete environments
9. [LIST]   List all environments
10. [CLEAN] Clean up backup files (YAML/conda-pack)
11. [EXIT]  Exit
```

### Key Workflow Improvements
- **⚡ Lightning Fast Startup**: Menu loads instantly, no upfront environment scanning
- **🎯 Task-Oriented**: Choose your intent first, then specify details
- **📦 Flexible Input**: Environment names, paths, or "all" environments
- **🔧 Method Choice**: YAML vs conda-pack for each operation
- **🤖 Smart Naming**: Auto-naming option throughout
- **📊 Batch Operations**: Process multiple environments efficiently
- **🗑️ Safe Deletion**: Multi-confirmation environment deletion with list input
- **🔬 Enhanced Kernels**: Create Jupyter kernels with list input support

## 📁 Project Structure

```
├── environment_manager.py         # Main environment management tool
├── requirements.txt               # Python dependencies
├── README.md                      # This file
│
├── 📁 scripts/                    # Utility scripts
│   ├── batch_process.py           # Batch processing script
│   ├── package_config.py          # Package configuration
│   ├── yaml_analyzer.py           # YAML file analysis utility
│   └── yaml_conflict_solver.py    # YAML conflict resolution
│
├── 📁 utils/                      # Core utilities
│   ├── environment_cloner.py      # Enhanced environment cloning
│   ├── simple_log_analyzer.py     # Log analysis and debugging
│   ├── config_template.py         # Configuration templates
│   └── ...                        # Other utility modules
│
├── 📁 tests/                      # Test suite
│   ├── test_manager.py            # Main manager tests
│   ├── test_enhanced_cloning.py   # Cloning tests
│   ├── test_smart_naming.py       # Naming tests
│   └── ...                        # Other test files
│
├── 📁 demos/                      # Demo scripts
│   ├── demo_enhanced_cloning.py   # Cloning demo
│   ├── demo_environment_deletion.py # Deletion demo
│   ├── demo_kernel_list_input.py  # Kernel creation demo
│   └── ...                        # Other demos
│
├── 📁 documentation/              # Documentation
│   ├── ENHANCED_CLONING_SUMMARY.md
│   ├── ENVIRONMENT_DELETION_SUMMARY.md
│   ├── KERNEL_LIST_INPUT_SUMMARY.md
│   └── ...                        # Other documentation
│
├── 📁 backup_environments/        # YAML backups and logs
├── 📁 exported_environments/      # Exported YAML files
├── 📁 cloned_environments/        # Conda-pack archives
├── 📁 logs/                       # Log files
└── 📁 docs/                       # Additional documentation
├── batch_process.py              # Batch processing script
├── README.md                     # This documentation
├── requirements.txt              # Python dependencies
├── tests/                        # All test files
│   ├── test_manager.py          # Core functionality tests
│   ├── test_smart_naming.py     # Naming convention tests
│   └── ...                      # Additional test files
├── utils/                        # Utility and debug scripts
│   ├── environment_cloner.py    # 🆕 Environment cloning tool
│   ├── simple_log_analyzer.py   # 🆕 Log analysis and debugging
│   ├── demo_new_features.py     # Feature demonstrations
│   ├── debug_*.py              # Debug utilities
│   └── ...                      # Additional utilities
├── docs/                         # Documentation and examples
│   └── environment_manager_demo.ipynb  # Jupyter notebook demo
├── exported_environments/        # YAML exports (auto-created)
├── cloned_environments/          # 🆕 conda-pack archives (auto-created)
└── backup_environments/          # Operation logs (auto-created)
```

## Features

### 🎯 User-Centric Operations

#### 1. 📦 Backup Environment
- **Purpose**: Preserve environments without modification
- **Methods**: YAML export or conda-pack archives
- **Scope**: Single environment, path, or all environments
- **Use Case**: Create portable backups before system changes

#### 2. 🔄 Clone Environment  
- **Purpose**: Create renamed/modified copies of environments
- **Methods**: conda-pack (exact replication) or YAML (cross-platform)
- **Features**: Auto-naming, optional original removal
- **Use Case**: Environment migration, testing, or cleanup

#### 3. ⚡ Batch Processing
- **Backup Multiple**: Process many environments efficiently
- **Clone Multiple**: Batch clone with auto-naming
- **From Files**: Process existing YAML/conda-pack files
- **Use Case**: System-wide environment management

#### 4. 🐛 Debug & Analysis
- **Failure Analysis**: Analyze all failures or specific environments
- **Interactive Debugging**: Step-through debugging sessions
- **Pattern Detection**: Identify common failure patterns
- **Use Case**: Troubleshooting installation and compatibility issues

### Core Environment Management
- **Export & Reinstall**: Export broken environments to YAML files and reinstall them
- **Smart Renaming**: Rename environments to lowercase with Python/R version suffixes
- **Verification**: Verify successful installation before cleanup
- **Safe Cleanup**: Remove old environments only after successful reinstall
- **Error Handling**: Comprehensive error handling and graceful recovery
- **Detailed Logging**: All operations logged to file with timestamps

### 🆕 Advanced Features
- **🆕 Environment Cloning**: Clone environments using conda-pack or YAML export
- **🆕 Failure Debugging**: Detailed analysis of environment failures with context
- **🆕 Log Analysis**: Comprehensive log analysis to identify patterns and issues
- **🆕 Performance Optimized**: Smart menu routing with on-demand environment scanning
- **🆕 YAML Analysis**: Analyze exported files for duplicates and conflicts
- **🆕 Jupyter Kernel Recreation**: Automatically update/create Jupyter kernels for environments
- **🆕 conda-pack Integration**: Create portable environment archives for deployment

## Usage

### Interactive Mode (Recommended)
```bash
python environment_manager.py
```
This mode allows you to:
- View all environments with their current and proposed new names
- **Preview changes** before processing (no modifications made)
- Choose to process all environments or select specific ones
- **🆕 Clone environments** with conda-pack or YAML (Option 7)
- **🆕 Debug specific environment failures** (Option 8)
- **🆕 Analyze all log failures** (Option 9)
- **Analyze YAML files** for duplicates and conflicts (Option 4)
- **Clean up YAML files** with smart duplicate detection (Option 5)
- **Recreate Jupyter kernels** for Python/R environments (Option 6)
- See real-time progress and results
- Review smart naming decisions and conflict resolutions

### 🆕 Environment Cloning (Standalone)
```bash
# Clone with conda-pack (exact replication, recommended)
python utils/environment_cloner.py myenv new_env --method conda-pack

# Clone with YAML export (cross-platform compatible)
python utils/environment_cloner.py myenv new_env --method yaml

# Auto-detect method and smart naming
python utils/environment_cloner.py myenv auto

# Clone from environment path
python utils/environment_cloner.py /path/to/env auto --method conda-pack
```

### 🆕 Failure Analysis & Debugging
```bash
# Analyze all failures in log
python utils/simple_log_analyzer.py

# Debug specific environment
python utils/simple_log_analyzer.py myenv

# Interactive debugging session
python utils/simple_log_analyzer.py --debug
```

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

## 🆕 Environment Cloning with conda-pack

The environment cloner supports two methods:

### 1. conda-pack Method (Recommended)
- **Exact replication** of environments including all packages, versions, and dependencies
- **Portable archives** that can be deployed on any compatible system
- **No conda/python required** on target machine initially
- **Faster deployment** as packages are pre-compiled

```bash
# Install conda-pack if not available
conda install conda-pack

# Create portable archive
python utils/environment_cloner.py myenv deployment_env --method conda-pack

# On target machine
mkdir -p deployment_env
tar -xzf cloned_environments/deployment_env.tar.gz -C deployment_env
source deployment_env/bin/activate
conda-unpack
```

### 2. YAML Method
- **Cross-platform compatible** environments
- **Latest package versions** (may differ from source)
- **Requires conda** on target machine
- **Better for updating** dependencies

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

## 🆕 Troubleshooting & Debugging

### Analyze Environment Failures
If environments fail to export or reinstall, use the debugging tools:

```bash
# See overview of all failures
python utils/simple_log_analyzer.py

# Debug specific environment with detailed context
python utils/simple_log_analyzer.py myenv

# Interactive debugging session
python utils/simple_log_analyzer.py --debug
```

### Common Issues & Solutions

1. **Environment Export Fails**
   ```bash
   # Check environment exists and is accessible
   conda env list | grep myenv
   conda list -n myenv
   ```

2. **Permission Errors**
   ```bash
   # Check write permissions for output directories
   ls -la exported_environments/
   ls -la cloned_environments/
   ```

3. **Package Conflicts During Reinstall**
   ```bash
   # Review the exported YAML for conflicts
   python yaml_analyzer.py --analyze
   # Edit the YAML file manually if needed
   ```

4. **conda-pack Errors**
   ```bash
   # Install or update conda-pack
   conda install conda-pack
   conda update conda-pack
   ```

### Log Analysis Examples
```bash
# Find all ERROR entries
grep "ERROR" environment_manager.log

# Search for specific environment issues
grep -A 5 -B 5 "myenv" environment_manager.log

# Count success vs failure rates
grep -c "Successfully" environment_manager.log
grep -c "Failed\|ERROR" environment_manager.log
```

## Dependencies

Install required packages:
```bash
pip install -r requirements.txt
```

Required:
- `PyYAML` - YAML file processing
- `colorama` - Colored console output

Optional but recommended:
- `conda-pack` - For environment cloning (`conda install conda-pack`)

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

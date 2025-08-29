# Mamba Environment Manager

A comprehensive Python tool for managing conda/mamba environments with automated backup, cloning, analysis, and Jupyter kernel management.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run interactive manager
python environment_manager.py
```

## 📋 Main Features

```
Environment Management Options:
1. [BACKUP] Backup environment (preserve original)
2. [CLONE]  Clone environment (backup + rename/recreate)
3. [UNPACK] Unpack conda-pack archive to environment
4. [ANALYZE] Analyze exported YAML files for duplicates
5. [BATCH]  Batch processing (multiple environments)
6. [DEBUG]  Debug and analyze failures
7. [KERNEL] Manage Jupyter kernels
8. [DELETE] Delete environments
9. [LIST]   List all environments
10. [CLEAN] Clean up backup files (YAML/conda-pack)
```

## 📦 Requirements

- **Python**: 3.8+
- **Conda/Mamba**: Environment management
- **Required packages**: 
  - `PyYAML>=6.0` - YAML file processing
  - `colorama>=0.4.0` - Colored console output
  - `conda-pack>=0.7.0` - Environment packaging

```bash
pip install -r requirements.txt
```

## 🎯 Core Functionality

### Environment Management
- **Backup & Clone**: Export to YAML/conda-pack, recreate with smart naming
- **Smart Naming**: Auto-lowercase with Python/R version detection (`myenv_py310`)
- **Batch Processing**: Handle multiple environments efficiently
- **Safe Operations**: Verification before cleanup, comprehensive error handling

### Jupyter Kernel Management
- **Create/Remove/Reinstall**: Full kernel lifecycle management
- **Rename Kernels**: Change display names in Jupyter interface
- **Advanced Configuration**: Custom environment variables for HPC/cluster setups
- **List Input Support**: Manage multiple kernels with `[1,3,5]` or `[2,4-7]` syntax

### Utilities
- **YAML Analysis**: Find duplicates, conflicts, and cleanup options
- **Debug Tools**: Analyze failures with detailed context
- **Log Analysis**: Pattern detection and troubleshooting assistance
- **Workspace Cleanup**: Organize and remove temporary files

## 📁 Project Structure

```
├── environment_manager.py         # Main application
├── requirements.txt               # Dependencies
│
├── scripts/                       # Utility scripts
│   ├── batch_process.py           # Batch processing
│   ├── yaml_analyzer.py           # YAML analysis
│   └── package_config.py          # Package configuration
│
├── utils/                         # Core utilities
│   ├── environment_cloner.py      # Environment cloning
│   ├── simple_log_analyzer.py     # Log analysis & debugging
│   └── config_template.py         # Configuration templates
│
├── tests/                         # Test suite
├── demos/                         # Feature demonstrations
├── documentation/                 # Detailed documentation
│
├── exported_environments/         # YAML exports (auto-created)
├── cloned_environments/           # conda-pack archives (auto-created)
├── backup_environments/           # Operation logs (auto-created)
└── logs/                          # Application logs
```

## 🔧 Usage Examples

### Environment Operations
```bash
# Interactive mode (recommended)
python environment_manager.py

# Clone environment with conda-pack
python utils/environment_cloner.py myenv new_env --method conda-pack

# Batch processing
python scripts/batch_process.py
```

### YAML Analysis
```bash
# Analyze for duplicates
python scripts/yaml_analyzer.py --analyze

# Clean up duplicates
python scripts/yaml_analyzer.py --cleanup-duplicates keep_newest
```

### Debugging
```bash
# Analyze all failures
python utils/simple_log_analyzer.py

# Debug specific environment
python utils/simple_log_analyzer.py myenv
```

## 🧠 Smart Features

### Intelligent Naming
- **Auto-cleanup**: `py_jjans_3.10_scanpy` → `py_jjans_scanpy_py310`
- **Version detection**: Extracts Python/R versions from packages
- **Conflict resolution**: Adds `_v1`, `_v2` suffixes when needed
- **Package detection**: Includes key package versions (`_scanpy19`)

### Environment Cloning Methods
1. **conda-pack**: Exact replication, portable archives, faster deployment
2. **YAML**: Cross-platform compatible, latest versions, requires conda on target

### Advanced Kernel Management
- **Environment Variables**: Custom PATH, LD_LIBRARY_PATH for HPC setups
- **Interactive Editor**: Add/edit/delete environment variables
- **Safety Features**: Confirmation prompts, preview before execution
- **HPC Support**: Optimized for cluster/server environments

## 📚 Documentation

- **Main Guide**: This README
- **Feature Details**: `documentation/` folder
- **API Examples**: `demos/` folder  
- **Testing**: `tests/` folder

## 🔍 Troubleshooting

### Common Issues
```bash
# Check environment exists
conda env list | grep myenv

# Verify permissions
ls -la exported_environments/

# Analyze failures
python utils/simple_log_analyzer.py

# Check logs
grep "ERROR" logs/environment_manager.log
```

### File Locations
- **Logs**: `logs/environment_manager.log`
- **YAML exports**: `exported_environments/`
- **Archives**: `cloned_environments/`
- **Jupyter kernels**: `~/.local/share/jupyter/kernels/`

## ⚡ What's New

### v2.0 Features
- **Enhanced Jupyter Kernel Manager**: Complete lifecycle management with HPC support
- **Smart Environment Cloning**: conda-pack integration with version detection
- **Batch Operations**: Process multiple environments efficiently
- **Advanced Debugging**: Comprehensive failure analysis tools
- **YAML Analysis**: Duplicate detection and smart cleanup
- **List Input Support**: Manage multiple items with `[1,3,5]` syntax

### Recent Additions
- Advanced kernel configuration with custom environment variables
- Interactive environment variable editor
- HPC/cluster optimization features
- Comprehensive workspace organization
- Enhanced error handling and logging

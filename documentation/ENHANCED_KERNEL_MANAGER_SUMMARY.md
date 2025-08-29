# Enhanced Jupyter Kernel Manager

## Overview
Significantly expanded the Jupyter kernel management functionality to provide comprehensive kernel lifecycle management, advanced configuration, and HPC/cluster support with custom environment variables.

## What Was Added

### 🆕 New Menu Options

```
🔬 Jupyter Kernel Manager:
1. Create kernels for all environments
2. Select specific environments to create  
3. Select by environment numbers (list input)
4. Remove existing kernels                    [NEW]
5. Reinstall kernels                         [NEW]
6. Rename kernel display names               [NEW]
7. Configure advanced kernel settings        [NEW]
8. List installed kernels                    [NEW]
9. Back to main menu
```

### 🗑️ Kernel Removal (Option 4)
- **List Input Support**: Remove multiple kernels using `[1,3,5]` or `[2,4-7]` format
- **Safety Confirmations**: Requires explicit `yes` confirmation
- **Preview Mode**: Shows which kernels will be removed before execution
- **Comprehensive Display**: Shows kernel names and display names for clarity

### 🔄 Kernel Reinstallation (Option 5)
- **Clean Reinstall**: Removes existing kernels and creates new ones
- **Environment Selection**: Choose specific environments to reinstall
- **Automatic Detection**: Detects Python/R capabilities per environment
- **Progress Tracking**: Shows success/failure for each environment

### ✏️ Kernel Renaming (Option 6)
- **Display Name Editing**: Change how kernels appear in Jupyter interface
- **Live Preview**: Shows current display name before editing
- **Direct JSON Editing**: Modifies kernel.json configuration files
- **Validation**: Checks kernel existence and file permissions

### ⚙️ Advanced Kernel Configuration (Option 7)
- **Custom Environment Variables**: Full control over kernel environment
- **Auto-generation**: Smart defaults based on conda environment paths
- **Interactive Editor**: Built-in environment variable editor
- **HPC Support**: Designed for cluster/HPC environment requirements

### 📋 Kernel Listing (Option 8)
- **Comprehensive View**: Shows all installed kernels with details
- **JSON Integration**: Uses `jupyter kernelspec list --json` for accuracy
- **Rich Information**: Display names, languages, and file locations
- **Clean Formatting**: Easy-to-read numbered list format

## Advanced Configuration Features

### 🔧 Environment Variable Management

#### Auto-Generated Variables
```json
{
  "PATH": "/path/to/env/bin:/existing/path",
  "LD_LIBRARY_PATH": "/path/to/env/lib:/existing/lib/path", 
  "PYTHONPATH": "",
  "CONDA_DEFAULT_ENV": "environment_name",
  "CONDA_PREFIX": "/path/to/environment"
}
```

#### Interactive Environment Editor
```
Commands Available:
- add <key> <value>  : Add new environment variable
- edit <key>         : Edit existing variable
- delete <key>       : Remove variable
- list               : Show all current variables  
- done               : Finish editing
```

#### HPC/Cluster Support Example
```json
{
  "argv": [
    "/cluster/envs/myenv/bin/python",
    "-m", "ipykernel_launcher", 
    "-f", "{connection_file}"
  ],
  "display_name": "MyEnv (HPC)",
  "language": "python",
  "env": {
    "LD_LIBRARY_PATH": "/cluster/envs/myenv/lib:/cluster/cuda/lib64:/cluster/libs",
    "PATH": "/cluster/envs/myenv/bin:/cluster/slurm/bin:/usr/local/bin:/usr/bin",
    "PYTHONPATH": "",
    "CUDA_VISIBLE_DEVICES": "0,1,2,3",
    "SLURM_JOBID": "${SLURM_JOBID}"
  },
  "metadata": {
    "debugger": true,
    "advanced_config": true,
    "environment": "myenv"
  }
}
```

## Technical Implementation

### New Methods Added

#### `_list_installed_kernels()`
- Uses `jupyter kernelspec list --json` for accurate kernel detection
- Displays kernel name, display name, language, and location
- Handles errors gracefully with timeout protection

#### `_handle_kernel_removal()`
- Parses list input using shared `_parse_number_list()` method
- Shows preview of kernels to be removed
- Requires explicit `yes` confirmation for safety
- Uses `jupyter kernelspec remove -f` for actual removal

#### `_handle_kernel_reinstall()`
- Combines removal and recreation for clean reinstall
- Detects environment capabilities (Python/R)
- Provides progress feedback for each environment
- Integrates with existing kernel creation infrastructure

#### `_handle_kernel_rename()`
- Lists available kernels with current display names
- Allows selection and modification of display names
- Directly edits `kernel.json` configuration files
- Validates file existence and permissions

#### `_handle_advanced_kernel_config()`
- Generates smart default environment variables
- Provides interactive environment variable editor
- Creates advanced kernel configurations with custom env vars
- Supports both Python and R kernel types

#### `_generate_default_env_vars(env_path: str)`
- Automatically configures PATH with environment bin directory
- Sets up LD_LIBRARY_PATH for library dependencies
- Configures CONDA_PREFIX and CONDA_DEFAULT_ENV
- Provides clean PYTHONPATH for environment isolation

#### `_interactive_env_var_editor(env_vars: dict)`
- Command-line interface for environment variable management
- Supports add, edit, delete, list, and done commands
- Validates input and provides helpful error messages
- Maintains dictionary state throughout editing session

#### `_create_advanced_kernel(env_name, env_path, env_vars, is_python)`
- Creates kernel with full environment variable configuration
- Validates executable paths before kernel creation
- Generates appropriate argv based on kernel type
- Includes advanced metadata for kernel identification

### Utility Methods

#### `_parse_number_list(user_input: str)`
- Shared parsing for list input formats `[1,3,5]` and `[2,4-7]`
- Handles ranges with expansion: `[2,4-7]` → `[2,4,5,6,7]`
- Returns sorted, unique list of numbers
- Used across multiple kernel management features

#### `_remove_kernels_for_environment(env_name: str)`
- Helper method to remove all kernels for a specific environment
- Attempts to remove both Python and R kernels
- Silently ignores errors if kernels don't exist
- Used by reinstall functionality

## User Experience Improvements

### Safety-First Design
- **Multiple Confirmations**: Destructive operations require explicit confirmation
- **Preview Mode**: Always show what will be changed before execution
- **Clear Warnings**: Prominent warnings for permanent operations
- **Graceful Errors**: Helpful error messages with troubleshooting hints

### Enhanced Usability
- **List Input**: Consistent `[1,3,5]` format across all multi-selection features
- **Progress Feedback**: Real-time status updates during operations
- **Rich Display**: Detailed information about kernels and environments
- **Command Consistency**: Similar interaction patterns across all features

### HPC/Cluster Optimization
- **Environment Variables**: Full control over kernel runtime environment
- **Path Management**: Intelligent PATH and library path configuration
- **Custom Executables**: Support for non-standard Python/R installations
- **Metadata Tracking**: Advanced configuration metadata for management

## Usage Examples

### Example 1: Remove Multiple Kernels
```bash
# Navigate to kernel manager
python environment_manager.py
# Choose: 7 (Kernel Manager) → 4 (Remove kernels)
# Input: [1,3,5] to remove kernels 1, 3, and 5
# Confirm: yes
```

### Example 2: Create Advanced HPC Kernel
```bash
# Navigate to kernel manager  
python environment_manager.py
# Choose: 7 (Kernel Manager) → 7 (Advanced config)
# Select environment and review auto-generated variables
# Use interactive editor to add custom variables:
#   add CUDA_VISIBLE_DEVICES 0,1,2,3
#   add SLURM_PARTITION gpu
#   done
# Choose kernel type and create
```

### Example 3: Rename Kernel Display Name
```bash
# Navigate to kernel manager
python environment_manager.py  
# Choose: 7 (Kernel Manager) → 6 (Rename kernels)
# Select kernel to rename
# Enter new display name: "My Project (GPU-Enabled)"
```

## Files Modified
- `environment_manager.py`: Added 8 new methods for enhanced kernel management
- `demos/demo_enhanced_kernel_manager.py`: Comprehensive demonstration script

## Testing
- ✅ Menu navigation and option handling
- ✅ Kernel listing and JSON parsing
- ✅ List input parsing and validation
- ✅ Environment variable generation
- ✅ Interactive editor functionality
- ✅ Safety confirmations and error handling
- ✅ Integration with existing kernel creation

## Benefits

### For Users
- **Complete Control**: Full lifecycle management of Jupyter kernels
- **Safety**: Multiple protection layers against accidental damage
- **Flexibility**: Support for simple and advanced use cases
- **Efficiency**: Batch operations and list input for productivity

### For HPC/Cluster Users
- **Environment Control**: Full customization of kernel runtime environment
- **Path Management**: Intelligent handling of library and executable paths
- **Custom Variables**: Support for cluster-specific environment variables
- **Advanced Metadata**: Better tracking and management of complex configurations

### For Developers
- **Modular Design**: Clean separation of concerns across methods
- **Reusable Components**: Shared utilities for parsing and validation
- **Extensible**: Easy to add new kernel management features
- **Well-Documented**: Comprehensive logging and error reporting

## Demo Available
Run `python demos/demo_enhanced_kernel_manager.py` for feature overview, or with options:
- `config` - Show advanced configuration examples
- `examples` - Show detailed usage examples  
- `safety` - Show safety features
- `all` - Show comprehensive overview

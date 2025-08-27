# Mamba Environment Manager Project

## Project Overview
Python project for managing mamba/conda environments with comprehensive features for reinstallation and renaming of broken environments.

## Completed Setup Steps

✅ **Project Requirements Clarified**
- Export broken environments to YAML files
- Reinstall environments from YAML files  
- Rename environments to lowercase with Python/R version suffixes
- Verify successful installation
- Remove old environments after successful reinstall
- Comprehensive error handling and logging

✅ **Project Scaffolded**
- environment_manager.py (main script)
- requirements.txt (dependencies)
- README.md (documentation)
- Export and backup directories created automatically

✅ **Project Customized**
- Interactive and batch processing modes
- Environment listing with Python/R version detection
- YAML export/import functionality
- Environment verification and cleanup
- Colored console output and detailed logging
- Graceful error handling throughout

✅ **Dependencies Installed**
- PyYAML for YAML file handling
- colorama for colored console output
- No compilation errors found

✅ **Testing Completed**
- Basic functionality verified
- Environment detection working
- Naming convention logic tested

✅ **Documentation Complete**
- Comprehensive README.md with usage instructions
- Inline code documentation
- Configuration template provided
- Logging system implemented

## Usage
- Interactive mode: `python environment_manager.py`
- Batch mode: `python batch_process.py` 
- Test mode: `python test_manager.py`

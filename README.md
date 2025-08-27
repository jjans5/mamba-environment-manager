# Mamba Environment Manager

A comprehensive Python tool for managing mamba/conda environments with automated reinstallation and renaming capabilities.

## Features

- **Export & Reinstall**: Export broken environments to YAML files and reinstall them
- **Smart Renaming**: Rename environments to lowercase with Python/R version suffixes
- **Verification**: Verify successful installation before cleanup
- **Safe Cleanup**: Remove old environments only after successful reinstall
- **Error Handling**: Comprehensive error handling and graceful recovery
- **Detailed Logging**: All operations logged to file with timestamps
- **Interactive Mode**: User-friendly interface for selective processing
- **Batch Mode**: Automated processing of all environments

## Usage

### Interactive Mode (Recommended)
```bash
python environment_manager.py
```
This mode allows you to:
- View all environments with their current and proposed new names
- Choose to process all environments or select specific ones
- See real-time progress and results

### Batch Mode (All Environments)
```bash
python batch_process.py
```
Processes all environments automatically after confirmation.

### Test Mode
```bash
python test_manager.py
```
Tests the functionality without making any changes.

## Environment Naming Convention

The tool renames environments using this pattern:
- Original: `MyEnvironment` → New: `myenvironment_py39`
- Original: `DataScience` → New: `datascience_py311_r41`

Rules:
- Convert to lowercase
- Add Python version suffix: `_py39`, `_py311`, etc.
- Add R version suffix if R is installed: `_r41`, `r42`, etc.
- Remove dots from version numbers

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
=== Processing environment: MyEnv ===
Step 1: Exporting environment...
Successfully exported MyEnv to exported_environments/MyEnv_20250827_102438.yml
New environment name: myenv_py39
Step 2: Creating new environment...
Successfully created environment myenv_py39
Step 3: Verifying new environment...
Environment myenv_py39 verified successfully
Step 4: Removing old environment...
Successfully removed environment MyEnv
✓ Successfully processed MyEnv -> myenv_py39
```

## Troubleshooting

- **Mamba not found**: The tool automatically falls back to conda
- **Export fails**: Check if the environment is corrupted or has dependency conflicts
- **Import fails**: Review the exported YAML file for invalid dependencies
- **Verification fails**: The new environment may have issues but won't be removed automatically

## Files Created

- `exported_environments/`: YAML exports of original environments
- `backup_environments/`: Additional backup location (future use)
- `environment_manager.log`: Detailed operation log

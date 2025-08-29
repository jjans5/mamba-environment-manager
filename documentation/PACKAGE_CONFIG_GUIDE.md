# Package Configuration Guide

This guide explains how to customize package detection for environment naming.

## Quick Start

The `package_config.py` file in your project root controls which packages are considered "important" for environment naming and how their versions are displayed.

## Configuration Format

```python
package_indicators = {
    'display_name': {
        'packages': ['package1', 'package2', 'alternative-name'],
        'include_version': True/False,
        'version_format': 'major.minor' or 'major' or 'full'
    }
}
```

## Configuration Options

### `packages`
List of package names that should trigger this indicator. The system checks for any of these names in the environment.

**Example:**
```python
'harmony': {
    'packages': ['harmonypy', 'harmony-pytorch', 'harmony'],
    # Will detect harmonypy, harmony-pytorch, or harmony packages
}
```

### `include_version`
Whether to include version information in the environment name.

- `True`: Include version (e.g., `harmony09` for harmonypy=0.0.9)
- `False`: Just use package name (e.g., `harmony`)

### `version_format`
How to format the version when `include_version` is `True`.

- `'major'`: Only major version (e.g., `pytorch1` for pytorch=1.9.0)
- `'major.minor'`: Major and minor (e.g., `pytorch19` for pytorch=1.9.0)  
- `'full'`: Full version (e.g., `pytorch190` for pytorch=1.9.0)

## Adding Your Own Packages

### Example 1: Add a new package with version
```python
'mypackage': {
    'packages': ['my-awesome-package', 'mypackage'],
    'include_version': True,
    'version_format': 'major.minor'
}
```

This will:
- Detect `my-awesome-package` or `mypackage` in environments
- Include version info: `mypackage12` for version 1.2.3
- Display as: `env_name_py38_mypackage12`

### Example 2: Add a package without version
```python
'specialtool': {
    'packages': ['special-analysis-tool'],
    'include_version': False,
    'version_format': 'major'  # Ignored when include_version=False
}
```

This will:
- Detect `special-analysis-tool` in environments  
- No version info: just `specialtool`
- Display as: `env_name_py38_specialtool`

## Real-World Examples

### Single-Cell Analysis Environment
```python
# Existing environment with packages:
# harmonypy=0.0.9, scanpy=1.8.2, pandas=1.3.3

# Results in name: my_env_py38_harmony09_scanpy18
```

### Machine Learning Environment  
```python
# Existing environment with packages:
# torch=1.9.0, tensorflow=2.6.0, scikit-learn=1.0.2

# Results in name: ml_env_py39_pytorch19_tensorflow26_sklearn10
```

### Web Development Environment
```python
# Existing environment with packages:
# streamlit=1.2.0, dash=2.0.0, flask=2.1.0

# Results in name: web_env_py38_streamlit12_dash20
# (flask not included as include_version=False in default config)
```

## Special Version Handling

The system handles edge cases automatically:

### 0.0.x Versions
- `harmonypy=0.0.9` → `harmony09` (uses patch version)
- `experimental=0.0.15` → `experimental015`

### Build Information
- `pytorch=1.9.0+cu111` → `pytorch19` (removes build info)
- `tensorflow=2.6.0-gpu` → `tensorflow26` (removes suffix)

## Testing Your Configuration

Test your package configuration:

```bash
# Test with a mock environment
python3 -c "
from utils.environment_cloner import EnvironmentCloner
cloner = EnvironmentCloner()

test_env = {
    'name': 'test_env',
    'python_version': '3.8',
    'packages': ['your-package=1.2.3', 'other-package=2.0.0']
}

packages = cloner._detect_key_packages(test_env)
name = cloner._generate_new_name(test_env, 'auto', interactive=False)
print(f'Detected: {packages}')
print(f'Name: {name}')
"
```

## Priority and Limits

- **Order matters**: Packages are detected in the order listed in the config
- **Limit**: Only first 2 detected packages are included in names to keep them reasonable
- **Fallback**: If config file fails to load, default configuration is used

## Default Packages Included

The default configuration includes detection for:

**Single-Cell/Bioinformatics:**
- harmonypy, scanpy, seurat

**Machine Learning:**  
- pytorch/torch, tensorflow, scikit-learn

**Data Science:**
- pandas, numpy (no version by default)

**Web Frameworks:**
- streamlit, dash, django, fastapi, flask

**Development:**
- jupyter, jupyterlab

**Visualization:**
- plotly, matplotlib

## Advanced Tips

### Environment-Specific Packages
Add packages specific to your research area:

```python
# Genomics
'gatk': {
    'packages': ['gatk', 'gatk4'],
    'include_version': True,
    'version_format': 'major'
}

# Imaging  
'napari': {
    'packages': ['napari', 'napari-hub'],
    'include_version': True,
    'version_format': 'major.minor'
}
```

### Version Strategy
- Use `include_version=True` for packages where version matters (e.g., ML frameworks)
- Use `include_version=False` for stable/common packages (e.g., pandas, numpy)

---

**Result**: Your environments will have meaningful names that reflect their actual contents and package versions!

# Environment Manager Configuration
# Copy this file to config.py and modify as needed

# Tool preference (True for mamba, False for conda)
USE_MAMBA = True

# Naming conventions
NAMING_CONFIG = {
    # Whether to add Python version suffix
    'add_python_version': True,
    
    # Whether to add R version suffix  
    'add_r_version': True,
    
    # Separator for version suffixes
    'version_separator': '_',
    
    # Prefix for Python version (e.g., 'py' -> 'py39')
    'python_prefix': 'py',
    
    # Prefix for R version (e.g., 'r' -> 'r41')
    'r_prefix': 'r',
    
    # Remove dots from version numbers
    'remove_version_dots': True
}

# Directories
DIRECTORIES = {
    'export_dir': 'exported_environments',
    'backup_dir': 'backup_environments',
    'log_file': 'environment_manager.log'
}

# Verification settings
VERIFICATION = {
    # Command to run for environment verification
    'test_command': ['python', '--version'],
    
    # Timeout for verification commands (seconds)
    'timeout': 30
}

# Logging configuration
LOGGING = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'file_logging': True,
    'console_logging': True
}

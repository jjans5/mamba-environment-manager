# Package Configuration for Environment Cloner
#
# This file allows you to customize which packages are considered "important"
# for environment naming and how their versions should be displayed.
#
# Format:
# package_indicators = {
#     'display_name': {
#         'packages': ['package1', 'package2', 'alternative-name'],
#         'include_version': True/False,
#         'version_format': 'major.minor' or 'major' or 'full'
#     }
# }

package_indicators = {
    # Single-cell analysis
    'harmony': {
        'packages': ['harmonypy', 'harmony-pytorch', 'harmony'],
        'include_version': True,
        'version_format': 'major.minor'
    },
    'scanpy': {
        'packages': ['scanpy'],
        'include_version': True,
        'version_format': 'major.minor'
    },
    'seurat': {
        'packages': ['seurat', 'seuratobject'],
        'include_version': True,
        'version_format': 'major'
    },
    
    # Machine Learning
    'pytorch': {
        'packages': ['torch', 'pytorch'],
        'include_version': True,
        'version_format': 'major.minor'
    },
    'tensorflow': {
        'packages': ['tensorflow', 'tensorflow-gpu'],
        'include_version': True,
        'version_format': 'major.minor'
    },
    'sklearn': {
        'packages': ['scikit-learn', 'sklearn'],
        'include_version': True,
        'version_format': 'major.minor'
    },
    
    # Data Science Core
    'pandas': {
        'packages': ['pandas'],
        'include_version': False,  # Too common, version not needed
        'version_format': 'major'
    },
    'numpy': {
        'packages': ['numpy'],
        'include_version': False,  # Too common, version not needed
        'version_format': 'major'
    },
    
    # Development/Notebooks
    'jupyter': {
        'packages': ['jupyter', 'jupyterlab'],
        'include_version': False,
        'version_format': 'major'
    },
    
    # Web Frameworks
    'streamlit': {
        'packages': ['streamlit'],
        'include_version': True,
        'version_format': 'major.minor'
    },
    'dash': {
        'packages': ['dash'],
        'include_version': True,
        'version_format': 'major.minor'
    },
    'flask': {
        'packages': ['flask'],
        'include_version': False,
        'version_format': 'major'
    },
    'django': {
        'packages': ['django'],
        'include_version': True,
        'version_format': 'major.minor'
    },
    'fastapi': {
        'packages': ['fastapi'],
        'include_version': True,
        'version_format': 'major.minor'
    },
    
    # Visualization
    'plotly': {
        'packages': ['plotly'],
        'include_version': False,
        'version_format': 'major'
    },
    'matplotlib': {
        'packages': ['matplotlib'],
        'include_version': False,
        'version_format': 'major'
    },
    
    # Add your custom packages here:
    # 'mypackage': {
    #     'packages': ['my-package-name', 'alternative-name'],
    #     'include_version': True,
    #     'version_format': 'major.minor'
    # },
}

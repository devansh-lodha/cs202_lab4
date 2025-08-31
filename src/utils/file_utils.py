import os

def classify_file_type(filepath):
    """Classifies a file into predefined categories based on its path."""
    if not isinstance(filepath, str):
        return 'Other'

    filename = os.path.basename(filepath).lower()
    
    if 'license' in filename:
        return 'LICENSE'
    if filename.startswith('readme'):
        return 'README'
    
    # Check for test files, a common pattern in Python projects
    path_lower = filepath.lower()
    if ('test' in path_lower or 'tests' in path_lower) and filename.endswith(('.py', '.pyx')):
        return 'Test Code'
    
    # Check for primary source code files
    if filename.endswith(('.py', '.pyi', '.pyx', '.pyd')):
        return 'Source Code'
        
    return 'Other'
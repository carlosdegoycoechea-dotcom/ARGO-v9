#!/usr/bin/env python3
"""
Dead Code Detection
Find Python files that are never imported
"""
import os
import sys
from pathlib import Path
import re

print("="*70)
print("DEAD CODE DETECTION")
print("="*70)

# Get all Python files
all_py_files = []
for root, dirs, files in os.walk('.'):
    # Skip certain directories
    skip_dirs = {'.git', '__pycache__', 'venv', 'env', '.pytest_cache', 'legacy'}
    dirs[:] = [d for d in dirs if d not in skip_dirs]
    
    for file in files:
        if file.endswith('.py'):
            path = Path(root) / file
            all_py_files.append(path)

print(f"\nFound {len(all_py_files)} Python files")

# Read all Python content to find imports
all_content = ""
for py_file in all_py_files:
    try:
        with open(py_file, 'r', encoding='utf-8') as f:
            all_content += f.read() + "\n"
    except:
        pass

# Check each file for references
print("\nChecking for unreferenced files...")
print("-"*70)

dead_files = []
critical_files = {
    'app/ui.py',  # Entry point
    'scripts/audit_architecture.py',  # Script
    'scripts/migrate_to_clean.py',  # Script
    'evaluation/evaluate.py',  # Script
    'tests/test_bootstrap.py',  # Test
    'tests/test_architecture.py',  # Test
}

for py_file in all_py_files:
    # Skip __init__.py and main entry points
    if py_file.name == '__init__.py':
        continue
    
    if str(py_file).replace('./', '') in critical_files:
        continue
    
    # Get module name
    rel_path = str(py_file).replace('./', '').replace('.py', '')
    module_name = rel_path.replace('/', '.')
    
    # Also check filename without path
    just_name = py_file.stem
    
    # Check if imported anywhere
    import_patterns = [
        f"from {module_name} import",
        f"import {module_name}",
        f"from {just_name} import",
        f"import {just_name}",
    ]
    
    referenced = False
    for pattern in import_patterns:
        if pattern in all_content:
            referenced = True
            break
    
    if not referenced:
        # Double check - maybe it's imported via parent package
        parts = module_name.split('.')
        if len(parts) > 1:
            parent_import = f"from {'.'.join(parts[:-1])} import"
            if parent_import in all_content and parts[-1] in all_content:
                referenced = True
    
    if not referenced:
        print(f"  ⚠ Potentially unreferenced: {py_file}")
        dead_files.append(py_file)

print("\n" + "="*70)
print("DEAD CODE SUMMARY")
print("="*70)

if dead_files:
    print(f"\n⚠ Found {len(dead_files)} potentially unreferenced files:")
    for f in dead_files:
        print(f"  - {f}")
    print("\nNOTE: These might be:")
    print("  - Scripts meant to be run directly")
    print("  - Modules imported dynamically")
    print("  - Future/planned modules")
    print("  - Test fixtures")
else:
    print("\n✓ No dead code detected - all files are referenced")

sys.exit(0)

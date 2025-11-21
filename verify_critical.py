#!/usr/bin/env python3
"""
Critical Files Verification
Checks that no functionality was lost and no dead code exists
"""
import os
import sys
from pathlib import Path

print("="*70)
print("CRITICAL FILES VERIFICATION")
print("="*70)

errors = []
warnings = []
passed = []

# 1. Check critical files exist
critical_files = [
    "config/settings.yaml",
    "core/__init__.py",
    "core/bootstrap.py",
    "core/config.py",
    "core/logger.py",
    "core/unified_database.py",
    "core/model_router.py",
    "core/llm_provider.py",
    "core/rag_engine.py",
    "core/library_manager.py",
    "tools/extractors.py",
    "tools/google_drive_sync.py",
    "app/ui.py",
    "app/panels/analytics_panel.py",
    "scripts/audit_architecture.py",
    "scripts/migrate_to_clean.py",
    "evaluation/evaluate.py",
]

print("\n1. Critical Files Check")
print("-"*70)
missing = []
for file in critical_files:
    if Path(file).exists():
        print(f"  ✓ {file}")
    else:
        print(f"  ✗ MISSING: {file}")
        missing.append(file)

if missing:
    errors.append(f"Missing critical files: {missing}")
else:
    passed.append("All critical files present")

# 2. Check for bootstrap duplication
print("\n2. Bootstrap Duplication Check")
print("-"*70)
bootstrap_files = list(Path("core").glob("bootstrap*.py"))
if len(bootstrap_files) == 1 and bootstrap_files[0].name == "bootstrap.py":
    print(f"  ✓ Single bootstrap: {bootstrap_files[0]}")
    passed.append("No bootstrap duplication")
else:
    print(f"  ✗ Multiple bootstrap files: {bootstrap_files}")
    errors.append(f"Bootstrap duplication: {bootstrap_files}")

# 3. Check for RAG duplication
print("\n3. RAG Engine Duplication Check")
print("-"*70)
rag_files = list(Path("core").glob("rag_engine*.py"))
if len(rag_files) == 1 and rag_files[0].name == "rag_engine.py":
    print(f"  ✓ Single RAG engine: {rag_files[0]}")
    passed.append("No RAG duplication")
else:
    print(f"  ✗ Multiple RAG files: {rag_files}")
    errors.append(f"RAG duplication: {rag_files}")

# 4. Check for database duplication
print("\n4. Database Duplication Check")
print("-"*70)
db_files = [f for f in Path("core").glob("*database*.py") if "unified" not in f.name and "__" not in f.name]
if not db_files:
    print(f"  ✓ No legacy database files")
    passed.append("No database duplication")
else:
    print(f"  ⚠ Legacy DB files found: {db_files}")
    warnings.append(f"Legacy database files: {db_files}")

# 5. Check key functions exist
print("\n5. Key Functions Check")
print("-"*70)

# Check bootstrap
try:
    with open("core/bootstrap.py", "r") as f:
        content = f.read()
        if "def initialize_argo(" in content:
            print("  ✓ initialize_argo() exists")
            passed.append("initialize_argo exists")
        else:
            print("  ✗ initialize_argo() NOT FOUND")
            errors.append("initialize_argo missing")
except Exception as e:
    errors.append(f"Cannot read bootstrap: {e}")

# Check Drive sync
try:
    with open("tools/google_drive_sync.py", "r") as f:
        content = f.read()
        if "class GoogleDriveSync:" in content and "def sync_library(" in content:
            print("  ✓ GoogleDriveSync complete")
            passed.append("Drive sync implemented")
        else:
            print("  ✗ GoogleDriveSync incomplete")
            errors.append("Drive sync incomplete")
except Exception as e:
    errors.append(f"Cannot read drive sync: {e}")

# Check analytics queries
try:
    with open("core/unified_database.py", "r") as f:
        content = f.read()
        methods = [
            "get_daily_usage",
            "get_usage_by_project",
            "get_usage_by_model",
            "check_budget_alert"
        ]
        missing_methods = []
        for method in methods:
            if f"def {method}(" in content:
                print(f"  ✓ {method}() exists")
            else:
                print(f"  ✗ {method}() NOT FOUND")
                missing_methods.append(method)
        
        if missing_methods:
            errors.append(f"Missing analytics methods: {missing_methods}")
        else:
            passed.append("All analytics queries present")
except Exception as e:
    errors.append(f"Cannot read database: {e}")

# 6. Check RAG capabilities
print("\n6. RAG Capabilities Check")
print("-"*70)
try:
    with open("core/rag_engine.py", "r") as f:
        content = f.read()
        capabilities = [
            ("HyDE", "class HyDE"),
            ("Semantic Cache", "class SemanticCache"),
            ("Unified Search", "def search("),
            ("Library Boost", "_get_library_boost"),
        ]
        missing = []
        for name, marker in capabilities:
            if marker in content:
                print(f"  ✓ {name}")
            else:
                print(f"  ✗ {name} NOT FOUND")
                missing.append(name)
        
        if missing:
            errors.append(f"Missing RAG capabilities: {missing}")
        else:
            passed.append("All RAG capabilities present")
except Exception as e:
    errors.append(f"Cannot read RAG engine: {e}")

# Summary
print("\n" + "="*70)
print("VERIFICATION SUMMARY")
print("="*70)
print(f"✓ Passed: {len(passed)}")
print(f"⚠ Warnings: {len(warnings)}")
print(f"✗ Errors: {len(errors)}")
print()

if errors:
    print("ERRORS:")
    for err in errors:
        print(f"  - {err}")

if warnings:
    print("\nWARNINGS:")
    for warn in warnings:
        print(f"  - {warn}")

# Exit code
if errors:
    sys.exit(1)
else:
    print("\n✓ All critical verifications PASSED")
    sys.exit(0)

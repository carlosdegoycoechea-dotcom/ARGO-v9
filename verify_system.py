#!/usr/bin/env python3
"""
ARGO v10 - System Verification Script
Comprehensive checks for system integrity
"""
import os
import sys
from pathlib import Path
import json
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_check(name, passed, details=""):
    symbol = f"{Colors.GREEN}✓{Colors.END}" if passed else f"{Colors.RED}✗{Colors.END}"
    print(f"  {symbol} {name}")
    if details:
        print(f"      {Colors.YELLOW}{details}{Colors.END}")

def check_file(filepath, description):
    exists = Path(filepath).exists()
    print_check(description, exists, filepath if not exists else "")
    return exists

def check_directory(dirpath, description):
    exists = Path(dirpath).is_dir()
    print_check(description, exists, dirpath if not exists else "")
    return exists

def verify_structure():
    """Verify directory structure"""
    print_header("DIRECTORY STRUCTURE")

    checks = [
        ("backend", "Backend directory"),
        ("frontend_ui", "Frontend directory"),
        ("ARGO_v9.0_CLEAN", "ARGO Core directory"),
        ("backend/main.py", "Backend main.py"),
        ("backend/requirements.txt", "Backend requirements.txt"),
        ("backend/.env", "Backend .env"),
        ("frontend_ui/package.json", "Frontend package.json"),
        ("frontend_ui/.env", "Frontend .env"),
        ("frontend_ui/client/src", "Frontend source directory"),
        ("start_all.sh", "Start all script"),
        ("start_backend.sh", "Start backend script"),
        ("start_frontend.sh", "Start frontend script"),
    ]

    passed = sum(1 for path, desc in checks if check_file(path, desc))
    total = len(checks)

    return passed, total

def verify_backend():
    """Verify backend components"""
    print_header("BACKEND COMPONENTS")

    passed = 0
    total = 0

    # Check backend files
    backend_files = [
        ("backend/main.py", "FastAPI application"),
        ("backend/requirements.txt", "Python dependencies"),
        ("backend/.env", "Environment configuration"),
    ]

    for path, desc in backend_files:
        total += 1
        if check_file(path, desc):
            passed += 1

    # Check .env content
    total += 1
    env_path = Path("backend/.env")
    if env_path.exists():
        content = env_path.read_text()
        has_openai_key = "OPENAI_API_KEY=" in content and "placeholder" not in content.lower()
        print_check(
            "OpenAI API key configured",
            has_openai_key,
            "Please set a valid OPENAI_API_KEY in backend/.env" if not has_openai_key else ""
        )
        if has_openai_key:
            passed += 1

    # Check ARGO core components
    argo_files = [
        ("ARGO_v9.0_CLEAN/core/rag_engine.py", "RAG Engine"),
        ("ARGO_v9.0_CLEAN/core/model_router.py", "Model Router"),
        ("ARGO_v9.0_CLEAN/core/unified_database.py", "Unified Database"),
        ("ARGO_v9.0_CLEAN/core/bootstrap.py", "Bootstrap"),
    ]

    for path, desc in argo_files:
        total += 1
        if check_file(path, desc):
            passed += 1

    return passed, total

def verify_frontend():
    """Verify frontend components"""
    print_header("FRONTEND COMPONENTS")

    passed = 0
    total = 0

    # Check frontend files
    frontend_files = [
        ("frontend_ui/package.json", "Package configuration"),
        ("frontend_ui/.env", "Environment configuration"),
        ("frontend_ui/client/src/App.tsx", "Main App component"),
        ("frontend_ui/client/src/lib/api.ts", "API client"),
        ("frontend_ui/client/src/pages/Dashboard.tsx", "Dashboard page"),
        ("frontend_ui/client/src/components/chat/ChatInterface.tsx", "Chat component"),
        ("frontend_ui/client/src/components/analytics/AnalyticsPanel.tsx", "Analytics component"),
        ("frontend_ui/client/src/components/documents/DocumentsPanel.tsx", "Documents component"),
    ]

    for path, desc in frontend_files:
        total += 1
        if check_file(path, desc):
            passed += 1

    # Check package.json
    total += 1
    package_path = Path("frontend_ui/package.json")
    if package_path.exists():
        try:
            with open(package_path) as f:
                package_data = json.load(f)
                has_deps = "dependencies" in package_data and len(package_data["dependencies"]) > 0
                print_check("Dependencies configured", has_deps)
                if has_deps:
                    passed += 1
        except Exception as e:
            print_check("Package.json valid", False, str(e))

    return passed, total

def verify_scripts():
    """Verify startup scripts"""
    print_header("STARTUP SCRIPTS")

    passed = 0
    total = 3

    scripts = [
        "start_all.sh",
        "start_backend.sh",
        "start_frontend.sh",
    ]

    for script in scripts:
        exists = Path(script).exists()
        executable = os.access(script, os.X_OK) if exists else False

        print_check(f"{script} exists and is executable", exists and executable,
                   f"Run: chmod +x {script}" if exists and not executable else "")
        if exists and executable:
            passed += 1

    return passed, total

def verify_documentation():
    """Verify documentation"""
    print_header("DOCUMENTATION")

    docs = [
        ("README_V10.md", "Main README"),
        ("backend/.env.example", "Backend env example"),
        ("frontend_ui/.env.example", "Frontend env example"),
    ]

    passed = sum(1 for path, desc in docs if check_file(path, desc))
    total = len(docs)

    return passed, total

def generate_report():
    """Generate verification report"""
    print_header("ARGO v10 - SYSTEM VERIFICATION")

    results = []

    # Run all verifications
    results.append(("Structure", *verify_structure()))
    results.append(("Backend", *verify_backend()))
    results.append(("Frontend", *verify_frontend()))
    results.append(("Scripts", *verify_scripts()))
    results.append(("Documentation", *verify_documentation()))

    # Summary
    print_header("VERIFICATION SUMMARY")

    total_passed = sum(r[1] for r in results)
    total_checks = sum(r[2] for r in results)

    for name, passed, total in results:
        percentage = (passed / total * 100) if total > 0 else 0
        status = f"{Colors.GREEN}PASS{Colors.END}" if passed == total else f"{Colors.YELLOW}PARTIAL{Colors.END}"
        print(f"  {name:20s} {passed:3d}/{total:3d} ({percentage:5.1f}%)  [{status}]")

    print(f"\n  {Colors.BOLD}Total:{Colors.END:20s} {total_passed:3d}/{total_checks:3d} ({(total_passed/total_checks*100):5.1f}%)")

    # Overall result
    print()
    if total_passed == total_checks:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL CHECKS PASSED!{Colors.END}")
        print(f"{Colors.GREEN}System is ready for deployment.{Colors.END}")
        return 0
    elif total_passed / total_checks >= 0.8:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠ MOST CHECKS PASSED{Colors.END}")
        print(f"{Colors.YELLOW}Review warnings above before deployment.{Colors.END}")
        return 1
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ VERIFICATION FAILED{Colors.END}")
        print(f"{Colors.RED}Critical issues detected. Fix errors before deployment.{Colors.END}")
        return 2

def main():
    print(f"{Colors.BOLD}")
    print("""
     █████╗ ██████╗  ██████╗  ██████╗     ██╗   ██╗ ██╗ ██████╗
    ██╔══██╗██╔══██╗██╔════╝ ██╔═══██╗    ██║   ██║███║██╔═████╗
    ███████║██████╔╝██║  ███╗██║   ██║    ██║   ██║╚██║██║██╔██║
    ██╔══██║██╔══██╗██║   ██║██║   ██║    ╚██╗ ██╔╝ ██║████╔╝██║
    ██║  ██║██║  ██║╚██████╔╝╚██████╔╝     ╚████╔╝  ██║╚██████╔╝
    ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝       ╚═══╝   ╚═╝ ╚═════╝
    """)
    print(f"{Colors.END}")
    print(f"{Colors.BOLD}Enterprise PMO Platform - System Verification{Colors.END}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Change to project root
    os.chdir(Path(__file__).parent)

    # Run verification
    exit_code = generate_report()

    print()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

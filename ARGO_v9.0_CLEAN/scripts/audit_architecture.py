#!/usr/bin/env python3
"""
ARGO Architecture Audit Script
Validates the clean architecture against design principles
"""
import os
import sys
from pathlib import Path
import ast
import re
from typing import List, Dict, Tuple, Set
from collections import defaultdict
import json

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class ArchitectureAuditor:
    """Audits ARGO architecture for compliance"""
    
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.issues = defaultdict(list)
        self.warnings = defaultdict(list)
        self.passed = defaultdict(list)
    
    def run_full_audit(self) -> Dict:
        """Run all audits"""
        print(f"{Colors.BOLD}ARGO Architecture Audit{Colors.END}")
        print("=" * 70)
        
        audits = [
            ("1. Duplicated Modules", self.audit_duplicates),
            ("2. Version Suffixes in Filenames", self.audit_version_suffixes),
            ("3. Direct LLM Instantiation", self.audit_direct_llm_calls),
            ("4. Direct Text Splitting", self.audit_direct_chunking),
            ("5. Emoji Usage", self.audit_emojis),
            ("6. Multiple Bootstrap Functions", self.audit_multiple_bootstraps),
            ("7. Import Consistency", self.audit_imports),
            ("8. Configuration Hardcoding", self.audit_hardcoded_config),
        ]
        
        for name, audit_func in audits:
            print(f"\n{Colors.BLUE}{name}{Colors.END}")
            print("-" * 70)
            audit_func()
        
        return self._generate_report()
    
    def audit_duplicates(self):
        """Check for duplicated module names"""
        files = list(self.root_path.rglob("*.py"))
        filenames = [f.name for f in files]
        
        duplicates = [name for name in set(filenames) if filenames.count(name) > 1]
        
        if duplicates:
            self.issues['duplicates'].extend(duplicates)
            print(f"{Colors.RED}✗ Found {len(duplicates)} duplicated filenames:{Colors.END}")
            for dup in duplicates:
                print(f"  - {dup}")
        else:
            self.passed['duplicates'].append("No duplicated filenames")
            print(f"{Colors.GREEN}✓ No duplicated filenames{Colors.END}")
    
    def audit_version_suffixes(self):
        """Check for version suffixes in filenames"""
        patterns = [
            r'_v\d+',   # _v8, _v9
            r'_f\d+',   # _f1, _f2
            r'_old',    # _old
            r'_new',    # _new
            r'_backup', # _backup
        ]
        
        files = list(self.root_path.rglob("*.py"))
        versioned_files = []
        
        for f in files:
            for pattern in patterns:
                if re.search(pattern, f.stem):
                    versioned_files.append((f.relative_to(self.root_path), pattern))
        
        if versioned_files:
            self.issues['version_suffixes'] = versioned_files
            print(f"{Colors.RED}✗ Found {len(versioned_files)} files with version suffixes:{Colors.END}")
            for filepath, pattern in versioned_files[:10]:
                print(f"  - {filepath} (pattern: {pattern})")
            if len(versioned_files) > 10:
                print(f"  ... and {len(versioned_files) - 10} more")
        else:
            self.passed['version_suffixes'].append("No version suffixes in filenames")
            print(f"{Colors.GREEN}✓ No version suffixes in filenames{Colors.END}")
    
    def audit_direct_llm_calls(self):
        """Check for direct LLM instantiation (should use ModelRouter)"""
        prohibited_patterns = [
            (r'ChatOpenAI\s*\(', 'ChatOpenAI'),
            (r'ChatAnthropic\s*\(', 'ChatAnthropic'),
            (r'OpenAI\s*\(', 'OpenAI direct'),
        ]
        
        files = list(self.root_path.rglob("*.py"))
        violations = []
        
        # Exceptions: files allowed to instantiate directly
        exceptions = ['llm_provider.py', 'model_router.py', 'bootstrap.py']
        
        for filepath in files:
            if filepath.name in exceptions:
                continue
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for pattern, name in prohibited_patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        violations.append((
                            filepath.relative_to(self.root_path),
                            line_num,
                            name
                        ))
            except Exception as e:
                pass
        
        if violations:
            self.issues['direct_llm'].extend(violations)
            print(f"{Colors.RED}✗ Found {len(violations)} direct LLM instantiations:{Colors.END}")
            for filepath, line, pattern in violations[:5]:
                print(f"  - {filepath}:{line} ({pattern})")
            if len(violations) > 5:
                print(f"  ... and {len(violations) - 5} more")
            print(f"{Colors.YELLOW}  All LLM calls should go through ModelRouter!{Colors.END}")
        else:
            self.passed['direct_llm'].append("All LLM calls via ModelRouter")
            print(f"{Colors.GREEN}✓ No direct LLM instantiations found{Colors.END}")
    
    def audit_direct_chunking(self):
        """Check for direct RecursiveCharacterTextSplitter usage"""
        pattern = r'RecursiveCharacterTextSplitter\s*\('
        
        files = list(self.root_path.rglob("*.py"))
        violations = []
        
        # Exception: extractors.py is allowed
        exceptions = ['extractors.py']
        
        for filepath in files:
            if filepath.name in exceptions:
                continue
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                matches = re.finditer(pattern, content)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    violations.append((
                        filepath.relative_to(self.root_path),
                        line_num
                    ))
            except Exception as e:
                pass
        
        if violations:
            self.issues['direct_chunking'].extend(violations)
            print(f"{Colors.RED}✗ Found {len(violations)} direct text splitter usages:{Colors.END}")
            for filepath, line in violations:
                print(f"  - {filepath}:{line}")
            print(f"{Colors.YELLOW}  All chunking should use tools.extractors.extract_and_chunk()!{Colors.END}")
        else:
            self.passed['direct_chunking'].append("Chunking centralized in extractors")
            print(f"{Colors.GREEN}✓ No direct text splitter usage{Colors.END}")
    
    def audit_emojis(self):
        """Check for emoji usage in code"""
        emoji_pattern = r'[\U0001F300-\U0001F9FF]|[\u2600-\u26FF]|[\u2700-\u27BF]'
        
        files = list(self.root_path.rglob("*.py"))
        violations = []
        
        for filepath in files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Skip if in comments only
                lines_with_emojis = []
                for i, line in enumerate(content.split('\n'), 1):
                    # Skip comments
                    if '#' in line:
                        line = line[:line.index('#')]
                    
                    if re.search(emoji_pattern, line):
                        lines_with_emojis.append(i)
                
                if lines_with_emojis:
                    violations.append((
                        filepath.relative_to(self.root_path),
                        lines_with_emojis[:3]  # First 3 lines
                    ))
            except Exception as e:
                pass
        
        if violations:
            self.warnings['emojis'].extend(violations)
            print(f"{Colors.YELLOW}⚠ Found {len(violations)} files with emojis:{Colors.END}")
            for filepath, lines in violations[:5]:
                print(f"  - {filepath} (lines: {', '.join(map(str, lines))})")
            print(f"{Colors.YELLOW}  Corporate mode should avoid emojis{Colors.END}")
        else:
            self.passed['emojis'].append("No emojis in code")
            print(f"{Colors.GREEN}✓ No emojis in code (corporate mode){Colors.END}")
    
    def audit_multiple_bootstraps(self):
        """Check for multiple bootstrap/initialization functions"""
        pattern = r'def\s+initialize_argo[_\w]*\s*\('
        
        files = list(self.root_path.rglob("*.py"))
        init_functions = []
        
        for filepath in files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                matches = re.finditer(pattern, content)
                for match in matches:
                    func_name = match.group().split('def ')[1].split('(')[0].strip()
                    init_functions.append((
                        filepath.relative_to(self.root_path),
                        func_name
                    ))
            except Exception as e:
                pass
        
        # Should only be one: initialize_argo() in bootstrap.py
        if len(init_functions) > 1:
            self.warnings['multiple_inits'] = init_functions
            print(f"{Colors.YELLOW}⚠ Found {len(init_functions)} initialization functions:{Colors.END}")
            for filepath, func_name in init_functions:
                print(f"  - {func_name}() in {filepath}")
            print(f"{Colors.YELLOW}  Should only have initialize_argo() in bootstrap.py{Colors.END}")
        elif len(init_functions) == 1:
            self.passed['bootstrap'].append("Single initialization function")
            print(f"{Colors.GREEN}✓ Single initialization function: {init_functions[0][1]}(){Colors.END}")
        else:
            self.issues['bootstrap'].append("No initialization function found!")
            print(f"{Colors.RED}✗ No initialization function found{Colors.END}")
    
    def audit_imports(self):
        """Check import consistency"""
        files = list(self.root_path.rglob("*.py"))
        
        # Check for imports from legacy locations
        legacy_patterns = [
            (r'from\s+database\s+import', 'database.py (should be unified_database)'),
            (r'from\s+logger_system\s+import', 'logger_system.py (should be core.logger)'),
        ]
        
        violations = []
        
        for filepath in files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for pattern, desc in legacy_patterns:
                    if re.search(pattern, content):
                        violations.append((filepath.relative_to(self.root_path), desc))
            except Exception as e:
                pass
        
        if violations:
            self.warnings['imports'].extend(violations)
            print(f"{Colors.YELLOW}⚠ Found {len(violations)} legacy imports:{Colors.END}")
            for filepath, desc in violations[:5]:
                print(f"  - {filepath}: {desc}")
        else:
            self.passed['imports'].append("No legacy imports")
            print(f"{Colors.GREEN}✓ No legacy imports detected{Colors.END}")
    
    def audit_hardcoded_config(self):
        """Check for hardcoded configuration values"""
        patterns = [
            (r'api_key\s*=\s*["\']sk-', 'Hardcoded API key'),
            (r'temperature\s*=\s*0\.\d+(?!\s*#)', 'Hardcoded temperature'),
            (r'chunk_size\s*=\s*\d+(?!\s*#)', 'Hardcoded chunk_size'),
        ]
        
        files = list(self.root_path.rglob("*.py"))
        violations = []
        
        # Exceptions
        exceptions = ['config.py', 'settings.yaml', 'test_', 'audit_']
        
        for filepath in files:
            if any(exc in str(filepath) for exc in exceptions):
                continue
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for pattern, desc in patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        violations.append((
                            filepath.relative_to(self.root_path),
                            line_num,
                            desc
                        ))
            except Exception as e:
                pass
        
        if violations:
            self.warnings['hardcoded_config'].extend(violations)
            print(f"{Colors.YELLOW}⚠ Found {len(violations)} hardcoded config values:{Colors.END}")
            for filepath, line, desc in violations[:5]:
                print(f"  - {filepath}:{line} ({desc})")
            print(f"{Colors.YELLOW}  Configuration should come from settings.yaml{Colors.END}")
        else:
            self.passed['hardcoded_config'].append("No hardcoded configuration")
            print(f"{Colors.GREEN}✓ No hardcoded configuration values{Colors.END}")
    
    def _generate_report(self) -> Dict:
        """Generate final report"""
        print("\n" + "=" * 70)
        print(f"{Colors.BOLD}AUDIT SUMMARY{Colors.END}")
        print("=" * 70)
        
        total_issues = sum(len(v) for v in self.issues.values())
        total_warnings = sum(len(v) for v in self.warnings.values())
        total_passed = sum(len(v) for v in self.passed.values())
        
        print(f"{Colors.RED}Issues: {total_issues}{Colors.END}")
        print(f"{Colors.YELLOW}Warnings: {total_warnings}{Colors.END}")
        print(f"{Colors.GREEN}Passed: {total_passed}{Colors.END}")
        
        # Score calculation
        max_score = 100
        deductions = total_issues * 10 + total_warnings * 3
        score = max(0, max_score - deductions)
        
        print(f"\n{Colors.BOLD}Architecture Score: {score}/100{Colors.END}")
        
        if score >= 90:
            print(f"{Colors.GREEN}Grade: A (Enterprise-ready){Colors.END}")
        elif score >= 75:
            print(f"{Colors.YELLOW}Grade: B (Production-ready with minor issues){Colors.END}")
        elif score >= 60:
            print(f"{Colors.YELLOW}Grade: C (Needs improvement){Colors.END}")
        else:
            print(f"{Colors.RED}Grade: D (Major refactoring needed){Colors.END}")
        
        return {
            'score': score,
            'issues': dict(self.issues),
            'warnings': dict(self.warnings),
            'passed': dict(self.passed)
        }


def main():
    """Main audit execution"""
    if len(sys.argv) > 1:
        root_path = Path(sys.argv[1])
    else:
        root_path = Path(__file__).parent.parent
    
    if not root_path.exists():
        print(f"{Colors.RED}Error: Path {root_path} does not exist{Colors.END}")
        sys.exit(1)
    
    auditor = ArchitectureAuditor(root_path)
    report = auditor.run_full_audit()
    
    # Save report
    report_file = root_path / "AUDIT_REPORT.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\nFull report saved to: {report_file}")
    
    # Exit code
    if report['score'] < 60:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

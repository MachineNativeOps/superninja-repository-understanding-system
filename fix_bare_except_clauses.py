#!/usr/bin/env python3
"""
Fix bare except clauses - Phase 4C error handling improvements.
"""
import re
from pathlib import Path
from typing import List, Tuple

def find_bare_except_clauses(directory: str = ".") -> List[Tuple[str, int, str]]:
    """Find all bare except clauses in Python files."""
    findings = []
    
    python_files = list(Path(directory).rglob('*.py'))
    skip_dirs = ['.git', '__pycache__', 'node_modules', '.pytest_cache', 'venv', 'env', 'archive']
    python_files = [f for f in python_files if not any(d in str(f) for d in skip_dirs)]
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for i, line in enumerate(lines, 1):
                # Look for bare except
                if re.search(r'except\s*:\s*$', line):
                    # Check if it's already commented or in a docstring
                    stripped = line.strip()
                    if not stripped.startswith('#'):
                        findings.append((str(file_path), i, line.rstrip()))
                        
        except Exception as e:
            continue
    
    return findings

def fix_bare_except_in_file(file_path: str) -> int:
    """Fix bare except clauses in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace bare except with except Exception
        # Be careful not to replace comments
        fixed_content = re.sub(
            r'(\s+)except\s*:\s*$',
            r'\1except Exception as e:',
            content,
            flags=re.MULTILINE
        )
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        return 1
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return 0

def main():
    """Main function."""
    print("=" * 60)
    print("Phase 4C: Fix Bare Except Clauses")
    print("=" * 60)
    
    # Find all bare except clauses
    findings = find_bare_except_clauses()
    
    print(f"\n📊 Found {len(findings)} bare except clauses")
    
    if not findings:
        print("✨ No bare except clauses found!")
        return
    
    # Show sample findings
    print("\nSample findings:")
    for file_path, line_num, line_content in findings[:5]:
        print(f"  {file_path}:{line_num}")
        print(f"  {line_content}")
        print()
    
    # Fix them
    print("\n🔧 Fixing bare except clauses...")
    
    fixed_files = set()
    total_fixed = 0
    
    for file_path, line_num, line_content in findings:
        if file_path not in fixed_files:
            if fix_bare_except_in_file(file_path):
                fixed_files.add(file_path)
                total_fixed += 1
    
    print(f"\n✅ Fixed {len(fixed_files)} files with bare except clauses")
    print(f"   Total clauses fixed: {len(findings)}")
    
    # Verify the fixes
    print("\n🔍 Verifying fixes...")
    remaining = find_bare_except_clauses()
    
    if remaining:
        print(f"⚠️  {len(remaining)} bare except clauses remaining")
    else:
        print("✅ All bare except clauses have been fixed!")

if __name__ == "__main__":
    main()
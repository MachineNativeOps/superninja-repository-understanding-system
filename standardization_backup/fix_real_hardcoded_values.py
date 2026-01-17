#!/usr/bin/env python3
"""
Fix real hardcoded values that should be moved to configuration.
"""
import re
import os
from pathlib import Path
from typing import List, Dict, Any

def is_real_hardcoded_url(url: str, context: str, file_path: str) -> bool:
    """
    Determine if this is a real hardcoded URL that needs fixing.
    Filter out:
    - Regex patterns (with backslashes)
    - Test URLs
    - Documentation/example URLs
    - Localhost defaults (acceptable for development)
    """
    # Skip regex patterns
    if '\\\\' in url or '\\\\.' in url or '\\\\/' in url:
        return False
    
    # Skip test files
    if 'test' in file_path.lower():
        return False
    
    # Skip documentation and example URLs
    if any(domain in url for domain in ['example.com', 'json-schema.org', 'w3.org', 'iana.org']):
        return False
    
    # Skip localhost URLs (acceptable defaults)
    if 'localhost' in url or '127.0.0.1' in url or '0.0.0.0' in url:
        return False
    
    # Skip if it's in a default parameter
    if 'default=' in context.lower():
        return False
    
    # Skip if it's using os.getenv
    if 'os.getenv' in context or 'environ' in context:
        return False
    
    # Skip comments
    if context.strip().startswith('#'):
        return False
    
    # Skip docstrings
    if '"""' in context or "'''" in context:
        return False
    
    return True

def find_real_hardcoded_urls(directory: str = ".") -> List[Dict[str, Any]]:
    """Find real hardcoded URLs that need fixing."""
    results = []
    
    # Skip certain directories
    skip_dirs = ['.git', '__pycache__', 'node_modules', '.pytest_cache', 'venv', 'env', 'archive']
    
    python_files = list(Path(directory).rglob("*.py"))
    python_files = [f for f in python_files if not any(d in str(f) for d in skip_dirs)]
    python_files = [f for f in python_files if 'test' not in str(f).lower()]
    
    # URL pattern - more precise, requiring domain
    url_pattern = r'https?://[a-zA-Z0-9\-]+(\.[a-zA-Z0-9\-]+)+[a-zA-Z0-9\-._~:/?#[\]@!$&\'()*+,;=%]*'
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                for i, line in enumerate(lines, 1):
                    matches = re.finditer(url_pattern, line)
                    for match in matches:
                        url = match.group()
                        
                        if is_real_hardcoded_url(url, line, str(file_path)):
                            results.append({
                                'file': str(file_path),
                                'line': i,
                                'url': url,
                                'context': line.strip(),
                                'suggestion': f"os.getenv('API_URL', '{url}')"
                            })
                            
        except Exception as e:
            continue
    
    return results

def categorize_issues(issues: List[Dict]) -> Dict[str, List[Dict]]:
    """Categorize issues by type."""
    categories = {
        'api_endpoints': [],
        'external_services': [],
        'github_references': [],
        'other': []
    }
    
    for issue in issues:
        url = issue['url']
        
        if 'api.' in url or '/api/' in url:
            categories['api_endpoints'].append(issue)
        elif 'github.com' in url:
            categories['github_references'].append(issue)
        elif any(service in url for service in ['openai', 'aws', 'google', 'azure']):
            categories['external_services'].append(issue)
        else:
            categories['other'].append(issue)
    
    return categories

def generate_fix_script(issues: List[Dict]) -> str:
    """Generate a script to fix the issues."""
    script_lines = [
        "#!/bin/bash",
        "# Auto-generated script to fix hardcoded URLs",
        "# Run this to backup files before making changes",
        "",
        "echo 'Creating backups...'",
        "mkdir -p backup_phase4b",
        ""
    ]
    
    # Group by file to avoid duplicate backups
    files_to_fix = set(issue['file'] for issue in issues)
    
    for file_path in files_to_fix:
        relative_path = str(Path(file_path).relative_to('.'))
        script_lines.append(f"cp {relative_path} backup_phase4b/")
    
    script_lines.extend([
        "",
        "echo 'Backups created in backup_phase4b/'",
        "echo 'Please review the changes manually before committing'",
        ""
    ])
    
    return '\n'.join(script_lines)

def main():
    """Main function."""
    print("=" * 60)
    print("Phase 4B: Real Hardcoded Values Analysis")
    print("=" * 60)
    
    # Find real issues
    issues = find_real_hardcoded_urls()
    
    # Categorize
    categorized = categorize_issues(issues)
    
    # Print summary
    print(f"\n📊 Analysis Results:")
    print(f"   Total issues found: {len(issues)}")
    print(f"   API endpoints: {len(categorized['api_endpoints'])}")
    print(f"   External services: {len(categorized['external_services'])}")
    print(f"   GitHub references: {len(categorized['github_references'])}")
    print(f"   Other: {len(categorized['other'])}")
    
    # Generate fix script
    if issues:
        fix_script = generate_fix_script(issues)
        
        with open('fix_hardcoded_urls.sh', 'w') as f:
            f.write(fix_script)
        
        os.chmod('fix_hardcoded_urls.sh', 0o755)
        
        print(f"\n📝 Generated fix script: fix_hardcoded_urls.sh")
        print(f"   Run: ./fix_hardcoded_urls.sh to create backups")
        
        # Show sample issues
        print(f"\n⚠️  Sample Issues:")
        for issue in issues[:5]:
            print(f"   File: {issue['file']}:{issue['line']}")
            print(f"   URL: {issue['url']}")
            print(f"   Suggestion: {issue['suggestion']}")
            print()
    else:
        print("\n✨ No real hardcoded URL issues found!")
        print("   All URLs are either:")
        print("   - Localhost defaults (acceptable)")
        print("   - Regex patterns")
        print("   - Reference URLs")
        print("   - Already using environment variables")
    
    return issues

if __name__ == "__main__":
    issues = main()
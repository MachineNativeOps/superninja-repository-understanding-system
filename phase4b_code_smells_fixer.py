#!/usr/bin/env python3
"""
Phase 4B: Fix code smells - hardcoded URLs and configuration values
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
import json

def is_problematic_hardcoded(url: str, context: str) -> Tuple[bool, str]:
    """
    Determine if a hardcoded URL is problematic.
    Returns (is_problematic, reason)
    """
    # These are acceptable defaults or reference URLs
    acceptable_patterns = [
        'localhost', '127.0.0.1', '0.0.0.0',  # Development defaults
        'json-schema.org', 'example.com',      # Reference URLs
        'w3.org', 'iana.org',                   # Standard URLs
    ]
    
    # These patterns in context indicate it's a default parameter
    acceptable_contexts = [
        'default=', 'DEFAULT_', '= ',          # Default values
        'os.getenv', 'environ',                # Environment variable fallbacks
        '# ', '// ',                            # Comments
        '"""', "'''",                           # Docstrings
        'http://localhost:',                   # Default development URLs
    ]
    
    # Check if URL itself is acceptable
    for pattern in acceptable_patterns:
        if pattern in url:
            return False, f"Acceptable reference URL ({pattern})"
    
    # Check context
    for context_pattern in acceptable_contexts:
        if context_pattern in context:
            return False, f"Acceptable context ({context_pattern})"
    
    # Check if it's in a test file
    if 'test' in url or 'spec' in url:
        return False, "Test file"
    
    return True, "Potentially problematic hardcoded URL"

def find_problematic_hardcoded_values(directory: str = ".") -> Dict[str, Any]:
    """Find problematic hardcoded values."""
    results = {
        'problematic_urls': [],
        'acceptable_defaults': [],
        'summary': {}
    }
    
    python_files = list(Path(directory).rglob("*.py"))
    
    # Skip certain directories
    skip_dirs = ['.git', '__pycache__', 'node_modules', '.pytest_cache', 'venv', 'env']
    python_files = [f for f in python_files if not any(d in str(f) for d in skip_dirs)]
    
    # Skip test files
    python_files = [f for f in python_files if 'test' not in str(f).lower()]
    
    url_patterns = [
        r'http[s]?://[^\s"\'<>]+',
        r'localhost:\d+',
        r'127\.0\.0\.1:\d+',
    ]
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    # Skip comments
                    stripped = line.strip()
                    if stripped.startswith('#'):
                        continue
                    
                    # Skip docstrings
                    if '"""' in line or "'''" in line:
                        continue
                    
                    for pattern in url_patterns:
                        matches = re.finditer(pattern, line)
                        for match in matches:
                            url = match.group()
                            is_problematic, reason = is_problematic_hardcoded(url, stripped)
                            
                            finding = {
                                'file': str(file_path),
                                'line': i,
                                'url': url,
                                'context': stripped,
                                'reason': reason
                            }
                            
                            if is_problematic:
                                results['problematic_urls'].append(finding)
                            else:
                                results['acceptable_defaults'].append(finding)
                                
        except Exception as e:
            continue
    
    # Generate summary
    results['summary'] = {
        'total_files_scanned': len(python_files),
        'problematic_urls_found': len(results['problematic_urls']),
        'acceptable_defaults_found': len(results['acceptable_defaults']),
    }
    
    return results

def generate_fix_suggestions(problematic_urls: List[Dict]) -> List[Dict]:
    """Generate fix suggestions for problematic URLs."""
    suggestions = []
    
    for item in problematic_urls:
        url = item['url']
        file = item['file']
        line = item['line']
        
        suggestion = {
            'file': file,
            'line': line,
            'current': url,
            'suggested': f"os.getenv('API_URL', '{url}')",
            'explanation': "Move hardcoded URL to environment variable"
        }
        suggestions.append(suggestion)
    
    return suggestions

def create_config_recommendations() -> Dict[str, Any]:
    """Create recommendations for configuration management."""
    return {
        'create_env_file': True,
        'env_variables': [
            'LOCAL_API_URL',
            'SERVICE_URL', 
            'DATABASE_URL',
            'REDIS_URL',
            'API_ENDPOINT',
        ],
        'config_file_structure': {
            'config/__init__.py': 'Configuration module',
            'config/settings.py': 'Application settings',
            '.env.example': 'Environment variables template',
            '.env': 'Actual environment variables (gitignored)',
        }
    }

def main():
    """Main function."""
    print("=" * 60)
    print("Phase 4B: Code Smells Analysis - Hardcoded Values")
    print("=" * 60)
    
    # Analyze
    results = find_problematic_hardcoded_values()
    
    # Print summary
    print(f"\n📊 Analysis Summary:")
    print(f"   Files scanned: {results['summary']['total_files_scanned']}")
    print(f"   Problematic URLs: {results['summary']['problematic_urls_found']}")
    print(f"   Acceptable defaults: {results['summary']['acceptable_defaults_found']}")
    
    # Generate suggestions
    suggestions = generate_fix_suggestions(results['problematic_urls'])
    config_recs = create_config_recommendations()
    
    # Create report
    report = {
        'analysis_results': results,
        'fix_suggestions': suggestions[:20],  # Limit to first 20
        'configuration_recommendations': config_recs
    }
    
    # Save report
    with open('phase4b_code_smells_analysis.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Analysis complete!")
    print(f"📄 Detailed report saved to: phase4b_code_smells_analysis.json")
    
    # Print sample findings
    if results['problematic_urls']:
        print(f"\n⚠️  Found {len(results['problematic_urls'])} potentially problematic URLs")
        print("   Sample issues:")
        for item in results['problematic_urls'][:5]:
            print(f"   - {item['file']}:{item['line']}")
            print(f"     URL: {item['url']}")
            print(f"     Reason: {item['reason']}")
    else:
        print("\n✨ No problematic hardcoded URLs found!")
        print("   All hardcoded values appear to be acceptable defaults or references.")
    
    # Print recommendations
    print(f"\n💡 Configuration Recommendations:")
    print(f"   - Create config/ directory structure")
    print(f"   - Move sensitive values to .env file")
    print(f"   - Use environment variables for configuration")
    print(f"   - Update {len(suggestions)} files with suggested fixes")

if __name__ == "__main__":
    main()
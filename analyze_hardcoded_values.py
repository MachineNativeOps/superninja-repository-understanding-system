#!/usr/bin/env python3
"""
Analyze hardcoded URLs and configuration values in the codebase.
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Any
import json

def find_hardcoded_urls(directory: str = ".") -> Dict[str, List[str]]:
    """Find hardcoded URLs in Python files."""
    url_patterns = [
        r'http[s]?://[^\s"\'<>]+',
        r'localhost:\d+',
        r'127\.0\.0\.1:\d+',
        r'0\.0\.0\.0:\d+',
    ]
    
    results = {}
    python_files = list(Path(directory).rglob("*.py"))
    
    for file_path in python_files:
        # Skip test files
        if 'test' in str(file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    for pattern in url_patterns:
                        matches = re.finditer(pattern, line)
                        for match in matches:
                            url = match.group()
                            # Filter out comments and docstrings
                            stripped = line.strip()
                            if not (stripped.startswith('#') or 
                                   ('"""' in line and 'http' not in line)):
                                if str(file_path) not in results:
                                    results[str(file_path)] = []
                                results[str(file_path)].append({
                                    'line': i,
                                    'url': url,
                                    'context': line.strip()
                                })
        except Exception as e:
            continue
    
    return results

def find_hardcoded_config_values(directory: str = ".") -> Dict[str, List[str]]:
    """Find hardcoded configuration values."""
    config_patterns = [
        r'password\s*=\s*["\'][^"\']+["\']',
        r'secret\s*=\s*["\'][^"\']+["\']',
        r'token\s*=\s*["\'][^"\']+["\']',
        r'api_key\s*=\s*["\'][^"\']+["\']',
    ]
    
    results = {}
    python_files = list(Path(directory).rglob("*.py"))
    
    for file_path in python_files:
        # Skip test files
        if 'test' in str(file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    for pattern in config_patterns:
                        matches = re.finditer(pattern, line, re.IGNORECASE)
                        for match in matches:
                            if str(file_path) not in results:
                                results[str(file_path)] = []
                            results[str(file_path)].append({
                                'line': i,
                                'value': match.group(),
                                'context': line.strip()
                            })
        except Exception as e:
            continue
    
    return results

def analyze_results(urls: Dict, configs: Dict) -> Dict[str, Any]:
    """Analyze and categorize the results."""
    total_url_files = len(urls)
    total_config_files = len(configs)
    
    # Categorize URLs
    localhost_urls = []
    external_urls = []
    
    for file, findings in urls.items():
        for finding in findings:
            url = finding['url']
            if 'localhost' in url or '127.0.0.1' in url:
                localhost_urls.append((file, finding))
            elif 'json-schema.org' in url or 'example.com' in url:
                continue  # These are reference URLs, not problematic
            else:
                external_urls.append((file, finding))
    
    return {
        'summary': {
            'total_files_with_urls': total_url_files,
            'total_files_with_configs': total_config_files,
            'localhost_urls_count': len(localhost_urls),
            'external_urls_count': len(external_urls),
        },
        'localhost_urls': localhost_urls[:10],  # Limit to first 10
        'external_urls': external_urls[:10],   # Limit to first 10
        'config_values': list(configs.items())[:10]  # Limit to first 10
    }

def main():
    """Main analysis function."""
    print("Analyzing hardcoded values in codebase...")
    
    urls = find_hardcoded_urls()
    configs = find_hardcoded_config_values()
    analysis = analyze_results(urls, configs)
    
    # Print summary
    print("\n=== Analysis Summary ===")
    print(f"Files with hardcoded URLs: {analysis['summary']['total_files_with_urls']}")
    print(f"Files with hardcoded configs: {analysis['summary']['total_files_with_configs']}")
    print(f"Localhost URLs found: {analysis['summary']['localhost_urls_count']}")
    print(f"External URLs found: {analysis['summary']['external_urls_count']}")
    
    # Save to file
    with open('hardcoded_values_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print("\nDetailed analysis saved to: hardcoded_values_analysis.json")
    
    # Print sample findings
    if analysis['localhost_urls']:
        print("\n=== Sample Localhost URLs ===")
        for file, finding in analysis['localhost_urls'][:5]:
            print(f"{file}:{finding['line']} - {finding['url']}")
    
    if analysis['external_urls']:
        print("\n=== Sample External URLs ===")
        for file, finding in analysis['external_urls'][:5]:
            print(f"{file}:{finding['line']} - {finding['url']}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Phase 4C: Medium-Risk Issue Review
Review and categorize remaining medium-risk issues for prioritization.
"""
import json
import re
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict

def analyze_code_quality_issues() -> Dict[str, Any]:
    """Analyze remaining code quality issues."""
    issues = {
        'import_order': [],
        'unused_imports': [],
        'code_style': [],
        'documentation': [],
        'error_handling': []
    }
    
    # Scan Python files for common medium-risk issues
    python_files = list(Path('.').rglob('*.py'))
    skip_dirs = ['.git', '__pycache__', 'node_modules', '.pytest_cache', 'venv', 'env', 'archive']
    python_files = [f for f in python_files if not any(d in str(f) for d in skip_dirs)]
    python_files = [f for f in python_files if 'test' not in str(f).lower()]
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                # Check for import order issues
                imports = []
                for i, line in enumerate(lines, 1):
                    stripped = line.strip()
                    
                    # Import order
                    if stripped.startswith('import ') or stripped.startswith('from '):
                        imports.append((i, stripped))
                
                # Analyze import order
                stdlib_imports = []
                third_party_imports = []
                local_imports = []
                
                stdlib_modules = ['os', 'sys', 'json', 're', 'pathlib', 'typing', 'datetime', 
                                'time', 'hashlib', 'shutil', 'subprocess', 'logging']
                
                for line_num, import_line in imports:
                    if any(module in import_line for module in stdlib_modules):
                        stdlib_imports.append((line_num, import_line))
                    elif 'from .' in import_line or 'from ..' in import_line:
                        local_imports.append((line_num, import_line))
                    else:
                        third_party_imports.append((line_num, import_line))
                
                # Check if imports are in wrong order
                if stdlib_imports and third_party_imports:
                    first_stdlib = stdlib_imports[0][0]
                    first_third_party = third_party_imports[0][0]
                    
                    if first_third_party < first_stdlib:
                        issues['import_order'].append({
                            'file': str(file_path),
                            'line': first_third_party,
                            'issue': 'Third-party import before standard library import',
                            'severity': 'low',
                            'suggestion': 'Reorder imports: stdlib -> third-party -> local'
                        })
                
                # Check for bare except
                for i, line in enumerate(lines, 1):
                    if re.search(r'except\s*:', line) and 'except:' in line:
                        issues['error_handling'].append({
                            'file': str(file_path),
                            'line': i,
                            'issue': 'Bare except clause',
                            'severity': 'medium',
                            'suggestion': 'Specify exception type: except Exception as e:'
                        })
                
        except Exception as e:
            continue
    
    return issues

def categorize_by_severity(issues: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
    """Categorize issues by severity."""
    categorized = {
        'high': [],
        'medium': [],
        'low': []
    }
    
    for category, issue_list in issues.items():
        for issue in issue_list:
            severity = issue.get('severity', 'low')
            categorized[severity].append(issue)
    
    return categorized

def generate_recommendations(issues: Dict[str, List[Dict]]) -> List[Dict[str, Any]]:
    """Generate prioritized recommendations."""
    recommendations = []
    
    # Count issues by category
    category_counts = {category: len(issue_list) 
                      for category, issue_list in issues.items()}
    
    # Generate recommendations based on priority
    if category_counts.get('error_handling', 0) > 0:
        recommendations.append({
            'priority': 'high',
            'category': 'Error Handling',
            'count': category_counts['error_handling'],
            'action': 'Fix bare except clauses',
            'rationale': 'Bare except can hide unexpected errors and make debugging difficult',
            'effort': 'medium'
        })
    
    if category_counts.get('import_order', 0) > 10:
        recommendations.append({
            'priority': 'medium',
            'category': 'Code Style',
            'count': category_counts['import_order'],
            'action': 'Reorder imports according to PEP 8',
            'rationale': 'Improves code readability and follows Python conventions',
            'effort': 'low'
        })
    
    return recommendations

def create_review_report(issues: Dict[str, List[Dict]], 
                        recommendations: List[Dict]) -> Dict[str, Any]:
    """Create comprehensive review report."""
    categorized = categorize_by_severity(issues)
    
    total_issues = sum(len(issue_list) for issue_list in issues.values())
    
    return {
        'summary': {
            'total_issues_found': total_issues,
            'high_severity': len(categorized['high']),
            'medium_severity': len(categorized['medium']),
            'low_severity': len(categorized['low']),
            'categories_analyzed': len(issues)
        },
        'issues_by_category': issues,
        'issues_by_severity': categorized,
        'recommendations': recommendations,
        'status': 'review_complete'
    }

def main():
    """Main function."""
    print("=" * 60)
    print("Phase 4C: Medium-Risk Issue Review")
    print("=" * 60)
    
    # Analyze issues
    issues = analyze_code_quality_issues()
    
    # Generate recommendations
    recommendations = generate_recommendations(issues)
    
    # Create report
    report = create_review_report(issues, recommendations)
    
    # Save report
    with open('phase4c_review_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print(f"\n📊 Review Summary:")
    print(f"   Total issues found: {report['summary']['total_issues_found']}")
    print(f"   High severity: {report['summary']['high_severity']}")
    print(f"   Medium severity: {report['summary']['medium_severity']}")
    print(f"   Low severity: {report['summary']['low_severity']}")
    
    # Print recommendations
    if recommendations:
        print(f"\n💡 Prioritized Recommendations:")
        for rec in recommendations:
            print(f"   [{rec['priority'].upper()}] {rec['category']}")
            print(f"   Action: {rec['action']}")
            print(f"   Count: {rec['count']} issues")
            print(f"   Effort: {rec['effort']}")
            print(f"   Rationale: {rec['rationale']}")
            print()
    else:
        print("\n✨ No major issues found!")
        print("   Code quality is good.")
    
    print(f"📄 Detailed report saved to: phase4c_review_report.json")
    
    return report

if __name__ == "__main__":
    report = main()
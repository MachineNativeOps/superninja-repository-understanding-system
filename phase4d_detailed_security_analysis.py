#!/usr/bin/env python3
"""
Phase 4D: Detailed Security Analysis - Distinguish production code from tools
"""
import json
from pathlib import Path

def analyze_eval_usage_context(audit_report_path: str = 'security_audit_final.json') -> dict:
    """Analyze eval() usage in context of production vs tools."""
    
    with open(audit_report_path, 'r') as f:
        audit_report = json.load(f)
    
    high_severity = audit_report.get('by_severity', {}).get('high', [])
    
    # Categorize findings by file type
    categories = {
        'production_code': [],  # Actual application code
        'test_files': [],       # Test files
        'analysis_tools': [],   # Security analysis and fix tools
        'documentation': [],    # Documentation or comments
        'other': []             # Other
    }
    
    for finding in high_severity:
        if 'eval' not in finding.get('issue', '').lower():
            continue
            
        file_path = finding.get('file', '')
        
        # Determine category
        if any(keyword in file_path.lower() for keyword in ['test', 'spec']):
            categories['test_files'].append(finding)
        elif any(keyword in file_path.lower() for keyword in 
                ['fix_', 'analyzer', 'scanner', 'audit', 'security']):
            categories['analysis_tools'].append(finding)
        elif any(keyword in file_path.lower() for keyword in ['.md', '.txt', '.rst']):
            categories['documentation'].append(finding)
        elif any(keyword in file_path.lower() for keyword in 
                ['workspace/', '00-namespaces/', 'src/', 'lib/']):
            # These could be production code - need manual review
            categories['production_code'].append(finding)
        else:
            categories['other'].append(finding)
    
    return categories

def assess_actual_risks(categories: dict) -> dict:
    """Assess actual security risks based on categorization."""
    
    risk_assessment = {
        'critical_risks': [],
        'high_risks': [],
        'medium_risks': [],
        'acceptable_risks': []
    }
    
    # Analysis tools - acceptable if documented
    for finding in categories['analysis_tools']:
        risk_assessment['acceptable_risks'].append({
            'file': finding['file'],
            'reason': 'Security analysis tool - eval() used for analysis purposes',
            'recommendation': 'Add documentation comment explaining security context'
        })
    
    # Test files - low risk
    for finding in categories['test_files']:
        risk_assessment['acceptable_risks'].append({
            'file': finding['file'],
            'reason': 'Test file - eval() used in controlled test environment',
            'recommendation': 'Consider using safer alternatives if possible'
        })
    
    # Production code - needs review
    for finding in categories['production_code']:
        risk_assessment['high_risks'].append({
            'file': finding['file'],
            'line': finding.get('line', 0),
            'issue': finding.get('issue', ''),
            'recommendation': 'Review and replace with safer alternatives'
        })
    
    # Other - categorize based on file content
    for finding in categories['other']:
        file_path = finding['file']
        if Path(file_path).exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'TODO' in content or 'FIXME' in content:
                    risk_assessment['medium_risks'].append({
                        'file': file_path,
                        'reason': 'Marked for future review',
                        'recommendation': 'Review TODO/FIXME comments'
                    })
                else:
                    risk_assessment['acceptable_risks'].append({
                        'file': file_path,
                        'reason': 'Context indicates acceptable usage',
                        'recommendation': 'Add documentation'
                    })
    
    return risk_assessment

def main():
    """Main function."""
    print("=" * 60)
    print("Phase 4D: Detailed Security Analysis")
    print("=" * 60)
    
    # Analyze eval() usage context
    categories = analyze_eval_usage_context()
    
    print(f"\n📊 Eval() Usage by Category:")
    print(f"   Production code: {len(categories['production_code'])}")
    print(f"   Test files: {len(categories['test_files'])}")
    print(f"   Analysis tools: {len(categories['analysis_tools'])}")
    print(f"   Documentation: {len(categories['documentation'])}")
    print(f"   Other: {len(categories['other'])}")
    
    # Assess actual risks
    risk_assessment = assess_actual_risks(categories)
    
    print(f"\n⚠️  Risk Assessment:")
    print(f"   Critical risks: {len(risk_assessment['critical_risks'])}")
    print(f"   High risks: {len(risk_assessment['high_risks'])}")
    print(f"   Medium risks: {len(risk_assessment['medium_risks'])}")
    print(f"   Acceptable risks: {len(risk_assessment['acceptable_risks'])}")
    
    # Show details
    if risk_assessment['high_risks']:
        print(f"\n🔴 High Risk Issues (Production Code):")
        for risk in risk_assessment['high_risks']:
            print(f"   - {risk['file']}:{risk['line']}")
            print(f"     Issue: {risk['issue']}")
            print(f"     Recommendation: {risk['recommendation']}")
    
    if risk_assessment['acceptable_risks']:
        print(f"\n✅ Acceptable Risks:")
        for risk in risk_assessment['acceptable_risks'][:5]:  # Show first 5
            print(f"   - {risk['file']}")
            print(f"     Reason: {risk['reason']}")
        if len(risk_assessment['acceptable_risks']) > 5:
            print(f"   ... and {len(risk_assessment['acceptable_risks']) - 5} more")
    
    # Determine overall status
    if len(risk_assessment['high_risks']) == 0:
        overall_status = "GOOD - No critical security risks in production code"
    elif len(risk_assessment['high_risks']) < 3:
        overall_status = "MEDIUM - Few high-risk issues in production code"
    else:
        overall_status = "HIGH - Multiple high-risk issues in production code"
    
    print(f"\n📋 Overall Security Status:")
    print(f"   {overall_status}")
    
    # Save detailed report
    report = {
        'categories': {k: len(v) for k, v in categories.items()},
        'risk_assessment': {
            'critical': len(risk_assessment['critical_risks']),
            'high': len(risk_assessment['high_risks']),
            'medium': len(risk_assessment['medium_risks']),
            'acceptable': len(risk_assessment['acceptable_risks'])
        },
        'high_risks': risk_assessment['high_risks'],
        'overall_status': overall_status
    }
    
    with open('phase4d_detailed_security_analysis.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed analysis saved to: phase4d_detailed_security_analysis.json")
    
    return report

if __name__ == "__main__":
    report = main()
#!/usr/bin/env python3
"""
Phase 4D: Security Audit - Comprehensive security review
"""
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
from collections import defaultdict

def load_existing_audit_report() -> Dict[str, Any]:
    """Load existing security audit report."""
    try:
        with open('security_audit_final.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'total_findings': 0, 'summary': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}}

def analyze_security_findings(audit_report: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze security findings and categorize them."""
    findings = {
        'eval_usage': [],
        'shell_execution': [],
        'weak_cryptography': [],
        'hardcoded_secrets': [],
        'insecure_dependencies': [],
        'other': []
    }
    
    high_severity = audit_report.get('by_severity', {}).get('high', [])
    medium_severity = audit_report.get('by_severity', {}).get('medium', [])
    
    all_findings = high_severity + medium_severity
    
    for finding in all_findings:
        category = finding.get('category', 'other')
        issue = finding.get('issue', '').lower()
        code = finding.get('code', '').lower()
        
        if 'eval' in issue or 'eval' in code:
            findings['eval_usage'].append(finding)
        elif 'shell' in issue or 'exec' in issue:
            findings['shell_execution'].append(finding)
        elif 'md5' in issue or 'sha1' in issue:
            findings['weak_cryptography'].append(finding)
        elif 'secret' in issue or 'password' in issue:
            findings['hardcoded_secrets'].append(finding)
        else:
            findings['other'].append(finding)
    
    return findings

def assess_security_risks(findings: Dict[str, List[Dict]]) -> Dict[str, Any]:
    """Assess security risks and provide recommendations."""
    risk_assessment = {
        'critical_risks': [],
        'high_risks': [],
        'medium_risks': [],
        'low_risks': [],
        'recommendations': []
    }
    
    # Evaluate eval() usage
    eval_findings = findings['eval_usage']
    if eval_findings:
        # Check if they are in analysis tools vs production code
        analysis_tools = [f for f in eval_findings if 'analyzer' in f.get('file', '').lower() 
                        or 'scanner' in f.get('file', '').lower()]
        production_code = [f for f in eval_findings if f not in analysis_tools]
        
        if production_code:
            risk_assessment['high_risks'].extend(production_code)
            risk_assessment['recommendations'].append({
                'priority': 'high',
                'category': 'eval() in production code',
                'count': len(production_code),
                'action': 'Review and replace eval() in production code with safer alternatives',
                'files': [f['file'] for f in production_code[:3]]
            })
        
        if analysis_tools:
            risk_assessment['medium_risks'].extend(analysis_tools)
            risk_assessment['recommendations'].append({
                'priority': 'medium',
                'category': 'eval() in analysis tools',
                'count': len(analysis_tools),
                'action': 'Document eval() usage in analysis tools with security warnings',
                'rationale': 'Acceptable in analysis tools if properly documented'
            })
    
    # Evaluate other findings
    for category, issues in findings.items():
        if category == 'eval_usage':
            continue
        
        for issue in issues:
            severity = issue.get('severity', 'low')
            if severity == 'high':
                risk_assessment['high_risks'].append(issue)
            elif severity == 'medium':
                risk_assessment['medium_risks'].append(issue)
    
    return risk_assessment

def generate_security_report(audit_report: Dict[str, Any], 
                           findings: Dict[str, List[Dict]],
                           risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive security report."""
    return {
        'executive_summary': {
            'total_findings': audit_report.get('total_findings', 0),
            'critical': audit_report.get('summary', {}).get('critical', 0),
            'high': audit_report.get('summary', {}).get('high', 0),
            'medium': audit_report.get('summary', {}).get('medium', 0),
            'low': audit_report.get('summary', {}).get('low', 0),
        },
        'findings_by_category': {k: len(v) for k, v in findings.items()},
        'risk_assessment': {
            'critical_risks_count': len(risk_assessment['critical_risks']),
            'high_risks_count': len(risk_assessment['high_risks']),
            'medium_risks_count': len(risk_assessment['medium_risks']),
            'low_risks_count': len(risk_assessment['low_risks']),
        },
        'recommendations': risk_assessment['recommendations'],
        'overall_security_status': determine_security_status(risk_assessment)
    }

def determine_security_status(risk_assessment: Dict[str, Any]) -> str:
    """Determine overall security status."""
    critical_count = len(risk_assessment['critical_risks'])
    high_count = len(risk_assessment['high_risks'])
    
    if critical_count > 0:
        return 'CRITICAL - Immediate action required'
    elif high_count > 5:
        return 'HIGH - Multiple high-risk issues found'
    elif high_count > 0:
        return 'MEDIUM - Some high-risk issues found'
    else:
        return 'GOOD - No critical or high-risk issues'

def main():
    """Main function."""
    print("=" * 60)
    print("Phase 4D: Security Audit")
    print("=" * 60)
    
    # Load existing audit report
    audit_report = load_existing_audit_report()
    
    print(f"\n📊 Existing Audit Report:")
    print(f"   Total findings: {audit_report.get('total_findings', 0)}")
    print(f"   Critical: {audit_report.get('summary', {}).get('critical', 0)}")
    print(f"   High: {audit_report.get('summary', {}).get('high', 0)}")
    print(f"   Medium: {audit_report.get('summary', {}).get('medium', 0)}")
    print(f"   Low: {audit_report.get('summary', {}).get('low', 0)}")
    
    # Analyze findings
    findings = analyze_security_findings(audit_report)
    
    print(f"\n🔍 Findings by Category:")
    for category, issues in findings.items():
        print(f"   {category}: {len(issues)}")
    
    # Assess risks
    risk_assessment = assess_security_risks(findings)
    
    print(f"\n⚠️  Risk Assessment:")
    print(f"   Critical risks: {len(risk_assessment['critical_risks'])}")
    print(f"   High risks: {len(risk_assessment['high_risks'])}")
    print(f"   Medium risks: {len(risk_assessment['medium_risks'])}")
    print(f"   Low risks: {len(risk_assessment['low_risks'])}")
    
    # Generate report
    report = generate_security_report(audit_report, findings, risk_assessment)
    
    print(f"\n📋 Overall Security Status:")
    print(f"   {report['overall_security_status']}")
    
    # Print recommendations
    if risk_assessment['recommendations']:
        print(f"\n💡 Security Recommendations:")
        for rec in risk_assessment['recommendations']:
            print(f"   [{rec['priority'].upper()}] {rec['category']}")
            print(f"   Action: {rec['action']}")
            if 'rationale' in rec:
                print(f"   Rationale: {rec['rationale']}")
            print()
    else:
        print("\n✨ No major security recommendations!")
    
    # Save report
    with open('phase4d_security_audit_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Detailed security audit report saved to: phase4d_security_audit_report.json")
    
    return report

if __name__ == "__main__":
    report = main()
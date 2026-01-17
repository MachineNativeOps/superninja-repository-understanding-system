#!/usr/bin/env python3
"""
命名分析工具 - 掃描整個項目並識別命名問題
"""

import os
import re
import ast
import json
from pathlib import Path
from typing import Dict, List, Any, Set
from collections import defaultdict

class NamingAnalyzer:
    def __init__(self, workspace: str = "/workspace"):
        self.workspace = Path(workspace)
        self.issues = defaultdict(list)
        self.stats = {
            'total_files': 0,
            'total_classes': 0,
            'total_functions': 0,
            'total_variables': 0,
            'issues_found': 0
        }
        
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """分析單個Python文件的命名"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            file_issues = {
                'file': str(file_path.relative_to(self.workspace)),
                'classes': [],
                'functions': [],
                'variables': []
            }
            
            # 分析類名
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self.stats['total_classes'] += 1
                    if not self.is_pascal_case(node.name):
                        file_issues['classes'].append({
                            'name': node.name,
                            'line': node.lineno,
                            'issue': 'Class name should be PascalCase',
                            'severity': 'medium'
                        })
                
                # 分析函數名
                elif isinstance(node, ast.FunctionDef):
                    self.stats['total_functions'] += 1
                    # 跳過魔術方法和雙下劃線方法
                    if node.name.startswith('__') and node.name.endswith('__'):
                        continue
                    # 跳過私有方法（單下劃線開頭）
                    if node.name.startswith('_') and not node.name.startswith('__'):
                        continue
                    if not self.is_snake_case(node.name):
                        file_issues['functions'].append({
                            'name': node.name,
                            'line': node.lineno,
                            'issue': 'Function name should be snake_case',
                            'severity': 'medium'
                        })
                
                # 分析變量名
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            self.stats['total_variables'] += 1
                            # 跳過Python特殊變量（雙下劃線）
                            if target.id.startswith('__') and target.id.endswith('__'):
                                continue
                            # 跳過私有變量（單下劃線開頭）
                            if target.id.startswith('_'):
                                continue
                            # 檢查是否為常量（全大寫）
                            if target.id.isupper():
                                if not self.is_upper_snake_case(target.id):
                                    file_issues['variables'].append({
                                        'name': target.id,
                                        'line': node.lineno,
                                        'issue': 'Constant name should be UPPER_SNAKE_CASE',
                                        'severity': 'low'
                                    })
                            else:
                                if not self.is_snake_case(target.id):
                                    file_issues['variables'].append({
                                        'name': target.id,
                                        'line': node.lineno,
                                        'issue': 'Variable name should be snake_case',
                                        'severity': 'low'
                                    })
            
            return file_issues
            
        except Exception as e:
            return {'error': str(e)}
    
    def is_pascal_case(self, name: str) -> bool:
        """檢查是否為PascalCase"""
        return re.match(r'^[A-Z][a-zA-Z0-9]*$', name) is not None
    
    def is_snake_case(self, name: str) -> bool:
        """檢查是否為snake_case"""
        return re.match(r'^[a-z][a-z0-9_]*$', name) is not None
    
    def is_upper_snake_case(self, name: str) -> bool:
        """檢查是否為UPPER_SNAKE_CASE"""
        return re.match(r'^[A-Z][A-Z0-9_]*$', name) is not None
    
    def scan_project(self) -> Dict[str, Any]:
        """掃描整個項目"""
        print("🔍 開始掃描項目...")
        
        all_issues = []
        
        for py_file in self.workspace.rglob("*.py"):
            # 跳過測試文件和臨時文件
            if any(skip in str(py_file) for skip in [
                "__pycache__", ".pyc", "node_modules",
                ".git", "venv", "env", "backup",
                "final_cleanup_backup", "standardization_backup",
                "cleanup_backup"
            ]):
                continue
            
            self.stats['total_files'] += 1
            issues = self.analyze_file(py_file)
            
            if 'error' not in issues:
                if issues['classes']:
                    all_issues.extend([{
                        **issue,
                        'type': 'class',
                        'file': issues['file']
                    } for issue in issues['classes']])
                    self.stats['issues_found'] += len(issues['classes'])
                
                if issues['functions']:
                    all_issues.extend([{
                        **issue,
                        'type': 'function',
                        'file': issues['file']
                    } for issue in issues['functions']])
                    self.stats['issues_found'] += len(issues['functions'])
                
                if issues['variables']:
                    all_issues.extend([{
                        **issue,
                        'type': 'variable',
                        'file': issues['file']
                    } for issue in issues['variables']])
                    self.stats['issues_found'] += len(issues['variables'])
        
        print(f"✅ 掃描完成！分析了 {self.stats['total_files']} 個文件")
        
        return {
            'stats': self.stats,
            'issues': all_issues[:100],  # 限制為前100個問題
            'summary': self.generate_summary(all_issues)
        }
    
    def generate_summary(self, issues: List[Dict]) -> Dict[str, Any]:
        """生成問題摘要"""
        summary = {
            'by_type': defaultdict(int),
            'by_severity': defaultdict(int),
            'by_file': defaultdict(int)
        }
        
        for issue in issues:
            summary['by_type'][issue['type']] += 1
            summary['by_severity'][issue['severity']] += 1
            summary['by_file'][issue['file']] += 1
        
        return {
            'by_type': dict(summary['by_type']),
            'by_severity': dict(summary['by_severity']),
            'top_files': sorted(summary['by_file'].items(), key=lambda x: x[1], reverse=True)[:10]
        }
    
    def save_report(self, report: Dict[str, Any], output_file: str = "naming_analysis_report.json"):
        """保存報告到文件"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"📄 報告已保存到: {output_file}")

def main():
    analyzer = NamingAnalyzer()
    
    # 掃描項目
    report = analyzer.scan_project()
    
    # 保存報告
    analyzer.save_report(report)
    
    # 打印摘要
    print("\n" + "="*60)
    print("命名分析摘要")
    print("="*60)
    print(f"📊 統計信息:")
    print(f"   總文件數: {report['stats']['total_files']}")
    print(f"   總類數: {report['stats']['total_classes']}")
    print(f"   總函數數: {report['stats']['total_functions']}")
    print(f"   總變量數: {report['stats']['total_variables']}")
    print(f"   發現問題: {report['stats']['issues_found']}")
    
    print(f"\n📋 問題按類型分類:")
    for issue_type, count in report['summary']['by_type'].items():
        print(f"   {issue_type}: {count}")
    
    print(f"\n⚠️ 問題按嚴重程度分類:")
    for severity, count in report['summary']['by_severity'].items():
        print(f"   {severity}: {count}")
    
    print(f"\n📁 問題最多的文件:")
    for file_path, count in report['summary']['top_files']:
        print(f"   {file_path}: {count} 個問題")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
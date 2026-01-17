#!/usr/bin/env python3
"""
Root Layer Consistency Checker - 检测和标准化命名、标记、注释的一致性
"""
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Any
import json
from collections import defaultdict

class RootLayerConsistencyChecker:
    """Root Layer 一致性检查器"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.issues = {
            'naming_inconsistencies': [],
            'comment_inconsistencies': [],
            'marker_inconsistencies': [],
            'documentation_gaps': [],
            'formatting_issues': []
        }
        self.statistics = {
            'total_files_scanned': 0,
            'files_with_issues': 0,
            'total_issues_found': 0
        }
        self._visited_files = set()
    
    def scan_directory(self) -> None:
        """扫描目录"""
        print("🔍 开始扫描 Root Layer...")
        
        # 扫描 Python 文件
        python_files = list(self.root_dir.rglob("*.py"))
        # 扫描 Markdown 文件
        md_files = list(self.root_dir.rglob("*.md"))
        # 扫描配置文件
        config_files = list(self.root_dir.rglob("*.yaml")) + list(self.root_dir.rglob("*.yml")) + list(self.root_dir.rglob("*.json"))
        # 扫描 Shell 脚本
        shell_files = list(self.root_dir.rglob("*.sh"))
        
        all_files = python_files + md_files + config_files + shell_files
        
        print(f"📁 找到 {len(all_files)} 个文件待检查")
        
        for file_path in all_files:
            self.check_file_consistency(file_path)
        
        self.statistics['total_files_scanned'] = len(all_files)
        self.statistics['files_with_issues'] = len(set(
            issue['file'] for category in self.issues.values() 
            for issue in category
        ))
        self.statistics['total_issues_found'] = sum(len(issues) for issues in self.issues.values())
    
    def check_file_consistency(self, file_path: Path) -> None:
        """检查单个文件的一致性"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_ext = file_path.suffix.lower()
            
            if file_ext == '.py':
                self.check_python_consistency(file_path, content)
            elif file_ext == '.md':
                self.check_markdown_consistency(file_path, content)
            elif file_ext in ['.yaml', '.yml', '.json']:
                self.check_config_consistency(file_path, content)
            elif file_ext == '.sh':
                self.check_shell_consistency(file_path, content)
                
        except Exception as e:
            print(f"⚠️  检查文件时出错 {file_path}: {e}")
    
    def check_python_consistency(self, file_path: Path, content: str) -> None:
        """检查 Python 文件一致性"""
        lines = content.split('\n')
        
        # 检查命名约定
        self.check_naming_conventions(file_path, lines)
        
        # 检查注释风格
        self.check_comment_style(file_path, lines)
        
        # 检查文档字符串
        self.check_docstrings(file_path, content)
        
        # 检查标记和 TODO
        self.check_markers(file_path, lines)
    
    def check_naming_conventions(self, file_path: Path, lines: List[str]) -> None:
        """检查命名约定"""
        filename = file_path.name
        
        # 文件命名约定
        if filename.lower().startswith('test_') or filename.lower().endswith('_test.py'):
            # 测试文件 - 应该用 snake_case
            if re.search(r'[A-Z]', filename) and not filename.replace('.py', '').isupper():
                self.issues['naming_inconsistencies'].append({
                    'file': str(file_path),
                    'type': 'filename',
                    'severity': 'low',
                    'issue': '测试文件名应使用 snake_case',
                    'current': filename,
                    'suggested': re.sub(r'(?<!^)(?=[A-Z])', '_', filename).lower()
                })
        
        # 检查函数命名
        for i, line in enumerate(lines, 1):
            # 函数定义
            func_match = re.match(r'\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', line)
            if func_match:
                func_name = func_match.group(1)
                
                # 检查是否使用 PEP 8 命名
                if re.search(r'[A-Z]', func_name) and not func_name.isupper():
                    self.issues['naming_inconsistencies'].append({
                        'file': str(file_path),
                        'line': i,
                        'type': 'function_name',
                        'severity': 'medium',
                        'issue': '函数名应使用 snake_case',
                        'current': func_name,
                        'suggested': re.sub(r'(?<!^)(?=[A-Z])', '_', func_name).lower()
                    })
            
            # 类定义
            class_match = re.match(r'\s*class\s+([A-Z][a-zA-Z0-9_]*)\s*:', line)
            if class_match:
                class_name = class_match.group(1)
                
                # 检查是否使用 CapWords
                if '_' in class_name:
                    self.issues['naming_inconsistencies'].append({
                        'file': str(file_path),
                        'line': i,
                        'type': 'class_name',
                        'severity': 'medium',
                        'issue': '类名应使用 CapWords (PascalCase)',
                        'current': class_name,
                        'suggested': ''.join(word.capitalize() for word in class_name.split('_'))
                    })
            
            # 常量定义（全大写）
            const_match = re.match(r'\s*([A-Z_][A-Z0-9_]*)\s*=', line)
            if const_match and not const_match.group(1).isupper():
                const_name = const_match.group(1)
                self.issues['naming_inconsistencies'].append({
                    'file': str(file_path),
                    'line': i,
                    'type': 'constant_name',
                    'severity': 'low',
                    'issue': '常量应使用 UPPER_CASE_WITH_UNDERSCORES',
                    'current': const_name,
                    'suggested': const_name.upper()
                })
    
    def check_comment_style(self, file_path: Path, lines: List[str]) -> None:
        """检查注释风格一致性"""
        comment_styles = []
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # 检查注释
            if stripped.startswith('#'):
                comment = stripped[1:].strip()
                
                # 检查注释风格是否一致
                if comment and not comment.startswith(' ') and not comment.startswith('#'):
                    # 有些有空格，有些没有
                    pass
                
                # 检查是否使用了不同的标记语言
                if re.search(r'[\u4e00-\u9fff]', comment):
                    comment_styles.append('chinese')
                elif re.search(r'[a-zA-Z]', comment):
                    comment_styles.append('english')
        
        # 检查注释语言混合
        if len(set(comment_styles)) > 1:
            self.issues['comment_inconsistencies'].append({
                'file': str(file_path),
                'type': 'language_mixing',
                'severity': 'low',
                'issue': '文件中混用了中文和英文注释',
                'styles_found': set(comment_styles),
                'suggestion': '统一使用一种语言进行注释'
            })
    
    def check_docstrings(self, file_path: Path, content: str) -> None:
        """检查文档字符串"""
        if 'def ' not in content:
            return
        
        lines = content.split('\n')
        in_docstring = False
        docstring_start = 0
        
        for i, line in enumerate(lines, 1):
            if '"""' in line or "'''" in line:
                if not in_docstring:
                    in_docstring = True
                    docstring_start = i
                else:
                    in_docstring = False
                    
                    # 检查函数/类是否有文档字符串
                    if i - docstring_start > 0:
                        # 检查是否有函数定义在文档字符串之前
                        for j in range(max(0, docstring_start - 5), docstring_start):
                            if re.search(r'\s*(def|class)\s+', lines[j]):
                                # 这是一个有效的文档字符串
                                # 检查文档字符串风格
                                docstring_content = '\n'.join(lines[docstring_start:i])
                                self.check_docstring_style(file_path, docstring_start, docstring_content)
                                break
    
    def check_docstring_style(self, file_path: Path, line_num: int, docstring: str) -> None:
        """检查文档字符串风格"""
        # 检查文档字符串是否使用了不同的格式
        has_google_style = bool(re.search(r'Args?:|Returns?:|Raises?:', docstring))
        has_sphinx_style = bool(re.search(r':param|:type|:return:', docstring))
        has_numpy_style = bool(re.search(r'Parameters\n----------|Returns\n-------', docstring))
        
        styles = []
        if has_google_style:
            styles.append('Google')
        if has_sphinx_style:
            styles.append('Sphinx')
        if has_numpy_style:
            styles.append('NumPy')
        
        # 如果没有统一的风格，标记为不一致
        if len(styles) > 1:
            self.issues['comment_inconsistencies'].append({
                'file': str(file_path),
                'line': line_num,
                'type': 'docstring_style',
                'severity': 'low',
                'issue': '文档字符串混用了多种风格',
                'styles_found': styles,
                'suggestion': '统一使用一种文档字符串风格（推荐 Google 风格）'
            })
        
        # 如果完全没有格式，标记为需要改进
        if len(styles) == 0 and len(docstring) > 50:
            self.issues['documentation_gaps'].append({
                'file': str(file_path),
                'line': line_num,
                'type': 'docstring_formatting',
                'severity': 'low',
                'issue': '文档字符串缺少标准格式',
                'current': docstring[:100] + '...',
                'suggestion': '使用 Google 或 Sphinx 风格格式化文档字符串'
            })
    
    def check_markers(self, file_path: Path, lines: List[str]) -> None:
        """检查标记和 TODO"""
        todo_patterns = [
            r'# TODO[:\s]',
            r'# FIXME[:\s]',
            r'# HACK[:\s]',
            r'# NOTE[:\s]',
            r'# WARNING[:\s]',
            r'# SECURITY[:\s]',
            r'# XXX[:\s]'
        ]
        
        markers_found = set()
        
        for i, line in enumerate(lines, 1):
            for pattern in todo_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    marker_type = pattern.split(r'[:\s]')[0].replace('#', '').upper()
                    markers_found.add(marker_type)
        
        # 检查标记格式的一致性
        if markers_found:
            # 检查是否使用了不同的标记格式
            marker_formats = []
            for marker in markers_found:
                if marker in ['TODO', 'FIXME', 'HACK', 'NOTE']:
                    marker_formats.append('standard')
                elif marker in ['WARNING', 'SECURITY']:
                    marker_formats.append('important')
                elif marker == 'XXX':
                    marker_formats.append('deprecated')
            
            if len(set(marker_formats)) > 1:
                self.issues['marker_inconsistencies'].append({
                    'file': str(file_path),
                    'type': 'marker_format',
                    'severity': 'low',
                    'issue': '使用了多种不同类型的标记',
                    'markers_found': list(markers_found),
                    'suggestion': '统一标记格式，优先使用标准标记（TODO, FIXME, NOTE）'
                })
    
    def check_markdown_consistency(self, file_path: Path, content: str) -> None:
        """检查 Markdown 文件一致性"""
        lines = content.split('\n')
        
        # 检查标题一致性
        heading_levels = []
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('#'):
                # 计算标题级别
                level = len(line) - len(line.lstrip('#'))
                heading_levels.append((i, level, line.strip()))
        
        # 检查标题级别跳跃
        for i in range(len(heading_levels) - 1):
            current_line, current_level, current_text = heading_levels[i]
            next_line, next_level, next_text = heading_levels[i + 1]
            
            if next_level - current_level > 1:
                self.issues['formatting_issues'].append({
                    'file': str(file_path),
                    'line': next_line,
                    'type': 'heading_skip',
                    'severity': 'low',
                    'issue': f'标题级别从 {current_level} 跳到 {next_level}',
                    'current': next_text,
                    'suggestion': f'应该使用 {current_level + 1} 级标题'
                })
    
    def check_config_consistency(self, file_path: Path, content: str) -> None:
        """检查配置文件一致性"""
        lines = content.split('\n')
        
        # 检查缩进一致性
        indent_sizes = set()
        for line in lines:
            if line.strip() and not line.strip().startswith('#'):
                # 计算缩进
                indent = len(line) - len(line.lstrip())
                if indent > 0:
                    indent_sizes.add(indent)
        
        if len(indent_sizes) > 1:
            self.issues['formatting_issues'].append({
                'file': str(file_path),
                'type': 'indentation',
                'severity': 'medium',
                'issue': '缩进不一致',
                'indent_sizes': list(indent_sizes),
                'suggestion': '统一缩进大小（推荐 2 空格或 4 空格）'
            })
    
    def check_shell_consistency(self, file_path: Path, content: str) -> None:
        """检查 Shell 脚本一致性"""
        lines = content.split('\n')
        
        # 检查注释风格
        comment_styles = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('#'):
                comment = stripped[1:].strip()
                
                if re.search(r'[\u4e00-\u9fff]', comment):
                    comment_styles.append('chinese')
                elif re.search(r'[a-zA-Z]', comment):
                    comment_styles.append('english')
        
        if len(set(comment_styles)) > 1:
            self.issues['comment_inconsistencies'].append({
                'file': str(file_path),
                'type': 'language_mixing',
                'severity': 'low',
                'issue': 'Shell 脚本中混用了中文和英文注释',
                'styles_found': set(comment_styles),
                'suggestion': '统一使用一种语言进行注释'
            })
    
    def _convert_to_serializable(self, obj):
        """将对象转换为可序列化的格式"""
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, dict):
            return {k: self._convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_serializable(item) for item in obj]
        else:
            return obj
    
    def generate_report(self) -> Dict[str, Any]:
        """生成报告"""
        return {
            'statistics': self.statistics,
            'issues': self._convert_to_serializable(self.issues),
            'summary': self._convert_to_serializable(self._generate_summary())
        }
    
    def _generate_summary(self) -> Dict[str, Any]:
        """生成摘要"""
        total_issues = self.statistics['total_issues_found']
        
        severity_counts = defaultdict(int)
        for category in self.issues.values():
            for issue in category:
                severity_counts[issue.get('severity', 'low')] += 1
        
        return {
            'total_files': self.statistics['total_files_scanned'],
            'files_with_issues': self.statistics['files_with_issues'],
            'total_issues': total_issues,
            'issues_by_severity': dict(severity_counts),
            'issues_by_category': {
                category: len(issues)
                for category, issues in self.issues.items()
            }
        }

def main():
    """主函数"""
    print("=" * 60)
    print("Root Layer 一致性检查工具")
    print("=" * 60)
    
    # 创建检查器
    checker = RootLayerConsistencyChecker()
    
    # 扫描目录
    checker.scan_directory()
    
    # 生成报告
    report = checker.generate_report()
    
    # 保存报告
    with open('root_layer_consistency_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 打印摘要
    print(f"\n📊 检查摘要:")
    print(f"   扫描文件数: {report['summary']['total_files']}")
    print(f"   有问题的文件: {report['summary']['files_with_issues']}")
    print(f"   总问题数: {report['summary']['total_issues']}")
    
    print(f"\n📋 问题按类别统计:")
    for category, count in report['summary']['issues_by_category'].items():
        print(f"   {category}: {count}")
    
    print(f"\n⚠️  问题按严重程度统计:")
    for severity, count in report['summary']['issues_by_severity'].items():
        print(f"   {severity.upper()}: {count}")
    
    print(f"\n📄 详细报告已保存到: root_layer_consistency_report.json")
    
    return report

if __name__ == "__main__":
    report = main()
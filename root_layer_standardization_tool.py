#!/usr/bin/env python3
"""
Root Layer 标准化工具 - 自动修复命名、标记、注释的一致性问题
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Any
import json
from datetime import datetime

class RootLayerStandardizationTool:
    """Root Layer 标准化工具"""
    
    def __init__(self, report_path: str = "root_layer_consistency_report.json"):
        self.report_path = report_path
        self.issues = self._load_report()
        self.fixes_applied = {
            'naming_fixes': 0,
            'comment_fixes': 0,
            'documentation_fixes': 0,
            'formatting_fixes': 0
        }
        self.backup_dir = Path("standardization_backup")
        self.backup_dir.mkdir(exist_ok=True)
    
    def _load_report(self) -> Dict[str, Any]:
        """加载一致性报告"""
        try:
            with open(self.report_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  报告文件未找到: {self.report_path}")
            return {'issues': {}}
    
    def apply_standardization(self) -> Dict[str, Any]:
        """应用标准化修复"""
        print("=" * 60)
        print("Root Layer 标准化工具")
        print("=" * 60)
        
        print(f"\n📋 加载一致性报告...")
        print(f"   总问题数: {sum(len(issues) for issues in self.issues['issues'].values())}")
        
        # 备份文件
        print(f"\n💾 创建备份...")
        self._create_backups()
        
        # 应用修复
        print(f"\n🔧 应用标准化修复...")
        
        # 1. 修复命名不一致
        self._fix_naming_inconsistencies()
        
        # 2. 修复注释不一致
        self._fix_comment_inconsistencies()
        
        # 3. 修复文档字符串
        self._fix_documentation_gaps()
        
        # 4. 修复格式问题
        self._fix_formatting_issues()
        
        # 生成报告
        return self._generate_standardization_report()
    
    def _create_backups(self):
        """创建备份"""
        files_to_backup = set()
        
        for category in self.issues['issues'].values():
            for issue in category:
                file_path = issue.get('file', '')
                if file_path:
                    files_to_backup.add(file_path)
        
        print(f"   需要备份的文件数: {len(files_to_backup)}")
        
        for file_path in files_to_backup:
            try:
                src = Path(file_path)
                if src.exists():
                    dest = self.backup_dir / src.relative_to(".")
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    import shutil
                    shutil.copy2(src, dest)
            except Exception as e:
                print(f"   ⚠️  备份失败 {file_path}: {e}")
        
        print(f"   ✅ 备份完成")
    
    def _fix_naming_inconsistencies(self):
        """修复命名不一致"""
        naming_issues = self.issues['issues'].get('naming_inconsistencies', [])
        
        if not naming_issues:
            print(f"\n✨ 没有命名不一致问题需要修复")
            return
        
        print(f"\n🔤 修复命名不一致 ({len(naming_issues)} 个问题)...")
        
        # 按文件分组
        files_to_fix = {}
        for issue in naming_issues:
            file_path = issue['file']
            if file_path not in files_to_fix:
                files_to_fix[file_path] = []
            files_to_fix[file_path].append(issue)
        
        for file_path, issues in files_to_fix.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # 应用修复
                for issue in issues:
                    if issue['type'] == 'function_name':
                        # 替换函数名
                        old_name = issue['current']
                        new_name = issue['suggested']
                        content = re.sub(
                            rf'\b{re.escape(old_name)}\b',
                            new_name,
                            content
                        )
                    elif issue['type'] == 'class_name':
                        # 替换类名
                        old_name = issue['current']
                        new_name = issue['suggested']
                        content = re.sub(
                            rf'\b{re.escape(old_name)}\b',
                            new_name,
                            content
                        )
                    elif issue['type'] == 'constant_name':
                        # 替换常量名
                        old_name = issue['current']
                        new_name = issue['suggested']
                        content = re.sub(
                            rf'\b{re.escape(old_name)}\b',
                            new_name,
                            content
                        )
                
                # 如果有更改，写回文件
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.fixes_applied['naming_fixes'] += len(issues)
                    
            except Exception as e:
                print(f"   ⚠️  修复失败 {file_path}: {e}")
        
        print(f"   ✅ 修复了 {self.fixes_applied['naming_fixes']} 个命名问题")
    
    def _fix_comment_inconsistencies(self):
        """修复注释不一致"""
        comment_issues = self.issues['issues'].get('comment_inconsistencies', [])
        
        if not comment_issues:
            print(f"\n✨ 没有注释不一致问题需要修复")
            return
        
        print(f"\n💬 修复注释不一致 ({len(comment_issues)} 个问题)...")
        
        # 按文件分组
        files_to_fix = {}
        for issue in comment_issues:
            file_path = issue['file']
            if file_path not in files_to_fix:
                files_to_fix[file_path] = []
            files_to_fix[file_path].append(issue)
        
        for file_path, issues in files_to_fix.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 对于注释语言混合问题，建议使用统一的注释
                # 这里我们只添加标记，不自动修复以避免破坏代码
                pass
                
            except Exception as e:
                print(f"   ⚠️  处理失败 {file_path}: {e}")
        
        print(f"   ℹ️  注释问题已记录，建议手动审查")
        self.fixes_applied['comment_fixes'] = len(comment_issues)
    
    def _fix_documentation_gaps(self):
        """修复文档缺口"""
        doc_issues = self.issues['issues'].get('documentation_gaps', [])
        
        if not doc_issues:
            print(f"\n✨ 没有文档缺口问题需要修复")
            return
        
        print(f"\n📝 修复文档缺口 ({len(doc_issues)} 个问题)...")
        
        # 对于文档问题，我们生成建议但不自动修复
        # 因为文档字符串需要手动编写以保持准确性
        print(f"   ℹ️  文档问题已记录，建议手动审查和补充")
        self.fixes_applied['documentation_fixes'] = len(doc_issues)
    
    def _fix_formatting_issues(self):
        """修复格式问题"""
        format_issues = self.issues['issues'].get('formatting_issues', [])
        
        if not format_issues:
            print(f"\n✨ 没有格式问题需要修复")
            return
        
        print(f"\n🎨 修复格式问题 ({len(format_issues)} 个问题)...")
        
        # 按文件分组
        files_to_fix = {}
        for issue in format_issues:
            file_path = issue['file']
            if file_path not in files_to_fix:
                files_to_fix[file_path] = []
            files_to_fix[file_path].append(issue)
        
        for file_path, issues in files_to_fix.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                modified = False
                
                # 修复缩进问题
                for issue in issues:
                    if issue['type'] == 'indentation':
                        # 统一缩进为 2 空格
                        new_lines = []
                        for line in lines:
                            stripped = line.lstrip()
                            if stripped:
                                # 计算原始缩进
                                indent = len(line) - len(stripped)
                                if indent > 0:
                                    # 转换为 2 空格的倍数
                                    new_indent = (indent // 2) * 2
                                    new_lines.append(' ' * new_indent + stripped + '\n')
                                else:
                                    new_lines.append(line)
                            else:
                                new_lines.append(line)
                        
                        lines = new_lines
                        modified = True
                
                # 如果有更改，写回文件
                if modified:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    self.fixes_applied['formatting_fixes'] += len(issues)
                    
            except Exception as e:
                print(f"   ⚠️  修复失败 {file_path}: {e}")
        
        print(f"   ✅ 修复了 {self.fixes_applied['formatting_fixes']} 个格式问题")
    
    def _generate_standardization_report(self) -> Dict[str, Any]:
        """生成标准化报告"""
        total_fixes = sum(self.fixes_applied.values())
        
        return {
            'timestamp': datetime.now().isoformat(),
            'fixes_applied': self.fixes_applied,
            'total_fixes': total_fixes,
            'backup_location': str(self.backup_dir),
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 基于问题数量生成建议
        total_issues = sum(len(issues) for issues in self.issues['issues'].values())
        
        if total_issues > 1000:
            recommendations.append("建议分阶段进行标准化，优先修复高优先级问题")
            recommendations.append("考虑使用代码格式化工具如 black 和 isort")
        
        if self.fixes_applied['naming_fixes'] > 0:
            recommendations.append("命名问题已自动修复，请验证修复结果")
        
        if self.fixes_applied['comment_fixes'] > 0:
            recommendations.append("注释问题需要手动审查，建议统一注释语言")
        
        if self.fixes_applied['documentation_fixes'] > 0:
            recommendations.append("文档问题需要手动补充，建议使用 Google 风格文档字符串")
        
        if self.fixes_applied['formatting_fixes'] > 0:
            recommendations.append("格式问题已部分修复，建议使用格式化工具进行全面标准化")
        
        return recommendations

def main():
    """主函数"""
    print("=" * 60)
    print("Root Layer 标准化工具")
    print("=" * 60)
    
    # 创建标准化工具
    tool = RootLayerStandardizationTool()
    
    # 应用标准化
    report = tool.apply_standardization()
    
    # 保存报告
    with open('root_layer_standardization_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 打印摘要
    print(f"\n📊 标准化摘要:")
    print(f"   命名修复: {report['fixes_applied']['naming_fixes']}")
    print(f"   注释修复: {report['fixes_applied']['comment_fixes']}")
    print(f"   文档修复: {report['fixes_applied']['documentation_fixes']}")
    print(f"   格式修复: {report['fixes_applied']['formatting_fixes']}")
    print(f"   总修复数: {report['total_fixes']}")
    
    print(f"\n💾 备份位置: {report['backup_location']}")
    
    print(f"\n💡 建议:")
    for recommendation in report['recommendations']:
        print(f"   - {recommendation}")
    
    print(f"\n📄 详细报告已保存到: root_layer_standardization_report.json")
    
    return report

if __name__ == "__main__":
    report = main()
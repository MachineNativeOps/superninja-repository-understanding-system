#!/usr/bin/env python3
"""
FHS Integration Automator
自動將成熟的組件從 workspace/ 遷移到 FHS 目錄

Usage:
    python3 fhs_integrator.py repository-understanding --dry-run
    python3 fhs_integrator.py repository-understanding --execute
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import argparse

class FHSIntegrator:
    """FHS 整合自動化工具"""
    
    def __init__(self, repo_root: str = None, dry_run: bool = True):
        self.repo_root = repo_root or os.getcwd()
        self.dry_run = dry_run
        self.workspace_tools = os.path.join(self.repo_root, "workspace", "tools")
        
    def integrate_component(self, component_name: str, maturity_score: int = 0) -> Dict:
        """整合組件到 FHS 目錄"""
        component_path = os.path.join(self.workspace_tools, component_name)
        
        if not os.path.exists(component_path):
            return {"error": f"Component {component_name} not found"}
        
        if maturity_score < 80:
            return {
                "error": f"Component maturity score ({maturity_score}) below threshold (80)",
                "recommendation": "Improve component maturity before integration"
            }
        
        results = {
            "component": component_name,
            "dry_run": self.dry_run,
            "actions": []
        }
        
        # 1. 分析組件結構
        structure = self._analyze_component_structure(component_path)
        results["structure"] = structure
        
        # 2. 創建 FHS 目錄結構
        fhs_structure = self._create_fhs_structure(component_name, structure, results)
        
        # 3. 生成命令包裝器
        wrappers = self._generate_command_wrappers(component_name, structure, results)
        
        # 4. 複製庫文件
        self._copy_library_files(component_name, component_path, results)
        
        # 5. 複製配置文件
        self._copy_configuration_files(component_name, component_path, results)
        
        # 6. 複製服務文件
        self._copy_service_files(component_name, component_path, results)
        
        # 7. 生成遷移文檔
        self._generate_migration_docs(component_name, results)
        
        return results
    
    def _analyze_component_structure(self, path: str) -> Dict:
        """分析組件結構"""
        structure = {
            "python_files": [],
            "shell_scripts": [],
            "config_files": [],
            "service_files": [],
            "doc_files": [],
            "test_files": []
        }
        
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, path)
                
                if file.endswith('.py'):
                    if 'test' in file.lower():
                        structure["test_files"].append(rel_path)
                    else:
                        structure["python_files"].append(rel_path)
                elif file.endswith('.sh'):
                    structure["shell_scripts"].append(rel_path)
                elif file.endswith(('.yaml', '.yml', '.conf', '.cfg')):
                    structure["config_files"].append(rel_path)
                elif file.endswith('.service'):
                    structure["service_files"].append(rel_path)
                elif file.endswith('.md'):
                    structure["doc_files"].append(rel_path)
        
        return structure
    
    def _create_fhs_structure(self, component_name: str, structure: Dict, results: Dict) -> Dict:
        """創建 FHS 目錄結構"""
        fhs_dirs = {
            "lib": os.path.join(self.repo_root, "lib", component_name),
            "etc": os.path.join(self.repo_root, "etc", component_name),
            "bin": os.path.join(self.repo_root, "bin"),
            "sbin": os.path.join(self.repo_root, "sbin")
        }
        
        for dir_type, dir_path in fhs_dirs.items():
            if not os.path.exists(dir_path):
                action = f"Create directory: {dir_path}"
                results["actions"].append(action)
                
                if not self.dry_run:
                    os.makedirs(dir_path, exist_ok=True)
                    print(f"✓ {action}")
                else:
                    print(f"[DRY RUN] {action}")
        
        return fhs_dirs
    
    def _generate_command_wrappers(self, component_name: str, structure: Dict, results: Dict) -> List[str]:
        """生成命令包裝器"""
        wrappers = []
        
        # 識別主要的命令腳本
        main_scripts = self._identify_main_scripts(component_name, structure)
        
        for script_info in main_scripts:
            wrapper_path = os.path.join(
                self.repo_root,
                script_info["target_dir"],
                script_info["command_name"]
            )
            
            wrapper_content = self._generate_wrapper_content(
                component_name,
                script_info["source_script"],
                script_info["is_admin"]
            )
            
            action = f"Create wrapper: {wrapper_path}"
            results["actions"].append(action)
            
            if not self.dry_run:
                with open(wrapper_path, 'w') as f:
                    f.write(wrapper_content)
                os.chmod(wrapper_path, 0o755)
                print(f"✓ {action}")
            else:
                print(f"[DRY RUN] {action}")
            
            wrappers.append(wrapper_path)
        
        return wrappers
    
    def _identify_main_scripts(self, component_name: str, structure: Dict) -> List[Dict]:
        """識別主要命令腳本"""
        main_scripts = []
        
        # 根據命名模式識別
        for py_file in structure["python_files"]:
            base_name = os.path.basename(py_file).replace('.py', '')
            
            # 識別主腳本
            if base_name in ['main', '__main__', component_name]:
                main_scripts.append({
                    "source_script": py_file,
                    "command_name": f"mno-{component_name}",
                    "target_dir": "bin",
                    "is_admin": False
                })
            
            # 識別系統管理腳本
            elif 'system' in base_name or 'admin' in base_name or 'maintain' in base_name:
                main_scripts.append({
                    "source_script": py_file,
                    "command_name": f"mno-{component_name}-{base_name}",
                    "target_dir": "sbin",
                    "is_admin": True
                })
        
        # 如果沒有明顯的主腳本，使用第一個 Python 文件
        if not main_scripts and structure["python_files"]:
            first_script = structure["python_files"][0]
            base_name = os.path.basename(first_script).replace('.py', '')
            main_scripts.append({
                "source_script": first_script,
                "command_name": f"mno-{base_name}",
                "target_dir": "bin",
                "is_admin": False
            })
        
        return main_scripts
    
    def _generate_wrapper_content(self, component_name: str, source_script: str, is_admin: bool) -> str:
        """生成包裝器腳本內容"""
        admin_note = "# Requires elevated privileges\n" if is_admin else ""
        
        wrapper = f"""#!/bin/bash
# Auto-generated FHS wrapper for {component_name}
# Source: workspace/tools/{component_name}/{source_script}
{admin_note}
set -e

# Determine script directory
SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
LIB_DIR="$SCRIPT_DIR/../lib/{component_name}"

# Check if library directory exists
if [ ! -d "$LIB_DIR" ]; then
    echo "Error: Library directory not found: $LIB_DIR" >&2
    exit 1
fi

# Execute the Python script
exec python3 "$LIB_DIR/{source_script}" "$@"
"""
        return wrapper
    
    def _copy_library_files(self, component_name: str, component_path: str, results: Dict) -> None:
        """複製庫文件到 lib/"""
        lib_dir = os.path.join(self.repo_root, "lib", component_name)
        
        # 複製所有 Python 文件
        for root, dirs, files in os.walk(component_path):
            # 跳過測試目錄
            if 'test' in root.lower():
                continue
            
            for file in files:
                if file.endswith('.py') or file == 'requirements.txt':
                    source = os.path.join(root, file)
                    rel_path = os.path.relpath(source, component_path)
                    dest = os.path.join(lib_dir, rel_path)
                    
                    action = f"Copy library file: {rel_path} -> lib/{component_name}/{rel_path}"
                    results["actions"].append(action)
                    
                    if not self.dry_run:
                        os.makedirs(os.path.dirname(dest), exist_ok=True)
                        shutil.copy2(source, dest)
                        print(f"✓ {action}")
                    else:
                        print(f"[DRY RUN] {action}")
    
    def _copy_configuration_files(self, component_name: str, component_path: str, results: Dict) -> None:
        """複製配置文件到 etc/"""
        etc_dir = os.path.join(self.repo_root, "etc", component_name)
        
        for root, dirs, files in os.walk(component_path):
            for file in files:
                if file.endswith(('.yaml', '.yml', '.conf', '.cfg')):
                    source = os.path.join(root, file)
                    dest = os.path.join(etc_dir, file)
                    
                    action = f"Copy config file: {file} -> etc/{component_name}/{file}"
                    results["actions"].append(action)
                    
                    if not self.dry_run:
                        os.makedirs(etc_dir, exist_ok=True)
                        shutil.copy2(source, dest)
                        print(f"✓ {action}")
                    else:
                        print(f"[DRY RUN] {action}")
    
    def _copy_service_files(self, component_name: str, component_path: str, results: Dict) -> None:
        """複製服務文件到 etc/systemd/"""
        systemd_dir = os.path.join(self.repo_root, "etc", "systemd")
        
        for root, dirs, files in os.walk(component_path):
            for file in files:
                if file.endswith('.service'):
                    source = os.path.join(root, file)
                    dest = os.path.join(systemd_dir, file)
                    
                    action = f"Copy service file: {file} -> etc/systemd/{file}"
                    results["actions"].append(action)
                    
                    if not self.dry_run:
                        os.makedirs(systemd_dir, exist_ok=True)
                        shutil.copy2(source, dest)
                        print(f"✓ {action}")
                    else:
                        print(f"[DRY RUN] {action}")
    
    def _generate_migration_docs(self, component_name: str, results: Dict) -> None:
        """生成遷移文檔"""
        doc_path = os.path.join(
            self.repo_root,
            "docs",
            f"fhs-migration-{component_name}.md"
        )
        
        doc_content = f"""# FHS Migration: {component_name}

## Migration Date
{subprocess.check_output(['date'], text=True).strip()}

## Component Information
- **Name**: {component_name}
- **Source**: `workspace/tools/{component_name}/`
- **FHS Integration**: Completed

## Migrated Files

### Command Wrappers (bin/)
"""
        
        for action in results["actions"]:
            if "Create wrapper" in action:
                doc_content += f"- {action.split(': ')[1]}\n"
        
        doc_content += "\n### Library Files (lib/)\n"
        for action in results["actions"]:
            if "Copy library file" in action:
                doc_content += f"- {action.split(' -> ')[1]}\n"
        
        doc_content += f"""

## Usage

### Old Way (Workspace)
```bash
cd workspace/tools/{component_name}
python3 main.py [options]
```

### New Way (FHS)
```bash
mno-{component_name} [options]
```

## Backward Compatibility

The original files in `workspace/tools/{component_name}/` are preserved for backward compatibility.
They can be removed in a future cleanup once all references are updated.

## Next Steps

1. Update all documentation references
2. Update scripts that call the old paths
3. Test the new FHS commands
4. Create deprecation notice for workspace usage
5. Schedule cleanup of workspace files (after 1-2 release cycles)
"""
        
        action = f"Generate migration documentation: {doc_path}"
        results["actions"].append(action)
        
        if not self.dry_run:
            os.makedirs(os.path.dirname(doc_path), exist_ok=True)
            with open(doc_path, 'w') as f:
                f.write(doc_content)
            print(f"✓ {action}")
        else:
            print(f"[DRY RUN] {action}")


def main():
    parser = argparse.ArgumentParser(description="FHS Integration Automator")
    parser.add_argument("component", help="Component name to integrate")
    parser.add_argument("--execute", action="store_true", help="Execute integration (default is dry-run)")
    parser.add_argument("--maturity-score", type=int, default=80, help="Maturity score of component")
    parser.add_argument("--repo-root", help="Repository root path")
    
    args = parser.parse_args()
    
    integrator = FHSIntegrator(
        repo_root=args.repo_root,
        dry_run=not args.execute
    )
    
    print("=" * 80)
    print(f"FHS Integration: {args.component}")
    print(f"Mode: {'EXECUTE' if args.execute else 'DRY RUN'}")
    print("=" * 80)
    print("")
    
    results = integrator.integrate_component(args.component, args.maturity_score)
    
    if "error" in results:
        print(f"Error: {results['error']}")
        if "recommendation" in results:
            print(f"Recommendation: {results['recommendation']}")
        sys.exit(1)
    
    print("")
    print("=" * 80)
    print("Integration Summary")
    print("=" * 80)
    print(f"Total actions: {len(results['actions'])}")
    print("")
    
    if args.execute:
        print("✓ Integration completed successfully!")
        print("")
        print("Next steps:")
        print("  1. Review migrated files")
        print("  2. Test the new commands")
        print("  3. Update documentation")
        print("  4. Commit changes to git")
    else:
        print("To execute this integration, run:")
        print(f"  python3 fhs_integrator.py {args.component} --execute")


if __name__ == "__main__":
    main()

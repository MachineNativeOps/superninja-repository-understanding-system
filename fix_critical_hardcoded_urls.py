#!/usr/bin/env python3
"""
Fix critical hardcoded URLs in key files.
"""
import re
from pathlib import Path

def fix_file(file_path: str, replacements: list) -> bool:
    """Apply replacements to a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Apply each replacement
        for old_url, new_code in replacements:
            content = content.replace(old_url, new_code)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Main function."""
    print("Phase 4B: Fixing Critical Hardcoded URLs")
    print("=" * 60)
    
    # Define critical files and their replacements
    fixes = {
        '00-namespaces/namespaces-mcp/level1/verification/github-oauth-verifier.py': [
            ('https://api.github.com', "os.getenv('GITHUB_API_URL', 'https://api.github.com')")
        ],
        '00-namespaces/namespaces-mcp/level1/instant-system/deployer.py': [
            ('https://api.instant.com/auth', "os.getenv('INSTANT_AUTH_URL', 'https://api.instant.com/auth')"),
            ('https://api.instant.com/validation', "os.getenv('INSTANT_VALIDATION_URL', 'https://api.instant.com/validation')"),
            ('https://api.instant.com/v1', "os.getenv('INSTANT_API_V1_URL', 'https://api.instant.com/v1')"),
            ('https://api.instant.com/tools', "os.getenv('INSTANT_TOOLS_URL', 'https://api.instant.com/tools')"),
        ]
    }
    
    # Create backup
    import shutil
    backup_dir = Path('backup_phase4b_critical')
    backup_dir.mkdir(exist_ok=True)
    
    total_fixed = 0
    total_files = 0
    
    for file_path, replacements in fixes.items():
        if Path(file_path).exists():
            # Backup the file
            backup_path = backup_dir / Path(file_path).name
            shutil.copy2(file_path, backup_path)
            
            # Fix the file
            if fix_file(file_path, replacements):
                print(f"✅ Fixed: {file_path}")
                total_fixed += len(replacements)
                total_files += 1
            else:
                print(f"❌ Failed to fix: {file_path}")
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print(f"\n📊 Summary:")
    print(f"   Files fixed: {total_files}")
    print(f"   URLs replaced: {total_fixed}")
    print(f"   Backups created in: {backup_dir}/")
    
    # Create .env.example if it doesn't exist
    env_example = Path('.env.example')
    if not env_example.exists():
        env_content = """# API Configuration
GITHUB_API_URL=https://api.github.com
INSTANT_AUTH_URL=https://api.instant.com/auth
INSTANT_VALIDATION_URL=https://api.instant.com/validation
INSTANT_API_V1_URL=https://api.instant.com/v1
INSTANT_TOOLS_URL=https://api.instant.com/tools
"""
        env_example.write_text(env_content)
        print(f"✅ Created .env.example with environment variables")

if __name__ == "__main__":
    main()
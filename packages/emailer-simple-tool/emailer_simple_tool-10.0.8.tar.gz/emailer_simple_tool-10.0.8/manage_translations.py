#!/usr/bin/env python3
"""
Systematic Translation Management Script
This script ensures consistent translation management without regressions.
"""

import os
import subprocess
import sys
from pathlib import Path

class TranslationManager:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.translations_dir = self.project_root / "src/emailer_simple_tool/gui/translations"
        self.ts_file = self.translations_dir / "emailer_simple_tool_fr.ts"
        self.qm_file = self.translations_dir / "emailer_simple_tool_fr.qm"
        self.backup_file = self.translations_dir / "emailer_simple_tool_fr_backup.ts"
        
    def backup_current_translations(self):
        """Backup current translation file"""
        if self.ts_file.exists():
            import shutil
            shutil.copy2(self.ts_file, self.backup_file)
            print(f"✅ Backed up translations to {self.backup_file}")
        else:
            print("⚠️ No translation file to backup")
    
    def restore_from_backup(self):
        """Restore from backup"""
        if self.backup_file.exists():
            import shutil
            shutil.copy2(self.backup_file, self.ts_file)
            print(f"✅ Restored translations from {self.backup_file}")
        else:
            print("❌ No backup file found")
    
    def update_source_strings(self):
        """Update translation file with new source strings"""
        gui_files = [
            "src/emailer_simple_tool/gui/main_window.py",
            "src/emailer_simple_tool/gui/tabs/campaign_tab.py", 
            "src/emailer_simple_tool/gui/tabs/picture_tab.py",
            "src/emailer_simple_tool/gui/tabs/send_tab.py",
            "src/emailer_simple_tool/gui/tabs/smtp_tab.py"
        ]
        
        cmd = ["pyside6-lupdate"] + gui_files + ["-ts", str(self.ts_file)]
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Updated source strings successfully")
            print(result.stdout)
        else:
            print("❌ Failed to update source strings")
            print(result.stderr)
            
    def compile_translations(self):
        """Compile .ts to .qm file"""
        cmd = ["pyside6-lrelease", str(self.ts_file), "-qm", str(self.qm_file)]
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Compiled translations successfully")
            print(result.stdout)
            return True
        else:
            print("❌ Failed to compile translations")
            print(result.stderr)
            return False
    
    def get_translation_stats(self):
        """Get translation statistics"""
        if not self.ts_file.exists():
            return "No translation file found"
            
        with open(self.ts_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        total_messages = content.count('<message>')
        finished = content.count('</translation>')
        unfinished = content.count('type="unfinished"')
        
        return f"📊 Translation Stats: {finished} finished, {unfinished} unfinished, {total_messages} total"
    
    def install_package(self):
        """Install the package"""
        cmd = ["pip", "install", "-e", ".[gui]"]
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Package installed successfully")
        else:
            print("❌ Failed to install package")
            print(result.stderr)

def main():
    if len(sys.argv) < 2:
        print("Usage: python manage_translations.py <command>")
        print("Commands:")
        print("  backup     - Backup current translations")
        print("  restore    - Restore from backup")
        print("  update     - Update source strings")
        print("  compile    - Compile translations")
        print("  stats      - Show translation statistics")
        print("  install    - Install package")
        print("  full       - Full workflow: backup, update, compile, install")
        return
    
    manager = TranslationManager(".")
    command = sys.argv[1]
    
    if command == "backup":
        manager.backup_current_translations()
    elif command == "restore":
        manager.restore_from_backup()
    elif command == "update":
        manager.update_source_strings()
    elif command == "compile":
        manager.compile_translations()
    elif command == "stats":
        print(manager.get_translation_stats())
    elif command == "install":
        manager.install_package()
    elif command == "full":
        print("🔄 Starting full translation workflow...")
        manager.backup_current_translations()
        manager.update_source_strings()
        manager.compile_translations()
        print(manager.get_translation_stats())
        manager.install_package()
        print("✅ Full workflow completed!")
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()

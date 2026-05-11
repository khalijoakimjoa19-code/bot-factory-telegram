#!/usr/bin/env python3
# Fix UTF-8 encoding issues in Python files

import os
import sys

def fix_encoding(filepath):
    """Fix UTF-8 encoding by reading and rewriting file"""
    try:
        # Read as binary first to detect BOM
        with open(filepath, 'rb') as f:
            content = f.read()
        
        # Write back as clean UTF-8 without BOM
        with open(filepath, 'wb') as f:
            f.write(content.decode('utf-8', errors='replace').encode('utf-8'))
        
        print(f"✓ {filepath}")
        return True
    except Exception as e:
        print(f"✗ {filepath}: {e}")
        return False

def fix_all_python_files(directory):
    """Fix all .py files in directory"""
    files = [
        'bot.py', 'factory_bot.py', 'factory_config.py', 'factory_database.py',
        'config.py', 'database.py', 'mpesa.py', 'webhook_server.py', 'main.py'
    ]
    
    fixed = 0
    failed = 0
    
    for filename in files:
        filepath = os.path.join(directory, filename)
        if os.path.exists(filepath):
            if fix_encoding(filepath):
                fixed += 1
            else:
                failed += 1
        else:
            print(f"✗ {filename} not found")
            failed += 1
    
    print(f"\nFixed: {fixed}, Failed: {failed}")
    return failed == 0

if __name__ == "__main__":
    directory = r"C:\Users\user\Downloads\bot-factory-telegram"
    success = fix_all_python_files(directory)
    sys.exit(0 if success else 1)

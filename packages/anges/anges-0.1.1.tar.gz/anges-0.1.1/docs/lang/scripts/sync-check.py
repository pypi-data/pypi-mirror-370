#!/usr/bin/env python3
"""
Bilingual Documentation Sync Checker

This script checks if English and Chinese documentation files are in sync
by comparing file existence, structure, and identifying missing translations.
"""

import os
import glob
from pathlib import Path

def find_english_docs(docs_dir="docs"):
    """Find all English documentation files."""
    english_files = []
    
    # Find markdown files that don't have .zh. in the name
    for md_file in glob.glob(f"{docs_dir}/**/*.md", recursive=True):
        if ".zh." not in md_file and "lang/" not in md_file:
            english_files.append(md_file)
    
    return english_files

def check_chinese_counterpart(english_file):
    """Check if Chinese counterpart exists for an English file."""
    if english_file.endswith(".md"):
        chinese_file = english_file[:-3] + ".zh.md"
        return os.path.exists(chinese_file), chinese_file
    return False, None

def check_language_switcher(file_path):
    """Check if file contains language switcher."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return "**Languages**:" in content or "**语言**:" in content
    except:
        return False

def main():
    print("🔍 Checking bilingual documentation sync...\n")
    
    # Check root README
    root_readme = "README.md"
    root_readme_zh = "README.zh.md"
    
    print("📄 Root Documentation:")
    if os.path.exists(root_readme):
        print(f"  ✅ {root_readme} exists")
        if check_language_switcher(root_readme):
            print(f"  ✅ {root_readme} has language switcher")
        else:
            print(f"  ⚠️  {root_readme} missing language switcher")
    else:
        print(f"  ❌ {root_readme} missing")
    
    if os.path.exists(root_readme_zh):
        print(f"  ✅ {root_readme_zh} exists")
        if check_language_switcher(root_readme_zh):
            print(f"  ✅ {root_readme_zh} has language switcher")
        else:
            print(f"  ⚠️  {root_readme_zh} missing language switcher")
    else:
        print(f"  ❌ {root_readme_zh} missing")
    
    print("\n📚 Documentation Directory:")
    
    english_docs = find_english_docs()
    missing_translations = []
    missing_switchers = []
    
    for eng_file in english_docs:
        has_chinese, zh_file = check_chinese_counterpart(eng_file)
        
        if has_chinese:
            print(f"  ✅ {eng_file} → {zh_file}")
            
            # Check language switchers
            if not check_language_switcher(eng_file):
                missing_switchers.append(eng_file)
            if not check_language_switcher(zh_file):
                missing_switchers.append(zh_file)
        else:
            print(f"  ❌ {eng_file} → {zh_file} (missing)")
            missing_translations.append(eng_file)
    
    # Summary
    print("\n📊 Summary:")
    print(f"  📄 Total English docs: {len(english_docs)}")
    print(f"  ✅ With Chinese translations: {len(english_docs) - len(missing_translations)}")
    print(f"  ❌ Missing translations: {len(missing_translations)}")
    print(f"  ⚠️  Missing language switchers: {len(missing_switchers)}")
    
    if missing_translations:
        print("\n🔄 Files needing translation:")
        for file in missing_translations:
            print(f"  - {file}")
    
    if missing_switchers:
        print("\n🔗 Files needing language switchers:")
        for file in missing_switchers:
            print(f"  - {file}")
    
    if not missing_translations and not missing_switchers:
        print("\n🎉 All documentation is in sync!")
    
    return len(missing_translations) == 0 and len(missing_switchers) == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
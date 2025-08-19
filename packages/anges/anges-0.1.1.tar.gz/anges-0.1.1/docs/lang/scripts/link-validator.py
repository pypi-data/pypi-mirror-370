#!/usr/bin/env python3
"""
Bilingual Documentation Link Validator

This script validates internal links in both English and Chinese documentation
to ensure language switching links work correctly and all references are valid.
"""

import os
import re
import glob
from pathlib import Path
from urllib.parse import urlparse

def extract_markdown_links(content):
    """Extract all markdown links from content."""
    # Pattern for [text](link) and [text](link#anchor)
    pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    return re.findall(pattern, content)

def is_internal_link(link):
    """Check if link is internal (relative path or anchor)."""
    parsed = urlparse(link)
    return not parsed.netloc and (link.startswith('./') or link.startswith('../') or link.endswith('.md') or link.startswith('#'))

def validate_file_link(link, current_file_dir):
    """Validate if a file link exists."""
    if link.startswith('#'):
        return True  # Anchor links need content analysis
    
    # Handle relative paths
    if link.startswith('./'):
        link = link[2:]
    elif link.startswith('../'):
        # Handle parent directory references
        pass
    
    # Remove anchor if present
    if '#' in link:
        link = link.split('#')[0]
    
    # Construct full path
    full_path = os.path.join(current_file_dir, link)
    full_path = os.path.normpath(full_path)
    
    return os.path.exists(full_path)

def check_language_switcher_links(file_path):
    """Check if language switcher links are valid."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for language switcher pattern
        lang_pattern = r'\*\*Languages?\*\*:|\*\*语言\*\*:'
        if not re.search(lang_pattern, content):
            return False, "No language switcher found"
        
        # Extract links from language switcher line
        lines = content.split('\n')
        switcher_line = None
        for line in lines:
            if re.search(lang_pattern, line):
                switcher_line = line
                break
        
        if not switcher_line:
            return False, "Language switcher pattern found but no switcher line"
        
        links = extract_markdown_links(switcher_line)
        current_dir = os.path.dirname(file_path)
        
        invalid_links = []
        for text, link in links:
            if is_internal_link(link) and not validate_file_link(link, current_dir):
                invalid_links.append(f"{text} -> {link}")
        
        if invalid_links:
            return False, f"Invalid links: {', '.join(invalid_links)}"
        
        return True, "All language switcher links valid"
    
    except Exception as e:
        return False, f"Error reading file: {e}"

def validate_all_internal_links(file_path):
    """Validate all internal links in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        links = extract_markdown_links(content)
        current_dir = os.path.dirname(file_path)
        
        invalid_links = []
        for text, link in links:
            if is_internal_link(link) and not validate_file_link(link, current_dir):
                invalid_links.append(f"{text} -> {link}")
        
        return len(invalid_links) == 0, invalid_links
    
    except Exception as e:
        return False, [f"Error reading file: {e}"]

def main():
    print("🔗 Validating bilingual documentation links...\n")
    
    # Find all markdown files
    all_md_files = []
    
    # Root README files
    for readme in ["README.md", "README.zh.md"]:
        if os.path.exists(readme):
            all_md_files.append(readme)
    
    # Documentation files
    for md_file in glob.glob("docs/**/*.md", recursive=True):
        if "lang/" not in md_file:  # Skip infrastructure files
            all_md_files.append(md_file)
    
    total_files = len(all_md_files)
    files_with_issues = 0
    
    print(f"📄 Checking {total_files} documentation files...\n")
    
    for file_path in all_md_files:
        print(f"Checking: {file_path}")
        
        # Check language switcher
        switcher_valid, switcher_msg = check_language_switcher_links(file_path)
        if switcher_valid:
            print(f"  ✅ Language switcher: {switcher_msg}")
        else:
            print(f"  ❌ Language switcher: {switcher_msg}")
            files_with_issues += 1
        
        # Check all internal links
        links_valid, invalid_links = validate_all_internal_links(file_path)
        if links_valid:
            print(f"  ✅ All internal links valid")
        else:
            print(f"  ❌ Invalid internal links:")
            for link in invalid_links[:3]:  # Show first 3 issues
                print(f"    - {link}")
            if len(invalid_links) > 3:
                print(f"    ... and {len(invalid_links) - 3} more")
            files_with_issues += 1
        
        print()
    
    # Summary
    print("📊 Validation Summary:")
    print(f"  📄 Total files checked: {total_files}")
    print(f"  ✅ Files without issues: {total_files - files_with_issues}")
    print(f"  ❌ Files with issues: {files_with_issues}")
    
    if files_with_issues == 0:
        print("\n🎉 All documentation links are valid!")
    else:
        print(f"\n⚠️  Found issues in {files_with_issues} files. Please review and fix.")
    
    return files_with_issues == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
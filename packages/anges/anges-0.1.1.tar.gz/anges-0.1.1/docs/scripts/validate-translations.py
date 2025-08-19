#!/usr/bin/env python3
"""
Translation Completeness Validator

This script validates the completeness of translations by comparing English and Chinese
documentation files, checking for missing translations, structural inconsistencies,
and broken cross-language links.
"""

import os
import re
import glob
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Set

class TranslationValidator:
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.docs_dir = self.root_dir / "docs"
        self.docs_zh_dir = self.docs_dir / "zh"
        self.issues = []
        self.stats = {
            "total_english_files": 0,
            "total_chinese_files": 0,
            "missing_translations": 0,
            "missing_english_originals": 0,
            "broken_language_links": 0,
            "structural_mismatches": 0
        }
    
    def log_issue(self, severity: str, category: str, file_path: str, message: str):
        """Log a validation issue."""
        self.issues.append({
            "severity": severity,
            "category": category,
            "file": str(file_path),
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def find_all_markdown_files(self) -> Tuple[List[Path], List[Path]]:
        """Find all English and Chinese markdown files."""
        english_files = []
        chinese_files = []
        
        # Root README files
        readme_en = self.root_dir / "README.md"
        readme_zh = self.root_dir / "README.zh.md"
        
        if readme_en.exists():
            english_files.append(readme_en)
        if readme_zh.exists():
            chinese_files.append(readme_zh)
        
        # Documentation files
        if self.docs_dir.exists():
            for md_file in self.docs_dir.glob("**/*.md"):
                # Skip infrastructure files
                if "lang/" not in str(md_file) and "/zh/" not in str(md_file):
                    english_files.append(md_file)
        
        if self.docs_zh_dir.exists():
            for md_file in self.docs_zh_dir.glob("**/*.md"):
                chinese_files.append(md_file)
        
        self.stats["total_english_files"] = len(english_files)
        self.stats["total_chinese_files"] = len(chinese_files)
        
        return english_files, chinese_files
    
    def get_chinese_counterpart(self, english_file: Path) -> Path:
        """Get the expected Chinese counterpart file path."""
        if english_file.name == "README.md":
            return self.root_dir / "README.zh.md"
        
        # For docs files, map to docs/zh/ structure
        relative_path = english_file.relative_to(self.docs_dir)
        return self.docs_zh_dir / relative_path
    
    def get_english_counterpart(self, chinese_file: Path) -> Path:
        """Get the expected English counterpart file path."""
        if chinese_file.name == "README.zh.md":
            return self.root_dir / "README.md"
        
        # For docs/zh files, map to docs/ structure
        relative_path = chinese_file.relative_to(self.docs_zh_dir)
        return self.docs_dir / relative_path
    
    def check_translation_completeness(self, english_files: List[Path], chinese_files: List[Path]):
        """Check for missing translations and orphaned Chinese files."""
        print("🔍 Checking translation completeness...")
        
        # Check for missing Chinese translations
        for eng_file in english_files:
            zh_file = self.get_chinese_counterpart(eng_file)
            if not zh_file.exists():
                self.log_issue("error", "missing_translation", eng_file, 
                             f"Missing Chinese translation: {zh_file}")
                self.stats["missing_translations"] += 1
                print(f"  ❌ Missing translation: {eng_file} → {zh_file}")
            else:
                print(f"  ✅ Translation exists: {eng_file} → {zh_file}")
        
        # Check for orphaned Chinese files
        for zh_file in chinese_files:
            eng_file = self.get_english_counterpart(zh_file)
            if not eng_file.exists():
                self.log_issue("warning", "orphaned_translation", zh_file,
                             f"Chinese file has no English counterpart: {eng_file}")
                self.stats["missing_english_originals"] += 1
                print(f"  ⚠️  Orphaned translation: {zh_file} (no {eng_file})")
    
    def extract_headers(self, content: str) -> List[str]:
        """Extract markdown headers from content."""
        headers = []
        for line in content.split('\n'):
            if line.strip().startswith('#'):
                # Remove markdown syntax and clean up
                header = re.sub(r'^#+\s*', '', line.strip())
                header = re.sub(r'\{[^}]*\}', '', header)  # Remove attributes
                headers.append(header.strip())
        return headers
    
    def check_structural_consistency(self, english_files: List[Path]):
        """Check if English and Chinese files have similar structure."""
        print("\n🏗️  Checking structural consistency...")
        
        for eng_file in english_files:
            zh_file = self.get_chinese_counterpart(eng_file)
            if not zh_file.exists():
                continue
            
            try:
                with open(eng_file, 'r', encoding='utf-8') as f:
                    eng_content = f.read()
                with open(zh_file, 'r', encoding='utf-8') as f:
                    zh_content = f.read()
                
                eng_headers = self.extract_headers(eng_content)
                zh_headers = self.extract_headers(zh_content)
                
                # Compare header count
                if len(eng_headers) != len(zh_headers):
                    self.log_issue("warning", "structure_mismatch", eng_file,
                                 f"Header count mismatch: EN={len(eng_headers)}, ZH={len(zh_headers)}")
                    self.stats["structural_mismatches"] += 1
                    print(f"  ⚠️  Structure mismatch: {eng_file} (EN: {len(eng_headers)} headers, ZH: {len(zh_headers)} headers)")
                else:
                    print(f"  ✅ Structure matches: {eng_file}")
                
            except Exception as e:
                self.log_issue("error", "read_error", eng_file, f"Error reading files: {e}")
                print(f"  ❌ Error checking structure: {eng_file} - {e}")
    
    def extract_language_switcher_links(self, content: str) -> List[str]:
        """Extract links from language switcher section."""
        links = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if "**Language" in line or "**语言" in line:
                # Check current and next few lines for links
                for j in range(i, min(i + 3, len(lines))):
                    link_matches = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', lines[j])
                    for text, link in link_matches:
                        if link.endswith('.md') or '.md#' in link:
                            links.append(link)
                break
        
        return links
    
    def check_language_switcher_links(self, english_files: List[Path]):
        """Check if language switcher links are valid."""
        print("\n🔗 Checking language switcher links...")
        
        all_files = english_files.copy()
        for eng_file in english_files:
            zh_file = self.get_chinese_counterpart(eng_file)
            if zh_file.exists():
                all_files.append(zh_file)
        
        for file_path in all_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if language switcher exists
                if "**Language" not in content and "**语言" not in content:
                    self.log_issue("warning", "missing_language_switcher", file_path,
                                 "No language switcher found")
                    print(f"  ⚠️  No language switcher: {file_path}")
                    continue
                
                # Extract and validate links
                links = self.extract_language_switcher_links(content)
                file_dir = file_path.parent
                
                broken_links = []
                for link in links:
                    # Handle relative paths
                    if link.startswith('./'):
                        link = link[2:]
                    
                    # Remove anchor if present
                    if '#' in link:
                        link = link.split('#')[0]
                    
                    target_path = file_dir / link
                    target_path = target_path.resolve()
                    
                    if not target_path.exists():
                        broken_links.append(link)
                
                if broken_links:
                    self.log_issue("error", "broken_language_link", file_path,
                                 f"Broken language switcher links: {', '.join(broken_links)}")
                    self.stats["broken_language_links"] += len(broken_links)
                    print(f"  ❌ Broken links in {file_path}: {', '.join(broken_links)}")
                else:
                    print(f"  ✅ Language switcher OK: {file_path}")
            
            except Exception as e:
                self.log_issue("error", "read_error", file_path, f"Error checking language switcher: {e}")
                print(f"  ❌ Error checking {file_path}: {e}")
    
    def generate_report(self, output_file: str = None) -> Dict:
        """Generate a comprehensive validation report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": self.stats,
            "issues": self.issues,
            "recommendations": []
        }
        
        # Generate recommendations
        if self.stats["missing_translations"] > 0:
            report["recommendations"].append(
                f"Create {self.stats['missing_translations']} missing Chinese translations"
            )
        
        if self.stats["broken_language_links"] > 0:
            report["recommendations"].append(
                f"Fix {self.stats['broken_language_links']} broken language switcher links"
            )
        
        if self.stats["structural_mismatches"] > 0:
            report["recommendations"].append(
                f"Review {self.stats['structural_mismatches']} files with structural mismatches"
            )
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n📄 Detailed report saved to: {output_file}")
        
        return report
    
    def run_validation(self) -> bool:
        """Run complete translation validation."""
        print("🚀 Starting translation validation...\n")
        
        english_files, chinese_files = self.find_all_markdown_files()
        
        if not english_files:
            print("❌ No English documentation files found!")
            return False
        
        self.check_translation_completeness(english_files, chinese_files)
        self.check_structural_consistency(english_files)
        self.check_language_switcher_links(english_files)
        
        # Print summary
        print("\n📊 Validation Summary:")
        print(f"  📄 English files: {self.stats['total_english_files']}")
        print(f"  📄 Chinese files: {self.stats['total_chinese_files']}")
        print(f"  ❌ Missing translations: {self.stats['missing_translations']}")
        print(f"  ⚠️  Orphaned translations: {self.stats['missing_english_originals']}")
        print(f"  🔗 Broken language links: {self.stats['broken_language_links']}")
        print(f"  🏗️  Structural mismatches: {self.stats['structural_mismatches']}")
        
        total_issues = (self.stats['missing_translations'] + 
                       self.stats['broken_language_links'] + 
                       self.stats['structural_mismatches'])
        
        if total_issues == 0:
            print("\n🎉 All translations are complete and consistent!")
            return True
        else:
            print(f"\n⚠️  Found {total_issues} issues that need attention.")
            return False

def main():
    parser = argparse.ArgumentParser(description="Validate translation completeness")
    parser.add_argument("--root", default=".", help="Root directory of the project")
    parser.add_argument("--report", help="Output file for detailed JSON report")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet mode - minimal output")
    
    args = parser.parse_args()
    
    validator = TranslationValidator(args.root)
    success = validator.run_validation()
    
    # Generate report if requested
    if args.report:
        validator.generate_report(args.report)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
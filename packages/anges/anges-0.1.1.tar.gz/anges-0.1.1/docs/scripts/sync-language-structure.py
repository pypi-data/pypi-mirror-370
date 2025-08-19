#!/usr/bin/env python3
"""
Bilingual Documentation Structure Synchronizer

This script maintains structural consistency between English and Chinese documentation
by detecting structural differences, synchronizing file organization, and providing
tools to keep both language versions aligned.
"""

import os
import re
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Set, Optional

class StructureSynchronizer:
    def __init__(self, root_dir: str = ".", dry_run: bool = True):
        self.root_dir = Path(root_dir)
        self.docs_dir = self.root_dir / "docs"
        self.docs_zh_dir = self.docs_dir / "zh"
        self.dry_run = dry_run
        self.operations = []
        self.stats = {
            "files_analyzed": 0,
            "structure_mismatches": 0,
            "missing_directories": 0,
            "operations_planned": 0,
            "operations_executed": 0
        }
    
    def log_operation(self, operation_type: str, source: str, target: str, description: str):
        """Log a planned or executed operation."""
        self.operations.append({
            "type": operation_type,
            "source": source,
            "target": target,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "executed": not self.dry_run
        })
        self.stats["operations_planned"] += 1
    
    def get_directory_structure(self, base_dir: Path) -> Dict[str, List[str]]:
        """Get the directory structure as a nested dictionary."""
        structure = {}
        
        if not base_dir.exists():
            return structure
        
        for item in base_dir.rglob("*"):
            if item.is_file() and item.suffix == ".md":
                # Skip infrastructure files
                if "lang/" in str(item):
                    continue
                
                relative_path = item.relative_to(base_dir)
                dir_path = str(relative_path.parent) if relative_path.parent != Path('.') else "."
                
                if dir_path not in structure:
                    structure[dir_path] = []
                structure[dir_path].append(item.name)
        
        return structure
    
    def compare_structures(self) -> Tuple[Dict, Dict, List[str]]:
        """Compare English and Chinese directory structures."""
        print("🔍 Analyzing directory structures...")
        
        en_structure = self.get_directory_structure(self.docs_dir)
        zh_structure = self.get_directory_structure(self.docs_zh_dir)
        
        # Find missing directories in Chinese structure
        missing_dirs = []
        for dir_path in en_structure:
            if dir_path not in zh_structure:
                missing_dirs.append(dir_path)
                print(f"  📁 Missing Chinese directory: docs/zh/{dir_path}")
        
        # Find extra directories in Chinese structure
        extra_dirs = []
        for dir_path in zh_structure:
            if dir_path not in en_structure:
                extra_dirs.append(dir_path)
                print(f"  📁 Extra Chinese directory: docs/zh/{dir_path}")
        
        self.stats["missing_directories"] = len(missing_dirs)
        
        return en_structure, zh_structure, missing_dirs
    
    def extract_document_outline(self, file_path: Path) -> List[Dict]:
        """Extract document outline (headers, sections, etc.)."""
        outline = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Headers
                if line.startswith('#'):
                    level = len(line) - len(line.lstrip('#'))
                    text = line.lstrip('#').strip()
                    outline.append({
                        "type": "header",
                        "level": level,
                        "text": text,
                        "line": i
                    })
                
                # Code blocks
                elif line.startswith('```'):
                    language = line[3:].strip()
                    outline.append({
                        "type": "code_block",
                        "language": language,
                        "line": i
                    })
                
                # Lists
                elif re.match(r'^\s*[-*+]\s', line) or re.match(r'^\s*\d+\.\s', line):
                    outline.append({
                        "type": "list_item",
                        "text": re.sub(r'^\s*[-*+\d.]+\s*', '', line),
                        "line": i
                    })
                
                # Tables
                elif '|' in line and line.count('|') >= 2:
                    outline.append({
                        "type": "table_row",
                        "line": i
                    })
        
        except Exception as e:
            print(f"  ❌ Error reading {file_path}: {e}")
        
        return outline
    
    def compare_document_structures(self, en_structure: Dict, zh_structure: Dict):
        """Compare the internal structure of corresponding documents."""
        print("\n📋 Comparing document structures...")
        
        for dir_path, en_files in en_structure.items():
            if dir_path not in zh_structure:
                continue
            
            zh_files = zh_structure[dir_path]
            
            for en_file in en_files:
                if en_file not in zh_files:
                    continue
                
                # Build full paths
                if dir_path == ".":
                    en_path = self.docs_dir / en_file
                    zh_path = self.docs_zh_dir / en_file
                else:
                    en_path = self.docs_dir / dir_path / en_file
                    zh_path = self.docs_zh_dir / dir_path / en_file
                
                if not en_path.exists() or not zh_path.exists():
                    continue
                
                print(f"  📄 Comparing: {en_path.relative_to(self.root_dir)}")
                
                en_outline = self.extract_document_outline(en_path)
                zh_outline = self.extract_document_outline(zh_path)
                
                # Compare header structures
                en_headers = [item for item in en_outline if item["type"] == "header"]
                zh_headers = [item for item in zh_outline if item["type"] == "header"]
                
                if len(en_headers) != len(zh_headers):
                    self.log_operation("structure_mismatch", str(en_path), str(zh_path),
                                     f"Header count mismatch: EN={len(en_headers)}, ZH={len(zh_headers)}")
                    self.stats["structure_mismatches"] += 1
                    print(f"    ⚠️  Header count mismatch: EN={len(en_headers)}, ZH={len(zh_headers)}")
                    continue
                
                # Compare header levels
                level_mismatch = False
                for i, (en_h, zh_h) in enumerate(zip(en_headers, zh_headers)):
                    if en_h["level"] != zh_h["level"]:
                        level_mismatch = True
                        print(f"    ⚠️  Header {i+1} level mismatch: EN=H{en_h['level']}, ZH=H{zh_h['level']}")
                
                if level_mismatch:
                    self.log_operation("structure_mismatch", str(en_path), str(zh_path),
                                     "Header level inconsistencies detected")
                    self.stats["structure_mismatches"] += 1
                else:
                    print(f"    ✅ Structure matches")
                
                self.stats["files_analyzed"] += 1
    
    def create_missing_directories(self, missing_dirs: List[str]):
        """Create missing directories in the Chinese documentation structure."""
        if not missing_dirs:
            return
        
        print(f"\n📁 Creating {len(missing_dirs)} missing directories...")
        
        for dir_path in missing_dirs:
            if dir_path == ".":
                continue
            
            zh_dir = self.docs_zh_dir / dir_path
            
            if self.dry_run:
                print(f"  [DRY RUN] Would create: {zh_dir}")
                self.log_operation("create_directory", "", str(zh_dir), 
                                 f"Create missing directory: {dir_path}")
            else:
                try:
                    zh_dir.mkdir(parents=True, exist_ok=True)
                    print(f"  ✅ Created: {zh_dir}")
                    self.log_operation("create_directory", "", str(zh_dir), 
                                     f"Created directory: {dir_path}")
                    self.stats["operations_executed"] += 1
                except Exception as e:
                    print(f"  ❌ Failed to create {zh_dir}: {e}")
    
    def generate_structure_template(self, en_file: Path, zh_file: Path):
        """Generate a Chinese template based on English file structure."""
        try:
            with open(en_file, 'r', encoding='utf-8') as f:
                en_content = f.read()
            
            # Extract structure and create template
            lines = en_content.split('\n')
            template_lines = []
            
            for line in lines:
                if line.strip().startswith('#'):
                    # Keep headers but add translation placeholder
                    template_lines.append(line)
                    template_lines.append("<!-- TODO: Translate header -->")
                elif line.strip().startswith('```'):
                    # Keep code blocks as-is
                    template_lines.append(line)
                elif re.match(r'^\s*[-*+]\s', line) or re.match(r'^\s*\d+\.\s', line):
                    # Keep list structure but add translation placeholder
                    template_lines.append(line)
                    template_lines.append("<!-- TODO: Translate list item -->")
                elif line.strip() == "":
                    # Keep empty lines
                    template_lines.append(line)
                else:
                    # For other content, add placeholder
                    if line.strip():
                        template_lines.append("<!-- TODO: Translate content -->")
                        template_lines.append("")
            
            template_content = '\n'.join(template_lines)
            
            if self.dry_run:
                print(f"  [DRY RUN] Would create template: {zh_file}")
            else:
                zh_file.parent.mkdir(parents=True, exist_ok=True)
                with open(zh_file, 'w', encoding='utf-8') as f:
                    f.write(template_content)
                print(f"  ✅ Created template: {zh_file}")
                self.stats["operations_executed"] += 1
            
            self.log_operation("create_template", str(en_file), str(zh_file),
                             "Generated Chinese template from English structure")
        
        except Exception as e:
            print(f"  ❌ Failed to create template for {zh_file}: {e}")
    
    def sync_file_structure(self, en_structure: Dict, zh_structure: Dict):
        """Synchronize file structure between English and Chinese versions."""
        print("\n📄 Synchronizing file structures...")
        
        for dir_path, en_files in en_structure.items():
            zh_files = zh_structure.get(dir_path, [])
            
            for en_file in en_files:
                if en_file not in zh_files:
                    # Missing Chinese file
                    if dir_path == ".":
                        en_path = self.docs_dir / en_file
                        zh_path = self.docs_zh_dir / en_file
                    else:
                        en_path = self.docs_dir / dir_path / en_file
                        zh_path = self.docs_zh_dir / dir_path / en_file
                    
                    print(f"  📄 Missing Chinese file: {zh_path.relative_to(self.root_dir)}")
                    self.generate_structure_template(en_path, zh_path)
    
    def generate_sync_report(self, output_file: str = None) -> Dict:
        """Generate a synchronization report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "statistics": self.stats,
            "operations": self.operations,
            "recommendations": []
        }
        
        # Generate recommendations
        if self.stats["missing_directories"] > 0:
            report["recommendations"].append(
                f"Create {self.stats['missing_directories']} missing directories in Chinese documentation"
            )
        
        if self.stats["structure_mismatches"] > 0:
            report["recommendations"].append(
                f"Review and fix {self.stats['structure_mismatches']} structural inconsistencies"
            )
        
        if self.stats["operations_planned"] > 0 and self.dry_run:
            report["recommendations"].append(
                f"Run without --dry-run to execute {self.stats['operations_planned']} planned operations"
            )
        
        if output_file:
            import json
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n📄 Sync report saved to: {output_file}")
        
        return report
    
    def run_synchronization(self) -> bool:
        """Run complete structure synchronization."""
        mode = "DRY RUN" if self.dry_run else "EXECUTION"
        print(f"🚀 Starting structure synchronization ({mode})...\n")
        
        # Ensure Chinese docs directory exists
        if not self.docs_zh_dir.exists() and not self.dry_run:
            self.docs_zh_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created Chinese docs directory: {self.docs_zh_dir}")
        
        # Compare and sync structures
        en_structure, zh_structure, missing_dirs = self.compare_structures()
        self.create_missing_directories(missing_dirs)
        self.compare_document_structures(en_structure, zh_structure)
        self.sync_file_structure(en_structure, zh_structure)
        
        # Print summary
        print("\n📊 Synchronization Summary:")
        print(f"  📄 Files analyzed: {self.stats['files_analyzed']}")
        print(f"  📁 Missing directories: {self.stats['missing_directories']}")
        print(f"  🏗️  Structure mismatches: {self.stats['structure_mismatches']}")
        print(f"  🔧 Operations planned: {self.stats['operations_planned']}")
        if not self.dry_run:
            print(f"  ✅ Operations executed: {self.stats['operations_executed']}")
        
        total_issues = (self.stats['missing_directories'] + 
                       self.stats['structure_mismatches'])
        
        if total_issues == 0:
            print("\n🎉 All structures are synchronized!")
            return True
        else:
            if self.dry_run:
                print(f"\n📋 Found {total_issues} issues. Run without --dry-run to fix them.")
            else:
                print(f"\n⚠️  {total_issues} issues remain after synchronization.")
            return False

def main():
    parser = argparse.ArgumentParser(description="Synchronize bilingual documentation structure")
    parser.add_argument("--root", default=".", help="Root directory of the project")
    parser.add_argument("--execute", action="store_true", help="Execute operations (default is dry-run)")
    parser.add_argument("--report", help="Output file for detailed JSON report")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet mode - minimal output")
    
    args = parser.parse_args()
    
    synchronizer = StructureSynchronizer(args.root, dry_run=not args.execute)
    success = synchronizer.run_synchronization()
    
    # Generate report if requested
    if args.report:
        synchronizer.generate_sync_report(args.report)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
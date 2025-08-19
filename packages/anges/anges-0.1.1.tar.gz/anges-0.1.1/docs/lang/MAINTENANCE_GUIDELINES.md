# Bilingual Documentation Maintenance Guidelines

This document provides comprehensive guidelines for maintaining the bilingual (English/Chinese) documentation system, including automated validation tools and best practices.

## Overview

Our documentation system supports both English and Chinese versions with automated validation to ensure consistency and completeness. The system includes:

- **Primary Documentation**: English files in `docs/` and root `README.md`
- **Chinese Translations**: Chinese files in `docs/zh/` and root `README.zh.md`
- **Language Switching**: Embedded language switchers in all documentation files
- **Automated Validation**: Scripts to check translation completeness and structural consistency

## Validation Scripts

### 1. Translation Completeness Validator

**Location**: `scripts/validate-translations.py`

**Purpose**: Validates translation completeness by comparing English and Chinese documentation files.

**Usage**:
```bash
# Basic validation
python scripts/validate-translations.py

# Generate detailed report
python scripts/validate-translations.py --report validation-report.json

# Validate specific directory
python scripts/validate-translations.py --root /path/to/project

# Quiet mode
python scripts/validate-translations.py --quiet
```

**What it checks**:
- Missing Chinese translations for English files
- Orphaned Chinese files without English counterparts
- Broken language switcher links
- Structural consistency between language versions
- Header count and structure mismatches

### 2. Structure Synchronizer

**Location**: `scripts/sync-language-structure.py`

**Purpose**: Maintains structural consistency between English and Chinese documentation.

**Usage**:
```bash
# Dry run (preview changes)
python scripts/sync-language-structure.py

# Execute synchronization
python scripts/sync-language-structure.py --execute

# Generate sync report
python scripts/sync-language-structure.py --report sync-report.json

# Quiet mode
python scripts/sync-language-structure.py --quiet
```

**What it does**:
- Compares directory structures between English and Chinese versions
- Creates missing directories in Chinese documentation
- Generates template files for missing translations
- Detects structural inconsistencies in document organization
- Provides detailed synchronization reports

## Maintenance Workflow

### Daily/Weekly Checks

1. **Run Translation Validation**:
   ```bash
   python scripts/validate-translations.py --report daily-validation.json
   ```

2. **Review Validation Report**:
   - Check for missing translations
   - Fix broken language switcher links
   - Address structural mismatches

3. **Run Structure Synchronization** (if needed):
   ```bash
   # Preview changes first
   python scripts/sync-language-structure.py
   
   # Execute if changes look correct
   python scripts/sync-language-structure.py --execute
   ```

### When Adding New Documentation

1. **Create English Version First**:
   - Write the English documentation in the appropriate `docs/` subdirectory
   - Include proper language switcher section
   - Follow established documentation structure

2. **Generate Chinese Template**:
   ```bash
   python scripts/sync-language-structure.py --execute
   ```
   This will create a template Chinese file with the same structure.

3. **Translate Content**:
   - Replace template placeholders with Chinese translations
   - Maintain the same header structure and organization
   - Update language switcher links

4. **Validate Results**:
   ```bash
   python scripts/validate-translations.py
   ```

### When Modifying Existing Documentation

1. **Update English Version**:
   - Make changes to the English documentation
   - Ensure language switcher remains intact

2. **Check Impact on Chinese Version**:
   ```bash
   python scripts/validate-translations.py
   ```

3. **Update Chinese Translation**:
   - Apply corresponding changes to Chinese version
   - Maintain structural consistency
   - Update any affected cross-references

4. **Validate Synchronization**:
   ```bash
   python scripts/sync-language-structure.py
   python scripts/validate-translations.py
   ```

## Language Switcher Guidelines

### Required Format

Every documentation file must include a language switcher section:

**English files**:
```markdown
**Language**: [English](./README.md) | [中文](./README.zh.md)
```

**Chinese files**:
```markdown
**语言**: [English](../README.md) | [中文](./README.zh.md)
```

### Link Path Rules

1. **Root README files**:
   - `README.md` → `README.zh.md`
   - `README.zh.md` → `README.md`

2. **Documentation files**:
   - English: `docs/file.md` → `docs/zh/file.md`
   - Chinese: `docs/zh/file.md` → `docs/file.md`

3. **Subdirectory files**:
   - English: `docs/subdir/file.md` → `docs/zh/subdir/file.md`
   - Chinese: `docs/zh/subdir/file.md` → `docs/subdir/file.md`

## File Organization Standards

### Directory Structure

```
project-root/
├── README.md                 # English root README
├── README.zh.md             # Chinese root README
├── docs/
│   ├── README.md            # English docs index
│   ├── file1.md             # English documentation
│   ├── subdir/
│   │   └── file2.md         # English subdirectory docs
│   └── zh/                  # Chinese documentation mirror
│       ├── README.md        # Chinese docs index
│       ├── file1.md         # Chinese translation
│       └── subdir/
│           └── file2.md     # Chinese subdirectory docs
└── scripts/
    ├── validate-translations.py
    └── sync-language-structure.py
```

### Naming Conventions

1. **English files**: Use standard markdown filenames (`file.md`)
2. **Chinese files**: Use identical filenames in `zh/` subdirectory
3. **Root files**: Add `.zh` suffix for Chinese (`README.zh.md`)
4. **Assets**: Organize in `docs/assets/en/` and `docs/assets/zh/` for language-specific content

## Quality Assurance Checklist

### Before Committing Changes

- [ ] Run translation validation: `python scripts/validate-translations.py`
- [ ] Run structure synchronization check: `python scripts/sync-language-structure.py`
- [ ] Verify language switchers work correctly
- [ ] Check that all links resolve properly
- [ ] Ensure consistent formatting between language versions
- [ ] Validate that code examples work in both versions

### Monthly Maintenance

- [ ] Generate comprehensive validation report
- [ ] Review and fix any accumulated issues
- [ ] Update maintenance guidelines if needed
- [ ] Check for broken external links
- [ ] Verify asset files are properly organized

## Troubleshooting Common Issues

### Missing Translations

**Problem**: Validation shows missing Chinese translations.

**Solution**:
1. Run structure synchronizer to generate templates:
   ```bash
   python scripts/sync-language-structure.py --execute
   ```
2. Translate the generated template files
3. Validate results

### Broken Language Switcher Links

**Problem**: Language switcher links are broken.

**Solution**:
1. Check file paths and ensure target files exist
2. Verify relative path calculations
3. Update links according to the path rules above
4. Re-run validation

### Structural Mismatches

**Problem**: English and Chinese files have different structures.

**Solution**:
1. Compare the files manually
2. Ensure header levels and organization match
3. Update the Chinese version to match English structure
4. Maintain content organization consistency

### Directory Structure Issues

**Problem**: Missing directories in Chinese documentation.

**Solution**:
1. Run structure synchronizer:
   ```bash
   python scripts/sync-language-structure.py --execute
   ```
2. This will create missing directories and template files

## CI/CD Integration Guidelines

### Manual Validation Process

Since no CI workflows currently exist, follow this manual process:

1. **Pre-commit Validation**:
   ```bash
   # Run both validation scripts
   python scripts/validate-translations.py
   python scripts/sync-language-structure.py
   
   # Only commit if validation passes
   ```

2. **Weekly Validation**:
   ```bash
   # Generate reports for review
   python scripts/validate-translations.py --report weekly-validation.json
   python scripts/sync-language-structure.py --report weekly-sync.json
   ```

### Future CI Integration

When CI workflows are added, consider including:

```yaml
# Example GitHub Actions workflow
name: Documentation Validation

on:
  pull_request:
    paths:
      - 'docs/**'
      - 'README*.md'

jobs:
  validate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Validate translations
        run: python scripts/validate-translations.py
      - name: Check structure sync
        run: python scripts/sync-language-structure.py
```

## Best Practices

### Documentation Writing

1. **Consistency**: Maintain consistent terminology across languages
2. **Structure**: Keep the same document organization in both versions
3. **Links**: Always update language switchers when adding new files
4. **Assets**: Use shared assets when possible, language-specific when necessary
5. **Code Examples**: Ensure code examples work and are properly formatted in both versions

### Translation Guidelines

1. **Accuracy**: Prioritize accuracy over literal translation
2. **Context**: Consider cultural context for Chinese readers
3. **Technical Terms**: Use established Chinese technical terminology
4. **Formatting**: Maintain markdown formatting consistency
5. **Links**: Ensure all internal links point to Chinese versions

### Maintenance Schedule

- **Daily**: Quick validation check if documentation changes
- **Weekly**: Comprehensive validation and issue resolution
- **Monthly**: Full system review and guideline updates
- **Quarterly**: Process improvement and tool enhancement review

## Support and Resources

### Script Documentation

- Both validation scripts include `--help` options for detailed usage information
- Scripts generate JSON reports for programmatic analysis
- All scripts support quiet mode for automated execution

### Getting Help

If you encounter issues with the bilingual documentation system:

1. Check this maintenance guide first
2. Run validation scripts to identify specific problems
3. Review the troubleshooting section
4. Check existing documentation in `docs/lang/` for additional guidance

### Contributing Improvements

To improve the bilingual documentation system:

1. Test changes with validation scripts
2. Update maintenance guidelines if processes change
3. Consider backward compatibility for existing documentation
4. Document any new validation rules or processes

---

*This guide should be updated whenever the bilingual documentation system or validation tools are modified.*
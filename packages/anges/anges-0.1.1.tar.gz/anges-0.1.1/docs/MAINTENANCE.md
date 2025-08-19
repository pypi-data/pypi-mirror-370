<!-- Language Switcher -->
**Language**: [English](MAINTENANCE.md) | [中文](zh/MAINTENANCE.md)

---

# Bilingual Documentation Maintenance Guide

This guide provides comprehensive instructions for maintaining the bilingual (English/Chinese) documentation system in this repository.

## Overview

Our documentation system supports seamless switching between English and Chinese versions with the following structure:

```
.
├── README.md (English)
├── README.zh.md (Chinese)
├── docs/
│   ├── *.md (English docs)
│   └── zh/
│       └── *.md (Chinese docs)
└── scripts/
    ├── validate-translations.py
    └── sync-language-structure.py
```

## Language Switcher Format

Every markdown file must include a language switcher at the top:

### English Files
```markdown
<!-- Language Switcher -->
**Language**: [English](filename.md) | [中文](zh/filename.md)

---
```

### Chinese Files
```markdown
<!-- Language Switcher -->
**语言**: [English](../filename.md) | [中文](filename.md)

---
```

## Adding New Documentation

### Step 1: Create English Version
1. Create the English markdown file in the appropriate location
2. Add the language switcher header
3. Write the content

### Step 2: Create Chinese Version
1. Create the corresponding Chinese file in the `zh/` subdirectory
2. Add the Chinese language switcher header
3. Translate the content, maintaining the same structure

### Step 3: Validate
Run the validation script to ensure everything is correct:
```bash
python scripts/validate-translations.py
```

## Updating Existing Documentation

### When updating English files:
1. Make changes to the English version
2. Update the corresponding Chinese version
3. Ensure structural consistency (same number of headers)
4. Run validation script

### When updating Chinese files:
1. Make changes to the Chinese version
2. Consider if English version needs updates
3. Run validation script

## Validation Tools

### Translation Validator
```bash
python scripts/validate-translations.py
```

This script checks:
- Translation completeness
- Structural consistency
- Language switcher links
- Broken cross-references

### Structure Synchronizer
```bash
python scripts/sync-language-structure.py
```

This script helps maintain structural consistency between language versions.

## Common Issues and Solutions

### Issue: Missing Language Switcher
**Solution**: Add the appropriate language switcher header to the top of the file.

### Issue: Structural Mismatch
**Solution**: Ensure both language versions have the same number and level of headers.

### Issue: Broken Links
**Solution**: Update relative paths to ensure they work from both language versions.

### Issue: Orphaned Translations
**Solution**: Either create the missing English version or remove the orphaned Chinese file.

## Best Practices

1. **Consistency**: Maintain the same document structure across languages
2. **Regular Validation**: Run validation scripts before committing changes
3. **Atomic Updates**: Update both language versions together when possible
4. **Clear Paths**: Use relative paths that work from both language versions
5. **Header Hierarchy**: Keep the same header levels and organization

## File Naming Conventions

- English files: `filename.md`
- Chinese files: `filename.md` (in `zh/` subdirectory)
- Root Chinese files: `filename.zh.md`

## Directory Structure Rules

- Chinese translations go in parallel `zh/` subdirectories
- Root-level Chinese files use `.zh.md` suffix
- Maintain the same directory structure in both languages

## Automation and CI/CD

Consider adding these checks to your CI/CD pipeline:

```yaml
# Example GitHub Actions step
- name: Validate Translations
  run: python scripts/validate-translations.py
```

## Troubleshooting

### Validation Script Issues
- Ensure you're running from the project root directory
- Check that all markdown files have proper language switchers
- Verify directory structure matches expectations

### Link Issues
- Use relative paths consistently
- Test links from both language versions
- Consider using the sync script to fix structural issues

## Future Enhancements

Potential improvements to consider:
- Automated translation suggestions
- Link validation across languages
- Content synchronization alerts
- Translation status tracking

---

For questions or issues with the bilingual documentation system, please refer to this guide or create an issue in the repository.
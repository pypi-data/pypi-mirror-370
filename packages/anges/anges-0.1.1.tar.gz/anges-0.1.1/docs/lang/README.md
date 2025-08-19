# Language Switching Infrastructure for Anges Documentation

## Overview

This document outlines the bilingual documentation infrastructure for the Anges project, supporting both English and Chinese versions of all documentation.

## Research: GitHub Best Practices for Bilingual Documentation

### Common Approaches

1. **Language Badges in README**
   - Use language badges at the top of README files
   - Format: `[English](README.md) | [中文](README.zh.md)`
   - Provides clear visual indication of available languages

2. **File Naming Conventions**
   - English (default): `README.md`, `guide.md`
   - Chinese: `README.zh.md`, `guide.zh.md`
   - Alternative: `README.zh-CN.md` for specific locale

3. **Directory Structure Options**
   - **Option A**: Parallel files in same directory
     ```
     docs/
     ├── README.md (English)
     ├── README.zh.md (Chinese)
     ├── api-reference.md
     ├── api-reference.zh.md
     ```
   - **Option B**: Language-specific subdirectories
     ```
     docs/
     ├── en/
     │   ├── README.md
     │   └── api-reference.md
     ├── zh/
     │   ├── README.md
     │   └── api-reference.md
     ```
   - **Option C**: Mixed approach (recommended)
     ```
     docs/
     ├── README.md (English default)
     ├── README.zh.md (Chinese)
     ├── lang/
     │   ├── zh/
     │   │   ├── api-reference.md
     │   │   └── implementation-guide.md
     ```

### Selected Approach for Anges

We will use **Option A (Parallel Files)** with the following rationale:
- Maintains existing file structure
- Easy to discover and navigate
- Consistent with GitHub's language detection
- Simple linking between language versions

## Implementation Strategy

### Phase 1: Infrastructure Setup
1. Create language switching badges for all documentation
2. Establish consistent file naming convention
3. Create templates for bilingual documentation
4. Document translation workflow

### Phase 2: Content Translation
1. Translate main README.md
2. Translate docs/README.md
3. Translate core documentation files
4. Create Chinese versions of all docs

### Phase 3: Maintenance
1. Establish process for keeping translations in sync
2. Create automation tools if needed
3. Document contributor guidelines for bilingual content

## Language Switching Patterns

### 1. Language Badge Pattern
```markdown
<!-- Language switcher - place at top of every documentation file -->
**Languages**: [English](filename.md) | [中文](filename.zh.md)

---
```

### 2. File Naming Convention
- English (default): `{filename}.md`
- Chinese: `{filename}.zh.md`
- Examples:
  - `README.md` → `README.zh.md`
  - `api-reference.md` → `api-reference.zh.md`
  - `implementation-guide.md` → `implementation-guide.zh.md`

### 3. Cross-Reference Linking
- Always include language switcher at the top
- Link to corresponding sections in other language versions
- Maintain consistent anchor links across languages

### 4. Asset Handling
- Shared assets: Use same images/diagrams for both languages
- Language-specific assets: Use subdirectories `assets/en/` and `assets/zh/`
- Screenshots with text: Create separate versions for each language

## Directory Structure Plan

```
.
├── README.md (English)
├── README.zh.md (Chinese)
├── docs/
│   ├── README.md (English)
│   ├── README.zh.md (Chinese)
│   ├── api-reference.md
│   ├── api-reference.zh.md
│   ├── architecture.md
│   ├── architecture.zh.md
│   ├── implementation-guide.md
│   ├── implementation-guide.zh.md
│   ├── configuration-system.md
│   ├── configuration-system.zh.md
│   ├── utility-functions.md
│   ├── utility-functions.zh.md
│   ├── web-interface.md
│   ├── web-interface.zh.md
│   ├── assets/
│   │   ├── en/ (English-specific assets)
│   │   ├── zh/ (Chinese-specific assets)
│   │   └── shared/ (Language-neutral assets)
│   ├── examples/
│   │   ├── README.md
│   │   └── README.zh.md
│   └── lang/
│       ├── templates/
│       │   ├── doc-template.md
│       │   └── doc-template.zh.md
│       └── scripts/
│           └── sync-check.py
```

## Translation Guidelines

### Technical Terms
- Keep English technical terms in parentheses for first occurrence
- Example: "代理 (Agent)", "事件循环 (Event Loop)"
- Maintain consistency across all documents

### Code Examples
- Keep code examples identical between languages
- Translate only comments and documentation strings
- Maintain same file paths and examples

### Links and References
- Update internal links to point to corresponding language versions
- External links remain the same unless Chinese equivalent exists
- Maintain anchor link consistency

## Maintenance Workflow

1. **New Documentation**: Create both English and Chinese versions
2. **Updates**: Update English first, then Chinese
3. **Review**: Native speakers review translations
4. **Sync Check**: Regular verification that both versions cover same content

## Tools and Scripts

### Planned Utilities
1. **sync-check.py**: Verify translation completeness
2. **link-validator.py**: Check internal links work for both languages
3. **template-generator.py**: Generate bilingual file templates

This infrastructure provides a solid foundation for maintaining high-quality bilingual documentation that scales with the project.
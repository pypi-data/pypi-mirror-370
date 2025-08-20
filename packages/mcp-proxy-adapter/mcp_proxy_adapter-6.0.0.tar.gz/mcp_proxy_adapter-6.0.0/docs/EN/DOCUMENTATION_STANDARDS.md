# Documentation Standards

**Contents**: 1. Core Principles • 2. File Structure • 3. Formatting Rules • 4. Bilingual Requirements • 5. Tooling

## 1. Core Principles

### 1.1. Single Source of Truth
Each aspect of the project should have a single, authoritative documentation reference. Cross-references should be used instead of duplication.

### 1.2. Bilingual Equivalence
All documentation must exist in both English and Russian with identical structure, content, examples, and formatting.

### 1.3. Machine Readability
Documentation should be formatted in a way that is easily processable by documentation tools, language models, and search engines.

### 1.4. Developer-First Approach
Documentation should be organized to make it easy for developers to find information quickly and understand requirements unambiguously.

## 2. File Structure

### 2.1. Root Documentation Files
The following files must exist at the docs root level in both EN and RU directories:

| File                     | Purpose                                         |
|--------------------------|--------------------------------------------------|
| PROJECT_RULES.md         | Overall project rules and governance             |
| NAMING_STANDARDS.md      | Naming conventions and structure standards       |
| COMMAND_CHECKLIST.md     | Checklist for implementing new commands          |
| GLOSSARY.md              | Terminology definitions used across the project  |
| DOCUMENTATION_STANDARDS.md | Documentation requirements and formatting rules |

### 2.2. Command Documentation
Each command must have a dedicated documentation file:
- Location: `docs/{LANG}/commands/{command_name}_command.md`
- Must include all required sections (see Section 3.3)

### 2.3. Cross-References
Use relative path links to reference related documentation:
```markdown
See [CommandResult definition](../GLOSSARY.md#commandresult) for more details.
```

## 3. Formatting Rules

### 3.1. Markdown Syntax
- Use standard GitHub Flavored Markdown
- Headers should use the ATX style (#, ##, ###)
- All code blocks must specify language identifiers:
  ```python
  def example_code():
      return "This is properly formatted"
  ```

### 3.2. Section Numbering
Use consistent section numbering in the format:
```
# Main Title

## 1. First Section
### 1.1. Subsection

## 2. Second Section
### 2.1. Subsection
```

### 3.3. Required Sections in Command Documentation
1. **Overview** - Brief description of the command's purpose
2. **Parameters** - Table with name, type, description, required status
3. **Result** - Description and structure of the return value
4. **Examples** - Code examples in Python, JSON-RPC, and HTTP REST format
5. **Implementation Details** - Notes on implementation specifics
6. **Error Handling** - Possible error conditions and their responses

### 3.4. Code Examples
Each command documentation must include examples in:
- Python code
- JSON-RPC request/response
- HTTP REST request/response (if applicable)

## 4. Bilingual Requirements

### 4.1. File Equivalence
- Each documentation file must exist in both `/docs/EN/` and `/docs/RU/` directories
- Files must have identical names in both directories
- Section structure must be identical

### 4.2. Content Synchronization
- Updates must be made to both language versions simultaneously
- Code examples must be identical in both versions
- Diagrams and schemas must be identical (only text labels can be translated)

### 4.3. Translation Quality
- Technical terms should be accompanied by their English equivalents in parentheses in the Russian documentation
- Use the approved translations from the glossary for consistency

## 5. Tooling

### 5.1. Validation Checks
- Use CI/CD pipelines to validate bilingual consistency
- Check for broken links

### 5.2. Documentation Generation
- API documentation is generated from code annotations and schemas
- Command examples should be validated against latest code

### 5.3. Style Linting
- Use markdown linters to enforce consistent formatting
- Enforce section numbering and required sections

## 6. Maintenance

### 6.1. Review Process
- Documentation changes should be reviewed alongside code changes
- Bilingual consistency should be verified during review

### 6.2. Deprecation Marking
- Deprecated features should be clearly marked in documentation
- Include migration guidance for deprecated features 
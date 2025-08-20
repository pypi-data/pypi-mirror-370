# MCP Microservice Project Rules

## 1. Standards

### 1.1. Code Standards
- Each command in a separate file
- Strict typing for all parameters and return values
- Asynchronous command execution
- Unified response format via JSON-RPC
- Standardized error handling

### 1.2. Naming Standards
- snake_case for files and functions
- PascalCase for classes
- UPPER_CASE for constants and documentation files
- Prefix `_` for protected methods
- Prefix `__` for private methods

### 1.3. File Structure Standards
```python
# Section order in command files:
1. Module docstring
2. Imports (standard → third-party → project)
3. Constants and types
4. Result class
5. Helper functions
6. Command
```

### 1.4. Documentation Standards
- **MANDATORY** to maintain documentation in both languages:
  - Russian (directory `/docs/RU/`)
  - English (directory `/docs/EN/`)
- **Russian documentation MUST be an exact copy of the English version:**
  - Identical file structure
  - Identical section structure
  - Identical code examples
  - Identical formatting
  - Identical diagrams and schemas
- Prohibited:
  - Adding documentation in only one language
  - Having differences in structure or content between versions
  - Updating one version without updating the other
- When making changes:
  - Changes are made simultaneously to both versions
  - Version correspondence is verified
  - Commit must contain changes in both versions

## 2. Checklists

### 2.1. Adding a New Command
- [ ] Create `{command_name}_command.py` file
- [ ] Define result class
- [ ] Implement `to_dict()` and `get_schema()` methods
- [ ] Implement command
- [ ] Add tests
- [ ] Create documentation

### 2.2. Testing Command
- [ ] Success scenario tests
- [ ] Error tests
- [ ] Parameter validation checks
- [ ] Result serialization checks
- [ ] Schema generation checks

### 2.3. Documentation Check
- [ ] Module docstring
- [ ] Result class docstring
- [ ] Command docstring
- [ ] Usage examples
- [ ] Parameter descriptions
- [ ] JSON-RPC request/response examples
- [ ] **Check correspondence between Russian and English versions:**
  - [ ] File and section structure
  - [ ] Code examples
  - [ ] Formatting
  - [ ] Diagrams and schemas
  - [ ] Translation completeness

### 2.4. Code Review
- [ ] Compliance with naming standards
- [ ] Typing correctness
- [ ] Test coverage
- [ ] Documentation completeness
- [ ] Error handling
- [ ] **Bilingual documentation check:**
  - [ ] Presence of both versions
  - [ ] Structure identity
  - [ ] Change synchronization

## 3. Documentation

### 3.1. Documentation Structure
```
docs/
├── EN/                 # English documentation (mandatory)
│   ├── commands/       # Command documentation
│   │   └── {command_name}_command.md
│   ├── PROJECT_RULES.md
│   ├── NAMING_STANDARDS.md
│   └── api/           # API documentation
└── RU/                # Russian documentation (mandatory)
    ├── commands/      # Command documentation
    │   └── {command_name}_command.md
    ├── PROJECT_RULES.md
    ├── NAMING_STANDARDS.md
    └── api/           # API documentation
```

### 3.2. Required Sections in Command Documentation
1. Description (in both languages)
2. Result (with code example)
3. Command (with code example)
4. Implementation details
5. Usage examples
   - Python
   - HTTP REST
   - JSON-RPC

### 3.3. Documentation Requirements
- Up-to-date code examples
- Description of all parameters
- Description of possible errors
- Examples of successful and unsuccessful scenarios
- Data validation schemas
- **Synchronization of Russian and English versions**
- **Identical structure in both versions**
- **Identical code examples in both versions**

### 3.4. Documentation Formatting
- Markdown for all files
- Mermaid for diagrams
- Formatted code blocks with language specification
- Tables for structured data

## 4. Lifecycle

### 4.1. Development
1. Create command file
2. Implement result
3. Implement command
4. Write tests
5. Create documentation

### 4.2. Testing
1. Unit tests
2. Integration tests
3. Documentation check
4. API schema check

### 4.3. Deployment
1. Check dependencies
2. Update API schema
3. Data migration (if required)
4. Update documentation

### 4.4. Support
1. Execution monitoring
2. Error analysis
3. Update when necessary
4. Backward compatibility support 
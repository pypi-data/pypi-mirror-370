# Anti-Patterns

This example demonstrates common anti-patterns and bad practices when developing microservices. These examples are provided for educational purposes to help developers understand what to avoid.

## Structure

```
anti_patterns/
├── __init__.py                  # Package initialization
├── README.md                    # Documentation
├── bad_design/                  # Bad design patterns
│   ├── __init__.py
│   ├── large_command.py         # Monolithic command with too many responsibilities
│   ├── tight_coupling.py        # Tightly coupled components
│   └── magic_strings.py         # Hard-coded values and magic strings
├── performance_issues/          # Performance anti-patterns
│   ├── __init__.py
│   ├── blocking_operations.py   # Blocking operations in async code
│   ├── memory_leaks.py          # Memory leak examples
│   └── n_plus_one.py            # N+1 query problem
├── security_problems/           # Security anti-patterns
│   ├── __init__.py
│   ├── command_injection.py     # Command injection vulnerability
│   ├── insecure_deserialization.py # Insecure deserialization
│   └── no_input_validation.py   # Missing input validation
└── tests/                       # Tests demonstrating issues
```

## Bad Design Examples

### Monolithic Command

The `large_command.py` demonstrates a command that tries to do too much in a single class:

```python
class DoEverythingCommand(Command):
    """A command that tries to do everything in one place."""
    
    name = "do_everything"
    result_class = DoEverythingResult
    
    async def execute(
        self, 
        user_id: str,
        action: str,
        file_path: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None, 
        format: str = "json",
        notify: bool = False,
        # ... many more parameters
    ) -> DoEverythingResult:
        """
        Execute command that tries to do too many things.
        
        This command handles user authentication, file operations,
        data processing, notifications, and reporting all in one place.
        """
        # Hundreds of lines of code with multiple responsibilities
        # ...
```

### Tight Coupling

The `tight_coupling.py` shows components that are tightly coupled and hard to maintain:

```python
class DatabaseCommand(Command):
    """A command tightly coupled to a specific database implementation."""
    
    name = "db_operation"
    result_class = DatabaseResult
    
    async def execute(self, operation: str, data: Dict[str, Any]) -> DatabaseResult:
        # Direct instantiation of concrete implementation
        db = PostgreSQLDatabase(host="localhost", port=5432, user="admin")
        
        # Direct calls to implementation-specific methods
        if operation == "insert":
            result = db.execute_insert_query("INSERT INTO table VALUES (...)")
        elif operation == "update":
            result = db.execute_update_query("UPDATE table SET ...")
        
        return DatabaseResult(result)
```

## Performance Issues

### Blocking Operations

The `blocking_operations.py` demonstrates improper use of blocking calls in async code:

```python
class BlockingCommand(Command):
    """Command that blocks the event loop with synchronous operations."""
    
    name = "blocking"
    result_class = BlockingResult
    
    async def execute(self, operation: str) -> BlockingResult:
        if operation == "sleep":
            # Blocks the entire event loop!
            time.sleep(5)  # Should be await asyncio.sleep(5)
            
        elif operation == "io":
            # Blocking I/O operation
            with open("large_file.txt", "r") as f:  # Should use async file I/O
                content = f.read()
                
        return BlockingResult(True)
```

## Security Problems

### No Input Validation

The `no_input_validation.py` shows a command that doesn't validate user input:

```python
class InsecureCommand(Command):
    """Command with no input validation."""
    
    name = "insecure"
    result_class = InsecureResult
    
    async def execute(self, filename: str, content: str) -> InsecureResult:
        # No validation of filename - can contain path traversal
        # content is not sanitized or validated
        
        # Vulnerable to path traversal
        with open(filename, "w") as f:
            f.write(content)
            
        return InsecureResult(True)
```

## How to Avoid Anti-Patterns

For each anti-pattern demonstrated, this example also provides a corrected version showing the recommended approach:

1. **Split large commands** into smaller, single-responsibility commands
2. **Use dependency injection** and interfaces instead of tight coupling
3. **Always use async properly** and avoid blocking operations
4. **Validate all input** before processing
5. **Use parameterized queries** for database operations
6. **Implement proper error handling** with meaningful error messages
7. **Follow security best practices** for all operations

## Key Concepts Demonstrated

1. Common design anti-patterns
2. Performance pitfalls in async code
3. Security vulnerabilities
4. Memory management issues
5. Tight coupling problems
6. "Magic" values and hard-coding
7. Proper design alternatives 
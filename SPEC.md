# ArkTS Code Knowledge Graph - Dynamic Update Edition

## Concept & Vision

A real-time code knowledge graph system that keeps synchronized with codebase changes. Built on first principles: 99% of code changes involve only 1-2 files, so the system only processes changed files instead of re-parsing the entire project. This makes it a true development-time tool rather than a one-time analysis report.

The system monitors `.ets` files, extracts entities (classes, methods) and relationships (calls, components), and stores them in SQLite for fast queries. Updates complete in under 0.5 seconds for single-file changes.

## Architecture

```
Code File Changes → File System Watcher → Change Queue (Debounced) → Incremental Update Processor → SQLite Database
                                                                                    ↓
                                                                           Real-time Query API
```

## Data Model

### Tables

- **files**: Project source files with content hashes
  - `id`: Primary key
  - `path`: Unique file path
  - `hash`: 16-byte MD5 hash for change detection
  - `modified`: Unix timestamp

- **classes**: Class definitions
  - `id`: Primary key
  - `name`: Class name
  - `file_id`: Foreign key to files
  - `flags`: Access modifiers and type flags
  - `start_line`, `end_line`: Source location

- **methods**: Method/function definitions
  - `id`: Primary key
  - `name`: Method name
  - `class_id`: Foreign key to classes
  - `params`: Parameter signatures
  - `return_type`: Return type annotation
  - `start_line`, `end_line`: Source location

- **calls**: Function call relationships
  - `caller_id`: Calling method (FK)
  - `callee_name`: Called function name
  - `callee_file_id`: File containing the called function (if found)
  - `callee_id`: Specific method if resolved
  - Primary key: (caller_id, callee_name, callee_file_id)

- **components**: Component composition relationships
  - `parent_id`: Container class (FK)
  - `child_id`: Contained class (FK)
  - Primary key: (parent_id, child_id)

## Features

### Core Features

1. **ArkTS Parser**: Extracts classes, methods, decorators, and relationships from `.ets` files
2. **File System Watcher**: Monitors project for `.ets` file changes using watchdog
3. **Hash-based Change Detection**: Only processes files where content actually changed
4. **Debounced Updates**: Batches rapid successive changes to the same file
5. **Atomic Updates**: Each file update is a transaction - all or nothing
6. **Query API**: REST-like interface to query entities and relationships

### Query Capabilities

- Find class definition by name or path
- Find all methods in a class
- Find all callers of a function
- Find all classes that compose a given class
- Find component hierarchy
- Search by decorator (e.g., @Component, @Entry)

## Technical Approach

- **Language**: Python 3.11+
- **Database**: SQLite with DELETE journal mode for reliable transaction handling
- **Parsing**: Regex-based ArkTS parser with support for classes, structs, and functions
- **File Watching**: watchdog library with polling fallback
- **Concurrency**: Threading for file watching, synchronous database operations

## Performance Targets

| Operation | Target | Description |
|----------|--------|-------------|
| Single file update | <0.5s | Most common development scenario |
| 10 file batch | <2s | Small branch switch |
| 100 file batch | <10s | Code pull scenario |
| Full sync (1M lines) | 8min | Initial run or large branch switch |

## API Endpoints

- `GET /query/class/<name>` - Find class by name
- `GET /query/file/<path>` - Get all entities in file
- `GET /query/callers/<method>` - Find all callers of method
- `GET /query/callees/<method>` - Find all methods called by method
- `GET /query/components/<class>` - Find component relationships
- `GET /stats` - Database statistics

"""SQLite database management for code knowledge graph."""

import sqlite3
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import hashlib
import os


@dataclass
class FileRecord:
    """Represents a file record in the database."""
    id: int
    path: str
    hash: bytes
    modified: int


@dataclass
class ClassRecord:
    """Represents a class record in the database."""
    id: int
    name: str
    file_id: int
    flags: int
    start_line: int
    end_line: int


@dataclass
class MethodRecord:
    """Represents a method record in the database."""
    id: int
    name: str
    class_id: int
    params: str
    return_type: str
    start_line: int
    end_line: int


class Database:
    """Manages SQLite database for code knowledge graph."""
    
    def __init__(self, db_path: str = "code_graph.db"):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
    
    def initialize(self):
        """Initialize database connection and create tables."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA journal_mode=DELETE")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self._create_tables()
    
    def _create_tables(self):
        """Create all necessary tables."""
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY,
                path TEXT UNIQUE NOT NULL,
                hash BLOB NOT NULL,
                modified INTEGER NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                file_id INTEGER NOT NULL,
                flags INTEGER DEFAULT 0,
                start_line INTEGER NOT NULL,
                end_line INTEGER NOT NULL,
                FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
            );
            
            CREATE TABLE IF NOT EXISTS methods (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                class_id INTEGER,
                params TEXT DEFAULT '',
                return_type TEXT DEFAULT '',
                start_line INTEGER NOT NULL,
                end_line INTEGER NOT NULL,
                FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
            );
            
            CREATE TABLE IF NOT EXISTS calls (
                caller_id INTEGER NOT NULL,
                callee_name TEXT NOT NULL,
                callee_file_id INTEGER,
                callee_id INTEGER,
                PRIMARY KEY (caller_id, callee_name, callee_file_id),
                FOREIGN KEY (caller_id) REFERENCES methods(id) ON DELETE CASCADE,
                FOREIGN KEY (callee_file_id) REFERENCES files(id) ON DELETE SET NULL,
                FOREIGN KEY (callee_id) REFERENCES methods(id) ON DELETE SET NULL
            );
            
            CREATE TABLE IF NOT EXISTS components (
                parent_id INTEGER NOT NULL,
                child_id INTEGER NOT NULL,
                PRIMARY KEY (parent_id, child_id),
                FOREIGN KEY (parent_id) REFERENCES classes(id) ON DELETE CASCADE,
                FOREIGN KEY (child_id) REFERENCES classes(id) ON DELETE CASCADE
            );
            
            CREATE INDEX IF NOT EXISTS idx_classes_file ON classes(file_id);
            CREATE INDEX IF NOT EXISTS idx_classes_name ON classes(name);
            CREATE INDEX IF NOT EXISTS idx_methods_class ON methods(class_id);
            CREATE INDEX IF NOT EXISTS idx_methods_name ON methods(name);
            CREATE INDEX IF NOT EXISTS idx_calls_caller ON calls(caller_id);
            CREATE INDEX IF NOT EXISTS idx_calls_callee ON calls(callee_id);
            CREATE INDEX IF NOT EXISTS idx_files_path ON files(path);
        """)
        self.conn.commit()
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def compute_file_hash(self, file_path: str) -> bytes:
        """Compute MD5 hash of file content."""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        return hasher.digest()
    
    def get_file_hash(self, file_id: int) -> Optional[bytes]:
        """Get stored hash for a file."""
        cursor = self.conn.execute(
            "SELECT hash FROM files WHERE id = ?", (file_id,)
        )
        row = cursor.fetchone()
        return row[0] if row else None
    
    def get_all_file_paths(self) -> dict[str, tuple[int, bytes]]:
        """Get all file paths with their IDs and hashes."""
        cursor = self.conn.execute("SELECT id, path, hash FROM files")
        return {row[1]: (row[0], row[2]) for row in cursor.fetchall()}
    
    def begin_transaction(self):
        """Begin a database transaction."""
        self.conn.execute("BEGIN TRANSACTION")
    
    def commit(self):
        """Commit the current transaction."""
        self.conn.commit()
    
    def rollback(self):
        """Rollback the current transaction."""
        self.conn.rollback()
    
    def insert_file(self, path: str, file_hash: bytes, modified: int) -> int:
        """Insert a new file record and return its ID."""
        cursor = self.conn.execute(
            "INSERT INTO files (path, hash, modified) VALUES (?, ?, ?)",
            (path, file_hash, modified)
        )
        return cursor.lastrowid
    
    def update_file(self, file_id: int, file_hash: bytes, modified: int):
        """Update an existing file record."""
        self.conn.execute(
            "UPDATE files SET hash = ?, modified = ? WHERE id = ?",
            (file_hash, modified, file_id)
        )
    
    def delete_file(self, file_id: int):
        """Delete a file and all its associated data."""
        self.conn.execute("DELETE FROM files WHERE id = ?", (file_id,))
    
    def get_file_by_path(self, path: str) -> Optional[FileRecord]:
        """Get file record by path."""
        cursor = self.conn.execute(
            "SELECT id, path, hash, modified FROM files WHERE path = ?",
            (path,)
        )
        row = cursor.fetchone()
        if row:
            return FileRecord(id=row[0], path=row[1], hash=row[2], modified=row[3])
        return None
    
    def insert_class(self, name: str, file_id: int, flags: int = 0,
                     start_line: int = 0, end_line: int = 0) -> int:
        """Insert a new class record and return its ID."""
        cursor = self.conn.execute(
            "INSERT INTO classes (name, file_id, flags, start_line, end_line) VALUES (?, ?, ?, ?, ?)",
            (name, file_id, flags, start_line, end_line)
        )
        return cursor.lastrowid
    
    def get_classes_by_file(self, file_id: int) -> list[ClassRecord]:
        """Get all classes in a file."""
        cursor = self.conn.execute(
            "SELECT id, name, file_id, flags, start_line, end_line FROM classes WHERE file_id = ?",
            (file_id,)
        )
        return [
            ClassRecord(id=row[0], name=row[1], file_id=row[2], flags=row[3],
                       start_line=row[4], end_line=row[5])
            for row in cursor.fetchall()
        ]
    
    def get_class_by_name(self, name: str) -> Optional[ClassRecord]:
        """Get class record by name."""
        cursor = self.conn.execute(
            "SELECT id, name, file_id, flags, start_line, end_line FROM classes WHERE name = ?",
            (name,)
        )
        row = cursor.fetchone()
        if row:
            return ClassRecord(id=row[0], name=row[1], file_id=row[2], flags=row[3],
                             start_line=row[4], end_line=row[5])
        return None
    
    def insert_method(self, name: str, class_id: Optional[int], params: str = '',
                      return_type: str = '', start_line: int = 0, end_line: int = 0) -> int:
        """Insert a new method record and return its ID."""
        cursor = self.conn.execute(
            "INSERT INTO methods (name, class_id, params, return_type, start_line, end_line) VALUES (?, ?, ?, ?, ?, ?)",
            (name, class_id, params, return_type, start_line, end_line)
        )
        return cursor.lastrowid
    
    def get_methods_by_class(self, class_id: int) -> list[MethodRecord]:
        """Get all methods in a class."""
        cursor = self.conn.execute(
            "SELECT id, name, class_id, params, return_type, start_line, end_line FROM methods WHERE class_id = ?",
            (class_id,)
        )
        return [
            MethodRecord(id=row[0], name=row[1], class_id=row[2], params=row[3],
                        return_type=row[4], start_line=row[5], end_line=row[6])
            for row in cursor.fetchall()
        ]
    
    def get_method_by_name(self, name: str) -> Optional[MethodRecord]:
        """Get method record by name."""
        cursor = self.conn.execute(
            "SELECT id, name, class_id, params, return_type, start_line, end_line FROM methods WHERE name = ? AND class_id IS NULL",
            (name,)
        )
        row = cursor.fetchone()
        if row:
            return MethodRecord(id=row[0], name=row[1], class_id=row[2], params=row[3],
                              return_type=row[4], start_line=row[5], end_line=row[6])
        return None
    
    def insert_call(self, caller_id: int, callee_name: str,
                   callee_file_id: Optional[int] = None, callee_id: Optional[int] = None):
        """Insert a new call relationship."""
        self.conn.execute(
            "INSERT OR IGNORE INTO calls (caller_id, callee_name, callee_file_id, callee_id) VALUES (?, ?, ?, ?)",
            (caller_id, callee_name, callee_file_id, callee_id)
        )
    
    def insert_component(self, parent_id: int, child_id: int):
        """Insert a new component relationship."""
        self.conn.execute(
            "INSERT OR IGNORE INTO components (parent_id, child_id) VALUES (?, ?)",
            (parent_id, child_id)
        )
    
    def get_callers(self, method_name: str) -> list[dict]:
        """Get all callers of a method."""
        cursor = self.conn.execute("""
            SELECT m.id, m.name, c.id, c.name, f.path, f.id
            FROM calls call
            JOIN methods m ON call.caller_id = m.id
            LEFT JOIN classes c ON m.class_id = c.id
            LEFT JOIN files f ON c.file_id = f.id
            WHERE call.callee_name = ?
        """, (method_name,))
        return [
            {
                'method_id': row[0],
                'method_name': row[1],
                'class_id': row[2],
                'class_name': row[3],
                'file_path': row[4],
                'file_id': row[5]
            }
            for row in cursor.fetchall()
        ]
    
    def get_callees(self, method_id: int) -> list[dict]:
        """Get all methods called by a method."""
        cursor = self.conn.execute("""
            SELECT call.callee_name, call.callee_id, f.path, m.id, m.name
            FROM calls call
            LEFT JOIN files f ON call.callee_file_id = f.id
            LEFT JOIN methods m ON call.callee_id = m.id
            WHERE call.caller_id = ?
        """, (method_id,))
        return [
            {
                'callee_name': row[0],
                'callee_id': row[1],
                'file_path': row[2],
                'method_id': row[3],
                'method_name': row[4]
            }
            for row in cursor.fetchall()
        ]
    
    def get_components(self, class_name: str) -> tuple[list[dict], list[dict]]:
        """Get component relationships for a class."""
        class_record = self.get_class_by_name(class_name)
        if not class_record:
            return [], []
        
        cursor = self.conn.execute("""
            SELECT c2.id, c2.name, f.path
            FROM components comp
            JOIN classes c2 ON comp.child_id = c2.id
            LEFT JOIN files f ON c2.file_id = f.id
            WHERE comp.parent_id = ?
        """, (class_record.id,))
        children = [
            {'class_id': row[0], 'class_name': row[1], 'file_path': row[2]}
            for row in cursor.fetchall()
        ]
        
        cursor = self.conn.execute("""
            SELECT c2.id, c2.name, f.path
            FROM components comp
            JOIN classes c2 ON comp.parent_id = c2.id
            LEFT JOIN files f ON c2.file_id = f.id
            WHERE comp.child_id = ?
        """, (class_record.id,))
        parents = [
            {'class_id': row[0], 'class_name': row[1], 'file_path': row[2]}
            for row in cursor.fetchall()
        ]
        
        return children, parents
    
    def get_stats(self) -> dict:
        """Get database statistics."""
        cursor = self.conn.execute("""
            SELECT 
                (SELECT COUNT(*) FROM files) as file_count,
                (SELECT COUNT(*) FROM classes) as class_count,
                (SELECT COUNT(*) FROM methods) as method_count,
                (SELECT COUNT(*) FROM calls) as call_count,
                (SELECT COUNT(*) FROM components) as component_count
        """)
        row = cursor.fetchone()
        return {
            'files': row[0],
            'classes': row[1],
            'methods': row[2],
            'calls': row[3],
            'components': row[4]
        }

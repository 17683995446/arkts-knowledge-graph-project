"""
ArkAnalyzer SQLite Database Schema
Designed for storing code knowledge graph from ark_analyzer
"""

import sqlite3
from typing import Optional, List, Dict, Any
import json
import os


class ArkAnalyzerDB:
    """SQLite database for ArkAnalyzer code knowledge graph."""

    def __init__(self, db_path: str = "ark_graph.db"):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

    def initialize(self):
        """Initialize database connection and create tables."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA journal_mode=DELETE")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self._create_tables()

    def _create_tables(self):
        """Create all necessary tables for ArkAnalyzer output."""
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                path TEXT NOT NULL,
                analyzed_at INTEGER NOT NULL,
                total_files INTEGER DEFAULT 0,
                total_classes INTEGER DEFAULT 0,
                total_methods INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY,
                project_id INTEGER NOT NULL,
                path TEXT NOT NULL,
                hash TEXT,
                line_count INTEGER DEFAULT 0,
                analyzed_at INTEGER NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                UNIQUE(project_id, path)
            );

            CREATE TABLE IF NOT EXISTS namespaces (
                id INTEGER PRIMARY KEY,
                project_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                file_id INTEGER,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY,
                project_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                signature TEXT,
                file_id INTEGER,
                namespace_id INTEGER,
                flags INTEGER DEFAULT 0,
                start_line INTEGER DEFAULT 0,
                end_line INTEGER DEFAULT 0,
                source_code TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE SET NULL,
                FOREIGN KEY (namespace_id) REFERENCES namespaces(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS methods (
                id INTEGER PRIMARY KEY,
                project_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                signature TEXT,
                class_id INTEGER,
                namespace_id INTEGER,
                file_id INTEGER,
                params TEXT DEFAULT '',
                return_type TEXT DEFAULT '',
                flags INTEGER DEFAULT 0,
                start_line INTEGER DEFAULT 0,
                end_line INTEGER DEFAULT 0,
                source_code TEXT,
                is_constructor INTEGER DEFAULT 0,
                is_static INTEGER DEFAULT 0,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
                FOREIGN KEY (namespace_id) REFERENCES namespaces(id) ON DELETE SET NULL,
                FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS fields (
                id INTEGER PRIMARY KEY,
                project_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                type TEXT DEFAULT '',
                class_id INTEGER,
                flags INTEGER DEFAULT 0,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS calls (
                id INTEGER PRIMARY KEY,
                project_id INTEGER NOT NULL,
                caller_method_id INTEGER NOT NULL,
                callee_method_name TEXT,
                callee_signature TEXT,
                callee_method_id INTEGER,
                call_type TEXT DEFAULT 'instance',
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (caller_method_id) REFERENCES methods(id) ON DELETE CASCADE,
                FOREIGN KEY (callee_method_id) REFERENCES methods(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS imports (
                id INTEGER PRIMARY KEY,
                project_id INTEGER NOT NULL,
                file_id INTEGER NOT NULL,
                import_path TEXT NOT NULL,
                import_type TEXT DEFAULT 'normal',
                is_default INTEGER DEFAULT 0,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS exports (
                id INTEGER PRIMARY KEY,
                project_id INTEGER NOT NULL,
                file_id INTEGER NOT NULL,
                export_name TEXT NOT NULL,
                export_type TEXT DEFAULT 'named',
                target_name TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS decorators (
                id INTEGER PRIMARY KEY,
                project_id INTEGER NOT NULL,
                class_id INTEGER,
                method_id INTEGER,
                name TEXT NOT NULL,
                args TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
                FOREIGN KEY (method_id) REFERENCES methods(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_files_project ON files(project_id);
            CREATE INDEX IF NOT EXISTS idx_classes_project ON classes(project_id);
            CREATE INDEX IF NOT EXISTS idx_classes_file ON classes(file_id);
            CREATE INDEX IF NOT EXISTS idx_classes_name ON classes(name);
            CREATE INDEX IF NOT EXISTS idx_methods_project ON methods(project_id);
            CREATE INDEX IF NOT EXISTS idx_methods_class ON methods(class_id);
            CREATE INDEX IF NOT EXISTS idx_methods_name ON methods(name);
            CREATE INDEX IF NOT EXISTS idx_calls_caller ON calls(caller_method_id);
            CREATE INDEX IF NOT EXISTS idx_calls_callee ON calls(callee_method_id);
            CREATE INDEX IF NOT EXISTS idx_namespaces_project ON namespaces(project_id);
            CREATE INDEX IF NOT EXISTS idx_fields_class ON fields(class_id);
            CREATE INDEX IF NOT EXISTS idx_decorators_class ON decorators(class_id);
            CREATE INDEX IF NOT EXISTS idx_decorators_method ON decorators(method_id);
        """)
        self.conn.commit()

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def begin_transaction(self):
        """Begin a database transaction."""
        self.conn.execute("BEGIN TRANSACTION")

    def commit(self):
        """Commit the current transaction."""
        self.conn.commit()

    def rollback(self):
        """Rollback the current transaction."""
        self.conn.rollback()

    def insert_project(self, name: str, path: str, analyzed_at: int) -> int:
        """Insert a new project and return its ID."""
        cursor = self.conn.execute(
            "INSERT OR REPLACE INTO projects (name, path, analyzed_at) VALUES (?, ?, ?)",
            (name, path, analyzed_at)
        )
        return cursor.lastrowid

    def insert_file(self, project_id: int, path: str, hash_val: str,
                   line_count: int, analyzed_at: int) -> Optional[int]:
        """Insert a file and return its ID. Returns None if file hasn't changed."""
        cursor = self.conn.execute(
            """SELECT id, hash FROM files WHERE project_id = ? AND path = ?""",
            (project_id, path)
        )
        existing = cursor.fetchone()
        
        if existing and existing[1] == hash_val:
            return existing[0]
        
        cursor = self.conn.execute(
            """INSERT OR REPLACE INTO files (project_id, path, hash, line_count, analyzed_at)
               VALUES (?, ?, ?, ?, ?)""",
            (project_id, path, hash_val, line_count, analyzed_at)
        )
        return cursor.lastrowid

    def insert_class(self, project_id: int, name: str, signature: str,
                   file_id: int, namespace_id: Optional[int], flags: int,
                   start_line: int, end_line: int, source_code: Optional[str]) -> int:
        """Insert a class and return its ID."""
        cursor = self.conn.execute(
            """INSERT INTO classes (project_id, name, signature, file_id, namespace_id,
               flags, start_line, end_line, source_code)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (project_id, name, signature, file_id, namespace_id, flags,
             start_line, end_line, source_code)
        )
        return cursor.lastrowid

    def insert_method(self, project_id: int, name: str, signature: str,
                    class_id: Optional[int], namespace_id: Optional[int], file_id: Optional[int],
                    params: str, return_type: str, flags: int, start_line: int,
                    end_line: int, source_code: Optional[str], is_constructor: int,
                    is_static: int) -> int:
        """Insert a method and return its ID."""
        cursor = self.conn.execute(
            """INSERT INTO methods (project_id, name, signature, class_id, namespace_id,
               file_id, params, return_type, flags, start_line, end_line, source_code,
               is_constructor, is_static)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (project_id, name, signature, class_id, namespace_id, file_id,
             params, return_type, flags, start_line, end_line, source_code,
             is_constructor, is_static)
        )
        return cursor.lastrowid

    def insert_call(self, project_id: int, caller_method_id: int,
                   callee_method_name: str, callee_signature: Optional[str],
                   callee_method_id: Optional[int], call_type: str) -> int:
        """Insert a call relationship and return its ID."""
        cursor = self.conn.execute(
            """INSERT INTO calls (project_id, caller_method_id, callee_method_name,
               callee_signature, callee_method_id, call_type)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (project_id, caller_method_id, callee_method_name, callee_signature,
             callee_method_id, call_type)
        )
        return cursor.lastrowid

    def insert_namespace(self, project_id: int, name: str, file_id: int) -> int:
        """Insert a namespace and return its ID."""
        cursor = self.conn.execute(
            "INSERT INTO namespaces (project_id, name, file_id) VALUES (?, ?, ?)",
            (project_id, name, file_id)
        )
        return cursor.lastrowid

    def insert_field(self, project_id: int, name: str, type_val: str,
                    class_id: int, flags: int) -> int:
        """Insert a field and return its ID."""
        cursor = self.conn.execute(
            "INSERT INTO fields (project_id, name, type, class_id, flags) VALUES (?, ?, ?, ?, ?)",
            (project_id, name, type_val, class_id, flags)
        )
        return cursor.lastrowid

    def insert_decorator(self, project_id: int, class_id: int,
                        method_id: int, name: str, args: str) -> int:
        """Insert a decorator and return its ID."""
        cursor = self.conn.execute(
            """INSERT INTO decorators (project_id, class_id, method_id, name, args)
               VALUES (?, ?, ?, ?, ?)""",
            (project_id, class_id, method_id, name, args)
        )
        return cursor.lastrowid

    def insert_import(self, project_id: int, file_id: int,
                     import_path: str, import_type: str,
                     is_default: int) -> int:
        """Insert an import and return its ID."""
        cursor = self.conn.execute(
            """INSERT INTO imports (project_id, file_id, import_path, import_type, is_default)
               VALUES (?, ?, ?, ?, ?)""",
            (project_id, file_id, import_path, import_type, is_default)
        )
        return cursor.lastrowid

    def query_class(self, project_id: int, class_name: str) -> Optional[Dict]:
        """Query a class by name."""
        cursor = self.conn.execute("""
            SELECT c.id, c.project_id, c.name, c.signature, c.file_id, c.namespace_id,
                   c.flags, c.start_line, c.end_line, c.source_code, f.path as file_path
            FROM classes c
            LEFT JOIN files f ON c.file_id = f.id
            WHERE c.project_id = ? AND c.name = ?
        """, (project_id, class_name))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_dict(row, [
            'id', 'project_id', 'name', 'signature', 'file_id', 'namespace_id',
            'flags', 'start_line', 'end_line', 'source_code', 'file_path'
        ])

    def query_methods_by_class(self, class_id: int) -> List[Dict]:
        """Query all methods in a class."""
        cursor = self.conn.execute("""
            SELECT * FROM methods WHERE class_id = ? ORDER BY start_line
        """, (class_id,))
        columns = ['id', 'project_id', 'name', 'signature', 'class_id', 'namespace_id',
                  'params', 'return_type', 'flags', 'start_line', 'end_line',
                  'source_code', 'file_id', 'is_constructor', 'is_static']
        return [self._row_to_dict(row, columns) for row in cursor.fetchall()]

    def query_callers(self, method_id: int) -> List[Dict]:
        """Query all callers of a method."""
        cursor = self.conn.execute("""
            SELECT m.name as caller, c.name as class_name, f.path as file_path
            FROM calls call
            JOIN methods m ON call.caller_method_id = m.id
            LEFT JOIN classes c ON m.class_id = c.id
            LEFT JOIN files f ON c.file_id = f.id
            WHERE call.callee_method_id = ?
        """, (method_id,))
        return [
            {'method': row[0], 'class': row[1], 'file': row[2]}
            for row in cursor.fetchall()
        ]

    def query_callees(self, method_id: int) -> List[Dict]:
        """Query all methods called by a method."""
        cursor = self.conn.execute("""
            SELECT call.callee_method_name, call.callee_signature,
                   COALESCE(m.name, 'external') as method_name,
                   COALESCE(c.name, 'unknown') as class_name
            FROM calls call
            LEFT JOIN methods m ON call.callee_method_id = m.id
            LEFT JOIN classes c ON m.class_id = c.id
            WHERE call.caller_method_id = ?
        """, (method_id,))
        return [
            {'name': row[0], 'signature': row[1], 'method': row[2], 'class': row[3]}
            for row in cursor.fetchall()
        ]

    def get_project_stats(self, project_id: int) -> Dict:
        """Get project statistics."""
        cursor = self.conn.execute("""
            SELECT
                (SELECT COUNT(*) FROM files WHERE project_id = ?) as files,
                (SELECT COUNT(*) FROM classes WHERE project_id = ?) as classes,
                (SELECT COUNT(*) FROM methods WHERE project_id = ?) as methods,
                (SELECT COUNT(*) FROM calls WHERE project_id = ?) as calls,
                (SELECT COUNT(*) FROM namespaces WHERE project_id = ?) as namespaces
        """, (project_id, project_id, project_id, project_id, project_id))
        row = cursor.fetchone()
        return {
            'files': row[0],
            'classes': row[1],
            'methods': row[2],
            'calls': row[3],
            'namespaces': row[4]
        }

    def export_graph(self, project_id: int) -> Dict:
        """Export the entire knowledge graph as JSON."""
        files = self.conn.execute(
            "SELECT id, path, line_count FROM files WHERE project_id = ?",
            (project_id,)
        ).fetchall()

        classes = self.conn.execute(
            "SELECT id, name, signature, file_id, flags, start_line, end_line FROM classes WHERE project_id = ?",
            (project_id,)
        ).fetchall()

        methods = self.conn.execute(
            "SELECT id, name, signature, class_id, params, return_type, flags, start_line, end_line FROM methods WHERE project_id = ?",
            (project_id,)
        ).fetchall()

        calls = self.conn.execute(
            "SELECT caller_method_id, callee_method_name, callee_method_id FROM calls WHERE project_id = ?",
            (project_id,)
        ).fetchall()
        
        # 构建 nodes 数组
        nodes = []
        node_map = {}  # maps (type, id) -> node_index
        
        # 添加文件节点
        for i, row in enumerate(files):
            file_node = {
                'id': f"file_{row[0]}",
                'name': os.path.basename(row[1]),
                'type': 'file',
                'file': row[1],
                'lines': row[2]
            }
            nodes.append(file_node)
            node_map[('file', row[0])] = i
        
        # 添加类节点
        for row in classes:
            class_node = {
                'id': f"class_{row[0]}",
                'name': row[1],
                'type': 'class',
                'file': row[3],
                'flags': row[4],
                'start': row[5],
                'end': row[6]
            }
            nodes.append(class_node)
            node_map[('class', row[0])] = len(nodes) - 1
        
        # 添加方法节点
        for row in methods:
            method_node = {
                'id': f"method_{row[0]}",
                'name': row[1],
                'type': 'method',
                'class_id': row[3],
                'params': row[4],
                'return': row[5],
                'flags': row[6],
                'start': row[7],
                'end': row[8]
            }
            nodes.append(method_node)
            node_map[('method', row[0])] = len(nodes) - 1
        
        # 构建 links 数组
        links = []
        
        # 方法 -> 文件链接
        for row in methods:
            if row[3] is None:  # class_id
                method_id = row[0]
                links.append({
                    'source': f"method_{method_id}",
                    'target': None,  # 独立函数没有文件链接
                    'type': 'standalone'
                })
        
        # 方法 -> 类链接
        for row in methods:
            if row[3] is not None:
                method_id = row[0]
                class_id = row[3]
                links.append({
                    'source': f"method_{method_id}",
                    'target': f"class_{class_id}",
                    'type': 'member'
                })
        
        # 调用链接
        for row in calls:
            caller_id = row[0]
            callee_id = row[2]
            callee_name = row[1]
            
            if callee_id is not None:
                links.append({
                    'source': f"method_{caller_id}",
                    'target': f"method_{callee_id}",
                    'type': 'call',
                    'callee_name': callee_name
                })

        return {
            'nodes': nodes,
            'links': links,
            'files': [{'id': r[0], 'path': r[1], 'lines': r[2]} for r in files],
            'classes': [{'id': r[0], 'name': r[1], 'sig': r[2], 'file': r[3],
                        'flags': r[4], 'start': r[5], 'end': r[6]} for r in classes],
            'methods': [{'id': r[0], 'name': r[1], 'sig': r[2], 'class': r[3],
                        'params': r[4], 'ret': r[5], 'flags': r[6],
                        'start': r[7], 'end': r[8]} for r in methods],
            'calls': [{'from': r[0], 'to_name': r[1], 'to': r[2]} for r in calls],
            'stats': self.get_project_stats(project_id)
        }

    def _row_to_dict(self, row: Optional[tuple], columns: List[str]) -> Dict:
        """Convert a row to a dictionary."""
        if not row:
            return {}
        return dict(zip(columns, row))
    
    def get_all_projects(self) -> List[Dict]:
        """Get list of all projects."""
        cursor = self.conn.execute("""
            SELECT id, name, path, analyzed_at FROM projects ORDER BY analyzed_at DESC
        """)
        return [
            {
                'id': row[0],
                'name': row[1],
                'path': row[2],
                'analyzed_at': row[3]
            }
            for row in cursor.fetchall()
        ]
    
    def delete_project(self, project_id: int):
        """Delete a project and all associated data."""
        self.conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        self.conn.commit()

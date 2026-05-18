"""Query API for the code knowledge graph."""

import json
from typing import Optional, Any
from database import Database


class QueryAPI:
    """API for querying the code knowledge graph."""
    
    def __init__(self, db: Database):
        self.db = db
    
    def query_class(self, name: str) -> Optional[dict]:
        """Query a class by name."""
        class_record = self.db.get_class_by_name(name)
        if not class_record:
            return None
        
        file_record = self.db.get_file_by_path(
            self._get_file_path_from_id(class_record.file_id)
        ) if class_record.file_id else None
        
        methods = self.db.get_methods_by_class(class_record.id)
        
        return {
            'id': class_record.id,
            'name': class_record.name,
            'file': file_record.path if file_record else None,
            'line': class_record.start_line,
            'flags': class_record.flags,
            'methods': [
                {
                    'id': m.id,
                    'name': m.name,
                    'params': m.params,
                    'return_type': m.return_type,
                    'line': m.start_line
                }
                for m in methods
            ]
        }
    
    def query_file(self, path: str) -> Optional[dict]:
        """Query all entities in a file."""
        file_record = self.db.get_file_by_path(path)
        if not file_record:
            return None
        
        classes = self.db.get_classes_by_file(file_record.id)
        
        result = {
            'id': file_record.id,
            'path': file_record.path,
            'modified': file_record.modified,
            'classes': []
        }
        
        for cls in classes:
            methods = self.db.get_methods_by_class(cls.id)
            result['classes'].append({
                'id': cls.id,
                'name': cls.name,
                'line': cls.start_line,
                'end_line': cls.end_line,
                'flags': cls.flags,
                'methods': [
                    {
                        'id': m.id,
                        'name': m.name,
                        'params': m.params,
                        'return_type': m.return_type,
                        'line': m.start_line
                    }
                    for m in methods
                ]
            })
        
        return result
    
    def query_callers(self, method_name: str) -> list[dict]:
        """Query all callers of a method."""
        return self.db.get_callers(method_name)
    
    def query_callees(self, method_name: str, class_name: Optional[str] = None) -> list[dict]:
        """Query all methods called by a method."""
        if class_name:
            class_record = self.db.get_class_by_name(class_name)
            if not class_record:
                return []
            
            methods = self.db.get_methods_by_class(class_record.id)
            method_record = next((m for m in methods if m.name == method_name), None)
            if not method_record:
                return []
            
            return self.db.get_callees(method_record.id)
        
        method_record = self.db.get_method_by_name(method_name)
        if not method_record:
            return []
        
        return self.db.get_callees(method_record.id)
    
    def query_components(self, class_name: str) -> dict:
        """Query component relationships for a class."""
        children, parents = self.db.get_components(class_name)
        return {
            'class': class_name,
            'children': children,
            'parents': parents
        }
    
    def search_classes(self, pattern: str) -> list[dict]:
        """Search for classes matching a pattern."""
        cursor = self.db.conn.execute("""
            SELECT c.id, c.name, f.path, c.start_line
            FROM classes c
            LEFT JOIN files f ON c.file_id = f.id
            WHERE c.name LIKE ?
            LIMIT 50
        """, (f'%{pattern}%',))
        
        return [
            {
                'id': row[0],
                'name': row[1],
                'file': row[2],
                'line': row[3]
            }
            for row in cursor.fetchall()
        ]
    
    def search_methods(self, pattern: str) -> list[dict]:
        """Search for methods matching a pattern."""
        cursor = self.db.conn.execute("""
            SELECT m.id, m.name, c.name, f.path, m.start_line
            FROM methods m
            LEFT JOIN classes c ON m.class_id = c.id
            LEFT JOIN files f ON c.file_id = f.id
            WHERE m.name LIKE ?
            LIMIT 50
        """, (f'%{pattern}%',))
        
        return [
            {
                'id': row[0],
                'name': row[1],
                'class': row[2],
                'file': row[3],
                'line': row[4]
            }
            for row in cursor.fetchall()
        ]
    
    def get_stats(self) -> dict:
        """Get database statistics."""
        return self.db.get_stats()
    
    def get_all_files(self) -> list[dict]:
        """Get all files in the knowledge graph."""
        cursor = self.db.conn.execute("""
            SELECT id, path, modified FROM files ORDER BY path
        """)
        
        return [
            {
                'id': row[0],
                'path': row[1],
                'modified': row[2]
            }
            for row in cursor.fetchall()
        ]
    
    def export_graph(self) -> dict:
        """Export the entire knowledge graph."""
        stats = self.get_stats()
        
        cursor = self.db.conn.execute("""
            SELECT c.id, c.name, c.flags, c.start_line, c.end_line, f.path
            FROM classes c
            LEFT JOIN files f ON c.file_id = f.id
        """)
        classes = [
            {
                'id': row[0],
                'name': row[1],
                'flags': row[2],
                'start_line': row[3],
                'end_line': row[4],
                'file': row[5]
            }
            for row in cursor.fetchall()
        ]
        
        cursor = self.db.conn.execute("""
            SELECT m.id, m.name, m.params, m.return_type, m.start_line, m.end_line,
                   c.name as class_name, f.path
            FROM methods m
            LEFT JOIN classes c ON m.class_id = c.id
            LEFT JOIN files f ON c.file_id = f.id
        """)
        methods = [
            {
                'id': row[0],
                'name': row[1],
                'params': row[2],
                'return_type': row[3],
                'start_line': row[4],
                'end_line': row[5],
                'class': row[6],
                'file': row[7]
            }
            for row in cursor.fetchall()
        ]
        
        cursor = self.db.conn.execute("""
            SELECT m.name, c.name, f.path
            FROM calls call
            JOIN methods m ON call.caller_id = m.id
            LEFT JOIN classes c ON m.class_id = c.id
            LEFT JOIN files f ON c.file_id = f.id
        """)
        calls = [
            {
                'caller': row[0],
                'class': row[1],
                'file': row[2]
            }
            for row in cursor.fetchall()
        ]
        
        return {
            'stats': stats,
            'classes': classes,
            'methods': methods,
            'calls': calls
        }
    
    def _get_file_path_from_id(self, file_id: int) -> str:
        """Get file path from ID."""
        cursor = self.db.conn.execute("SELECT path FROM files WHERE id = ?", (file_id,))
        row = cursor.fetchone()
        return row[0] if row else ""


def format_json(data: Any, pretty: bool = True) -> str:
    """Format data as JSON string."""
    if pretty:
        return json.dumps(data, indent=2, ensure_ascii=False)
    return json.dumps(data, ensure_ascii=False)

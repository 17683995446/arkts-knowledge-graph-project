"""Incremental update engine for dynamic knowledge graph updates."""

import time
import os
from pathlib import Path
from typing import Optional
from database import Database
from parser import ArkTSParser, ParsedClass, ParsedMethod
from watcher import FileWatcher, FileChange, ChangeType


class UpdateEngine:
    """Handles incremental updates to the knowledge graph."""
    
    def __init__(self, db: Database, parser: Optional[ArkTSParser] = None):
        self.db = db
        self.parser = parser or ArkTSParser()
        self._update_count = 0
        self._last_update_time = 0.0
    
    def update_file(self, change: FileChange) -> bool:
        """Update knowledge graph for a single file change."""
        start_time = time.time()
        
        try:
            self.db.begin_transaction()
            
            resolved_path = str(Path(change.path).resolve())
            
            file_record = self.db.get_file_by_path(resolved_path)
            
            if change.change_type == ChangeType.DELETED:
                if file_record:
                    self._delete_file_data(file_record.id)
                    print(f"✓ Deleted: {resolved_path}")
                self.db.commit()
                return True
            
            if not os.path.exists(change.path):
                if file_record:
                    self._delete_file_data(file_record.id)
                self.db.commit()
                return True
            
            current_hash = self.db.compute_file_hash(change.path)
            
            if file_record and file_record.hash == current_hash:
                self.db.rollback()
                return True
            
            if file_record:
                self._delete_file_data(file_record.id)
            
            self._insert_file_data(change.path, current_hash)
            
            self.db.commit()
            
            elapsed = time.time() - start_time
            self._update_count += 1
            self._last_update_time = elapsed
            
            change_type_str = {
                ChangeType.CREATED: "Created",
                ChangeType.MODIFIED: "Updated"
            }.get(change.change_type, "Updated")
            
            print(f"✓ {change_type_str}: {change.path} ({elapsed:.3f}s)")
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"✗ Error updating {change.path}: {e}")
            return False
    
    def _delete_file_data(self, file_id: int):
        """Delete all data associated with a file."""
        self.db.conn.execute("""
            DELETE FROM calls WHERE caller_id IN (
                SELECT m.id FROM methods m
                JOIN classes c ON m.class_id = c.id
                WHERE c.file_id = ?
            )
        """, (file_id,))
        
        self.db.conn.execute("""
            DELETE FROM calls WHERE callee_id IN (
                SELECT m.id FROM methods m
                JOIN classes c ON m.class_id = c.id
                WHERE c.file_id = ?
            )
        """, (file_id,))
        
        self.db.conn.execute("""
            DELETE FROM components WHERE parent_id IN (
                SELECT id FROM classes WHERE file_id = ?
            )
        """, (file_id,))
        
        self.db.conn.execute("""
            DELETE FROM components WHERE child_id IN (
                SELECT id FROM classes WHERE file_id = ?
            )
        """, (file_id,))
        
        self.db.conn.execute(
            "DELETE FROM methods WHERE class_id IN (SELECT id FROM classes WHERE file_id = ?)",
            (file_id,)
        )
        
        self.db.conn.execute("DELETE FROM classes WHERE file_id = ?", (file_id,))
        
        self.db.conn.execute("DELETE FROM files WHERE id = ?", (file_id,))
    
    def _insert_file_data(self, file_path: str, file_hash: bytes):
        """Insert parsed file data into the database."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except (UnicodeDecodeError, OSError):
            content = ""
        
        file_path = str(Path(file_path).resolve())
        
        modified = int(os.path.getmtime(file_path))
        file_id = self.db.insert_file(file_path, file_hash, modified)
        
        entities = self.parser.parse_file(content, file_path)
        
        standalone_funcs = self.parser.extract_standalone_functions(content)
        
        self._insert_entities(entities, file_id)
        
        for func in standalone_funcs:
            self._insert_standalone_function(func, file_id)
    
    def _insert_entities(self, entities: list[ParsedClass], file_id: int):
        """Insert parsed entities into the database."""
        class_id_map = {}
        
        for entity in entities:
            class_id = self.db.insert_class(
                name=entity.name,
                file_id=file_id,
                flags=entity.flags,
                start_line=entity.start_line,
                end_line=entity.end_line
            )
            class_id_map[entity.name] = class_id
            
            for method in entity.methods:
                method_id = self.db.insert_method(
                    name=method.name,
                    class_id=class_id,
                    params=method.params,
                    return_type=method.return_type,
                    start_line=method.start_line,
                    end_line=method.end_line
                )
                
                for callee_name in method.calls:
                    self.db.insert_call(method_id, callee_name, None, None)
        
        self._resolve_component_relationships(class_id_map, file_id)
    
    def _insert_standalone_function(self, func: ParsedMethod, file_id: int):
        """Insert a standalone function into the database."""
        method_id = self.db.insert_method(
            name=func.name,
            class_id=None,
            params=func.params,
            return_type=func.return_type,
            start_line=func.start_line,
            end_line=func.end_line
        )
        
        for callee_name in func.calls:
            self.db.insert_call(method_id, callee_name, None, None)
    
    def _resolve_component_relationships(self, class_id_map: dict[str, int], file_id: int):
        """Resolve and insert component relationships."""
        pass
    
    def full_sync(self, project_path: str) -> tuple[int, float]:
        """Perform a full synchronization of the project."""
        start_time = time.time()
        
        project = Path(project_path).resolve()
        files_to_process = []
        
        for ets_file in project.rglob("*.ets"):
            file_path = str(ets_file)
            current_hash = self.db.compute_file_hash(file_path)
            file_record = self.db.get_file_by_path(file_path)
            
            if not file_record or file_record.hash != current_hash:
                files_to_process.append(file_path)
        
        self.db.begin_transaction()
        
        updated_count = 0
        try:
            for file_path in files_to_process:
                file_record = self.db.get_file_by_path(file_path)
                if file_record:
                    self._delete_file_data(file_record.id)
                
                current_hash = self.db.compute_file_hash(file_path)
                self._insert_file_data(file_path, current_hash)
                updated_count += 1
                
                if updated_count % 100 == 0:
                    elapsed = time.time() - start_time
                    print(f"  Progress: {updated_count} files, {elapsed:.1f}s elapsed")
            
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        
        elapsed = time.time() - start_time
        return updated_count, elapsed
    
    def get_stats(self) -> dict:
        """Get update statistics."""
        return {
            'total_updates': self._update_count,
            'last_update_time': self._last_update_time
        }

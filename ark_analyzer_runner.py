"""ArkAnalyzer integration - runs analysis and stores results in SQLite."""
import os
import time
import hashlib
from typing import List, Dict, Optional
from pathlib import Path

from ark_analyzer_db import ArkAnalyzerDB
from parser import ArkTSParser, ParsedClass, ParsedMethod


class ArkAnalyzerRunner:
    """Runs ArkAnalyzer and processes results."""
    
    def __init__(self, ark_analyzer_path: str, db: ArkAnalyzerDB):
        self.ark_analyzer_path = ark_analyzer_path
        self.db = db
        self.parser = ArkTSParser()
        self.project_id: Optional[int] = None

    def analyze_project(self, project_path: str, project_name: Optional[str] = None) -> bool:
        """Analyze an ArkTS project and store results in SQLite."""
        if not project_name:
            project_name = Path(project_path).name
            
        print(f"Analyzing project: {project_name}")
        print(f"Path: {project_path}")
        
        try:
            self.db.begin_transaction()
            
            # Create project entry
            self.project_id = self.db.insert_project(
                name=project_name,
                path=project_path,
                analyzed_at=int(time.time())
            )
            
            # Collect files
            files_to_process = self._collect_files(project_path)
            print(f"Found {len(files_to_process)} files to analyze")
            
            # Process each file
            for i, file_path in enumerate(files_to_process):
                self._process_file(file_path)
                if (i + 1) % 10 == 0:
                    print(f"  Processed {i + 1}/{len(files_to_process)} files")
            
            self.db.commit()
            
            # Show final stats
            stats = self.db.get_project_stats(self.project_id)
            print(f"\nAnalysis complete!")
            print(f"  Files: {stats['files']}")
            print(f"  Classes: {stats['classes']}")
            print(f"  Methods: {stats['methods']}")
            print(f"  Calls: {stats['calls']}")
            
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"\nError during analysis: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _collect_files(self, project_path: str) -> List[str]:
        """Collect all ArkTS/TypeScript files from the project."""
        files = []
        project = Path(project_path)
        
        for root, dirs, filenames in os.walk(project):
            # Skip node_modules and build directories
            dirs[:] = [d for d in dirs if d not in (
                'node_modules', 'build', '.build', '.cxx', 'dist', 'target', '.git'
            )]
            
            for filename in filenames:
                if filename.endswith(('.ets', '.ts')) and not filename.endswith('.d.ts'):
                    files.append(os.path.join(root, filename))
        
        return files

    def _process_file(self, file_path: str):
        """Process a single file and store its entities in the database."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
            return
        
        # Calculate file hash
        file_hash = hashlib.md5(content.encode()).hexdigest()
        line_count = content.count('\n') + 1
        
        # Insert file record
        file_id = self.db.insert_file(
            project_id=self.project_id,
            path=file_path,
            hash_val=file_hash,
            line_count=line_count,
            analyzed_at=int(time.time())
        )
        
        # Parse the file content
        entities = self.parser.parse_file(content, file_path)
        standalone_funcs = self.parser.extract_standalone_functions(content)
        
        # Process classes/structs
        for entity in entities:
            self._store_class(entity, file_id, file_path)
            
        # Process standalone functions
        for func in standalone_funcs:
            self._store_standalone_function(func, file_id, file_path)

    def _store_class(self, entity: ParsedClass, file_id: int, file_path: str):
        """Store a parsed class/struct in the database."""
        # Insert class
        class_id = self.db.insert_class(
            project_id=self.project_id,
            name=entity.name,
            signature=f"struct {entity.name}" if entity.flags else f"class {entity.name}",
            file_id=file_id,
            namespace_id=None,
            flags=entity.flags,
            start_line=entity.start_line,
            end_line=entity.end_line,
            source_code=None
        )
        
        # Insert decorators
        for decorator in entity.decorators:
            self.db.insert_decorator(
                project_id=self.project_id,
                class_id=class_id,
                method_id=None,
                name=decorator,
                args=None
            )
        
        # Insert methods and create relationships
        for method in entity.methods:
            method_id = self._store_method(method, class_id, None, file_id, file_path)
            self._store_method_calls(method, method_id)

    def _store_method(self, method: ParsedMethod, class_id: Optional[int], 
                     namespace_id: Optional[int], file_id: int, file_path: str) -> int:
        """Store a parsed method in the database."""
        return self.db.insert_method(
            project_id=self.project_id,
            name=method.name,
            signature=f"{method.name}({method.params})",
            class_id=class_id,
            namespace_id=namespace_id,
            file_id=file_id,
            params=method.params,
            return_type=method.return_type,
            flags=0,
            start_line=method.start_line,
            end_line=method.end_line,
            source_code=None,
            is_constructor=1 if method.name == 'constructor' else 0,
            is_static=1 if method.is_static else 0
        )

    def _store_method_calls(self, method: ParsedMethod, method_id: int):
        """Store all calls from a method."""
        # Skip known library functions that shouldn't be tracked
        SKIP_FUNCTIONS = {
            'console', 'log', 'error', 'warn', 'info', 'debug',
            'Text', 'Button', 'Column', 'Row', 'List', 
            'ListItem', 'ForEach', 'if', 'else', 'switch', 'case',
            'return', 'break', 'continue', 'push', 'pop', 'shift',
            'unshift', 'slice', 'splice', 'find', 'findIndex',
            'map', 'filter', 'reduce', 'forEach', 'some', 'every',
            'includes', 'indexOf', 'join', 'split', 'toString',
            'toUpperCase', 'toLowerCase', 'trim', 'substring',
            'substr', 'replace', 'match', 'test', 'exec',
            'setTimeout', 'setInterval', 'Promise', 'then', 'catch',
            'finally', 'resolve', 'reject', 'all', 'race', 'any',
            'get', 'set', 'has', 'delete', 'clear', 'keys',
            'values', 'entries', 'for...of', 'for...in', 'while',
            'do...while', 'try', 'catch', 'finally', 'throw',
            'new', 'typeof', 'instanceof', 'in', 'of', 'delete',
            'void', 'undefined', 'null', 'NaN', 'Infinity',
            'super', 'this', 'self', 'fn', 'callback'
        }
        
        for callee_name in method.calls:
            # Skip known library functions
            if callee_name in SKIP_FUNCTIONS:
                continue
            
            # Try to resolve the callee method ID
            callee_method_id = self._resolve_callee_method_id(callee_name)
            
            self.db.insert_call(
                project_id=self.project_id,
                caller_method_id=method_id,
                callee_method_name=callee_name,
                callee_signature=None,
                callee_method_id=callee_method_id,
                call_type='call'
            )

    def _resolve_callee_method_id(self, method_name: str) -> Optional[int]:
        """Try to resolve a method name to its database ID."""
        try:
            cursor = self.db.conn.execute(
                "SELECT id FROM methods WHERE name = ? AND project_id = ? LIMIT 1",
                (method_name, self.project_id)
            )
            result = cursor.fetchone()
            return result[0] if result else None
        except:
            return None

    def _store_standalone_function(self, func: ParsedMethod, file_id: int, file_path: str):
        """Store a standalone function in the database."""
        method_id = self.db.insert_method(
            project_id=self.project_id,
            name=func.name,
            signature=f"function {func.name}({func.params})",
            class_id=None,
            namespace_id=None,
            file_id=file_id,
            params=func.params,
            return_type=func.return_type,
            flags=0,
            start_line=func.start_line,
            end_line=func.end_line,
            source_code=None,
            is_constructor=0,
            is_static=0
        )
        
        self._store_method_calls(func, method_id)


def run_ark_analyzer(ark_analyzer_path: str, project_path: str, db_path: str = "ark_graph.db") -> bool:
    """Main function to run analysis and populate database."""
    # Clean up existing database
    if os.path.exists(db_path):
        os.remove(db_path)
    
    db = ArkAnalyzerDB(db_path)
    db.initialize()
    
    runner = ArkAnalyzerRunner(ark_analyzer_path, db)
    return runner.analyze_project(project_path)

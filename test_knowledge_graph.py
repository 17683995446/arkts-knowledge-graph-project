"""Unit tests for the knowledge graph components."""

import unittest
import tempfile
import os
from pathlib import Path

from database import Database
from parser import ArkTSParser, ParsedClass, ParsedMethod
from watcher import FileWatcher, FileChange, ChangeType
from updater import UpdateEngine
from query import QueryAPI


class TestDatabase(unittest.TestCase):
    """Test database operations."""
    
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = Database(self.temp_db.name)
        self.db.initialize()
    
    def tearDown(self):
        self.db.close()
        os.unlink(self.temp_db.name)
    
    def test_insert_file(self):
        """Test file insertion."""
        file_hash = b'\x00' * 16
        file_id = self.db.insert_file("/test/file.ets", file_hash, 123456)
        self.assertIsNotNone(file_id)
        self.assertGreater(file_id, 0)
    
    def test_get_file_by_path(self):
        """Test file retrieval by path."""
        file_hash = b'\x00' * 16
        self.db.insert_file("/test/file.ets", file_hash, 123456)
        
        record = self.db.get_file_by_path("/test/file.ets")
        self.assertIsNotNone(record)
        self.assertEqual(record.path, "/test/file.ets")
    
    def test_insert_class(self):
        """Test class insertion."""
        file_hash = b'\x00' * 16
        file_id = self.db.insert_file("/test/file.ets", file_hash, 123456)
        
        class_id = self.db.insert_class("TestClass", file_id, 0, 1, 10)
        self.assertIsNotNone(class_id)
        self.assertGreater(class_id, 0)
    
    def test_insert_method(self):
        """Test method insertion."""
        file_hash = b'\x00' * 16
        file_id = self.db.insert_file("/test/file.ets", file_hash, 123456)
        class_id = self.db.insert_class("TestClass", file_id, 0, 1, 10)
        
        method_id = self.db.insert_method("testMethod", class_id, "param1: string", "void", 5, 8)
        self.assertIsNotNone(method_id)
        self.assertGreater(method_id, 0)
    
    def test_insert_call(self):
        """Test call relationship insertion."""
        file_hash = b'\x00' * 16
        file_id = self.db.insert_file("/test/file.ets", file_hash, 123456)
        class_id = self.db.insert_class("TestClass", file_id, 0, 1, 10)
        method_id = self.db.insert_method("caller", class_id, "", "", 5, 8)
        
        self.db.insert_call(method_id, "callee", None, None)
        
        callers = self.db.get_callers("callee")
        self.assertEqual(len(callers), 1)
        self.assertEqual(callers[0]['method_name'], "caller")


class TestArkTSParser(unittest.TestCase):
    """Test ArkTS parser."""
    
    def setUp(self):
        self.parser = ArkTSParser()
    
    def test_parse_simple_class(self):
        """Test parsing a simple class."""
        code = """
@Component
export class MyComponent {
    message: string = "Hello";
    
    aboutToAppear(): void {
        console.log("Appearing");
    }
    
    build(): void {
        this.renderSomeContent();
    }
    
    private renderSomeContent(): void {
        Text(this.message)
    }
}
"""
        entities = self.parser.parse_file(code, "/test/MyComponent.ets")
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0].name, "MyComponent")
        self.assertGreater(len(entities[0].methods), 0)
    
    def test_parse_class_with_methods(self):
        """Test that methods are correctly parsed."""
        code = """
class SimpleClass {
    method1(): number {
        return this.method2();
    }
    
    method2(): string {
        return "test";
    }
}
"""
        entities = self.parser.parse_file(code, "/test/SimpleClass.ets")
        self.assertEqual(len(entities), 1)
        
        method_names = [m.name for m in entities[0].methods]
        self.assertIn("method1", method_names)
        self.assertIn("method2", method_names)
    
    def test_extract_standalone_functions(self):
        """Test parsing standalone functions."""
        code = """
function helper(): void {
    console.log("helper");
}

function main(): void {
    helper();
}
"""
        functions = self.parser.extract_standalone_functions(code)
        self.assertEqual(len(functions), 2)
        
        func_names = [f.name for f in functions]
        self.assertIn("helper", func_names)
        self.assertIn("main", func_names)


class TestUpdateEngine(unittest.TestCase):
    """Test update engine."""
    
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.temp_dir = tempfile.mkdtemp()
        self.db = Database(self.temp_db.name)
        self.db.initialize()
        self.parser = ArkTSParser()
        self.updater = UpdateEngine(self.db, self.parser)
    
    def tearDown(self):
        self.db.close()
        os.unlink(self.temp_db.name)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_update_new_file(self):
        """Test updating a new file."""
        test_file = os.path.join(self.temp_dir, "Test.ets")
        code = """
@Component
export class TestComponent {
    build(): void {
        Text("Hello")
    }
}
"""
        with open(test_file, 'w') as f:
            f.write(code)
        
        change = FileChange(path=test_file, change_type=ChangeType.CREATED)
        result = self.updater.update_file(change)
        
        self.assertTrue(result)
        
        file_record = self.db.get_file_by_path(test_file)
        self.assertIsNotNone(file_record)
    
    def test_update_modified_file(self):
        """Test updating a modified file."""
        test_file = os.path.join(self.temp_dir, "Test.ets")
        code1 = """
class TestClass {
    method1(): void {}
}
"""
        code2 = """
class TestClass {
    method1(): void {}
    method2(): void {}
}
"""
        with open(test_file, 'w') as f:
            f.write(code1)
        
        change = FileChange(path=test_file, change_type=ChangeType.CREATED)
        self.updater.update_file(change)
        
        classes = self.db.get_classes_by_file(self.db.get_file_by_path(test_file).id)
        self.assertEqual(len(classes), 1)
        
        with open(test_file, 'w') as f:
            f.write(code2)
        
        change = FileChange(path=test_file, change_type=ChangeType.MODIFIED)
        self.updater.update_file(change)
        
        file_record = self.db.get_file_by_path(test_file)
        self.assertIsNotNone(file_record)
    
    def test_delete_file(self):
        """Test deleting a file from the graph."""
        test_file = os.path.join(self.temp_dir, "Test.ets")
        code = """
class TestClass {
    method1(): void {}
}
"""
        with open(test_file, 'w') as f:
            f.write(code)
        
        change = FileChange(path=test_file, change_type=ChangeType.CREATED)
        self.updater.update_file(change)
        
        file_record = self.db.get_file_by_path(test_file)
        self.assertIsNotNone(file_record)
        
        os.unlink(test_file)
        
        change = FileChange(path=test_file, change_type=ChangeType.DELETED)
        self.updater.update_file(change)
        
        file_record = self.db.get_file_by_path(test_file)
        self.assertIsNone(file_record)


class TestQueryAPI(unittest.TestCase):
    """Test query API."""
    
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = Database(self.temp_db.name)
        self.db.initialize()
        self.query_api = QueryAPI(self.db)
        
        file_hash = b'\x00' * 16
        file_id = self.db.insert_file("/test/TestClass.ets", file_hash, 123456)
        class_id = self.db.insert_class("TestClass", file_id, 0, 1, 20)
        self.db.insert_method("method1", class_id, "", "number", 5, 10)
        self.db.insert_method("method2", class_id, "param: string", "void", 12, 18)
    
    def tearDown(self):
        self.db.close()
        os.unlink(self.temp_db.name)
    
    def test_query_class(self):
        """Test querying a class."""
        result = self.query_api.query_class("TestClass")
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], "TestClass")
        self.assertEqual(len(result['methods']), 2)
    
    def test_query_file(self):
        """Test querying a file."""
        result = self.query_api.query_file("/test/TestClass.ets")
        self.assertIsNotNone(result)
        self.assertEqual(result['path'], "/test/TestClass.ets")
        self.assertEqual(len(result['classes']), 1)
    
    def test_get_stats(self):
        """Test getting statistics."""
        stats = self.query_api.get_stats()
        self.assertEqual(stats['files'], 1)
        self.assertEqual(stats['classes'], 1)
        self.assertEqual(stats['methods'], 2)
    
    def test_search_classes(self):
        """Test searching for classes."""
        results = self.query_api.search_classes("Test")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], "TestClass")


if __name__ == '__main__':
    unittest.main()

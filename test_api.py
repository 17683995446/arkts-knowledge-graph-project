#!/usr/bin/env python3
"""Comprehensive API testing for ArkTS knowledge graph server."""
import os
import sys
import tempfile
import time
import threading
import json

sys.path.insert(0, '/workspace')

from ark_analyzer_db import ArkAnalyzerDB
from ark_analyzer_runner import ArkAnalyzerRunner


def log(msg):
    print(f"[API TEST] {msg}")


def test_api_logic():
    """Test API logic without starting the server."""
    print("="*80)
    print("  ARKTS KNOWLEDGE GRAPH - API LOGIC TESTS")
    print("="*80)
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        db_path = tmp_db.name
    
    try:
        # Step 1: Setup test data
        log("Initializing database and running analysis")
        db = ArkAnalyzerDB(db_path)
        db.initialize()
        runner = ArkAnalyzerRunner('/workspace', db)
        success = runner.analyze_project('/workspace/ultimate_chaos_project', 'ApiTestProject')
        assert success
        
        log("Testing get_all_projects")
        projects = db.get_all_projects()
        assert len(projects) == 1
        assert projects[0]['name'] == 'ApiTestProject'
        
        log("Testing get_project_stats")
        stats = db.get_project_stats(projects[0]['id'])
        log(f"Project stats: {stats}")
        
        log("Testing export_graph")
        graph = db.export_graph(projects[0]['id'])
        assert graph is not None
        assert len(graph['nodes']) if 'nodes' in graph else len(graph['files']) > 0
        
        log("Testing query_class")
        # Check some classes exist in the graph
        test_classes = graph.get('classes', [])
        if test_classes:
            test_class_name = test_classes[0]['name']
            class_data = db.query_class(projects[0]['id'], test_class_name)
            assert class_data is not None
            assert 'name' in class_data
            assert class_data['name'] == test_class_name
        
        log("✅ All API logic tests passed!")
        
        db.close()
        
        print("\n" + "="*80)
        print("  API LOGIC TEST COMPLETE - ALL TESTS PASSED")
        print("="*80)
        
    finally:
        try:
            os.unlink(db_path)
        except Exception:
            pass


def test_error_handling():
    """Test error handling for API endpoints."""
    print("\n" + "="*80)
    print("  ERROR HANDLING TESTS")
    print("="*80)
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        db_path = tmp_db.name
    
    try:
        log("Testing database initialization with empty database")
        db = ArkAnalyzerDB(db_path)
        db.initialize()
        
        # Test querying non-existent project
        log("Testing get_project_stats for invalid project ID")
        stats = db.get_project_stats(9999)
        log(f"Stats for invalid project: {stats}")
        assert stats is not None
        
        log("Testing query_class for non-existent class")
        result = db.query_class(1, 'NonExistentClassXYZ123')
        assert result is None
        
        log("Testing get_all_projects with empty DB")
        projects = db.get_all_projects()
        assert len(projects) == 0
        
        db.close()
        
        log("✅ All error handling tests passed!")
        
        print("\n" + "="*80)
        print("  ERROR HANDLING TEST COMPLETE")
        print("="*80)
        
    finally:
        try:
            os.unlink(db_path)
        except Exception:
            pass


def main():
    test_api_logic()
    test_error_handling()
    print("\n" + "="*80)
    print("  ALL API TESTS PASSED")
    print("="*80)


if __name__ == "__main__":
    main()

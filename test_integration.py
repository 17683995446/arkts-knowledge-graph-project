#!/usr/bin/env python3
"""Integration and module testing for the complete ArkTS knowledge graph system."""
import os
import sys
import tempfile
import time
import sqlite3
from pathlib import Path

sys.path.insert(0, '/workspace')

from ark_analyzer_db import ArkAnalyzerDB
from ark_analyzer_runner import ArkAnalyzerRunner


def log(msg):
    print(f"[INTEGRATION] {msg}")


def main():
    print("="*80)
    print("  ARKTS KNOWLEDGE GRAPH - MODULE INTEGRATION TEST")
    print("="*80)
    
    # Step 1: Test with the ultimate chaos project
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        db_path = tmp_db.name
    
    try:
        log("Initializing database")
        db = ArkAnalyzerDB(db_path)
        db.initialize()
        
        log("Running analysis on ultimate chaos project")
        runner = ArkAnalyzerRunner('/workspace', db)
        success = runner.analyze_project('/workspace/ultimate_chaos_project', 'ChaosIntegrationTest')
        
        assert success, "Analysis failed"
        
        log("Querying project statistics")
        stats = db.get_project_stats(runner.project_id)
        log(f"Project statistics: {stats}")
        
        # Verify basic data integrity
        assert stats['files'] >= 500, f"Expected at least 500 files, got {stats['files']}"
        assert stats['classes'] >= 100, f"Expected at least 100 classes, got {stats['classes']}"
        
        log("Exporting graph")
        graph = db.export_graph(runner.project_id)
        assert graph is not None
        assert len(graph['files']) > 0
        assert len(graph['classes']) > 0
        assert len(graph['methods']) > 0
        
        log("Testing project list retrieval")
        projects = db.get_all_projects()
        assert len(projects) >= 1
        
        log("Testing project deletion")
        db.delete_project(runner.project_id)
        assert len(db.get_all_projects()) == 0
        
        db.close()
        log("✅ All integration tests passed!")
        
    finally:
        try:
            os.unlink(db_path)
        except Exception:
            pass
    
    print("\n" + "="*80)
    print("  INTEGRATION TEST COMPLETE - ALL TESTS PASSED")
    print("="*80)


if __name__ == "__main__":
    main()

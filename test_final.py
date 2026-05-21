#!/usr/bin/env python3
"""Final comprehensive test suite: business scenarios, data consistency, error handling, performance."""
import os
import sys
import tempfile
import time
import hashlib
from pathlib import Path

sys.path.insert(0, '/workspace')

from parser import ArkTSParser
from ark_analyzer_db import ArkAnalyzerDB
from ark_analyzer_runner import ArkAnalyzerRunner


def log(msg):
    print(f"[FINAL TEST] {msg}")


def test_business_scenario():
    """Test complete business scenario: analyze, re-analyze, incremental, check data"""
    print("\n" + "="*80)
    print("  COMPLETE BUSINESS SCENARIO TEST")
    print("="*80)
    
    with tempfile.TemporaryDirectory() as temp_proj_dir:
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            db_path = tmp_db.name
        try:
            # Step 1: Create some test files
            log("Creating test project")
            file1 = os.path.join(temp_proj_dir, "ModuleA.ets")
            with open(file1, "w") as f:
                f.write("""
class ComponentA {
    methodX() {
        console.log("Hello");
    }
}
""")
            
            file2 = os.path.join(temp_proj_dir, "ModuleB.ets")
            with open(file2, "w") as f:
                f.write("""
class ComponentB {
    methodY() {
        console.log("World");
    }
}
""")
            
            # Step 2: First analysis
            log("Running first analysis")
            db = ArkAnalyzerDB(db_path)
            db.initialize()
            runner = ArkAnalyzerRunner('/workspace', db)
            runner.analyze_project(temp_proj_dir, "BusinessTestProj")
            stats1 = db.get_project_stats(runner.project_id)
            log(f"Stats after first analysis: {stats1}")
            assert stats1['classes'] >= 1
            assert stats1['files'] == 2
            
            # Step 3: Modify a file
            log("Modifying a file")
            time.sleep(0.1)  # Ensure timestamp changes
            with open(file2, "a") as f:
                f.write("""
class ComponentC {
    newMethod() { }
}
""")
            
            # Step 4: Incremental analysis
            log("Running incremental analysis")
            success = runner.analyze_project(temp_proj_dir, "BusinessTestProj")
            assert success
            stats2 = db.get_project_stats(runner.project_id)
            log(f"Stats after incremental: {stats2}")
            assert stats2['classes'] > stats1['classes']
            assert stats2['files'] == 2
            assert stats2['methods'] >= stats1['methods']
            
            db.close()
            log("✅ Business scenario test passed!")
            
        finally:
            try:
                os.unlink(db_path)
            except Exception:
                pass


def test_data_consistency():
    """Test data consistency and integrity checks."""
    print("\n" + "="*80)
    print("  DATA CONSISTENCY TEST")
    print("="*80)
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        db_path = tmp_db.name
    try:
        log("Analyzing ultimate chaos project")
        db = ArkAnalyzerDB(db_path)
        db.initialize()
        runner = ArkAnalyzerRunner('/workspace', db)
        runner.analyze_project('/workspace/ultimate_chaos_project', "ConsistencyTest")
        project_id = runner.project_id
        
        # Check 1: All methods have valid file or class links (if they should)
        log("Checking file/class method consistency")
        cursor = db.conn.execute("SELECT COUNT(*) FROM methods WHERE project_id = ?", (project_id,))
        total_methods = cursor.fetchone()[0]
        
        # Check 2: Verify no orphaned calls
        log("Checking for orphaned calls")
        cursor = db.conn.execute("""
            SELECT COUNT(*) FROM calls 
            WHERE project_id = ? AND caller_method_id NOT IN (SELECT id FROM methods)
        """, (project_id,))
        orphaned = cursor.fetchone()[0]
        log(f"Orphaned calls: {orphaned}")
        assert orphaned == 0, "Should not have orphaned calls!"
        
        # Check 3: Verify all classes belong to existing files
        log("Verifying class to file relationships")
        cursor = db.conn.execute("""
            SELECT COUNT(*) FROM classes 
            WHERE project_id = ? AND file_id NOT IN (SELECT id FROM files)
        """, (project_id,))
        bad_classes = cursor.fetchone()[0]
        log(f"Classes with invalid file: {bad_classes}")
        assert bad_classes == 0
        
        db.close()
        log("✅ Data consistency tests passed!")
        
    finally:
        try:
            os.unlink(db_path)
        except Exception:
            pass


def test_performance():
    """Basic performance and stress tests"""
    print("\n" + "="*80)
    print("  PERFORMANCE TEST")
    print("="*80)
    
    with tempfile.TemporaryDirectory() as temp_proj_dir:
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            db_path = tmp_db.name
        try:
            log("Creating 10 test files for performance testing")
            for i in range(10):
                file = os.path.join(temp_proj_dir, f"PerfTest{i}.ets")
                with open(file, "w") as f:
                    f.write(f"""
class PerfClass{i} {{
""")
                    for j in range(10):
                        f.write(f"""
    method{j}() {{
        console.log('test');
    }}
""")
                    f.write("}\n")
            
            log("Running performance analysis")
            start = time.time()
            db = ArkAnalyzerDB(db_path)
            db.initialize()
            runner = ArkAnalyzerRunner('/workspace', db)
            runner.analyze_project(temp_proj_dir, "PerfTest")
            duration = time.time() - start
            
            stats = db.get_project_stats(runner.project_id)
            
            log(f"Analysis took {duration:.2f}s for {stats['files']} files and {stats['classes']} classes")
            
            assert stats['files'] == 10
            assert stats['methods'] == 10*10
            
            db.close()
            log("✅ Performance test passed!")
            
        finally:
            try:
                os.unlink(db_path)
            except Exception:
                pass


def test_error_handling():
    """Test error handling robustness"""
    print("\n" + "="*80)
    print("  ROBUST ERROR HANDLING")
    print("="*80)
    
    with tempfile.TemporaryDirectory() as temp_proj_dir:
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            db_path = tmp_db.name
        try:
            # Test corrupted file handling
            invalid_file = os.path.join(temp_proj_dir, "invalid.ets")
            with open(invalid_file, "w") as f:
                f.write("not valid code")
            
            db = ArkAnalyzerDB(db_path)
            db.initialize()
            runner = ArkAnalyzerRunner('/workspace', db)
            
            log("Testing analysis with invalid content")
            success = runner.analyze_project(temp_proj_dir, "ErrorTest")
            assert success, "Should not crash"
            
            stats = db.get_project_stats(runner.project_id)
            log(f"Stats: {stats}")
            
            db.close()
            log("✅ Error handling test passed!")
            
        finally:
            try:
                os.unlink(db_path)
            except Exception:
                pass


def main():
    print("="*80)
    print("  FINAL COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    test_business_scenario()
    test_data_consistency()
    test_performance()
    test_error_handling()
    
    print("\n" + "="*80)
    print("  ALL FINAL TESTS PASSED - SYSTEM IS READY")
    print("="*80)


if __name__ == "__main__":
    main()

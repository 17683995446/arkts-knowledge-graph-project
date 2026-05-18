
#!/usr/bin/env python3
"""
Comprehensive stress and bug discovery test for the ArkTS knowledge graph system.
"""
import os
import sys
import time
import traceback
from pathlib import Path

# Add the project root to path
sys.path.insert(0, '/workspace')

# Clean up any existing database
DB_PATH = '/workspace/test_ark_graph.db'
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

print("=" * 80)
print("ARKTS KNOWLEDGE GRAPH SYSTEM - COMPREHENSIVE STRESS TEST")
print("=" * 80)

# Import our modules
from ark_analyzer_db import ArkAnalyzerDB
from ark_analyzer_runner import ArkAnalyzerRunner

print("\n[1] TESTING BASIC SYSTEM INITIALIZATION")
print("-" * 80)
try:
    db = ArkAnalyzerDB(DB_PATH)
    db.initialize()
    print("✓ Database initialized successfully")
except Exception as e:
    print(f"✗ ERROR: {e}")
    print(f"{traceback.format_exc()}")
    sys.exit(1)

print("\n[2] TESTING COMPLEX PROJECT ANALYSIS")
print("-" * 80)
complex_project_path = '/workspace/complex_project'
runner = None
success = False
try:
    runner = ArkAnalyzerRunner('/workspace', db)
    print(f"✓ Analyzing project at: {complex_project_path}")
    success = runner.analyze_project(complex_project_path)
    print(f"✓ Analysis completed: success={success}")
except Exception as e:
    print(f"✗ ERROR during analysis: {e}")
    print(f"{traceback.format_exc()}")
    db.close()
    sys.exit(1)

print("\n[3] CHECKING PROJECT STATISTICS")
print("-" * 80)
try:
    stats = db.get_project_stats(runner.project_id)
    print(f"✓ Project Statistics:")
    for key, value in stats.items():
        print(f"  - {key}: {value}")
    
    if stats.get('files', 0) == 0:
        print("✗ ERROR: No files found!")
except Exception as e:
    print(f"✗ ERROR getting stats: {e}")
    print(f"{traceback.format_exc()}")

print("\n[4] VERIFYING DATABASE CONTENTS")
print("-" * 80)
try:
    # Check files table
    cursor = db.conn.execute("SELECT COUNT(*) FROM files")
    file_count = cursor.fetchone()[0]
    print(f"✓ Number of files in DB: {file_count}")
    
    # Check classes
    cursor = db.conn.execute("SELECT id, name, file_id FROM classes")
    classes = cursor.fetchall()
    print(f"✓ Found {len(classes)} classes:")
    for cls in classes:
        print(f"  - {cls[1]} (file_id: {cls[2]})")
    
    # Check methods
    cursor = db.conn.execute("SELECT id, name, class_id FROM methods")
    methods = cursor.fetchall()
    print(f"✓ Found {len(methods)} methods:")
    for i, method in enumerate(methods[:15]):
        class_info = f" (class: {method[2]})" if method[2] else ""
        print(f"  - {method[1]}{class_info}")
    if len(methods) &gt; 15:
        print(f"  - ... and {len(methods) - 15} more methods")
        
    # Check calls
    cursor = db.conn.execute("SELECT COUNT(*) FROM calls")
    call_count = cursor.fetchone()[0]
    print(f"✓ Found {call_count} call relationships")
    
except Exception as e:
    print(f"✗ ERROR checking DB: {e}")
    print(f"{traceback.format_exc()}")

print("\n[5] TESTING WITH ORIGINAL EXAMPLE (EDGE CASES)")
print("-" * 80)
try:
    # Clean up and test original example
    db.close()
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    db = ArkAnalyzerDB(DB_PATH)
    db.initialize()
    runner2 = ArkAnalyzerRunner('/workspace', db)
    print("✓ Testing original example project...")
    success2 = runner2.analyze_project('/workspace/example')
    stats2 = db.get_project_stats(runner2.project_id)
    print(f"✓ Original example stats: {stats2}")
except Exception as e:
    print(f"✗ ERROR with original example: {e}")
    print(f"{traceback.format_exc()}")

print("\n[6] STRESS TEST - MULTIPLE RAPID ANALYSIS")
print("-" * 80)
try:
    db.close()
    start_time = time.time()
    for i in range(5):
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        db_i = ArkAnalyzerDB(DB_PATH)
        db_i.initialize()
        runner_i = ArkAnalyzerRunner('/workspace', db_i)
        s = runner_i.analyze_project('/workspace/complex_project')
        db_i.close()
        print(f"✓ Analysis run {i+1}/5: {'OK' if s else 'FAIL'}")
    elapsed = time.time() - start_time
    print(f"✓ 5 analysis runs completed in {elapsed:.2f}s")
except Exception as e:
    print(f"✗ ERROR during stress test: {e}")
    print(f"{traceback.format_exc()}")

print("\n[7] FINAL CLEANUP AND SUMMARY")
print("-" * 80)
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
print("✓ All tests complete")
print("\n" + "=" * 80)
print("STRESS TEST DONE - BUGS DISCOVERED SO FAR:")
print("=" * 80)
print("1. Check for parser edge cases")
print("2. Check for database constraints")
print("3. Check for large file handling")
print("\nNow let's check if the server can visualize!")

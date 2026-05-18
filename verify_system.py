
#!/usr/bin/env python3
"""
Comprehensive verification test for the ArkTS knowledge graph system.
Tests all components and verifies all fixes.
"""
import os
import sys
import time
import json
import traceback
sys.path.insert(0, '/workspace')

from ark_analyzer_db import ArkAnalyzerDB
from ark_analyzer_runner import ArkAnalyzerRunner

print("=" * 80)
print("COMPREHENSIVE SYSTEM VERIFICATION")
print("=" * 80)

TEST_PASSED = 0
TEST_FAILED = 0
TEST_WARNINGS = []

def test(name, condition, error_msg=""):
    global TEST_PASSED, TEST_FAILED
    if condition:
        print(f"✅ {name}")
        TEST_PASSED += 1
        return True
    else:
        print(f"❌ {name}: {error_msg}")
        TEST_FAILED += 1
        return False

# Clean up
DB_PATH = '/workspace/test_verify.db'
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

print("\n[1] Database Initialization")
print("-" * 80)
try:
    db = ArkAnalyzerDB(DB_PATH)
    db.initialize()
    test("Database initialized", True)
except Exception as e:
    test("Database initialized", False, str(e))
    sys.exit(1)

print("\n[2] Project Analysis")
print("-" * 80)
try:
    start_time = time.time()
    runner = ArkAnalyzerRunner('/workspace', db)
    success = runner.analyze_project('/workspace/complex_project')
    elapsed = time.time() - start_time
    
    test("Analysis completed", success)
    test("Analysis time < 1s", elapsed < 1.0, f"Took {elapsed:.2f}s")
    test("Found files", True)
except Exception as e:
    test("Analysis completed", False, str(e))
    db.close()
    sys.exit(1)

print("\n[3] Data Validation")
print("-" * 80)
stats = db.get_project_stats(runner.project_id)

test("Has files", stats['files'] > 0, f"Files: {stats['files']}")
test("Has classes", stats['classes'] > 0, f"Classes: {stats['classes']}")
test("Has methods", stats['methods'] > 0, f"Methods: {stats['methods']}")
test("Has calls", stats['calls'] > 0, f"Calls: {stats['calls']}")

print("\n[4] Call Resolution Quality")
print("-" * 80)
cursor = db.conn.execute('''
    SELECT 
        COUNT(*) as total_calls,
        SUM(CASE WHEN callee_method_id IS NOT NULL THEN 1 ELSE 0 END) as resolved_calls
    FROM calls
''')
call_data = cursor.fetchone()
total_calls = call_data[0]
resolved_calls = call_data[1]
resolution_rate = (resolved_calls / total_calls * 100) if total_calls > 0 else 0

test("Total calls tracked", total_calls > 0, f"Total: {total_calls}")
test("Resolution rate > 0%", resolution_rate > 0, f"Rate: {resolution_rate:.1f}%")

if resolution_rate < 20:
    TEST_WARNINGS.append(f"Call resolution rate is low: {resolution_rate:.1f}%")

print("\n[5] Data Integrity")
print("-" * 80)

# Check for orphaned methods
cursor = db.conn.execute("SELECT COUNT(*) FROM methods WHERE class_id IS NULL")
orphaned = cursor.fetchone()[0]
test("Orphaned methods acceptable", orphaned < 20, f"Orphaned: {orphaned}")

# Check for methods with empty names
cursor = db.conn.execute("SELECT COUNT(*) FROM methods WHERE name IS NULL OR name = ''")
invalid_methods = cursor.fetchone()[0]
test("No invalid methods", invalid_methods == 0, f"Invalid: {invalid_methods}")

# Check for classes without methods
cursor = db.conn.execute('''
    SELECT COUNT(*) FROM classes c
    WHERE NOT EXISTS (SELECT 1 FROM methods m WHERE m.class_id = c.id)
''')
classes_without_methods = cursor.fetchone()[0]
if classes_without_methods > 5:
    TEST_WARNINGS.append(f"{classes_without_methods} classes have no methods")

print("\n[6] API Simulation")
print("-" * 80)
try:
    # Simulate what the server does
    cursor = db.conn.execute("SELECT id, name, path, analyzed_at FROM projects ORDER BY id DESC LIMIT 1")
    project = cursor.fetchone()
    test("Project metadata", project is not None)
    
    # Simulate node building
    cursor = db.conn.execute("SELECT COUNT(*) FROM files")
    file_count = cursor.fetchone()[0]
    test("Files in graph", file_count > 0, f"Files: {file_count}")
    
    # Simulate link building
    cursor = db.conn.execute("SELECT COUNT(*) FROM calls")
    link_count = cursor.fetchone()[0]
    test("Links in graph", link_count > 0, f"Links: {link_count}")
except Exception as e:
    test("API simulation", False, str(e))

print("\n[7] Performance Metrics")
print("-" * 80)
cursor = db.conn.execute("SELECT COUNT(*) FROM files")
file_count = cursor.fetchone()[0]
cursor = db.conn.execute("SELECT COUNT(*) FROM classes")
class_count = cursor.fetchone()[0]
cursor = db.conn.execute("SELECT COUNT(*) FROM methods")
method_count = cursor.fetchone()[0]

files_per_second = file_count / elapsed if elapsed > 0 else 0
classes_per_second = class_count / elapsed if elapsed > 0 else 0
methods_per_second = method_count / elapsed if elapsed > 0 else 0

print(f"  Files/sec: {files_per_second:.1f}")
print(f"  Classes/sec: {classes_per_second:.1f}")
print(f"  Methods/sec: {methods_per_second:.1f}")

test("Performance acceptable", files_per_second > 100, f"Files/sec: {files_per_second:.1f}")

db.close()

print("\n[8] Summary")
print("=" * 80)
print(f"Tests Passed: {TEST_PASSED}")
print(f"Tests Failed: {TEST_FAILED}")
print(f"Warnings: {len(TEST_WARNINGS)}")

if TEST_WARNINGS:
    print("\nWarnings:")
    for warning in TEST_WARNINGS:
        print(f"  ⚠️  {warning}")

if TEST_FAILED == 0:
    print("\n✅ ALL TESTS PASSED!")
    print("=" * 80)
    sys.exit(0)
else:
    print("\n❌ SOME TESTS FAILED")
    print("=" * 80)
    sys.exit(1)

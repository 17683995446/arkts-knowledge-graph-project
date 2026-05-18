#!/usr/bin/env python3
"""Simple test script to verify parser and database functionality."""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from ark_analyzer_db import ArkAnalyzerDB
from ark_analyzer_runner import ArkAnalyzerRunner

# Cleanup old database
DB_PATH = "ark_graph.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

# Test 1: Initialize database
print("Test 1: Initializing database...")
db = ArkAnalyzerDB(DB_PATH)
db.initialize()
print("✓ Database initialized")

# Test 2: Run analysis
print("\nTest 2: Analyzing project...")
runner = ArkAnalyzerRunner(os.path.dirname(os.path.abspath(__file__)), db)
success = runner.analyze_project("./example")
print(f"✓ Analysis {'successful' if success else 'failed'}")

# Test 3: Query some stats
print("\nTest 3: Querying project stats...")
stats = db.get_project_stats(runner.project_id)
print(f"✓ Project Stats: {stats}")

# Test 4: List all nodes
print("\nTest 4: Listing all classes...")
cursor = db.conn.execute("SELECT id, name FROM classes WHERE project_id = ?", (runner.project_id,))
classes = cursor.fetchall()
print(f"✓ Found {len(classes)} classes:")
for cls in classes:
    print(f"  - {cls[1]} (id={cls[0]})")

print("\nTest 5: Listing all methods...")
cursor = db.conn.execute("SELECT id, name FROM methods WHERE project_id = ?", (runner.project_id,))
methods = cursor.fetchall()
print(f"✓ Found {len(methods)} methods:")
for method in methods:
    print(f"  - {method[1]} (id={method[0]})")

print("\n✅ All tests completed!")
db.close()

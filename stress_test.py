
#!/usr/bin/env python3
"""
Comprehensive stress and bug discovery test for the ArkTS knowledge graph system.
"""
import os
import sys
import traceback
from pathlib import Path

sys.path.insert(0, '/workspace')
DB_PATH = '/workspace/test_ark_graph.db'

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

print("=" * 80)
print("ARKTS KNOWLEDGE GRAPH SYSTEM - STRESS TEST")
print("=" * 80)

from ark_analyzer_db import ArkAnalyzerDB
from ark_analyzer_runner import ArkAnalyzerRunner

print("\n[1] Initializing database...")
db = ArkAnalyzerDB(DB_PATH)
db.initialize()
print("✓ Database initialized")

print("\n[2] Analyzing complex project...")
complex_project = '/workspace/complex_project'
runner = ArkAnalyzerRunner('/workspace', db)
try:
    success = runner.analyze_project(complex_project)
    print(f"✓ Analysis complete: {success}")
except Exception as e:
    print(f"✗ ERROR: {e}")
    print(traceback.format_exc())
    sys.exit(1)

print("\n[3] Checking stats...")
stats = db.get_project_stats(runner.project_id)
print(f"✓ Project stats: {stats}")

print("\n[4] Checking DB contents...")
cursor = db.conn.execute("SELECT COUNT(*) FROM files")
fc = cursor.fetchone()[0]
print(f"  - Files: {fc}")

cursor = db.conn.execute("SELECT COUNT(*) FROM classes")
cc = cursor.fetchone()[0]
print(f"  - Classes: {cc}")

cursor = db.conn.execute("SELECT COUNT(*) FROM methods")
mc = cursor.fetchone()[0]
print(f"  - Methods: {mc}")

cursor = db.conn.execute("SELECT COUNT(*) FROM calls")
callc = cursor.fetchone()[0]
print(f"  - Calls: {callc}")

print("\n[5] Testing with original example...")
db.close()
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
db = ArkAnalyzerDB(DB_PATH)
db.initialize()
runner2 = ArkAnalyzerRunner('/workspace', db)
success2 = runner2.analyze_project('/workspace/example')
print(f"✓ Original example analysis: {success2}")
stats2 = db.get_project_stats(runner2.project_id)
print(f"✓ Original example stats: {stats2}")

print("\n✓ All tests complete!")

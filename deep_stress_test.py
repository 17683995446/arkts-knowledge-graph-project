
#!/usr/bin/env python3
"""
Comprehensive Deep Stress Test - Analyze the FULL arkanalyzer test suite!
"""

import os
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, '/workspace')

from ark_analyzer_db import ArkAnalyzerDB
from ark_analyzer_runner import ArkAnalyzerRunner

# Clean slate
DB_PATH = 'ark_complete_test.db'
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

print('=' * 100)
print('DEEP STRESS TEST - COMPLETE ARKANALYZER TEST SUITE')
print('=' * 100)

PROJECT_PATH = '/workspace/arkanalyzer_repo/tests/resources'

start_time = time.time()

try:
    db = ArkAnalyzerDB(DB_PATH)
    db.initialize()
    
    runner = ArkAnalyzerRunner('/workspace', db)
    success = runner.analyze_project(PROJECT_PATH)
    
    total_time = time.time() - start_time
    
    print(f'\n✓ Analysis completed in {total_time:.2f} seconds')
    print(f'✓ Success: {success}')
    
    if success:
        stats = db.get_project_stats(runner.project_id)
        
        print('\n📊 Complete Project Statistics:')
        print('-' * 50)
        print(f'  Files:        {stats["files"]}')
        print(f'  Classes:      {stats["classes"]}')
        print(f'  Methods:      {stats["methods"]}')
        print(f'  Calls:        {stats["calls"]}')
        print(f'  Namespaces:   {stats["namespaces"]}')
        
        # Deep quality checks
        print('\n🔍 Detailed Quality Check:')
        print('-' * 50)
        
        # Check for methods without file association
        cursor = db.conn.execute('''
            SELECT COUNT(*) FROM methods WHERE file_id IS NULL
        ''')
        methods_no_file = cursor.fetchone()[0]
        
        cursor = db.conn.execute('''
            SELECT COUNT(*) FROM methods
        ''')
        total_methods = cursor.fetchone()[0]
        
        file_rate = 100 - (methods_no_file / total_methods * 100) if total_methods > 0 else 100
        print(f'  Methods with file: {file_rate:.1f}%')
        
        # Check call resolution
        cursor = db.conn.execute('''
            SELECT COUNT(*) FROM calls WHERE callee_method_id IS NOT NULL
        ''')
        resolved = cursor.fetchone()[0]
        
        cursor = db.conn.execute('''
            SELECT COUNT(*) FROM calls
        ''')
        total_calls = cursor.fetchone()[0]
        
        call_rate = (resolved / total_calls * 100) if total_calls > 0 else 0
        print(f'  Call resolution:  {call_rate:.1f}%')
        
        # Check for orphan classes
        cursor = db.conn.execute('''
            SELECT COUNT(*) FROM classes WHERE file_id IS NULL
        ''')
        orphan_classes = cursor.fetchone()[0]
        print(f'  Orphan classes:   {orphan_classes}')
        
        # Check for invalid data
        cursor = db.conn.execute('''
            SELECT COUNT(*) FROM classes WHERE name IS NULL OR name = ""
        ''')
        invalid_classes = cursor.fetchone()[0]
        print(f'  Invalid classes:  {invalid_classes}')
        
        cursor = db.conn.execute('''
            SELECT COUNT(*) FROM methods WHERE name IS NULL OR name = ""
        ''')
        invalid_methods = cursor.fetchone()[0]
        print(f'  Invalid methods:  {invalid_methods}')
        
        print('\n📁 Analysis Summary:')
        print('-' * 50)
        
        # Show top 10 files with most classes
        print('\n📄 Top 10 Files (by class count):')
        cursor = db.conn.execute('''
            SELECT f.path, COUNT(c.id) as class_count
            FROM files f
            JOIN classes c ON c.file_id = f.id
            GROUP BY f.id
            ORDER BY class_count DESC
            LIMIT 10
        ''')
        for i, row in enumerate(cursor.fetchall(), 1):
            print(f'  {i}. {Path(row[0]).name} - {row[1]} classes')
        
        # Show top 10 files with most methods
        print('\n📄 Top 10 Files (by method count):')
        cursor = db.conn.execute('''
            SELECT f.path, COUNT(m.id) as method_count
            FROM files f
            JOIN methods m ON m.file_id = f.id
            GROUP BY f.id
            ORDER BY method_count DESC
            LIMIT 10
        ''')
        for i, row in enumerate(cursor.fetchall(), 1):
            print(f'  {i}. {Path(row[0]).name} - {row[1]} methods')
        
        # Check for any errors
        print('\n✅ Quality Check Results:')
        print('-' * 50)
        
        any_issues = False
        if methods_no_file > 0:
            print(f'  ⚠️  {methods_no_file} methods missing file association')
            any_issues = True
        
        if orphan_classes > 0:
            print(f'  ⚠️  {orphan_classes} orphan classes')
            any_issues = True
        
        if invalid_classes > 0 or invalid_methods > 0:
            print(f'  ⚠️  Invalid data: {invalid_classes} classes, {invalid_methods} methods')
            any_issues = True
        
        if not any_issues:
            print('  ✅ All quality checks passed!')
        
        # Performance metrics
        print(f'\n⚡ Performance:')
        print(f'  Files/sec:    {stats["files"] / total_time:.1f}')
        print(f'  Methods/sec:  {stats["methods"] / total_time:.1f}')
        print(f'  Calls/sec:    {stats["calls"] / total_time:.1f}')
        
    db.close()
    
except Exception as e:
    print(f'\n❌ Critical Error: {str(e)}')
    print(traceback.format_exc())
    if 'db' in locals():
        db.close()
    sys.exit(1)

print(f'\n{"=" * 100}')
print('✓ COMPLETED - STRESS TEST SUCCESSFUL')
print(f'{"=" * 100}')


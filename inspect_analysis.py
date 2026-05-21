
#!/usr/bin/env python3
"""
Deep Analysis - Find all edge cases and optimization opportunities!
"""

import sys
from pathlib import Path

sys.path.insert(0, '/workspace')

from ark_analyzer_db import ArkAnalyzerDB

DB_PATH = 'ark_complete_test.db'

print('=' * 100)
print('DEEP INSPECTION - FINDING EDGE CASES')
print('=' * 100)

db = ArkAnalyzerDB(DB_PATH)
db.initialize()

# Check for method parameter complexity
print('\n📊 Parameter Complexity Analysis:')
print('-' * 50)
cursor = db.conn.execute('''
    SELECT id, name, params, return_type, 
           LENGTH(params) as param_len
    FROM methods 
    ORDER BY param_len DESC 
    LIMIT 20
''')
print('\nTop 20 Methods by Parameter Complexity:')
for row in cursor.fetchall():
    method_id, name, params, return_type, param_len = row
    if param_len > 0:
        params_display = params[:80] + '...' if len(params) > 80 else params
        print(f'  {name:20} (len: {param_len:4})')
        print(f'    Params: {params_display}')

# Check for the largest classes
print('\n\n🏛️ Largest Classes by Method Count:')
print('-' * 50)
cursor = db.conn.execute('''
    SELECT c.id, c.name, c.path, COUNT(m.id) as method_count
    FROM classes c
    LEFT JOIN methods m ON m.class_id = c.id
    GROUP BY c.id
    ORDER BY method_count DESC
    LIMIT 20
''')
for row in cursor.fetchall():
    class_id, class_name, path, count = row
    print(f'  {class_name:30} (file: {Path(path).name}) - {count} methods')

# Check the giant file - @arkts.collections.d.ets
print('\n\n📄 Detailed Look at the Largest File:')
print('-' * 50)
cursor = db.conn.execute('''
    SELECT id, path
    FROM files 
    WHERE path LIKE '%%@arkts.collections%%'
''')
file = cursor.fetchone()

if file:
    file_id, path = file
    print(f'File: {path}')
    
    cursor = db.conn.execute('''
        SELECT c.id, c.name, c.start_line, c.end_line,
               COUNT(m.id) as method_count
        FROM classes c
        LEFT JOIN methods m ON m.class_id = c.id
        WHERE c.file_id = ?
        GROUP BY c.id
        ORDER BY method_count DESC
    ''', (file_id,))
    
    print('  Classes in this file:')
    classes = cursor.fetchall()
    for row in classes:
        class_id, name, start, end, count = row
        print(f'    - {name} (lines {start}-{end}): {count} methods')
        
        # Show methods in the largest class
        if count > 0 and len(classes) <= 2:
            print(f'      Methods:')
            cursor = db.conn.execute('''
                SELECT name, params, return_type, start_line
                FROM methods 
                WHERE class_id = ? 
                ORDER BY start_line
            ''', (class_id,))
            for m in cursor.fetchall():
                m_name, m_params, m_ret, m_line = m
                params_short = m_params[:50] + '...' if len(m_params) > 50 else m_params
                print(f'        {m_line:4} - {m_name}({params_short})')

# Check calls
print('\n\n🔗 Call Analysis:')
print('-' * 50)
cursor = db.conn.execute('''
    SELECT caller.name as caller_name, 
           c.callee_method_name,
           target.name as target_name,
           c.call_type
    FROM calls c
    JOIN methods caller ON caller.id = c.caller_method_id
    LEFT JOIN methods target ON target.id = c.callee_method_id
    LIMIT 30
''')
print('Sample Calls (30):')
for row in cursor.fetchall():
    caller_name, callee_name, target_name, call_type = row
    resolution = f'→ {target_name}' if target_name else '[UNRESOLVED]'
    print(f'  {caller_name}() calls {callee_name}() {resolution}')

# Check what's being unresolved
print('\n\n❓ Top Unresolved Calls:')
print('-' * 50)
cursor = db.conn.execute('''
    SELECT callee_method_name, COUNT(*) as count
    FROM calls 
    WHERE callee_method_id IS NULL
    GROUP BY callee_method_name
    ORDER BY count DESC
    LIMIT 20
''')
for row in cursor.fetchall():
    name, count = row
    print(f'  {name:20} - {count} times')

db.close()

print(f'\n{"=" * 100}')


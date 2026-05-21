
#!/usr/bin/env python3
"""
诊断测试 - 验证增量更新是否真正跳过未改变的文件
"""

import os
import sys
import time
sys.path.insert(0, '/workspace')

from ark_analyzer_db import ArkAnalyzerDB
from ark_analyzer_runner import ArkAnalyzerRunner

# Clean
DB_PATH = 'test_incremental.db'
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

PROJECT_PATH = '/workspace/test_incremental'

# Create 100 small files
print('Creating 100 small test files...')
os.makedirs(PROJECT_PATH, exist_ok=True)

for i in range(100):
    content = f'''
export class Class{i} {{
    public method1(): void {{
        console.log("Method 1");
    }}
    
    public method2(): void {{
        this.method1();
    }}
}}
'''
    with open(f'{PROJECT_PATH}/file{i:03d}.ets', 'w') as f:
        f.write(content)

print('✅ Created 100 files')

# First analysis
print('\n【First Analysis】')
db = ArkAnalyzerDB(DB_PATH)
db.initialize()
runner = ArkAnalyzerRunner('/workspace', db)

start = time.time()
runner.analyze_project(PROJECT_PATH)
time1 = time.time() - start

stats = db.get_project_stats(runner.project_id)
print(f'First scan: {time1:.3f}s')
print(f'Files: {stats["files"]}, Classes: {stats["classes"]}, Methods: {stats["methods"]}, Calls: {stats["calls"]}')

# Second analysis - NO changes
print('\n【Second Analysis - NO changes】')
runner2 = ArkAnalyzerRunner('/workspace', db)

start = time.time()
runner2.analyze_project(PROJECT_PATH)
time2 = time.time() - start

stats2 = db.get_project_stats(runner2.project_id)
print(f'Second scan: {time2:.3f}s')
print(f'Files: {stats2["files"]}, Classes: {stats2["classes"]}, Methods: {stats2["methods"]}, Calls: {stats2["calls"]}')

if time2 < time1 * 0.5:
    print(f'✅ Incremental update working! {time2/time1*100:.1f}% of first scan time')
else:
    print(f'⚠️  Incremental update may not be working ({time2/time1*100:.1f}% of first scan time)')

# Third analysis - modify ONE file
print('\n【Third Analysis - Modify ONE file】')
with open(f'{PROJECT_PATH}/file050.ets', 'a') as f:
    f.write('\n    // Added line\n')

runner3 = ArkAnalyzerRunner('/workspace', db)

start = time.time()
runner3.analyze_project(PROJECT_PATH)
time3 = time.time() - start

stats3 = db.get_project_stats(runner3.project_id)
print(f'Third scan: {time3:.3f}s')
print(f'Files: {stats3["files"]}, Classes: {stats3["classes"]}, Methods: {stats3["methods"]}, Calls: {stats3["calls"]}')

if time3 < time1 * 0.5:
    print(f'✅ Incremental update working! {time3/time1*100:.1f}% of first scan time')
else:
    print(f'⚠️  Incremental update may not be working ({time3/time1*100:.1f}% of first scan time)')

db.close()

# Cleanup
import shutil
shutil.rmtree(PROJECT_PATH)
print('\n✅ Cleanup complete')


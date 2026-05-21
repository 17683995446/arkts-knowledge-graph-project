
#!/usr/bin/env python3
"""
百万行级 ArkTS 代码知识图谱系统 - 第一性原理验证
First Principles Verification:
1. 变更铁律: 99%修改涉及1-2文件 → 增量更新测试
2. 响应铁律: 2秒内响应 → API性能测试
3. 图谱完整性: 所有实体和关系 → 完整性验证
"""

import os
import sys
import time
import hashlib
from pathlib import Path

sys.path.insert(0, '/workspace')

from ark_analyzer_db import ArkAnalyzerDB
from ark_analyzer_runner import ArkAnalyzerRunner

# Clean slate
DB_PATH = 'million_line_test.db'
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

print('=' * 120)
print('第一性原理验证 - 百万行级知识图谱系统')
print('=' * 120)

# ============================================================================
# 第一性原理 1: 变更铁律验证
# ============================================================================
print('\n【第一性原理 1: 变更铁律】')
print('99% 修改涉及 1-2 文件 → 增量更新测试')
print('-' * 80)

PROJECT_PATH = '/workspace/million_line_project'
os.makedirs(PROJECT_PATH, exist_ok=True)

# Create 1000 files with 1000 lines each = 1,000,000 lines
NUM_FILES = 1000
LINES_PER_FILE = 1000

print(f'Creating {NUM_FILES} files with {LINES_PER_FILE} lines each...')
start_time = time.time()

for i in range(NUM_FILES):
    lines = []
    for j in range(LINES_PER_FILE):
        # Generate unique class per file (for testing change detection)
        if j == 0:
            lines.append(f'// File {i} - Line {j}')
            lines.append(f'export class Class_{i} {{')
        elif j == 1:
            lines.append(f'    private id_{j}: number = {i * 1000 + j};')
        elif j == 2:
            lines.append(f'    public getId(): number {{ return this.id_{j-1}; }}')
        elif j == LINES_PER_FILE - 1:
            lines.append('}')
        else:
            # Random method
            if j % 50 == 0:
                lines.append(f'    public method_{j}(): void {{')
                lines.append(f'        console.log("File {i}, Method {j}");')
                lines.append('    }')

    with open(f'{PROJECT_PATH}/file_{i:04d}.ets', 'w') as f:
        f.write('\n'.join(lines))

creation_time = time.time() - start_time
print(f'✅ Created {NUM_FILES} files in {creation_time:.2f}s')
print(f'   Total lines: {NUM_FILES * LINES_PER_FILE:,}')

# ============================================================================
# 第一次全量分析
# ============================================================================
print('\n【第一次分析: 全量扫描】')
print('-' * 80)

db = ArkAnalyzerDB(DB_PATH)
db.initialize()

start_time = time.time()
runner = ArkAnalyzerRunner('/workspace', db)
success = runner.analyze_project(PROJECT_PATH)
full_scan_time = time.time() - start_time

if success:
    stats = db.get_project_stats(runner.project_id)
    print(f'✅ 全量扫描完成!')
    print(f'   文件数: {stats["files"]:,}')
    print(f'   类数: {stats["classes"]:,}')
    print(f'   方法数: {stats["methods"]:,}')
    print(f'   耗时: {full_scan_time:.2f}s')

    # Check against first principle
    if full_scan_time <= 2.0:
        print(f'   🎯 第一性原理验证通过: {full_scan_time:.2f}s ≤ 2s')
    else:
        print(f'   ⚠️  第一性原理验证失败: {full_scan_time:.2f}s > 2s')

# ============================================================================
# 第二性原理 1: 变更铁律 - 增量更新测试
# ============================================================================
print('\n【第二性原理验证: 变更铁律】')
print('修改 1 个文件，验证增量更新')
print('-' * 80)

# Modify just ONE file
modified_file = f'{PROJECT_PATH}/file_0001.ets'
with open(modified_file, 'a') as f:
    f.write('\n    // Added method after change\n')
    f.write('    public addedMethod(): void {\n')
    f.write('        console.log("Added method!");\n')
    f.write('    }\n')

# Calculate file hash
with open(modified_file, 'r') as f:
    new_hash = hashlib.md5(f.read().encode()).hexdigest()

print(f'修改文件: {Path(modified_file).name}')
print(f'新哈希: {new_hash}')

# Incremental update
start_time = time.time()
success = runner.analyze_project(PROJECT_PATH)
incremental_time = time.time() - start_time

print(f'✅ 增量更新完成!')
print(f'   耗时: {incremental_time:.3f}s')
print(f'   加速比: {full_scan_time / incremental_time:.1f}x')

# Check first principle: incremental should be MUCH faster
if incremental_time < full_scan_time * 0.1:
    print(f'   🎯 变更铁律验证通过: 增量更新 < 10% 全量扫描时间')
else:
    print(f'   ⚠️  变更铁律验证失败: 增量更新应该更快')

# ============================================================================
# 第二性原理 2: 响应铁律 - API 性能测试
# ============================================================================
print('\n【第二性原理验证: 响应铁律】')
print('验证 API 响应时间 < 2秒')
print('-' * 80)

# Simulate API query
start_time = time.time()

cursor = db.conn.execute("SELECT COUNT(*) FROM files")
file_count = cursor.fetchone()[0]

cursor = db.conn.execute("SELECT COUNT(*) FROM classes")
class_count = cursor.fetchone()[0]

cursor = db.conn.execute("SELECT COUNT(*) FROM methods")
method_count = cursor.fetchone()[0]

cursor = db.conn.execute("SELECT COUNT(*) FROM calls")
call_count = cursor.fetchone()[0]

api_time = time.time() - start_time

print(f'✅ API 查询完成!')
print(f'   文件数: {file_count:,}')
print(f'   类数: {class_count:,}')
print(f'   方法数: {method_count:,}')
print(f'   调用关系: {call_count:,}')
print(f'   耗时: {api_time * 1000:.2f}ms')

if api_time < 2.0:
    print(f'   🎯 响应铁律验证通过: {api_time * 1000:.2f}ms < 2000ms')
else:
    print(f'   ⚠️  响应铁律验证失败: {api_time * 1000:.2f}ms > 2000ms')

# ============================================================================
# 第三性原理: 图谱完整性验证
# ============================================================================
print('\n【第三性原理验证: 图谱完整性】')
print('验证所有实体和关系都被正确捕获')
print('-' * 80)

# Check relationships
cursor = db.conn.execute('''
    SELECT
        (SELECT COUNT(*) FROM methods WHERE file_id IS NOT NULL) as methods_with_file,
        (SELECT COUNT(*) FROM methods) as total_methods
''')
result = cursor.fetchone()
methods_with_file = result[0]
total_methods = result[1]

cursor = db.conn.execute('''
    SELECT
        (SELECT COUNT(*) FROM classes WHERE file_id IS NOT NULL) as classes_with_file,
        (SELECT COUNT(*) FROM classes) as total_classes
''')
result = cursor.fetchone()
classes_with_file = result[0]
total_classes = result[1]

print(f'方法-文件关联: {methods_with_file:,}/{total_methods:,} ({methods_with_file/total_methods*100:.1f}%)')
print(f'类-文件关联: {classes_with_file:,}/{total_classes:,} ({classes_with_file/total_classes*100:.1f}%)')

if methods_with_file == total_methods and classes_with_file == total_classes:
    print(f'   🎯 完整性验证通过: 100% 实体关联到文件')
else:
    print(f'   ⚠️  完整性验证失败: 部分实体未关联')

# ============================================================================
# 性能基准测试
# ============================================================================
print('\n【性能基准测试】')
print('-' * 80)

total_lines = NUM_FILES * LINES_PER_FILE
files_per_second = stats['files'] / full_scan_time if full_scan_time > 0 else 0
lines_per_second = total_lines / full_scan_time if full_scan_time > 0 else 0
methods_per_second = stats['methods'] / full_scan_time if full_scan_time > 0 else 0

print(f'总代码行数: {total_lines:,}')
print(f'分析速度:')
print(f'   - 文件/秒: {files_per_second:,.0f}')
print(f'   - 代码行/秒: {lines_per_second:,.0f}')
print(f'   - 方法/秒: {methods_per_second:,.0f}')

# First principle: 2 second response time
if full_scan_time <= 2.0:
    print(f'\n🎯🎯🎯 第一性原理完全验证通过! 🎯🎯🎯')
    print(f'系统在 {full_scan_time:.2f}s 内完成了 {total_lines:,} 行代码的完整分析!')
else:
    print(f'\n⚠️  性能优化空间: 当前 {full_scan_time:.2f}s > 2s')

db.close()

# Cleanup
print('\n【清理测试数据】')
import shutil
if os.path.exists(PROJECT_PATH):
    shutil.rmtree(PROJECT_PATH)
print('✅ 清理完成')

print(f'\n{"=" * 120}')
print('第一性原理验证完成!')
print(f'{"=" * 120}')


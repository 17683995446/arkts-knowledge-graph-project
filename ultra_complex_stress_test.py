
#!/usr/bin/env python3
"""
慢工出细活 - 深度压力测试脚本
全面测试并发现系统问题
"""

import sys
import os
import time
import traceback
from pathlib import Path

sys.path.insert(0, '/workspace')

from ark_analyzer_db import ArkAnalyzerDB
from ark_analyzer_runner import ArkAnalyzerRunner


def main():
    print('=' * 120)
    print('深度压力测试 - 慢工出细活')
    print('=' * 120)
    
    # 清理旧数据库
    db_path = 'ultra_complex_test.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    print('\n📊 阶段 1: 测试环境准备')
    print('-' * 120)
    
    test_dir = Path('/workspace/ultra_complex_test_project')
    if not test_dir.exists():
        print(f'❌ 测试目录不存在: {test_dir}')
        return
    
    file_count = sum(1 for f in test_dir.rglob('*.ets'))
    print(f'✅ 找到 {file_count} 个 ArkTS 文件')
    
    files = list(test_dir.rglob('*.ets'))
    total_lines = 0
    for file in files:
        with open(file, 'r', encoding='utf-8', errors='replace') as f:
            total_lines += len(f.readlines())
    print(f'✅ 总计 {total_lines:,} 行代码')
    
    print('\n🚀 阶段 2: 完整分析')
    print('-' * 120)
    
    db = ArkAnalyzerDB(db_path)
    db.initialize()
    runner = ArkAnalyzerRunner('/workspace', db)
    
    start_time = time.time()
    try:
        success = runner.analyze_project(str(test_dir))
        analysis_time = time.time() - start_time
        
        print(f'✅ 分析完成！耗时: {analysis_time:.2f}秒')
        print(f'   成功率: {"✅ 成功" if success else "❌ 失败"}')
        
    except Exception as e:
        print(f'❌ 分析过程出错: {str(e)}')
        print(traceback.format_exc())
        db.close()
        return
    
    print('\n🔍 阶段 3: 深度数据分析')
    print('-' * 120)
    
    stats = db.get_project_stats(runner.project_id)
    print('项目统计:')
    print(f'  📄 文件:         {stats["files"]:,}')
    print(f'  🏛️  类/结构体:    {stats["classes"]:,}')
    print(f'  🔧 方法/函数:    {stats["methods"]:,}')
    print(f'  🔗 调用关系:     {stats["calls"]:,}')
    print(f'  📦 命名空间:     {stats["namespaces"]:,}')
    
    print('\n📈 阶段 4: 质量检查')
    print('-' * 120)
    
    passed = True
    
    # 检查 1: 文件关联
    print('1️⃣  检查方法-文件关联:')
    cursor = db.conn.execute('SELECT COUNT(*) FROM methods WHERE file_id IS NOT NULL')
    methods_with_file = cursor.fetchone()[0]
    cursor = db.conn.execute('SELECT COUNT(*) FROM methods')
    total_methods = cursor.fetchone()[0]
    
    if total_methods == 0:
        print(f'   ⚠️  没有找到任何方法')
        passed = False
    elif methods_with_file == total_methods:
        print(f'   ✅ {methods_with_file:,}/{total_methods:,} (100%) 方法有文件关联')
    else:
        percentage = (methods_with_file / total_methods) * 100
        print(f'   ❌ {methods_with_file:,}/{total_methods:,} ({percentage:.1f}%) 方法有文件关联')
        passed = False
    
    # 检查 2: 类-文件关联
    print('\n2️⃣  检查类-文件关联:')
    cursor = db.conn.execute('SELECT COUNT(*) FROM classes WHERE file_id IS NOT NULL')
    classes_with_file = cursor.fetchone()[0]
    cursor = db.conn.execute('SELECT COUNT(*) FROM classes')
    total_classes = cursor.fetchone()[0]
    
    if total_classes == 0:
        print(f'   ⚠️  没有找到任何类')
        passed = False
    elif classes_with_file == total_classes:
        print(f'   ✅ {classes_with_file:,}/{total_classes:,} (100%) 类有文件关联')
    else:
        percentage = (classes_with_file / total_classes) * 100
        print(f'   ❌ {classes_with_file:,}/{total_classes:,} ({percentage:.1f}%) 类有文件关联')
        passed = False
    
    # 检查 3: 调用关系解析
    print('\n3️⃣  检查调用关系解析:')
    cursor = db.conn.execute('SELECT COUNT(*) FROM calls WHERE callee_method_id IS NOT NULL')
    resolved_calls = cursor.fetchone()[0]
    cursor = db.conn.execute('SELECT COUNT(*) FROM calls')
    total_calls = cursor.fetchone()[0]
    
    if total_calls == 0:
        print(f'   ⚠️  没有找到任何调用关系')
    else:
        percentage = (resolved_calls / total_calls) * 100
        if percentage >= 50:
            print(f'   ✅ {resolved_calls:,}/{total_calls:,} ({percentage:.1f}%) 调用关系已解析')
        elif percentage >= 30:
            print(f'   ⚠️  {resolved_calls:,}/{total_calls:,} ({percentage:.1f}%) 调用关系已解析')
        else:
            print(f'   ❌ {resolved_calls:,}/{total_calls:,} ({percentage:.1f}%) 调用关系已解析')
    
    # 检查 4: 数据完整性
    print('\n4️⃣  检查数据完整性:')
    cursor = db.conn.execute('SELECT COUNT(*) FROM classes WHERE name IS NULL OR name = ""')
    invalid_classes = cursor.fetchone()[0]
    cursor = db.conn.execute('SELECT COUNT(*) FROM methods WHERE name IS NULL OR name = ""')
    invalid_methods = cursor.fetchone()[0]
    
    if invalid_classes > 0:
        print(f'   ❌ 发现 {invalid_classes} 个无效类')
        passed = False
    if invalid_methods > 0:
        print(f'   ❌ 发现 {invalid_methods} 个无效方法')
        passed = False
    if invalid_classes == 0 and invalid_methods == 0:
        print(f'   ✅ 没有发现无效数据')
    
    print('\n📄 阶段 5: 样本数据检查')
    print('-' * 120)
    
    # 显示前 10 个类
    print('前 10 个类:')
    cursor = db.conn.execute('SELECT id, name, file_id FROM classes LIMIT 10')
    for idx, (class_id, name, file_id) in enumerate(cursor.fetchall(), 1):
        cursor2 = db.conn.execute('SELECT path FROM files WHERE id = ?', (file_id,))
        file_row = cursor2.fetchone()
        file_path = Path(file_row[0]).name if file_row else 'unknown'
        print(f'   {idx:2d}. {name} ({file_path})')
    
    # 显示前 20 个方法
    print('\n前 20 个方法:')
    cursor = db.conn.execute('SELECT id, name, class_id, file_id FROM methods LIMIT 20')
    for idx, (method_id, name, class_id, file_id) in enumerate(cursor.fetchall(), 1):
        class_name = ''
        if class_id:
            cursor2 = db.conn.execute('SELECT name FROM classes WHERE id = ?', (class_id,))
            class_row = cursor2.fetchone()
            class_name = class_row[0] if class_row else ''
        
        file_path = ''
        if file_id:
            cursor2 = db.conn.execute('SELECT path FROM files WHERE id = ?', (file_id,))
            file_row = cursor2.fetchone()
            file_path = Path(file_row[0]).name if file_row else ''
        
        class_str = f' - {class_name}' if class_name else ''
        file_str = f' ({file_path})' if file_path else ''
        print(f'   {idx:2d}. {name}{class_str}{file_str}')
    
    # 显示一些调用关系
    print('\n前 20 个调用关系:')
    cursor = db.conn.execute('''
        SELECT c.id, cm.name as caller, c.callee_method_name as callee, c.callee_method_id
        FROM calls c
        JOIN methods cm ON c.caller_method_id = cm.id
        LIMIT 20
    ''')
    for idx, (call_id, caller, callee, callee_id) in enumerate(cursor.fetchall(), 1):
        resolved = '✅' if callee_id else '❌'
        print(f'   {idx:2d}. {resolved} {caller}() → {callee}()')
    
    print('\n🎯 阶段 6: 性能评估')
    print('-' * 120)
    
    print(f'分析速度:')
    print(f'  文件/秒:    {stats["files"] / analysis_time:,.1f}')
    print(f'  方法/秒:    {stats["methods"] / analysis_time:,.1f}')
    print(f'  调用/秒:    {stats["calls"] / analysis_time:,.1f}')
    print(f'  代码行/秒:  {total_lines / analysis_time:,.1f}')
    
    print('\n⏱️  API 查询测试:')
    query_start = time.time()
    
    cursor = db.conn.execute('SELECT COUNT(*) FROM files')
    cursor = db.conn.execute('SELECT COUNT(*) FROM classes')
    cursor = db.conn.execute('SELECT COUNT(*) FROM methods')
    cursor = db.conn.execute('SELECT COUNT(*) FROM calls')
    
    query_time = time.time() - query_start
    print(f'  基础查询: {query_time * 1000:.2f}ms')
    
    graph_start = time.time()
    # 模拟构建图数据
    nodes = []
    links = []
    
    cursor = db.conn.execute('SELECT id, path FROM files WHERE project_id = ?', (runner.project_id,))
    for (file_id, path) in cursor.fetchall():
        nodes.append({'id': f'file_{file_id}', 'type': 'file', 'name': Path(path).name})
    
    cursor = db.conn.execute('SELECT id, name, file_id FROM classes WHERE project_id = ?', (runner.project_id,))
    for (class_id, name, file_id) in cursor.fetchall():
        nodes.append({'id': f'class_{class_id}', 'type': 'class', 'name': name})
        if file_id:
            links.append({'source': f'class_{class_id}', 'target': f'file_{file_id}', 'type': 'contains'})
    
    cursor = db.conn.execute('SELECT id, name, class_id, file_id FROM methods WHERE project_id = ?', (runner.project_id,))
    for (method_id, name, class_id, file_id) in cursor.fetchall():
        nodes.append({'id': f'method_{method_id}', 'type': 'method', 'name': name})
        if class_id:
            links.append({'source': f'method_{method_id}', 'target': f'class_{class_id}', 'type': 'member'})
    
    graph_time = time.time() - graph_start
    print(f'  图构建:  {graph_time * 1000:.2f}ms ({len(nodes)} 个节点, {len(links)} 条边)')
    
    print('\n' + '=' * 120)
    if passed:
        print('🎉 所有质量检查通过！')
    else:
        print('⚠️  部分检查未通过，需要修复')
    print('=' * 120)
    
    db.close()
    
    print('\n✅ 深度压力测试完成！')


if __name__ == '__main__':
    main()


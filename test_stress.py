#!/usr/bin/env python3
"""
超大规模压力测试
测试系统在处理1000+文件、10000+类、100000+方法时的性能
"""
import os
import sys
import time
import tempfile
import traceback

sys.path.insert(0, '/workspace')

from ark_analyzer_db import ArkAnalyzerDB
from ark_analyzer_runner import ArkAnalyzerRunner


def log(msg):
    print(f"[STRESS TEST] {msg}")


def main():
    print("="*80)
    print("  超大规模压力测试")
    print("="*80)
    
    test_path = "/workspace/massive_chaos_project"
    
    if not os.path.exists(test_path):
        log(f"❌ 测试项目不存在: {test_path}")
        return
    
    # 统计文件数量
    file_count = sum(1 for root, dirs, files in os.walk(test_path)
                     for f in files if f.endswith(('.ets', '.ts')))
    log(f"测试项目包含 {file_count} 个文件")
    
    # 创建临时数据库
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        log("开始压力测试...")
        
        # 测试1: 完整分析
        log("="*60)
        log("测试1: 完整分析")
        log("="*60)
        
        start_time = time.time()
        
        db = ArkAnalyzerDB(db_path)
        db.initialize()
        runner = ArkAnalyzerRunner('/workspace', db)
        
        success = runner.analyze_project(test_path, "MassiveStressTest")
        
        duration = time.time() - start_time
        
        if not success:
            log("❌ 分析失败!")
            return
        
        stats = db.get_project_stats(runner.project_id)
        
        log(f"分析完成!")
        log(f"  耗时: {duration:.2f} 秒")
        log(f"  文件数: {stats['files']}")
        log(f"  类数量: {stats['classes']}")
        log(f"  方法数量: {stats['methods']}")
        log(f"  调用数量: {stats['calls']}")
        log(f"  处理速度: {stats['files']/duration:.2f} 文件/秒")
        log(f"  处理速度: {stats['classes']/duration:.2f} 类/秒")
        
        # 测试2: 增量更新（无变化）
        log("\n" + "="*60)
        log("测试2: 增量更新（无变化）")
        log("="*60)
        
        start_time = time.time()
        success = runner.analyze_project(test_path, "MassiveStressTest")
        duration = time.time() - start_time
        
        stats2 = db.get_project_stats(runner.project_id)
        
        log(f"增量更新完成!")
        log(f"  耗时: {duration:.2f} 秒")
        log(f"  文件数: {stats2['files']}")
        log(f"  类数量: {stats2['classes']}")
        log(f"  方法数量: {stats2['methods']}")
        log(f"  速度提升: {stats['files']/duration:.2f}x")
        
        # 测试3: 数据一致性检查
        log("\n" + "="*60)
        log("测试3: 数据一致性检查")
        log("="*60)
        
        # 检查孤儿记录
        cursor = db.conn.execute("""
            SELECT COUNT(*) FROM calls 
            WHERE caller_method_id NOT IN (SELECT id FROM methods WHERE project_id = ?)
        """, (runner.project_id,))
        orphaned_calls = cursor.fetchone()[0]
        log(f"孤儿调用记录: {orphaned_calls}")
        
        cursor = db.conn.execute("""
            SELECT COUNT(*) FROM classes 
            WHERE file_id NOT IN (SELECT id FROM files WHERE project_id = ?)
        """, (runner.project_id,))
        orphaned_classes = cursor.fetchone()[0]
        log(f"孤儿类记录: {orphaned_classes}")
        
        cursor = db.conn.execute("""
            SELECT COUNT(*) FROM methods 
            WHERE class_id NOT IN (SELECT id FROM classes WHERE project_id = ?) 
            AND class_id IS NOT NULL
        """, (runner.project_id,))
        orphaned_methods = cursor.fetchone()[0]
        log(f"孤儿方法记录: {orphaned_methods}")
        
        # 测试4: 图导出
        log("\n" + "="*60)
        log("测试4: 图导出性能")
        log("="*60)
        
        start_time = time.time()
        graph = db.export_graph(runner.project_id)
        duration = time.time() - start_time
        
        log(f"图导出完成!")
        log(f"  耗时: {duration:.2f} 秒")
        log(f"  节点数量: {len(graph.get('nodes', []))}")
        log(f"  链接数量: {len(graph.get('links', []))}")
        
        # 测试5: 查询性能
        log("\n" + "="*60)
        log("测试5: 查询性能")
        log("="*60)
        
        # 测试项目列表查询
        start_time = time.time()
        projects = db.get_all_projects()
        duration = time.time() - start_time
        log(f"项目列表查询: {duration*1000:.2f} ms")
        
        # 测试统计查询
        start_time = time.time()
        stats = db.get_project_stats(runner.project_id)
        duration = time.time() - start_time
        log(f"统计查询: {duration*1000:.2f} ms")
        
        # 测试类查询
        cursor = db.conn.execute("""
            SELECT id, name FROM classes WHERE project_id = ? LIMIT 100
        """, (runner.project_id,))
        class_rows = cursor.fetchall()
        
        if class_rows:
            start_time = time.time()
            test_class = class_rows[0]
            result = db.query_class(runner.project_id, test_class[1])
            duration = time.time() - start_time
            log(f"单类查询: {duration*1000:.2f} ms")
        
        db.close()
        
        # 总结
        print("\n" + "="*80)
        print("  压力测试完成")
        print("="*80)
        print(f"✅ 处理了 {file_count} 个文件")
        print(f"✅ 解析了 {stats['classes']} 个类")
        print(f"✅ 提取了 {stats['methods']} 个方法")
        print(f"✅ 识别了 {stats['calls']} 个调用关系")
        print(f"✅ 数据一致性: {orphaned_calls + orphaned_classes + orphaned_methods} 个孤儿记录")
        print("="*80)
        
    except Exception as e:
        log(f"❌ 测试失败: {e}")
        traceback.print_exc()
        
    finally:
        try:
            os.unlink(db_path)
        except Exception:
            pass


if __name__ == "__main__":
    main()

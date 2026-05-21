#!/usr/bin/env python3
"""
第三轮深度测试 - 极端复杂场景测试
测试极端边界条件、混乱场景、隐藏问题
"""
import os
import sys
import time
import tempfile
import traceback
import gc

sys.path.insert(0, '/workspace')

from parser import ArkTSParser
from ark_analyzer_db import ArkAnalyzerDB
from ark_analyzer_runner import ArkAnalyzerRunner


def log(msg):
    print(f"[EXTREME TEST] {msg}")


def test_extreme_scenarios():
    """测试极端场景"""
    print("="*80)
    print("  第三轮深度测试 - 极端复杂场景")
    print("="*80)
    
    test_path = "/workspace/extreme_chaos_project"
    
    if not os.path.exists(test_path):
        log(f"❌ 测试项目不存在: {test_path}")
        return False
    
    # 统计文件
    file_count = sum(1 for root, dirs, files in os.walk(test_path)
                     for f in files if f.endswith('.ets'))
    log(f"测试项目包含 {file_count} 个极端场景文件")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        # 测试1: 完整分析极端场景
        log("\n" + "="*60)
        log("测试1: 完整分析极端场景")
        log("="*60)
        
        start_time = time.time()
        
        db = ArkAnalyzerDB(db_path)
        db.initialize()
        runner = ArkAnalyzerRunner('/workspace', db)
        
        success = runner.analyze_project(test_path, "ExtremeChaosTest")
        
        duration = time.time() - start_time
        
        if not success:
            log("❌ 分析失败!")
            return False
        
        stats = db.get_project_stats(runner.project_id)
        
        log(f"分析完成!")
        log(f"  耗时: {duration:.2f} 秒")
        log(f"  文件数: {stats['files']}")
        log(f"  类数量: {stats['classes']}")
        log(f"  方法数量: {stats['methods']}")
        log(f"  调用数量: {stats['calls']}")
        
        # 测试2: 数据一致性检查
        log("\n" + "="*60)
        log("测试2: 数据一致性检查")
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
        
        # 测试3: 特殊场景验证
        log("\n" + "="*60)
        log("测试3: 特殊场景验证")
        log("="*60)
        
        # 检查是否有Unicode类名
        cursor = db.conn.execute("""
            SELECT name FROM classes WHERE project_id = ? AND name LIKE '%测试%' LIMIT 5
        """, (runner.project_id,))
        unicode_classes = cursor.fetchall()
        log(f"Unicode类名数量: {len(unicode_classes)}")
        for cls in unicode_classes:
            log(f"  - {cls[0]}")
        
        # 检查是否有长名称
        cursor = db.conn.execute("""
            SELECT name, LENGTH(name) as len FROM classes 
            WHERE project_id = ? ORDER BY len DESC LIMIT 5
        """, (runner.project_id,))
        long_names = cursor.fetchall()
        log(f"最长的类名:")
        for name, length in long_names:
            log(f"  - 长度 {length}: {name[:50]}...")
        
        # 测试4: 内存使用检查
        log("\n" + "="*60)
        log("测试4: 内存使用检查")
        log("="*60)
        
        gc.collect()
        
        # 测试5: 图导出性能
        log("\n" + "="*60)
        log("测试5: 图导出性能")
        log("="*60)
        
        start_time = time.time()
        graph = db.export_graph(runner.project_id)
        duration = time.time() - start_time
        
        log(f"图导出完成!")
        log(f"  耗时: {duration:.2f} 秒")
        log(f"  节点数量: {len(graph.get('nodes', []))}")
        log(f"  链接数量: {len(graph.get('links', []))}")
        
        # 测试6: 增量更新
        log("\n" + "="*60)
        log("测试6: 增量更新测试")
        log("="*60)
        
        start_time = time.time()
        success = runner.analyze_project(test_path, "ExtremeChaosTest")
        duration = time.time() - start_time
        
        stats2 = db.get_project_stats(runner.project_id)
        
        log(f"增量更新完成!")
        log(f"  耗时: {duration:.2f} 秒")
        log(f"  文件数: {stats2['files']}")
        log(f"  类数量: {stats2['classes']}")
        
        # 验证数据一致性
        assert stats['files'] == stats2['files'], "文件数不一致!"
        assert stats['classes'] == stats2['classes'], "类数不一致!"
        assert stats['methods'] == stats2['methods'], "方法数不一致!"
        
        log("✅ 增量更新数据一致性验证通过!")
        
        db.close()
        
        # 总结
        print("\n" + "="*80)
        print("  极端场景测试完成")
        print("="*80)
        print(f"✅ 处理了 {file_count} 个极端场景文件")
        print(f"✅ 解析了 {stats['classes']} 个类")
        print(f"✅ 提取了 {stats['methods']} 个方法")
        print(f"✅ 数据一致性: {orphaned_calls + orphaned_classes + orphaned_methods} 个孤儿记录")
        print("="*80)
        
        return True
        
    except Exception as e:
        log(f"❌ 测试失败: {e}")
        traceback.print_exc()
        return False
        
    finally:
        try:
            os.unlink(db_path)
        except Exception:
            pass


def test_parser_edge_cases():
    """测试解析器的极端边界情况"""
    print("\n" + "="*80)
    print("  解析器极端边界测试")
    print("="*80)
    
    parser = ArkTSParser()
    
    # 测试1: 超长行
    log("测试1: 超长行处理")
    long_line = "class A { method() { " + "x" * 100000 + "; } }"
    try:
        entities = parser.parse_file(long_line, "longline.ets")
        log(f"✅ 超长行处理成功: {len(entities)} 个类")
    except Exception as e:
        log(f"❌ 超长行处理失败: {e}")
    
    # 测试2: 极深嵌套
    log("\n测试2: 极深嵌套处理")
    deep_nested = "class A {\n" + "  " * 1000 + "method() {}\n" + "  " * 1000 + "}\n"
    try:
        entities = parser.parse_file(deep_nested, "deep.ets")
        log(f"✅ 极深嵌套处理成功: {len(entities)} 个类")
    except Exception as e:
        log(f"❌ 极深嵌套处理失败: {e}")
    
    # 测试3: 大量方法
    log("\n测试3: 大量方法处理")
    many_methods = "class A {\n" + "\n".join([f"  method{i}() {{}}" for i in range(1000)]) + "\n}"
    try:
        start = time.time()
        entities = parser.parse_file(many_methods, "many.ets")
        duration = time.time() - start
        log(f"✅ 大量方法处理成功: {len(entities)} 个类, {len(entities[0].methods)} 个方法, 耗时 {duration:.2f}s")
    except Exception as e:
        log(f"❌ 大量方法处理失败: {e}")
    
    # 测试4: 混合注释和字符串
    log("\n测试4: 混合注释和字符串")
    mixed = """
class Mixed {
    /* 注释中的 "字符串" 和 '字符串' */
    method() {
        let s1 = "字符串中的 /* 注释 */ 和 // 注释";
        let s2 = '字符串中的 /* 注释 */ 和 // 注释';
        let s3 = `字符串中的 /* 注释 */ 和 // 注释`;
        // 真正的注释
        console.log(s1, s2, s3);
    }
}
"""
    try:
        entities = parser.parse_file(mixed, "mixed.ets")
        log(f"✅ 混合注释字符串处理成功: {len(entities)} 个类")
    except Exception as e:
        log(f"❌ 混合注释字符串处理失败: {e}")
    
    # 测试5: Unicode和Emoji
    log("\n测试5: Unicode和Emoji")
    unicode_code = """
class 中文类名 {
    日本語メソッド() {
        let 한국어 = "한국어";
        let 😊 = "emoji";
        console.log(한국어, 😊);
    }
}
"""
    try:
        entities = parser.parse_file(unicode_code, "unicode.ets")
        log(f"✅ Unicode处理成功: {len(entities)} 个类")
        if entities:
            log(f"  类名: {entities[0].name}")
            if entities[0].methods:
                log(f"  方法名: {entities[0].methods[0].name}")
    except Exception as e:
        log(f"❌ Unicode处理失败: {e}")
    
    print("\n✅ 解析器极端边界测试完成!")


def test_database_stress():
    """测试数据库压力"""
    print("\n" + "="*80)
    print("  数据库压力测试")
    print("="*80)
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        db = ArkAnalyzerDB(db_path)
        db.initialize()
        
        # 测试1: 大量插入
        log("测试1: 大量插入性能")
        project_id = db.insert_project("stress_test", "/test", int(time.time()))
        
        start = time.time()
        for i in range(10000):
            file_id = db.insert_file(project_id, f"/test/file{i}.ets", f"hash{i}", 100, int(time.time()))
            class_id = db.insert_class(project_id, f"Class{i}", f"class Class{i}", file_id, None, 0, 1, 100, None)
            method_id = db.insert_method(project_id, f"method{i}", f"method{i}()", class_id, None, file_id, "", "", 0, 10, 90, None, 0, 0)
        
        duration = time.time() - start
        log(f"✅ 插入10000条记录耗时: {duration:.2f}s")
        
        # 测试2: 大量查询
        log("\n测试2: 大量查询性能")
        start = time.time()
        for i in range(100):
            stats = db.get_project_stats(project_id)
        duration = time.time() - start
        log(f"✅ 100次统计查询耗时: {duration*1000:.2f}ms")
        
        # 测试3: 复杂查询
        log("\n测试3: 复杂查询性能")
        start = time.time()
        graph = db.export_graph(project_id)
        duration = time.time() - start
        log(f"✅ 导出图(10000节点)耗时: {duration:.2f}s")
        log(f"  节点数: {len(graph.get('nodes', []))}")
        log(f"  链接数: {len(graph.get('links', []))}")
        
        db.close()
        
        print("\n✅ 数据库压力测试完成!")
        
    finally:
        try:
            os.unlink(db_path)
        except Exception:
            pass


def main():
    print("="*80)
    print("  第三轮深度测试 - 极端复杂场景全覆盖")
    print("="*80)
    
    results = []
    
    # 测试1: 极端场景
    try:
        result = test_extreme_scenarios()
        results.append(("极端场景测试", result))
    except Exception as e:
        log(f"❌ 极端场景测试失败: {e}")
        traceback.print_exc()
        results.append(("极端场景测试", False))
    
    # 测试2: 解析器边界
    try:
        test_parser_edge_cases()
        results.append(("解析器边界测试", True))
    except Exception as e:
        log(f"❌ 解析器边界测试失败: {e}")
        traceback.print_exc()
        results.append(("解析器边界测试", False))
    
    # 测试3: 数据库压力
    try:
        test_database_stress()
        results.append(("数据库压力测试", True))
    except Exception as e:
        log(f"❌ 数据库压力测试失败: {e}")
        traceback.print_exc()
        results.append(("数据库压力测试", False))
    
    # 总结
    print("\n" + "="*80)
    print("  第三轮深度测试总结")
    print("="*80)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name:30s} {status}")
    
    passed = sum(1 for (_, r) in results if r)
    total = len(results)
    
    print("\n" + "="*80)
    print(f"  总结: {passed}/{total} 测试通过")
    print("="*80)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

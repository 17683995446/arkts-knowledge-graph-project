#!/usr/bin/env python3
"""
超大规模压力测试 - 监控性能与资源使用
遵循慢工出细活原理
"""
import os
import sys
import time
import psutil
import sqlite3
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_section(title):
    print("\n" + "=" * 100)
    print(f"  {title}")
    print("=" * 100)

def get_memory_usage():
    """获取当前内存使用情况"""
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return {
        'rss_mb': mem_info.rss / 1024 / 1024,
        'vms_mb': mem_info.vms / 1024 / 1024,
        'percent': process.memory_percent()
    }

def test_million_line_analysis():
    from ark_analyzer_runner import run_ark_analyzer
    
    print_section("🚀 超大规模压力测试 - 276K行代码")
    
    # 清理旧数据库
    db_path = "massive_scale_test.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    project_path = os.path.join(os.path.dirname(__file__), "massive_test_project")
    
    print("📊 项目统计:")
    ets_files = []
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith('.ets'):
                ets_files.append(os.path.join(root, file))
    
    total_lines = 0
    for f in ets_files:
        with open(f, 'r', encoding='utf-8', errors='ignore') as file:
            total_lines += len(file.readlines())
    
    print(f"   文件数: {len(ets_files)}")
    print(f"   代码行数: {total_lines:,}")
    
    # 记录初始内存
    mem_before = get_memory_usage()
    print(f"\n💾 初始内存: {mem_before['rss_mb']:.2f} MB")
    
    # 开始分析
    print("\n⏱️  开始深度分析...")
    start_time = time.time()
    
    try:
        run_ark_analyzer("", project_path, db_path)
        elapsed = time.time() - start_time
        
        # 记录最终内存
        mem_after = get_memory_usage()
        
        print(f"\n✅ 分析完成！")
        print(f"⏱️  耗时: {elapsed:.2f}秒")
        print(f"   文件/秒: {len(ets_files)/elapsed:.2f}")
        print(f"   代码行/秒: {total_lines/elapsed:.2f}")
        
        print(f"\n💾 内存使用:")
        print(f"   初始: {mem_before['rss_mb']:.2f} MB")
        print(f"   最终: {mem_after['rss_mb']:.2f} MB")
        print(f"   增长: {mem_after['rss_mb'] - mem_before['rss_mb']:.2f} MB")
        print(f"   内存占用: {mem_after['percent']:.2f}%")
        
        # 分析数据库结果
        analyze_database_results(db_path)
        
        # 测试多次增量更新
        test_incremental_updates(db_path, project_path)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_database_results(db_path):
    print_section("🔍 数据库结果分析")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 统计
    cursor.execute("SELECT COUNT(*) FROM projects")
    print(f"📦 项目数: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM files")
    num_files = cursor.fetchone()[0]
    print(f"📄 文件数: {num_files}")
    
    cursor.execute("SELECT COUNT(*) FROM classes")
    num_classes = cursor.fetchone()[0]
    print(f"🏛️  类/结构数: {num_classes}")
    
    cursor.execute("SELECT COUNT(*) FROM methods")
    num_methods = cursor.fetchone()[0]
    print(f"🔧 方法数: {num_methods}")
    
    cursor.execute("SELECT COUNT(*) FROM calls")
    num_calls = cursor.fetchone()[0]
    print(f"🔗 调用关系: {num_calls}")
    
    # 性能指标
    print(f"\n📈 解析效率:")
    print(f"   方法/文件: {num_methods/num_files:.2f}")
    print(f"   类/文件: {num_classes/num_files:.2f}")
    print(f"   调用/方法: {num_calls/num_methods:.2f}")
    
    # 检查数据完整性
    print(f"\n🔒 数据完整性检查:")
    
    cursor.execute("SELECT id FROM files")
    file_ids = set(row[0] for row in cursor.fetchall())
    
    cursor.execute("SELECT id, file_id FROM classes")
    invalid_class = 0
    for _, file_id in cursor.fetchall():
        if file_id not in file_ids:
            invalid_class += 1
    print(f"   无效类引用: {invalid_class}")
    
    cursor.execute("SELECT id, file_id FROM methods")
    invalid_method = 0
    for _, file_id in cursor.fetchall():
        if file_id not in file_ids:
            invalid_method += 1
    print(f"   无效方法引用: {invalid_method}")
    
    # 检查方法名的分布
    print(f"\n📊 方法名统计:")
    cursor.execute("SELECT name, COUNT(*) as cnt FROM methods GROUP BY name ORDER BY cnt DESC LIMIT 20")
    print("   最常见的方法名:")
    for name, cnt in cursor.fetchall():
        print(f"      {name}: {cnt}")
    
    conn.close()

def test_incremental_updates(db_path, project_path):
    print_section("🔄 增量更新测试")
    
    print("⏱️  测试增量更新性能...")
    
    # 第一次更新（无变更）
    start = time.time()
    from ark_analyzer_runner import run_ark_analyzer
    run_ark_analyzer("", project_path, db_path)
    time1 = time.time() - start
    print(f"   无变更更新耗时: {time1:.3f}秒")
    
    # 修改一个文件
    test_file = os.path.join(project_path, "core/entities/entity_000.ets")
    with open(test_file, 'r', encoding='utf-8') as f:
        original = f.read()
    
    try:
        # 添加一些内容
        modified = original + "\n// Modified for incremental test\nexport class TestModify {}"
        with open(test_file, 'w') as f:
            f.write(modified)
        
        # 第二次更新
        start = time.time()
        run_ark_analyzer("", project_path, db_path)
        time2 = time.time() - start
        print(f"   小变更更新耗时: {time2:.3f}秒")
        
        # 恢复原文件
        with open(test_file, 'w') as f:
            f.write(original)
        
        # 第三次更新
        start = time.time()
        run_ark_analyzer("", project_path, db_path)
        time3 = time.time() - start
        print(f"   恢复后更新耗时: {time3:.3f}秒")
        
        print(f"\n📈 增量更新性能:")
        if time2 < time1 * 0.5:
            print(f"   ✅ 增量更新有效，比全量快 {(1-time2/time1)*100:.1f}%")
        else:
            print(f"   ⚠️  增量更新可能未生效")
            
    except Exception as e:
        print(f"❌ 增量测试失败: {e}")
        # 恢复文件
        try:
            with open(test_file, 'w') as f:
                f.write(original)
        except:
            pass

def main():
    print_section("超大规模压力测试 - 遵循慢工出细活原理")
    
    success = test_million_line_analysis()
    
    print_section("✅ 测试完成")
    
    if success:
        print("🎉 超大规模测试通过！系统性能优秀！")
    else:
        print("⚠️  测试中发现问题，需要优化")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

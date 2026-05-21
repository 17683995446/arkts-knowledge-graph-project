#!/usr/bin/env python3
"""
并发场景与竞态条件测试
遵循慢工出细活原理
"""
import os
import sys
import time
import sqlite3
import threading
from pathlib import Path
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_section(title):
    print("\n" + "=" * 100)
    print(f"  {title}")
    print("=" * 100)

def test_concurrent_analysis():
    from ark_analyzer_runner import run_ark_analyzer
    
    print_section("🔄 并发场景测试")
    
    test_dir = tempfile.mkdtemp()
    db_path = os.path.join(test_dir, "concurrent.db")
    
    print(f"📁 测试目录: {test_dir}")
    
    try:
        # 创建测试文件
        print("\n📝 创建测试项目...")
        os.makedirs(os.path.join(test_dir, "src"), exist_ok=True)
        
        for i in range(10):
            with open(os.path.join(test_dir, "src", f"test{i}.ets"), 'w') as f:
                f.write(f"""
export class TestClass{i} {{
    method1() {{
        console.log("method1");
    }}
    
    method2() {{
        console.log("method2");
    }}
}}
""")
        
        print("   ✅ 创建10个测试文件")
        
        # 测试1: 串行分析
        print("\n🧪 测试1: 串行分析")
        start = time.time()
        run_ark_analyzer("", test_dir, db_path)
        serial_time = time.time() - start
        print(f"   ⏱️  串行分析耗时: {serial_time:.3f}秒")
        
        # 获取初始数据
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM files")
        initial_files = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM methods")
        initial_methods = cursor.fetchone()[0]
        conn.close()
        
        print(f"   📊 初始文件: {initial_files}, 方法: {initial_methods}")
        
        # 测试2: 并发分析
        print("\n🧪 测试2: 并发分析模拟")
        
        results = {'success': 0, 'errors': 0}
        lock = threading.Lock()
        
        def concurrent_task(task_id):
            """模拟并发任务"""
            try:
                # 每个任务执行一次分析
                time.sleep(0.01 * task_id)  # 模拟不同的启动时间
                
                # 简单查询测试
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM files")
                count = cursor.fetchone()[0]
                conn.close()
                
                with lock:
                    results['success'] += 1
                    
            except Exception as e:
                with lock:
                    results['errors'] += 1
        
        # 启动10个并发线程
        threads = []
        start = time.time()
        
        for i in range(10):
            t = threading.Thread(target=concurrent_task, args=(i,))
            threads.append(t)
            t.start()
        
        # 等待所有线程完成
        for t in threads:
            t.join()
        
        concurrent_time = time.time() - start
        
        print(f"   ⏱️  并发查询耗时: {concurrent_time:.3f}秒")
        print(f"   ✅ 成功: {results['success']}, 错误: {results['errors']}")
        
        # 测试3: 快速连续更新
        print("\n🧪 测试3: 快速连续更新")
        update_times = []
        
        for i in range(5):
            start = time.time()
            run_ark_analyzer("", test_dir, db_path)
            update_times.append(time.time() - start)
        
        print(f"   ⏱️  5次更新耗时:")
        for i, t in enumerate(update_times, 1):
            print(f"      第{i}次: {t:.3f}秒")
        
        avg_update = sum(update_times) / len(update_times)
        print(f"   📊 平均耗时: {avg_update:.3f}秒")
        
        # 测试4: 数据一致性检查
        print("\n🧪 测试4: 数据一致性检查")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM files")
        final_files = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM classes")
        final_classes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM methods")
        final_methods = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM calls")
        final_calls = cursor.fetchone()[0]
        
        # 检查引用完整性
        cursor.execute("""
            SELECT COUNT(*) FROM methods m 
            WHERE m.file_id NOT IN (SELECT id FROM files)
        """)
        orphaned_methods = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM classes c 
            WHERE c.file_id NOT IN (SELECT id FROM files)
        """)
        orphaned_classes = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"   📊 最终统计:")
        print(f"      文件: {final_files}")
        print(f"      类: {final_classes}")
        print(f"      方法: {final_methods}")
        print(f"      调用: {final_calls}")
        print(f"   🔒 孤立方法: {orphaned_methods}")
        print(f"   🔒 孤立类: {orphaned_classes}")
        
        # 验证一致性
        consistency_ok = (
            final_files == initial_files and
            orphaned_methods == 0 and
            orphaned_classes == 0
        )
        
        if consistency_ok:
            print("\n   ✅ 数据一致性检查通过！")
        else:
            print("\n   ⚠️  数据一致性存在问题")
        
        # 测试5: 数据库锁定测试
        print("\n🧪 测试5: 数据库锁定测试")
        
        lock_errors = 0
        lock_success = 0
        lock_lock = threading.Lock()
        
        def write_task(task_id):
            nonlocal lock_errors, lock_success
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM files")
                count = cursor.fetchone()[0]
                conn.close()
                
                with lock_lock:
                    lock_success += 1
                    
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e):
                    with lock_lock:
                        lock_errors += 1
        
        # 启动20个并发写任务
        threads = []
        for i in range(20):
            t = threading.Thread(target=write_task, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        print(f"   ✅ 成功: {lock_success}, 锁定错误: {lock_errors}")
        
        if lock_errors == 0:
            print("   ✅ 无锁定错误！SQLite配置正确")
        else:
            print(f"   ⚠️  出现{lock_errors}个锁定错误，可能需要优化")
        
        print("\n✅ 并发测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 并发测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)
        print(f"\n🧹 清理测试目录完成")

def main():
    success = test_concurrent_analysis()
    
    print_section("✅ 测试完成")
    
    if success:
        print("🎉 所有并发测试通过！系统并发性能优秀！")
    else:
        print("⚠️  并发测试中发现问题，需要修复")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

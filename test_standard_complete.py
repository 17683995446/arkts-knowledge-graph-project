#!/usr/bin/env python3
"""标准化全流程测试 - 包含所有要求的测试步骤"""

import sys
import os
import time
import tempfile
import shutil
import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Any

from parser import ArkTSParser
from ark_analyzer_db import ArkAnalyzerDB
from ark_analyzer_runner import ArkAnalyzerRunner

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('StandardCompleteTest')


def test_module_integration() -> bool:
    """模块集成联调测试"""
    logger.info("=" * 80)
    logger.info("开始模块集成联调测试")
    logger.info("=" * 80)
    
    try:
        test_dir = tempfile.mkdtemp(prefix="integration_test_")
        logger.info(f"创建测试目录: {test_dir}")
        
        file1 = os.path.join(test_dir, "TestFile1.ets")
        file2 = os.path.join(test_dir, "TestFile2.ets")
        
        with open(file1, "w", encoding="utf-8") as f:
            f.write("""@Entry
@Component
struct IndexPage {
    build() {
        Column() {
            Text("Hello World");
            this.showMessage();
        }
    }
    
    showMessage() {
        console.log("Showing message");
    }
}

class Utils {
    static formatDate(date: string) {
        return date;
    }
}
""")
        
        with open(file2, "w", encoding="utf-8") as f:
            f.write("""class DataManager {
    saveData(data: any) {
        this.validateData(data);
        console.log("Data saved");
    }
    
    validateData(data: any) {
        return true;
    }
}

function globalHelper() {
    return "helper";
}
""")
        
        db_path = os.path.join(test_dir, "test.db")
        db = ArkAnalyzerDB(db_path)
        db.initialize()
        
        runner = ArkAnalyzerRunner("", db)
        
        result = runner.analyze_project(test_dir, "TestProject", incremental=False)
        
        if result:
            stats = db.get_project_stats(runner.project_id)
            logger.info(f"集成测试结果: {stats}")
            
            if (stats['files'] == 2 and 
                stats['classes'] >= 3 and 
                stats['methods'] >= 4):
                logger.info("✅ 模块集成联调测试通过")
                return True
        
        logger.error("❌ 模块集成联调测试失败")
        return False
        
    except Exception as e:
        logger.error(f"❌ 模块集成联调测试异常: {e}", exc_info=True)
        return False
    finally:
        try:
            db.close()
            shutil.rmtree(test_dir, ignore_errors=True)
        except:
            pass


def test_interface_traversal() -> bool:
    """接口全量遍历测试"""
    logger.info("=" * 80)
    logger.info("开始接口全量遍历测试")
    logger.info("=" * 80)
    
    try:
        db = ArkAnalyzerDB(":memory:")
        db.initialize()
        
        project_id = db.insert_project("InterfaceTest", "/test", int(time.time()))
        
        file_id = db.insert_file(project_id, "/test/file.ets", "hash1", 100, int(time.time()))
        
        class_id = db.insert_class(project_id, "TestClass", "class TestClass", file_id, None, 0, 1, 20, None)
        
        method_id = db.insert_method(project_id, "testMethod", "testMethod()", class_id, None, file_id, "param", "void", 0, 5, 10, None, 0, 0)
        
        db.insert_call(project_id, method_id, "otherMethod", None, None, "call")
        
        class_result = db.query_class(project_id, "TestClass")
        methods_result = db.query_methods_by_class(class_id)
        stats = db.get_project_stats(project_id)
        
        callers = db.query_callers(method_id)
        callees = db.query_callees(method_id)
        
        graph = db.export_graph(project_id)
        
        if (class_result and 
            methods_result is not None and 
            stats and 
            callers is not None and 
            callees is not None and 
            graph):
            logger.info("✅ 接口全量遍历测试通过")
            return True
        
        logger.error("❌ 接口全量遍历测试失败")
        return False
        
    except Exception as e:
        logger.error(f"❌ 接口全量遍历测试异常: {e}", exc_info=True)
        return False
    finally:
        db.close()


def test_business_scenario() -> bool:
    """业务场景闭环测试"""
    logger.info("=" * 80)
    logger.info("开始业务场景闭环测试")
    logger.info("=" * 80)
    
    try:
        test_dir = tempfile.mkdtemp(prefix="business_test_")
        
        for i in range(3):
            file_path = os.path.join(test_dir, f"Component{i}.ets")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"""@Component
struct Component{i} {{
    build() {{
        Text("Component {i}");
    }}
    
    doSomething() {{
        console.log("Component {i} doing something");
    }}
}}

class Service{i} {{
    process() {{
        console.log("Service {i} processing");
    }}
}}
""")
        
        db = ArkAnalyzerDB(":memory:")
        db.initialize()
        runner = ArkAnalyzerRunner("", db)
        
        result1 = runner.analyze_project(test_dir, "BusinessTest", incremental=False)
        
        if not result1:
            logger.error("第一次分析失败")
            return False
        
        stats1 = db.get_project_stats(runner.project_id)
        logger.info(f"第一次分析统计: {stats1}")
        
        time.sleep(0.1)
        
        file_to_modify = os.path.join(test_dir, "Component0.ets")
        with open(file_to_modify, "w", encoding="utf-8") as f:
            f.write("""@Component
struct Component0 {
    build() {
        Text("Component 0 Modified");
    }
    
    doSomething() {
        console.log("Component 0 doing something");
    }
    
    newMethod() {
        console.log("New method added");
    }
}

class Service0 {
    process() {
        console.log("Service 0 processing");
    }
}
""")
        
        result2 = runner.analyze_project(test_dir, "BusinessTest", incremental=True)
        
        if not result2:
            logger.error("第二次分析失败")
            return False
        
        stats2 = db.get_project_stats(runner.project_id)
        logger.info(f"第二次分析统计: {stats2}")
        
        if (stats1['files'] == 3 and 
            stats2['files'] == 3 and 
            stats1['classes'] > 0 and 
            stats2['classes'] > 0):
            logger.info("✅ 业务场景闭环测试通过")
            return True
        
        logger.error("❌ 业务场景闭环测试失败")
        return False
        
    except Exception as e:
        logger.error(f"❌ 业务场景闭环测试异常: {e}", exc_info=True)
        return False
    finally:
        try:
            db.close()
            shutil.rmtree(test_dir, ignore_errors=True)
        except:
            pass


def test_data_consistency() -> bool:
    """数据一致性校验"""
    logger.info("=" * 80)
    logger.info("开始数据一致性校验测试")
    logger.info("=" * 80)
    
    try:
        db = ArkAnalyzerDB(":memory:")
        db.initialize()
        
        content = """class TestClass {
    method1() {
        this.method2();
    }
    
    method2() {}
}"""
        
        parser = ArkTSParser()
        entities = parser.parse_file(content, "/test/consistency.ets")
        
        project_id = db.insert_project("ConsistencyTest", "/test", int(time.time()))
        file_id = db.insert_file(project_id, "/test/consistency.ets", "hash", 10, int(time.time()))
        
        class_id = db.insert_class(project_id, entities[0].name, "class", file_id, None, entities[0].flags, 
                                    entities[0].start_line, entities[0].end_line, None)
        
        method_ids = []
        for method in entities[0].methods:
            m_id = db.insert_method(project_id, method.name, f"{method.name}()", class_id, 
                                   None, file_id, method.params, method.return_type, 0,
                                   method.start_line, method.end_line, None, 0, 1 if method.is_static else 0)
            method_ids.append(m_id)
            
            for call in method.calls:
                db.insert_call(project_id, m_id, call, None, None, "call")
        
        stats = db.get_project_stats(project_id)
        
        class_methods = db.query_methods_by_class(class_id)
        
        all_projects = db.get_all_projects()
        
        if (stats['files'] == 1 and
            stats['classes'] == 1 and
            stats['methods'] == len(entities[0].methods) and
            len(class_methods) == len(entities[0].methods) and
            len(all_projects) >= 1):
            logger.info("✅ 数据一致性校验测试通过")
            return True
        
        logger.error("❌ 数据一致性校验测试失败")
        return False
        
    except Exception as e:
        logger.error(f"❌ 数据一致性校验测试异常: {e}", exc_info=True)
        return False
    finally:
        db.close()


def test_exception_handling() -> bool:
    """异常容错测试"""
    logger.info("=" * 80)
    logger.info("开始异常容错测试")
    logger.info("=" * 80)
    
    try:
        parser = ArkTSParser()
        
        invalid_code = "class TestClass {"
        try:
            result = parser.parse_file(invalid_code, "/test/invalid.ets")
            logger.info(f"无效代码解析测试: 解析了 {len(result)} 个实体")
        except Exception as e:
            logger.error(f"无效代码解析抛出异常: {e}")
            return False
        
        empty_code = ""
        try:
            result = parser.parse_file(empty_code, "/test/empty.ets")
            logger.info(f"空代码解析测试: 解析了 {len(result)} 个实体")
        except Exception as e:
            logger.error(f"空代码解析抛出异常: {e}")
            return False
        
        weird_code = "@#$%^&*()_+{}[]|;':\",./<>?"
        try:
            result = parser.parse_file(weird_code, "/test/weird.ets")
            logger.info(f"奇异代码解析测试: 解析了 {len(result)} 个实体")
        except Exception as e:
            logger.error(f"奇异代码解析抛出异常: {e}")
            return False
        
        try:
            db = ArkAnalyzerDB(":memory:")
            db.initialize()
            
            project_id = db.insert_project("ExceptionTest", "/test", int(time.time()))
            
            db.begin_transaction()
            db.insert_file(project_id, "/test/file.ets", "hash", 10, int(time.time()))
            db.rollback()
            
            db.begin_transaction()
            file_id = db.insert_file(project_id, "/test/file2.ets", "hash2", 20, int(time.time()))
            db.commit()
            
            db.close()
            
        except Exception as e:
            logger.error(f"数据库异常处理测试失败: {e}")
            return False
        
        logger.info("✅ 异常容错测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ 异常容错测试异常: {e}", exc_info=True)
        return False


def test_performance() -> bool:
    """基础性能核验"""
    logger.info("=" * 80)
    logger.info("开始基础性能核验测试")
    logger.info("=" * 80)
    
    try:
        test_dir = tempfile.mkdtemp(prefix="performance_test_")
        
        for i in range(50):
            file_path = os.path.join(test_dir, f"PerfTest{i}.ets")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"""class PerfTest{i} {{
    method1() {{ }}
    method2() {{ }}
    method3() {{ }}
    method4() {{ }}
    method5() {{ }}
}}
""")
        
        logger.info("创建了50个测试文件")
        
        start_time = time.time()
        
        db = ArkAnalyzerDB(":memory:")
        db.initialize()
        runner = ArkAnalyzerRunner("", db)
        
        result = runner.analyze_project(test_dir, "PerfTest", incremental=False)
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        stats = db.get_project_stats(runner.project_id)
        
        logger.info(f"性能测试结果:")
        logger.info(f"  耗时: {elapsed:.3f} 秒")
        logger.info(f"  解析文件数: {stats['files']}")
        logger.info(f"  解析类数: {stats['classes']}")
        logger.info(f"  解析方法数: {stats['methods']}")
        
        if elapsed < 60:
            logger.info("✅ 基础性能核验测试通过")
            return True
        
        logger.error("❌ 基础性能核验测试超时")
        return False
        
    except Exception as e:
        logger.error(f"❌ 基础性能核验测试异常: {e}", exc_info=True)
        return False
    finally:
        try:
            db.close()
            shutil.rmtree(test_dir, ignore_errors=True)
        except:
            pass


def run_all_standard_tests() -> Dict[str, bool]:
    """运行所有标准化测试"""
    results = {}
    
    logger.info("\n" + "=" * 80)
    logger.info("开始运行标准化全流程测试")
    logger.info("=" * 80)
    
    results['module_integration'] = test_module_integration()
    results['interface_traversal'] = test_interface_traversal()
    results['business_scenario'] = test_business_scenario()
    results['data_consistency'] = test_data_consistency()
    results['exception_handling'] = test_exception_handling()
    results['performance'] = test_performance()
    
    return results


if __name__ == '__main__':
    results = run_all_standard_tests()
    
    logger.info("\n" + "=" * 80)
    logger.info("测试结果汇总")
    logger.info("=" * 80)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        logger.info(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    logger.info("=" * 80)
    
    if all_passed:
        logger.info("✅ 所有标准化全流程测试通过！")
        sys.exit(0)
    else:
        logger.error("❌ 部分标准化全流程测试失败！")
        sys.exit(1)

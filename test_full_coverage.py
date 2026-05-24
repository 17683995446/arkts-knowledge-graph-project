#!/usr/bin/env python3
"""单元全覆盖测试 - 测试所有分支和边界情况"""

import sys
import os
import tempfile
import unittest
from parser import ArkTSParser
from ark_analyzer_db import ArkAnalyzerDB


class TestParserEdgeCases(unittest.TestCase):
    """测试解析器的边界情况"""

    def setUp(self):
        self.parser = ArkTSParser()

    def test_empty_file(self):
        """测试空文件"""
        result = self.parser.parse_file("", "/test/empty.ets")
        self.assertEqual(len(result), 0)
        logger.info("✓ 空文件测试通过")

    def test_only_whitespace(self):
        """测试只有空白字符"""
        result = self.parser.parse_file("   \n  \t  ", "/test/whitespace.ets")
        self.assertEqual(len(result), 0)
        logger.info("✓ 只有空白字符测试通过")

    def test_only_comments(self):
        """测试只有注释"""
        content = """
// 这是单行注释
/* 这是多行
注释 */
"""
        result = self.parser.parse_file(content, "/test/comments.ets")
        self.assertEqual(len(result), 0)
        logger.info("✓ 只有注释测试通过")

    def test_empty_class(self):
        """测试空类"""
        content = "class EmptyClass {}"
        result = self.parser.parse_file(content, "/test/empty_class.ets")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "EmptyClass")
        self.assertEqual(len(result[0].methods), 0)
        logger.info("✓ 空类测试通过")

    def test_empty_struct(self):
        """测试空结构体"""
        content = "struct EmptyStruct {}"
        result = self.parser.parse_file(content, "/test/empty_struct.ets")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "EmptyStruct")
        logger.info("✓ 空结构体测试通过")

    def test_simple_class(self):
        """测试简单类"""
        content = """
class SimpleClass {
    method1() {
        console.log("hello");
    }

    method2(param: string) {
        return param;
    }
}
"""
        result = self.parser.parse_file(content, "/test/simple.ets")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "SimpleClass")
        self.assertEqual(len(result[0].methods), 2)
        logger.info("✓ 简单类测试通过")

    def test_multiple_classes(self):
        """测试多个类"""
        content = """
class ClassA {
    methodA() {}
}

class ClassB {
    methodB() {}
}

struct StructC {
    methodC() {}
}
"""
        result = self.parser.parse_file(content, "/test/multiple.ets")
        self.assertEqual(len(result), 3)
        class_names = {c.name for c in result}
        self.assertEqual(class_names, {"ClassA", "ClassB", "StructC"})
        logger.info("✓ 多个类测试通过")

    def test_class_with_decorators(self):
        """测试带装饰器的类"""
        content = """
@Component
@Entry
struct MyComponent {
    build() {}
}

@State
class MyState {
    update() {}
}
"""
        result = self.parser.parse_file(content, "/test/decorators.ets")
        self.assertEqual(len(result), 2)
        logger.info("✓ 带装饰器的类测试通过")

    def test_unicode_identifiers(self):
        """测试Unicode标识符"""
        content = """
class 中文类 {
    中文方法() {}
}

struct 日本語構造体 {
    日本語メソッド() {}
}

function 한국어함수() {}
"""
        result = self.parser.parse_file(content, "/test/unicode.ets")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].name, "中文类")
        self.assertEqual(len(result[0].methods), 1)
        self.assertEqual(result[0].methods[0].name, "中文方法")
        
        functions = self.parser.extract_standalone_functions(content)
        self.assertEqual(len(functions), 1)
        self.assertEqual(functions[0].name, "한국어함수")
        logger.info("✓ Unicode标识符测试通过")

    def test_standalone_functions(self):
        """测试独立函数"""
        content = """
function func1() {}

export function func2(param: number) {
    return param;
}

function 日本語関数() {}
"""
        functions = self.parser.extract_standalone_functions(content)
        self.assertEqual(len(functions), 3)
        function_names = {f.name for f in functions}
        self.assertEqual(function_names, {"func1", "func2", "日本語関数"})
        logger.info("✓ 独立函数测试通过")

    def test_method_calls(self):
        """测试方法调用提取"""
        content = """
class Caller {
    methodA() {
        this.methodB();
        this.methodC();
        this.methodB(); // duplicate call
    }
    
    methodB() {}
    methodC() {}
}
"""
        result = self.parser.parse_file(content, "/test/calls.ets")
        self.assertEqual(len(result), 1)
        method_a = result[0].methods[0]
        self.assertEqual(method_a.name, "methodA")
        # 调用关系应该去重
        self.assertEqual(len(method_a.calls), 2)
        self.assertIn("methodB", method_a.calls)
        self.assertIn("methodC", method_a.calls)
        logger.info("✓ 方法调用测试通过")

    def test_modifiers(self):
        """测试访问修饰符"""
        content = """
class Modifiers {
    public publicMethod() {}
    private privateMethod() {}
    protected protectedMethod() {}
    static staticMethod() {}
    async asyncMethod() {}
}
"""
        result = self.parser.parse_file(content, "/test/modifiers.ets")
        self.assertEqual(len(result), 1)
        logger.info("✓ 访问修饰符测试通过")

    def test_complex_comments(self):
        """测试复杂注释情况"""
        content = """
/* class CommentedOut {
    thisShouldNotBeParsed() {}
} */

class RealClass {
    // 这是方法注释
    realMethod() {
        // 内部注释
        console.log("/* 这不是注释 */");
    }
}
"""
        result = self.parser.parse_file(content, "/test/complex_comments.ets")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "RealClass")
        self.assertEqual(len(result[0].methods), 1)
        self.assertEqual(result[0].methods[0].name, "realMethod")
        logger.info("✓ 复杂注释测试通过")

    def test_skip_keywords(self):
        """测试关键字被正确跳过"""
        content = """
class Test {
    method() {
        if (true) {}
        for (let i = 0; i < 10; i++) {}
        while (true) {}
        return true;
    }
}
"""
        result = self.parser.parse_file(content, "/test/keywords.ets")
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0].methods), 1)
        # 关键字不应该被识别为方法
        self.assertEqual(len(result[0].methods), 1)
        logger.info("✓ 关键字跳过测试通过")


class TestDatabase(unittest.TestCase):
    """测试数据库功能"""

    def setUp(self):
        self.db = ArkAnalyzerDB(":memory:")
        self.db.initialize()

    def tearDown(self):
        self.db.close()

    def test_basic_operations(self):
        """测试基本数据库操作"""
        # 插入项目
        project_id = self.db.insert_project("TestProject", "/test", 1234567890)
        self.assertIsNotNone(project_id)

        # 插入文件
        file_id = self.db.insert_file(project_id, "/test/file.ets", "hash123", 100, 1234567890)
        self.assertIsNotNone(file_id)

        # 插入类
        class_id = self.db.insert_class(project_id, "TestClass", "class TestClass", file_id, None, 0, 1, 10, None)
        self.assertIsNotNone(class_id)

        # 插入方法
        method_id = self.db.insert_method(
            project_id, "testMethod", "testMethod()", class_id, None, file_id,
            "", "", 0, 2, 5, None, 0, 0
        )
        self.assertIsNotNone(method_id)

        # 查询类
        found_class = self.db.query_class(project_id, "TestClass")
        self.assertIsNotNone(found_class)
        self.assertEqual(found_class["name"], "TestClass")

        # 查询统计
        stats = self.db.get_project_stats(project_id)
        self.assertEqual(stats["files"], 1)
        self.assertEqual(stats["classes"], 1)
        self.assertEqual(stats["methods"], 1)
        logger.info("✓ 基本数据库操作测试通过")

    def test_transaction_rollback(self):
        """测试事务回滚"""
        self.db.begin_transaction()
        
        project_id = self.db.insert_project("RollbackTest", "/test", 1234567890)
        self.db.insert_file(project_id, "/test/f.ets", "hash", 10, 1234567890)
        
        self.db.rollback()
        
        # 回滚后应该没有项目
        projects = self.db.get_all_projects()
        self.assertEqual(len(projects), 0)
        logger.info("✓ 事务回滚测试通过")


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def test_full_workflow(self):
        """测试完整工作流程"""
        parser = ArkTSParser()
        db = ArkAnalyzerDB(":memory:")
        db.initialize()
        
        content = """
@Entry
@Component
struct TestComponent {
    build() {
        Column() {
            Text("Hello");
        }
    }
}

class Helper {
    help() {}
}

function globalFunc() {}
"""
        # 解析
        entities = parser.parse_file(content, "/test/workflow.ets")
        functions = parser.extract_standalone_functions(content)
        
        self.assertEqual(len(entities), 2)
        self.assertEqual(len(functions), 1)
        
        db.close()
        logger.info("✓ 完整工作流程测试通过")


def run_tests():
    """运行所有测试"""
    # 设置日志
    import logging
    global logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('FullCoverageTest')
    
    logger.info("=" * 80)
    logger.info("开始单元全覆盖测试")
    logger.info("=" * 80)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestParserEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    logger.info("=" * 80)
    if result.wasSuccessful():
        logger.info("✅ 所有单元全覆盖测试通过！")
        return 0
    else:
        logger.error("❌ 部分测试失败！")
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())

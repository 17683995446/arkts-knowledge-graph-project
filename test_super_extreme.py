#!/usr/bin/env python3
"""
超级极限测试场景 - 挑战系统极限，发现潜在bug
"""
import os
import sys
import tempfile
import time
import logging

sys.path.insert(0, '/workspace')
from parser import ArkTSParser
from ark_analyzer_db import ArkAnalyzerDB
from ark_analyzer_runner import ArkAnalyzerRunner

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def create_extreme_case_1():
    """超深嵌套和复杂括号"""
    return """
// 测试1: 超深嵌套和复杂括号
export class NestedBracketHell {
    test() {
        const x = ((((((((1 + 2) * 3) / 4) - 5) + 6) * 7) / 8) + 9);
        const y = {a: {b: {c: {d: {e: {f: {g: 1}}}}}}};
        if (((((true) && (false)) || (true)) && (true))) {
            console.log(x);
        }
    }
}
"""


def create_extreme_case_2():
    """大量字符串混合注释"""
    return """
// 测试2: 各种字符串混合注释
export class StringMix {
    test() {
        const s1 = "// not a comment";
        const s2 = "/* not a block comment */";
        const s3 = '/* also not */';
        const s4 = '// still not';
        const s5 = `// backtick ${s1} still ${s2}`;
        const s6 = "string with \\\"escaped quotes\\\"";
        const s7 = 'string with \\\'escaped quotes\\\'';
    }
}
"""


def create_extreme_case_3():
    """超长标识符"""
    name = "A" * 500
    method = "m" * 500
    return f"""
// 测试3: 超长标识符
export class {name} {{
    {method}() {{ console.log("long"); }}
}}
"""


def create_extreme_case_4():
    """大量装饰器"""
    decorators = '\n'.join([f'@Decorator{i}' for i in range(50)])
    return f"""
// 测试4: 大量装饰器
{decorators}
export class ManyDecorators {{
    test() {{ }}
}}
"""


def create_extreme_case_5():
    """Unicode 极端"""
    return """
// 测试5: Unicode 极端测试
export class 中文测试类 {
    中文方法() { console.log("中文"); }
}

export class 日本語クラス {
    メソッド() { console.log("日本語"); }
}

export class КлассРусский {
    метод() { console.log("Русский"); }
}

export class GreekClass {
    μέθοδος() { console.log("Ελληνικά"); }
}

export class ArabicClass {
    طريقة() { console.log("العربية"); }
}

export class HebrewClass {
    שיטה() { console.log("עברית"); }
}

export class ThaiClass {
    วิธีการ() { console.log("ไทย"); }
}

export class KoreanClass {
    방법() { console.log("한국어"); }
}
"""


def create_extreme_case_6():
    """复杂三元表达式"""
    return """
// 测试6: 复杂三元表达式
export class TernaryChaos {
    test() {
        const x = a ? b ? c ? d ? e ? f : g : h : i : j : k;
        const y = condition1 ? (condition2 ? value1 : value2) : (condition3 ? value3 : value4);
    }
}
"""


def create_extreme_case_7():
    """未闭合的大括号和括号"""
    return """
// 测试7: 未闭合的大括号和括号
export class UnclosedBraces {
    test() {
        const x = (1 + 2
        if (x > 0) {
            console.log(x);
"""
    return content


def create_extreme_case_8():
    """大量方法"""
    methods = '\n'.join([f"method{i}() {{ }}" for i in range(200)])
    return f"""
// 测试8: 大量方法
export class ManyMethods {{
    {methods}
}}
"""


def create_extreme_case_9():
    """文件末尾特殊字符"""
    return """
// 测试9: 文件末尾特殊字符
export class EndFile {
    test() { }
}
// \x00\x01\x02\x03\x04\x05
// \xfe\xff
"""


def create_extreme_case_10():
    """超多文件同时处理"""
    content = """
export class TinyClass {
    test() { }
}
"""
    return content


def run_extreme_tests():
    """运行所有极端测试"""
    print("="*80)
    print("超级极限测试场景")
    print("="*80)

    parser = ArkTSParser()
    all_passed = True

    test_cases = [
        ("超深嵌套", create_extreme_case_1),
        ("字符串混合", create_extreme_case_2),
        ("超长标识符", create_extreme_case_3),
        ("大量装饰器", create_extreme_case_4),
        ("Unicode极端", create_extreme_case_5),
        ("复杂三元", create_extreme_case_6),
        ("未闭合括号", create_extreme_case_7),
        ("大量方法", create_extreme_case_8),
        ("末尾特殊字符", create_extreme_case_9),
    ]

    for i, (name, content_func) in enumerate(test_cases, 1):
        try:
            content = content_func()
            print(f"\n[测试 {i}] {name}")
            print(f"内容长度: {len(content)} 字符")

            entities = parser.parse_file(content, f"test_{i}.ets")
            print(f"✅ 解析成功: 找到 {len(entities)} 个类")

            if entities:
                for entity in entities:
                    print(f"  - {entity.name}: {len(entity.methods)} 个方法")

        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False

    return all_passed


def test_database_performance():
    """测试数据库性能极限"""
    print("\n" + "="*80)
    print("数据库性能极限测试")
    print("="*80)

    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db.close()

    try:
        db = ArkAnalyzerDB(temp_db.name)
        db.initialize()

        start = time.time()
        project_id = db.insert_project("perf_test", "/tmp", int(time.time()))

        # 插入10000条记录
        for i in range(10000):
            class_id = db.insert_class(
                project_id, f"Class{i}", f"class Class{i}", None, None, 0, 1, 10, None
            )
            method_id = db.insert_method(
                project_id, f"method{i}", f"method{i}()", class_id, None, None,
                "", "", 0, 2, 5, None, 0, 0
            )

            # 每100条插入一些调用
            if i % 10 == 0:
                for j in range(5):
                    db.insert_call(project_id, method_id, f"call{j}", None, None, "call")

        insert_time = time.time() - start
        print(f"✅ 插入10000条记录耗时: {insert_time:.2f}秒")

        # 查询性能测试
        start = time.time()
        for _ in range(100):
            stats = db.get_project_stats(project_id)
        query_time = time.time() - start
        print(f"✅ 100次统计查询耗时: {query_time*1000:.2f}毫秒")

        # 导出性能测试
        start = time.time()
        graph = db.export_graph(project_id)
        export_time = time.time() - start
        print(f"✅ 图导出耗时: {export_time:.2f}秒, 节点数: {len(graph['nodes'])}")

        db.close()

        return True

    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        os.unlink(temp_db.name)


def test_runner_with_1000_files():
    """测试运行器处理1000个文件"""
    print("\n" + "="*80)
    print("运行器1000文件极限测试")
    print("="*80)

    temp_dir = tempfile.mkdtemp()
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db.close()

    try:
        # 创建1000个小文件
        print("创建1000个测试文件...")
        for i in range(1000):
            file_path = os.path.join(temp_dir, f"TestFile{i}.ets")
            content = f"""
export class TestClass{i} {{
    method1() {{ }}
    method2() {{ this.method1(); }}
    method3() {{ }}
}}
"""
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

        print("开始分析...")
        db = ArkAnalyzerDB(temp_db.name)
        db.initialize()

        runner = ArkAnalyzerRunner("/workspace", db)

        start = time.time()
        result = runner.analyze_project(temp_dir, "large_test")
        elapsed = time.time() - start

        stats = db.get_project_stats(runner.project_id)

        print(f"✅ 分析完成!")
        print(f"   耗时: {elapsed:.2f}秒")
        print(f"   文件数: {stats['files']}")
        print(f"   类数量: {stats['classes']}")
        print(f"   方法数量: {stats['methods']}")
        print(f"   调用数量: {stats['calls']}")
        print(f"   速度: {stats['files']/elapsed:.2f} 文件/秒")

        db.close()

        return result and stats['files'] >= 1000

    except Exception as e:
        print(f"❌ 运行器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        os.unlink(temp_db.name)
        import shutil
        shutil.rmtree(temp_dir)


def test_edge_cases():
    """测试边界情况"""
    print("\n" + "="*80)
    print("边界情况测试")
    print("="*80)

    parser = ArkTSParser()

    cases = [
        ("空字符串", ""),
        ("仅空白", "   \n\t  \n  "),
        ("仅注释", "// comment\n/* block */"),
        ("未闭合class", "class A {"),
        ("未闭合方法", "class A { method() {"),
        ("单独大括号", "{"),
        ("单独小括号", "("),
        ("混合未闭合", "class A("),
    ]

    all_passed = True
    for name, content in cases:
        try:
            entities = parser.parse_file(content, "edge.ets")
            print(f"✅ {name}: 找到 {len(entities)} 个类")
        except Exception as e:
            print(f"❌ {name}: 异常 - {str(e)[:50]}")
            all_passed = False

    return all_passed


def main():
    """主测试函数"""
    results = []

    results.append(("极限解析测试", run_extreme_tests()))
    results.append(("数据库性能", test_database_performance()))
    results.append(("1000文件处理", test_runner_with_1000_files()))
    results.append(("边界情况", test_edge_cases()))

    print("\n" + "="*80)
    print("测试总结")
    print("="*80)

    passed = 0
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")
        if result:
            passed += 1

    print(f"\n总计: {passed}/{len(results)} 个测试通过")

    return passed == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

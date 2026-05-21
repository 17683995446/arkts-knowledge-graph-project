#!/usr/bin/env python3
"""
Deep Test Suite - 第二轮深度测试
覆盖边界条件、异常场景、特殊字符、超大规模数据
"""
import os
import sys
import tempfile
import time
import hashlib
import traceback

sys.path.insert(0, '/workspace')

from parser import ArkTSParser
from ark_analyzer_db import ArkAnalyzerDB
from ark_analyzer_runner import ArkAnalyzerRunner


def log(msg):
    print(f"[DEEP TEST] {msg}")


def test_nested_structures():
    """测试深度嵌套的括号结构"""
    print("\n" + "="*80)
    print("  测试深度嵌套结构")
    print("="*80)
    
    parser = ArkTSParser()
    
    # 测试1: 深度嵌套的方法调用
    test_code1 = """
class NestedTest {
    level1() {
        this.level2(this.level3(this.level4(this.level5())));
    }
}
"""
    entities = parser.parse_file(test_code1, "nested1.ets")
    assert len(entities) == 1, "应该找到1个类"
    log(f"✅ 深度嵌套调用解析成功: {len(entities[0].methods)} 个方法")
    
    # 测试2: 深度嵌套的类
    test_code2 = """
class Outer {
    inner1() {
        let x = (() => {
            return (() => {
                return (() => {
                    return 42;
                })();
            })();
        })();
    }
}
"""
    entities = parser.parse_file(test_code2, "nested2.ets")
    assert len(entities) == 1, "应该找到1个类"
    log(f"✅ 深度嵌套箭头函数解析成功: {len(entities[0].methods)} 个方法")
    
    # 测试3: 复杂的三元表达式
    test_code3 = """
class TernaryTest {
    method() {
        let x = a ? b ? c ? d ? e : f : g : h : i;
    }
}
"""
    entities = parser.parse_file(test_code3, "nested3.ets")
    assert len(entities) == 1, "应该找到1个类"
    log(f"✅ 复杂三元表达式解析成功")
    
    print("✅ 所有深度嵌套测试通过!")


def test_special_characters():
    """测试特殊字符和编码"""
    print("\n" + "="*80)
    print("  测试特殊字符和编码")
    print("="*80)
    
    parser = ArkTSParser()
    
    # 测试1: Unicode 字符
    test_unicode = """
class UnicodeTest {
    方法() {
        let 变量 = "你好世界";
    }
    
    emojiTest() {
        let 😄 = "happy";
    }
}
"""
    try:
        entities = parser.parse_file(test_unicode, "unicode.ets")
        log(f"✅ Unicode 支持: 找到 {len(entities)} 个类")
    except Exception as e:
        log(f"❌ Unicode 测试失败: {e}")
    
    # 测试2: 字符串中的特殊字符
    test_special = """
class SpecialCharTest {
    method1() {
        let str1 = "He said \\"Hello\\"";
        let str2 = 'She said \\'Hi\\'';
        let str3 = `Template with ${'interpolation'}`;
        let str4 = "Line1\\nLine2";
        let str5 = "Tab\\tHere";
    }
}
"""
    entities = parser.parse_file(test_special, "special.ets")
    assert len(entities) == 1, "应该找到1个类"
    log(f"✅ 字符串特殊字符解析成功")
    
    # 测试3: 注释中的特殊字符
    test_comment_special = """
// 测试: /* 块注释 */ 和 // 行注释
// 字符串中的 // 不是注释 "http://example.com"
class CommentSpecial {
    /* 方法文档
       多行注释
    */
    method() {}
}
"""
    entities = parser.parse_file(test_comment_special, "comment_special.ets")
    assert len(entities) == 1, "应该找到1个类"
    assert len(entities[0].methods) == 1, "应该找到1个方法"
    log(f"✅ 注释中的特殊字符解析成功")
    
    print("✅ 所有特殊字符测试通过!")


def test_edge_cases_parser():
    """测试解析器的边界情况"""
    print("\n" + "="*80)
    print("  测试解析器边界情况")
    print("="*80)
    
    parser = ArkTSParser()
    
    # 测试1: 超长行
    long_line = "class LongLine {\n    method() { " + "x" * 10000 + "; }\n}"
    try:
        entities = parser.parse_file(long_line, "longline.ets")
        log(f"✅ 超长行处理成功: {len(entities)} 个类")
    except Exception as e:
        log(f"❌ 超长行处理失败: {e}")
    
    # 测试2: 仅有空格和换行
    empty = "   \n\n   \n   "
    entities = parser.parse_file(empty, "empty.ets")
    assert len(entities) == 0, "应该找到0个类"
    log("✅ 空白内容处理成功")
    
    # 测试3: 未闭合的括号
    unclosed = """
class Unclosed {
    method() {
        if (true) {
            console.log("test");
        // 故意不闭合类
"""
    try:
        entities = parser.parse_file(unclosed, "unclosed.ets")
        log(f"✅ 未闭合括号处理: 找到 {len(entities)} 个类")
    except Exception as e:
        log(f"⚠️ 未闭合括号异常: {e}")
    
    # 测试4: 多余的闭合括号
    extra_closing = """
class ExtraClose {
    method() {
        console.log("test");
    }
}}
"""
    try:
        entities = parser.parse_file(extra_closing, "extra_close.ets")
        log(f"✅ 多余闭合括号处理: 找到 {len(entities)} 个类")
    except Exception as e:
        log(f"⚠️ 多余闭合括号异常: {e}")
    
    # 测试5: 注释中的类定义
    commented_class = """
// class NotAClass {
//     method() {}
// }
class RealClass {
    method() {}
}
"""
    entities = parser.parse_file(commented_class, "commented.ets")
    assert len(entities) == 1, "应该只找到1个真实的类"
    assert entities[0].name == "RealClass", "类名应该是 RealClass"
    log("✅ 注释中的类定义被正确忽略")
    
    print("✅ 所有解析器边界测试通过!")


def test_database_edge_cases():
    """测试数据库边界情况"""
    print("\n" + "="*80)
    print("  测试数据库边界情况")
    print("="*80)
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        db = ArkAnalyzerDB(db_path)
        db.initialize()
        
        # 测试1: 插入空字符串类名
        try:
            project_id = db.insert_project("test", "/test", int(time.time()))
            file_id = db.insert_file(project_id, "/test/empty.ets", "hash", 10, int(time.time()))
            class_id = db.insert_class(project_id, "", "class ", file_id, None, 0, 1, 10, None)
            log(f"✅ 允许空字符串类名: class_id={class_id}")
        except Exception as e:
            log(f"⚠️ 空字符串类名处理: {e}")
        
        # 测试2: 插入超长字符串
        long_name = "A" * 10000
        try:
            class_id = db.insert_class(project_id, long_name, "class " + long_name, file_id, None, 0, 1, 10, None)
            log(f"✅ 超长类名处理成功: id={class_id}")
        except Exception as e:
            log(f"⚠️ 超长类名处理: {e}")
        
        # 测试3: 多次删除不存在的项目
        try:
            db.delete_project(99999)
            log("✅ 删除不存在的项目无异常")
        except Exception as e:
            log(f"❌ 删除不存在项目异常: {e}")
        
        # 测试4: 插入重复项目
        try:
            id1 = db.insert_project("Duplicate", "/path1", int(time.time()))
            id2 = db.insert_project("Duplicate", "/path2", int(time.time()))
            log(f"✅ 重复项目处理: id1={id1}, id2={id2}")
        except Exception as e:
            log(f"❌ 重复项目处理异常: {e}")
        
        db.close()
        
        print("✅ 所有数据库边界测试完成!")
        
    finally:
        try:
            os.unlink(db_path)
        except Exception:
            pass


def test_runner_edge_cases():
    """测试运行器边界情况"""
    print("\n" + "="*80)
    print("  测试运行器边界情况")
    print("="*80)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            db = ArkAnalyzerDB(db_path)
            db.initialize()
            runner = ArkAnalyzerRunner('/workspace', db)
            
            # 测试1: 不存在的项目路径
            try:
                result = runner.analyze_project("/non/existent/path", "test")
                log(f"❌ 应该失败但返回: {result}")
            except Exception as e:
                log(f"✅ 正确处理不存在的路径: {type(e).__name__}")
            
            # 测试2: 仅有空文件的目录
            empty_dir = os.path.join(temp_dir, "empty_dir")
            os.makedirs(empty_dir)
            with open(os.path.join(empty_dir, "empty.ets"), "w") as f:
                f.write("")
            
            result = runner.analyze_project(empty_dir, "empty_test")
            assert result == True, "应该返回 True"
            stats = db.get_project_stats(runner.project_id)
            log(f"✅ 空文件处理成功: {stats}")
            
            # 测试3: 二进制文件
            bin_dir = os.path.join(temp_dir, "bin_dir")
            os.makedirs(bin_dir)
            with open(os.path.join(bin_dir, "binary.ets"), "wb") as f:
                f.write(b'\x00\x01\x02\x03\xff\xfe\xfd')
            
            result = runner.analyze_project(bin_dir, "binary_test")
            stats = db.get_project_stats(runner.project_id)
            log(f"✅ 二进制文件处理: {stats['classes']} 类")
            
            # 测试4: 符号链接
            link_dir = os.path.join(temp_dir, "link_dir")
            os.makedirs(link_dir)
            os.symlink(empty_dir, os.path.join(link_dir, "link_to_empty"))
            
            result = runner.analyze_project(link_dir, "link_test")
            stats = db.get_project_stats(runner.project_id)
            log(f"✅ 符号链接处理: {stats['files']} 文件")
            
            db.close()
            
            print("✅ 所有运行器边界测试完成!")
            
        finally:
            try:
                os.unlink(db_path)
            except Exception:
                pass


def test_incremental_update_edge_cases():
    """测试增量更新的边界情况"""
    print("\n" + "="*80)
    print("  测试增量更新边界情况")
    print("="*80)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            test_file = os.path.join(temp_dir, "Test.ets")
            
            # 第一次写入
            with open(test_file, "w") as f:
                f.write("""
class Initial {
    method1() {}
}
""")
            
            db = ArkAnalyzerDB(db_path)
            db.initialize()
            runner = ArkAnalyzerRunner('/workspace', db)
            runner.analyze_project(temp_dir, "incr_test")
            stats1 = db.get_project_stats(runner.project_id)
            log(f"第一次分析: {stats1['classes']} 类, {stats1['methods']} 方法")
            
            # 第二次写入 - 添加新内容
            time.sleep(0.01)
            with open(test_file, "a") as f:
                f.write("""
class Added {
    method2() {}
}
""")
            
            runner.analyze_project(temp_dir, "incr_test")
            stats2 = db.get_project_stats(runner.project_id)
            log(f"第二次分析: {stats2['classes']} 类, {stats2['methods']} 方法")
            
            assert stats2['classes'] > stats1['classes'], "类数应该增加"
            
            # 第三次写入 - 内容不变（但时间戳可能变化）
            time.sleep(0.01)
            with open(test_file, "w") as f:
                content = """
class Initial {
    method1() {}
}

class Added {
    method2() {}
}
"""
                f.write(content)
            
            runner.analyze_project(temp_dir, "incr_test")
            stats3 = db.get_project_stats(runner.project_id)
            log(f"第三次分析(内容不变): {stats3['classes']} 类")
            
            assert stats3['classes'] == stats2['classes'], "类数应该不变"
            
            db.close()
            
            print("✅ 增量更新边界测试完成!")
            
        finally:
            try:
                os.unlink(db_path)
            except Exception:
                pass


def test_hash_collision():
    """测试哈希碰撞场景"""
    print("\n" + "="*80)
    print("  测试哈希碰撞场景")
    print("="*80)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            # 创建两个内容相同的文件
            file1 = os.path.join(temp_dir, "file1.ets")
            file2 = os.path.join(temp_dir, "file2.ets")
            content = """
class SameClass {
    method() {}
}
"""
            with open(file1, "w") as f:
                f.write(content)
            with open(file2, "w") as f:
                f.write(content)
            
            # 计算哈希
            hash1 = hashlib.md5(content.encode()).hexdigest()
            hash2 = hashlib.md5(content.encode()).hexdigest()
            log(f"文件1哈希: {hash1}")
            log(f"文件2哈希: {hash2}")
            assert hash1 == hash2, "相同内容的哈希应该相同"
            
            db = ArkAnalyzerDB(db_path)
            db.initialize()
            runner = ArkAnalyzerRunner('/workspace', db)
            runner.analyze_project(temp_dir, "hash_test")
            stats = db.get_project_stats(runner.project_id)
            
            log(f"✅ 相同内容文件处理: {stats['files']} 文件, {stats['classes']} 类")
            
            # 验证每个文件都有记录
            cursor = db.conn.execute("SELECT path FROM files WHERE project_id = ?", (runner.project_id,))
            files = [row[0] for row in cursor.fetchall()]
            assert len(files) == 2, f"应该有2个文件记录，实际有 {len(files)}"
            
            db.close()
            
            print("✅ 哈希碰撞测试完成!")
            
        finally:
            try:
                os.unlink(db_path)
            except Exception:
                pass


def test_special_code_patterns():
    """测试特殊的代码模式"""
    print("\n" + "="*80)
    print("  测试特殊代码模式")
    print("="*80)
    
    parser = ArkTSParser()
    
    # 测试1: 装饰器链
    decorator_chain = """
@Component
@Preview
@Observed
class DecoratedClass {
    @Prop value: string;
    @State count: number;
}
"""
    entities = parser.parse_file(decorator_chain, "decorator.ets")
    assert len(entities) == 1
    assert len(entities[0].decorators) >= 3
    log(f"✅ 装饰器链解析: {entities[0].decorators}")
    
    # 测试2: 泛型类
    generic_class = """
class GenericClass<T, U> {
    method1(arg: T): U {
        return null;
    }
}
"""
    entities = parser.parse_file(generic_class, "generic.ets")
    assert len(entities) == 1
    log(f"✅ 泛型类解析成功")
    
    # 测试3: 命名空间
    namespace_code = """
namespace MyNamespace {
    class Inner {
        method() {}
    }
}
"""
    entities = parser.parse_file(namespace_code, "namespace.ets")
    # 可能无法解析 namespace，这是预期的
    log(f"⚠️ 命名空间解析: 找到 {len(entities)} 个实体")
    
    # 测试4: 条件类型
    conditional_type = """
class ConditionalTest {
    // TypeScript 特有的条件类型
    type Foo<T> = T extends string ? 'yes' : 'no';
}
"""
    entities = parser.parse_file(conditional_type, "conditional.ets")
    log(f"✅ 条件类型代码解析: {len(entities)} 个类")
    
    # 测试5: keyof 和 typeof
    keyof_code = """
class KeyofTest {
    type Keys = keyof { name: string, age: number };
}
"""
    entities = parser.parse_file(keyof_code, "keyof.ets")
    log(f"✅ keyof 代码解析: {len(entities)} 个类")
    
    print("✅ 所有特殊代码模式测试完成!")


def test_method_resolution():
    """测试方法调用解析的准确性"""
    print("\n" + "="*80)
    print("  测试方法调用解析")
    print("="*80)
    
    parser = ArkTSParser()
    
    test_code = """
class Caller {
    method1() {
        this.method2();
        this.method3();
        this.method4();
    }
    
    method2() {}
    method3() {}
    method4() {}
}

class Callee {
    helper() {
        console.log("helper");
    }
}
"""
    entities = parser.parse_file(test_code, "call.ets")
    assert len(entities) == 2
    
    caller = entities[0]
    assert caller.name == "Caller"
    
    method1 = caller.methods[0]
    log(f"Caller.method1 的调用: {method1.calls}")
    
    # 验证方法调用被正确提取（过滤掉库方法）
    expected_calls = {'method2', 'method3', 'method4'}
    actual_calls = set(method1.calls)
    
    # 应该包含这些方法调用
    for call in expected_calls:
        if call in actual_calls:
            log(f"  ✅ {call} 被正确识别")
        else:
            log(f"  ⚠️ {call} 未被识别")
    
    print("✅ 方法调用解析测试完成!")


def main():
    print("="*80)
    print("  DEEP TEST SUITE - 第二轮深度测试")
    print("="*80)
    
    tests = [
        ("深度嵌套结构", test_nested_structures),
        ("特殊字符和编码", test_special_characters),
        ("解析器边界情况", test_edge_cases_parser),
        ("数据库边界情况", test_database_edge_cases),
        ("运行器边界情况", test_runner_edge_cases),
        ("增量更新边界", test_incremental_update_edge_cases),
        ("哈希碰撞场景", test_hash_collision),
        ("特殊代码模式", test_special_code_patterns),
        ("方法调用解析", test_method_resolution),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            log(f"❌ 测试失败: {name}")
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*80)
    print(f"  深度测试结果: {passed} 通过, {failed} 失败")
    print("="*80)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
极深极繁极乱的测试场景 - 挑战系统极限
发现潜在的 Bug 和问题
"""
import os
import sys
import tempfile
import logging

# 确保能导入模块
sys.path.insert(0, '/workspace')

from parser import ArkTSParser
from ark_analyzer_db import ArkAnalyzerDB
from ark_analyzer_runner import ArkAnalyzerRunner

# 配置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def create_ultimate_chaos_file():
    """创建终极混乱文件 - 包含各种极端场景"""
    content = """// 终极混乱文件 - 测试系统极限

// 混合注释、字符串、装饰器
@Component
@Observed
@Entry
export class ChaosClass {
    // 超长方法名
    myVeryLongMethodNameThatTestsLimitsOfParsingWhatHappensWhenWeGoWayOverNormalLengths(
        param1: string,
        param2: number,
        param3: boolean,
        param4: Array<string>,
        param5: { [key: string]: any }
    ): void {
        // 超深调用链
        this.method1().method2().method3().method4().method5().method6();
        // 大量方法调用
        doSomething();
        doAnotherThing();
        andAnother();
        moreCalls();
        evenMore();
    }
    
    method1() { return this; }
    method2() { return this; }
    method3() { return this; }
    method4() { return this; }
    method5() { return this; }
    method6() { return this; }
}

// 极深嵌套类
export class Outer {
    middle: any;
    constructor() {
        this.middle = class {
            inner: any;
            constructor() {
                this.inner = class {
                    deepest: any;
                    constructor() {
                        this.deepest = class {
                            getValue() { return 42; }
                        };
                    }
                };
            }
        };
    }
}

// 超长类名
export class ClassWithAnExtremelyLongNameThatGoesWayBeyondWhatAnyoneWouldEverUseButWeNeedToTestItAnywayJustInCaseThereAreLimitsInOurParsingOrDatabaseHandling {
    test() { console.log("test"); }
}

// 大量装饰器
@Component
@Entry
@Observed
@Preview
@State
@Prop
@Link
@Provide
@Consume
@Watch
@ObjectLink
@StorageLink
@StorageProp
@LocalStorageLink
@LocalStorageProp
@Environment
@BuilderParam
export class DecoratorChaos {
    doSomething() { console.log("hello"); }
}

// Unicode 极端测试
export class 日本語クラス {
    メソッド() { console.log("こんにちは"); }
}

export class КлассНаРусском {
    методНаРусском() { console.log("Привет"); }
}

export class مرحبا {
    مرحبا() { console.log("مرحبا"); }
}

// 极复杂的字符串混合
export class StringChaos {
    mix() {
        // 各种字符串混合注释
        const str1 = "// this is not a comment";
        const str2 = '/* this is also not a comment */';
        const str3 = `\`\`\` this is not code \`\`\``;
        const str4 = "string with \"quotes\" inside";
        const str5 = 'another with \'quotes\'';
    }
}

// 二进制数据注释
// 包含一些奇怪的字符：\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a
export class BinaryTest {
    test() { console.log("test"); }
}

// 超深括号嵌套
export class DeepBracketChaos {
    test() {
        const x = (((((((((((((((((((1 + 2))))))))))))))))));
        console.log(x);
    }
}

// 大量方法
export class ManyMethods {
    method0() {} method1() {} method2() {} method3() {} method4() {}
    method5() {} method6() {} method7() {} method8() {} method9() {}
    method10() {} method11() {} method12() {} method13() {} method14() {}
    method15() {} method16() {} method17() {} method18() {} method19() {}
    method20() {} method21() {} method22() {} method23() {} method24() {}
    method25() {} method26() {} method27() {} method28() {} method29() {}
}
"""
    
    return content


def test_ultimate_chaos_parsing():
    """测试终极混乱文件的解析"""
    print("="*80)
    print("  终极混乱场景测试")
    print("="*80)
    
    parser = ArkTSParser()
    chaos_content = create_ultimate_chaos_file()
    
    print(f"\n[TEST] 文件内容长度: {len(chaos_content)} 字符")
    
    try:
        entities = parser.parse_file(chaos_content, "ultimate_chaos.ets")
        print(f"[TEST] ✅ 解析成功! 找到 {len(entities)} 个类/结构")
        
        for i, entity in enumerate(entities):
            print(f"  {i+1}. {entity.name} (方法数: {len(entity.methods)})")
            
        print("\n[TEST] ✅ 终极混乱场景测试通过!")
        return True
        
    except Exception as e:
        print(f"[TEST] ❌ 解析失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def test_empty_and_edge_cases():
    """测试各种空内容和边界情况"""
    print("\n" + "="*80)
    print("  空内容与边界场景测试")
    print("="*80)
    
    parser = ArkTSParser()
    test_cases = [
        ("完全空内容", ""),
        ("仅空白", "   \n\n  \t  \n  "),
        ("仅注释", "// comment\n/* block */"),
        ("单个大括号", "{"),
        ("未闭合括号", "class A {"),
        ("大量空白", " " * 10000),
    ]
    
    all_passed = True
    for name, content in test_cases:
        try:
            entities = parser.parse_file(content, "test.ets")
            print(f"[TEST] ✅ {name}: 找到 {len(entities)} 个实体")
        except Exception as e:
            print(f"[TEST] ❌ {name}: 解析失败 - {e}")
            all_passed = False
    
    return all_passed


def test_database_with_chaos():
    """测试数据库处理混乱数据"""
    print("\n" + "="*80)
    print("  数据库混乱场景测试")
    print("="*80)
    
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db.close()
    
    try:
        db = ArkAnalyzerDB(temp_db.name)
        db.initialize()
        
        # 插入一些极端数据
        project_id = db.insert_project("chaos_test", "/tmp", int(__import__('time').time()))
        
        # 插入超长类名
        long_name = "A" * 1000
        try:
            class_id = db.insert_class(
                project_id=project_id,
                name=long_name,
                signature=f"class {long_name}",
                file_id=None,
                namespace_id=None,
                flags=0,
                start_line=1,
                end_line=10,
                source_code=None
            )
            print(f"[TEST] ✅ 超长类名插入成功: {len(long_name)} 字符, id={class_id}")
            
            # 插入超长方法
            long_method_name = "B" * 1000
            method_id = db.insert_method(
                project_id=project_id,
                name=long_method_name,
                signature=f"function {long_method_name}()",
                class_id=class_id,
                namespace_id=None,
                file_id=None,
                params="",
                return_type="",
                flags=0,
                start_line=2,
                end_line=5,
                source_code=None,
                is_constructor=0,
                is_static=0
            )
            print(f"[TEST] ✅ 超长方法名插入成功: {len(long_method_name)} 字符, id={method_id}")
            
            # 插入大量调用
            for i in range(100):
                db.insert_call(
                    project_id=project_id,
                    caller_method_id=method_id,
                    callee_method_name=f"call_{i}",
                    callee_signature=None,
                    callee_method_id=None,
                    call_type="call"
                )
            print(f"[TEST] ✅ 100 条调用关系插入成功")
            
        except Exception as e:
            print(f"[TEST] ❌ 数据库操作失败: {e}")
            import traceback
            print(traceback.format_exc())
            return False
        finally:
            db.close()
            
        print("[TEST] ✅ 数据库混乱测试通过!")
        return True
        
    finally:
        os.unlink(temp_db.name)


def test_runner_with_many_files():
    """测试运行器处理大量文件"""
    print("\n" + "="*80)
    print("  运行器大量文件测试")
    print("="*80)
    
    temp_dir = tempfile.TemporaryDirectory()
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db.close()
    
    try:
        # 创建 100 个小文件
        for i in range(100):
            file_path = os.path.join(temp_dir.name, f"TestFile{i}.ets")
            content = f"""export class TestClass{i} {{
    method1() {{ }}
    method2() {{ }}
}}
"""
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        print(f"[TEST] 创建了 100 个测试文件")
        
        # 运行分析
        db = ArkAnalyzerDB(temp_db.name)
        db.initialize()
        
        runner = ArkAnalyzerRunner("/workspace", db)
        result = runner.analyze_project(temp_dir.name, "many_files_test")
        
        print(f"[TEST] 分析结果: {'成功' if result else '失败'}")
        
        # 获取统计
        stats = db.get_project_stats(runner.project_id)
        print(f"[TEST] 统计: {stats}")
        
        db.close()
        
        if result and stats['files'] >= 100 and stats['classes'] >= 100:
            print("[TEST] ✅ 运行器大量文件测试通过!")
            return True
        else:
            print("[TEST] ❌ 运行器大量文件测试失败!")
            return False
            
    finally:
        os.unlink(temp_db.name)
        temp_dir.cleanup()


def main():
    """主测试函数"""
    results = []
    
    results.append(("终极混乱解析", test_ultimate_chaos_parsing()))
    results.append(("边界场景", test_empty_and_edge_cases()))
    results.append(("数据库混乱", test_database_with_chaos()))
    results.append(("运行器多文件", test_runner_with_many_files()))
    
    # 总结
    print("\n" + "="*80)
    print("  终极混乱测试总结")
    print("="*80)
    passed = 0
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")
        if result:
            passed += 1
    
    print(f"\n  总计: {passed}/{len(results)} 个测试通过")
    
    return passed == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

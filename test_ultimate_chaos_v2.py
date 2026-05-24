#!/usr/bin/env python3
"""
Ultimate Chaos V2 - 最极端和混乱的测试场景
发现潜在的边界情况和 bug
"""
import os
import sys
import tempfile
import random
import string
import logging
import time

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


def generate_mixed_chars(length=50):
    """生成混合了各种 Unicode 字符的字符串"""
    chars = []
    for _ in range(length):
        category = random.randint(0, 10)
        if category < 3:
            # 拉丁字符
            chars.append(random.choice(string.ascii_letters))
        elif category < 5:
            # 中文
            chars.append(chr(random.randint(0x4e00, 0x9fff)))
        elif category < 7:
            # 日文
            chars.append(chr(random.randint(0x3040, 0x30ff)))
        elif category < 8:
            # 韩文
            chars.append(chr(random.randint(0xac00, 0xd7af)))
        elif category < 9:
            # 泰语
            chars.append(chr(random.randint(0x0e00, 0x0e7f)))
        else:
            # 其他 Unicode
            chars.append(chr(random.randint(0x0400, 0x06ff)))
    return ''.join(chars)


def create_extreme_decorator_test():
    """大量、嵌套、复杂的装饰器测试"""
    decorators = []
    for i in range(50):
        if random.random() < 0.5:
            decorators.append(f"@Decorator{i}")
        else:
            decorators.append(f"@Decorator{i}(param{i}='value{i}')")
    
    methods = []
    for i in range(30):
        method_name = f"{generate_mixed_chars(5)}{i}"
        methods.append(f"  {method_name}() {{ /* do something */ }}")
    
    return f"""
{'\n'.join(decorators)}
export class ExtremeDecoratorClass {{
{'\n'.join(methods)}
}}
"""


def create_mixed_string_comment_test():
    """极其混乱的字符串、注释混合测试"""
    return '''
export class StringCommentMix {
    /* This is a block comment */
    var1 = "/* not a comment */";
    // This is a line comment
    var2 = '// also not a comment';
    /* This is a /* nested comment */ which causes issues */
    method1() { 
        console.log("hello"); 
        /* block inside method */
    }
    
    // Another line /* with a comment */ inside it
    method2() { 
        /* 
           multi-line block comment
           with "quotes" inside
        */
        var3 = "string with // comments";
    }
}
'''


def create_extremely_nested_test():
    """超深嵌套结构"""
    content = "export class NestedClass {\n"
    current_indent = 2
    for i in range(50):
        # 随机嵌套层级
        action = random.choice(['if', 'for', 'while', 'block'])
        
        if action == 'block':
            content += ' ' * current_indent + "{\n"
            current_indent += 2
        elif action == 'if':
            content += ' ' * current_indent + f"if (condition{i}) {{\n"
            current_indent += 2
        elif action == 'for':
            content += ' ' * current_indent + f"for (let i = 0; i < 10; i++) {{\n"
            current_indent += 2
        else:  # while
            content += ' ' * current_indent + f"while (condition{i}) {{\n"
            current_indent += 2
    
    # 随机添加一些变量或方法
    for i in range(20):
        content += ' ' * current_indent + f"x{i} = {i};\n"
    
    # 随机关闭一些括号
    for _ in range(25):
        current_indent = max(0, current_indent - 2)
        content += ' ' * current_indent + "}\n"
    
    content += "  simpleMethod() { /* end simple */ }\n"
    content += "}\n"
    
    return content


def create_unicode_crazy_test():
    """最疯狂的 Unicode 类名和方法名"""
    classes = []
    for i in range(15):
        class_name = generate_mixed_chars(20)
        methods = []
        for j in range(10):
            method_name = generate_mixed_chars(10)
            methods.append(f"  {method_name}() {{ }}")
        classes.append(f'''
export class {class_name} {{
{chr(10).join(methods)}
}}''')
    return '\n'.join(classes)


def create_malformed_but_legal_test():
    """奇怪但语法合法的边界情况"""
    return '''
export class WeButLegal {
    var1 = `backtick string with "double quotes"`;
    var2 = "string with 'single quotes'";
    
    /* 空方法体 */
    method1() {}
    
    /* 超长空行 */
    
    
    /* 只有换行的方法 */
    method2() {
    
    
    }
    
    /* 混合不同的空格 */
    method3   (   )   {    }
}
'''


def create_1000_files_test_project():
    """创建1000个文件的测试项目"""
    temp_dir = tempfile.mkdtemp(prefix="ark_analyzer_ultimate_chaos_")
    
    # 创建 1000 个文件
    for i in range(1000):
        file_path = os.path.join(temp_dir, f"Test{i}.ets")
        
        # 随机选择一种混乱模式
        choice = random.randint(0, 5)
        if choice == 0:
            content = create_extreme_decorator_test()
        elif choice == 1:
            content = create_mixed_string_comment_test()
        elif choice == 2:
            content = create_extremely_nested_test()
        elif choice == 3:
            content = create_unicode_crazy_test()
        elif choice == 4:
            content = create_malformed_but_legal_test()
        else:
            # 普通文件
            content = f'''export class TestClass{i} {{
  method1() {{ }}
  method2() {{ method1(); }}
}}'''
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return temp_dir


def run_ultimate_chaos_test():
    """运行最混乱的终极测试"""
    print("="*80)
    print("  ULTIMATE CHAOS V2 - 极端混乱测试")
    print("="*80)
    
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db.close()
    
    db = ArkAnalyzerDB(temp_db.name)
    db.initialize()
    
    # 测试单独的极端情况
    print("\n[1] 极端装饰器测试...")
    parser = ArkTSParser()
    decorator_content = create_extreme_decorator_test()
    entities1 = parser.parse_file(decorator_content, "decorators.ets")
    print(f"  ✓ 找到 {len(entities1)} 个类")
    
    print("\n[2] 字符串混合注释测试...")
    string_content = create_mixed_string_comment_test()
    entities2 = parser.parse_file(string_content, "strings.ets")
    print(f"  ✓ 找到 {len(entities2)} 个类")
    
    print("\n[3] 超深嵌套测试...")
    nested_content = create_extremely_nested_test()
    entities3 = parser.parse_file(nested_content, "nested.ets")
    print(f"  ✓ 找到 {len(entities3)} 个类")
    
    print("\n[4] Unicode 疯狂测试...")
    unicode_content = create_unicode_crazy_test()
    entities4 = parser.parse_file(unicode_content, "unicode.ets")
    print(f"  ✓ 找到 {len(entities4)} 个类")
    
    print("\n[5] 奇怪但合法测试...")
    weird_content = create_malformed_but_legal_test()
    entities5 = parser.parse_file(weird_content, "weird.ets")
    print(f"  ✓ 找到 {len(entities5)} 个类")
    
    # 最后，1000 个文件的项目！
    print("\n" + "="*80)
    print("  [最终考验] 1000 文件大规模测试")
    print("="*80)
    
    project_dir = create_1000_files_test_project()
    print(f"  测试项目位置: {project_dir}")
    
    try:
        runner = ArkAnalyzerRunner("/workspace", db)
        
        start = time.time()
        result = runner.analyze_project(project_dir, "ultimate_chaos_v2")
        elapsed = time.time() - start
        
        if not result:
            print("  ❌ 分析失败！")
            return False
        
        print(f"  ✓ 分析完成!")
        print(f"  耗时: {elapsed:.2f}s")
        
        stats = db.get_project_stats(runner.project_id)
        print(f"  文件: {stats['files']}")
        print(f"  类: {stats['classes']}")
        print(f"  方法: {stats['methods']}")
        print(f"  调用关系: {stats['calls']}")
        print(f"  孤儿记录: {stats['orphaned_calls']}")
        
        if stats['orphaned_calls'] > 0:
            print(f"  ⚠️  有 {stats['orphaned_calls']} 条孤儿调用关系")
        
        orphans = db.get_orphaned_calls(runner.project_id)
        if len(orphans) > 0:
            print(f"  孤儿示例: {orphans[:5]}")
        
        print("\n" + "="*80)
        print("  所有测试成功！系统运行稳定！")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"  ❌ 测试失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        import shutil
        try:
            shutil.rmtree(project_dir)
            os.unlink(temp_db.name)
        except:
            pass


if __name__ == "__main__":
    print("开始终极混乱测试...")
    success = run_ultimate_chaos_test()
    sys.exit(0 if success else 1)

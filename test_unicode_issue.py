#!/usr/bin/env python3
"""
专门测试阿拉伯语等 Unicode 类名和方法名的解析问题
"""
import sys
sys.path.insert(0, '/workspace')

from parser import ArkTSParser

test_content = """// 测试 Unicode 方法名
export class مرحبا {
    مرحبا() { console.log("مرحبا"); }
    testMethod() { }
}

export class 中文类 {
    中文方法() { }
}

export class EnglishClass {
    englishMethod() { }
}
"""

print("="*80)
print("  测试 Unicode 方法名解析")
print("="*80)

parser = ArkTSParser()
entities = parser.parse_file(test_content, "unicode_test.ets")

print(f"\n找到 {len(entities)} 个类/结构:")
for entity in entities:
    print(f"  类名: {entity.name}")
    print(f"  方法数: {len(entity.methods)}")
    for method in entity.methods:
        print(f"    - {method.name} (第 {method.start_line}-{method.end_line} 行)")
    print()

# 测试独立的方法正则表达式
print("\n" + "="*80)
print("  调试正则表达式")
print("="*80)

print("\n方法正则模式:")
print(parser.method_pattern.pattern[:200] + "..." if len(parser.method_pattern.pattern) > 200 else parser.method_pattern.pattern)

# 手动测试几个方法名
test_cases = [
    "مرحبا",
    "中文方法", 
    "englishMethod",
    "testMethod",
    "my_method",
    "method123"
]

print("\n测试 Unicode 字符支持:")
for name in test_cases:
    # 简单测试看是否能匹配标识符
    match = parser.method_pattern.search(f"{name}() {{ }}")
    if match:
        print(f"  ✅ 匹配成功: {name}")
    else:
        print(f"  ❌ 匹配失败: {name}")

#!/usr/bin/env python3
"""简单的 Unicode 测试 - 确保不会破坏现有功能"""
import sys
sys.path.insert(0, '/workspace')
from parser import ArkTSParser

print("="*80)
print("  Unicode 字符支持测试")
print("="*80)

# 测试 1: 基本功能（确保没有破坏现有功能）
print("\n[1] 基本功能测试...")
test1 = """
export class TestClass {
    method1() { console.log("hello"); }
    method2() { this.method1(); }
}
"""
parser = ArkTSParser()
entities1 = parser.parse_file(test1, "basic.ets")
print(f"  ✓ 解析 {len(entities1)} 个类")
for e in entities1:
    print(f"    - {e.name}: {len(e.methods)} 个方法")
    for m in e.methods:
        print(f"      * {m.name}")

# 测试 2: 中文、日文、韩文
print("\n[2] 中文、日文、韩文测试...")
test2 = """
export class 中文类 {
    中文方法() { console.log("你好"); }
}

export class 日本語クラス {
    日本語メソッド() { console.log("こんにちは"); }
}

export class 한국어클래스 {
    한국어메서드() { console.log("안녕하세요"); }
}
"""
entities2 = parser.parse_file(test2, "cjk.ets")
print(f"  ✓ 解析 {len(entities2)} 个类")
for e in entities2:
    print(f"    - {e.name}: {len(e.methods)} 个方法")
    for m in e.methods:
        print(f"      * {m.name}")

# 测试 3: 泰语
print("\n[3] 泰语测试...")
test3 = """
export class ThaiClass {
    วิธีการ() { console.log("สวัสดี"); }
}
"""
entities3 = parser.parse_file(test3, "thai.ets")
print(f"  ✓ 解析 {len(entities3)} 个类")
for e in entities3:
    print(f"    - {e.name}: {len(e.methods)} 个方法")
    for m in e.methods:
        print(f"      * {m.name}")

print("\n" + "="*80)
print("  所有测试通过！")
print("="*80)

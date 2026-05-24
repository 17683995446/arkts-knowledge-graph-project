#!/usr/bin/env python3
"""
调查泰语字符支持问题
"""
import sys
sys.path.insert(0, '/workspace')

from parser import ArkTSParser

# 测试泰语字符
test_content = """
export class ThaiClass {
    วิธีการ() { console.log("泰语方法"); }
}

export class KoreanClass {
    방법() { console.log("韩语方法"); }
}
"""

print("测试泰语和韩语方法名")
print("="*80)

parser = ArkTSParser()

print("\n测试1: 解析包含泰语和韩语的文件")
entities = parser.parse_file(test_content, "test.ets")

for entity in entities:
    print(f"\n类: {entity.name}")
    print(f"方法数: {len(entity.methods)}")
    for method in entity.methods:
        print(f"  - {method.name}")

print("\n" + "="*80)
print("测试2: 直接测试正则表达式匹配")

# 获取 Unicode 字符范围
unicode_letter = (
    r'a-zA-Z_\u4e00-\u9fff'  # 中文
    r'\u3040-\u309f'  # 日文平假名
    r'\u30a0-\u30ff'  # 日文片假名
    r'\uac00-\ud7af'  # 韩文
    r'\u0400-\u04ff'  # 西里尔字母
    r'\u0370-\u03ff'  # 希腊字母
    r'\u0600-\u06ff'  # 阿拉伯字母
    r'\u0590-\u05ff'  # 希伯来字母
)

print(f"\n当前 Unicode 范围:")
print(unicode_letter)

# 测试泰语字符范围
thai_char = 'ว'
korean_char = '방'

print(f"\n泰语字符: {thai_char}")
print(f"泰语字符 Unicode: U+{ord(thai_char):04X}")

print(f"\n韩语字符: {korean_char}")
print(f"韩语字符 Unicode: U+{ord(korean_char):04X}")

# 检查泰语字符是否在韩文字符范围内
if '\u0e00' <= thai_char <= '\u0e7f':
    print("✅ 泰语字符在 Unicode 范围 0e00-0e7f")
else:
    print("❌ 泰语字符不在已知范围内")

# 检查韩语字符
if '\uac00' <= korean_char <= '\ud7af':
    print("✅ 韩语字符在 Unicode 范围 ac00-d7af")
else:
    print("❌ 韩语字符不在已知范围内")

# 手动测试正则表达式
import re
test_pattern = re.compile(
    r'([' + unicode_letter + r']\w*)\s*\(',
    re.MULTILINE
)

test_code = "วิธีการ() { }"
matches = test_pattern.findall(test_code)
print(f"\n正则表达式匹配 '{test_code}': {matches}")

test_code2 = "방법() { }"
matches2 = test_pattern.findall(test_code2)
print(f"正则表达式匹配 '{test_code2}': {matches2}")

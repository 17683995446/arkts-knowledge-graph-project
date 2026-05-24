#!/usr/bin/env python3
"""调试正则表达式 - 找到问题根源"""
import re

unicode_letter = (
    r'a-zA-Z_\u4e00-\u9fff'
    r'\u3040-\u309f'
    r'\u30a0-\u30ff'
    r'\uac00-\ud7af'
    r'\u0400-\u04ff'
    r'\u0370-\u03ff'
    r'\u0600-\u06ff'
    r'\u0590-\u05ff'
    r'\u0e00-\u0e7f'
)

print("="*80)
print("  正则表达式调试")
print("="*80)

# 测试 1: 简单字符类匹配
pattern1 = re.compile(r'[' + unicode_letter + r']')
test1 = 'ว'  # 泰语字符
match1 = pattern1.match(test1)
print(f"\n[1] 泰语字符匹配: {test1!r}")
print(f"  {'✓ 匹配成功!' if match1 else '✗ 匹配失败!'}")

# 测试 2: 完整方法模式
pattern2 = re.compile(r'^[' + unicode_letter + r']\w*\s*\(', re.MULTILINE)
test2 = 'วิธีการ() { '
match2 = pattern2.search(test2)
print(f"\n[2] 泰语方法匹配: {test2!r}")
print(f"  {'✓ 匹配成功!' if match2 else '✗ 匹配失败!'}")

# 测试 3: 问题分析
pattern3a = re.compile(r'[' + unicode_letter + r']\w*')  # 目前的模式
pattern3b = re.compile(r'[' + unicode_letter + r'][' + unicode_letter + r'\d]*')  # 更好的模式

print(f"\n[3] 问题分析:")
match3a = pattern3a.search('วิธีการ')
if match3a:
    print(f"  模式 3a (使用 \\w): {match3a.group(0)!r}")
else:
    print(f"  模式 3a (使用 \\w): None")

match3b = pattern3b.search('วิธีการ')
if match3b:
    print(f"  模式 3b (不使用 \\w): {match3b.group(0)!r}")
else:
    print(f"  模式 3b (不使用 \\w): None")

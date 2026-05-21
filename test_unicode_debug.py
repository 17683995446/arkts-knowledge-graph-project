#!/usr/bin/env python3
import sys
sys.path.insert(0, '/workspace')

from parser import ArkTSParser

parser = ArkTSParser()

unicode_code = """
class 中文类名 {
    日本語メソッド() {
        let 한국어 = "한국어";
        let 😊 = "emoji";
        console.log(한국어, 😊);
    }
}
"""

print("测试Unicode代码:")
print(unicode_code)

entities = parser.parse_file(unicode_code, "unicode.ets")
print(f"\n找到 {len(entities)} 个实体")

if entities:
    e = entities[0]
    print(f"类名: {e.name}")
    print(f"方法数: {len(e.methods)}")
    if e.methods:
        print(f"第一个方法: {e.methods[0].name}")
else:
    print("❌ 未找到任何实体")
    
# 测试正则表达式
import re

# 当前的 struct_pattern
struct_pattern = re.compile(
    r'(?:@([a-zA-Z_]\w*)\s*(?:\([^)]*\))?\s*(?:\n\s*@)?)*'
    r'(?:export\s+)?'
    r'(?:(abstract)\s+)?'
    r'(class|struct)\s+'
    r'([a-zA-Z_]\w*)',
    re.MULTILINE
)

print("\n测试正则表达式:")
match = struct_pattern.search(unicode_code)
if match:
    print(f"匹配成功: {match.group(0)}")
    print(f"类名: {match.group(4)}")
else:
    print("❌ 正则表达式未匹配")
    
# 测试支持Unicode的正则表达式
unicode_struct_pattern = re.compile(
    r'(?:@([a-zA-Z_]\w*)\s*(?:\([^)]*\))?\s*(?:\n\s*@)?)*'
    r'(?:export\s+)?'
    r'(?:(abstract)\s+)?'
    r'(class|struct)\s+'
    r'([a-zA-Z_\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]\w*)',
    re.MULTILINE
)

print("\n测试Unicode正则表达式:")
match = unicode_struct_pattern.search(unicode_code)
if match:
    print(f"✅ 匹配成功: {match.group(0)}")
    print(f"类名: {match.group(4)}")
else:
    print("❌ Unicode正则表达式未匹配")

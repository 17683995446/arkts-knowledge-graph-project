#!/usr/bin/env python3
import sys
sys.path.insert(0, '/workspace')

from parser import ArkTSParser
import re

parser = ArkTSParser()

test_code = """
@Component
@Entry
@Preview
struct TestComponent {
    method() {}
}
"""

# 手动模拟 _strip_comments_and_map
clean_content, pos_map = parser._strip_comments_and_map(test_code)

print("=== pos_map 前20个元素 ===")
for i in range(min(20, len(pos_map))):
    print(f"pos_map[{i}] = {pos_map[i]}, clean_content[{i}] = {repr(clean_content[i])}")

print(f"\n=== 原始内容前20个字符 ===")
for i in range(min(20, len(test_code))):
    print(f"test_code[{i}] = {repr(test_code[i])}")

print(f"\n=== 匹配 '@Component' 在 clean_content 中的位置 ===")
idx = clean_content.find('@Component')
print(f"idx = {idx}")
print(f"clean_content[idx:idx+10] = {repr(clean_content[idx:idx+10])}")

print(f"\n=== pos_map[idx] ===")
print(f"pos_map[{idx}] = {pos_map[idx]}")
print(f"test_code[{pos_map[idx]}] = {repr(test_code[pos_map[idx]])}")

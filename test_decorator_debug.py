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

# 查找 class/struct
struct_pattern = re.compile(
    r'(?:@([a-zA-Z_]\w*)\s*(?:\([^)]*\))?\s*(?:\n\s*@)?)*'
    r'(?:export\s+)?'
    r'(?:(abstract)\s+)?'
    r'(class|struct)\s+'
    r'([a-zA-Z_]\w*)',
    re.MULTILINE
)

match = struct_pattern.search(clean_content)
if match:
    # 映射到原始位置
    orig_positions = parser._map_positions(match.start(), match.end(), pos_map)
    if orig_positions:
        original_start, original_end = orig_positions
        print(f"original_start: {original_start}")
        print(f"original_end: {original_end}")
        print(f"before = test_code[:{original_start}]")
        print(f"before 内容: {repr(test_code[:original_start])}")
        
        # 查找装饰器
        before = test_code[:original_start]
        lines = before.split('\n')
        print(f"\n所有行:")
        for i, line in enumerate(lines):
            print(f"  {i}: {repr(line)}")
            stripped = line.lstrip()
            if stripped.startswith('@'):
                match_dec = re.match(r'@([a-zA-Z_]\w*)', stripped)
                if match_dec:
                    print(f"    -> 找到装饰器: {match_dec.group(1)}")

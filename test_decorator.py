#!/usr/bin/env python3
import sys
sys.path.insert(0, '/workspace')

from parser import ArkTSParser

parser = ArkTSParser()

test_code = """
@Component
@Entry
@Preview
struct TestComponent {
    method() {}
}
"""

entities = parser.parse_file(test_code, "test.ets")
print(f"找到 {len(entities)} 个实体")
if entities:
    e = entities[0]
    print(f"类名: {e.name}")
    print(f"装饰器数量: {len(e.decorators)}")
    print(f"装饰器列表: {e.decorators}")
    print(f"标志: {e.flags}")

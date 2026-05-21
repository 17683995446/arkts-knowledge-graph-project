#!/usr/bin/env python3
"""Debug the comment stripping test failure."""
import sys
sys.path.insert(0, '/workspace')

from parser import ArkTSParser

test_code = """
// This is a line comment
class CommentTest {
    /* This is a block comment
    that spans multiple lines */
    method1() {
        return 42;
    }
}
"""

print("=== Original code ===")
print(repr(test_code))
print("\n=== Parsing ===")
parser = ArkTSParser()
entities = parser.parse_file(test_code, "test.ets")

print(f"\nFound {len(entities)} entities:")
for entity in entities:
    print(f"\n- {type(entity).__name__}: {entity.name}")
    print(f"  Methods: {len(entity.methods)}")
    for method in entity.methods:
        print(f"    - Method: {method.name}")

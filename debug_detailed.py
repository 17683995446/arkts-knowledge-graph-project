#!/usr/bin/env python3
"""Detailed debugging of comment stripping issue."""
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

parser = ArkTSParser()

print("=== Step 1: Get clean content ===")
clean = parser._strip_comments(test_code)
print(repr(clean))
print(f"Length: {len(clean)}, Original length: {len(test_code)}")

print("\n=== Step 2: Find structs ===")
structs = parser._find_structs(clean, test_code)
print(f"Found {len(structs)} structs")
for s in structs:
    print(f"  - {s[0]}, brace at {s[5]}, end brace at {s[6]}")

print("\n=== Step 3: Extract body ===")
for s in structs:
    name, _, _, _, _, brace_pos, end_brace_pos, _ = s
    body = test_code[brace_pos+1:end_brace_pos]
    print(f"Body for {name}: {repr(body)}")
    clean_body = parser._strip_comments(body)
    print(f"Clean body: {repr(clean_body)}")
    
    print("\nLooking for methods in clean body...")
    match = parser.method_pattern.search(clean_body, 0)
    if match:
        print(f"Found method match: {match.group(0)}")
        print(f"Match at: {match.start()}-{match.end()}")
        target = clean_body[match.start():match.end()]
        print(f"Target string: {repr(target)}")
        orig = body.find(target)
        print(f"Found in full body at: {orig}")
        if orig != -1:
            print(f"Found: {repr(body[orig:orig+len(target)])}")

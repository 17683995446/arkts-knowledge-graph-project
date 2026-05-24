#!/usr/bin/env python3
"""深层次问题查找测试"""

import os
import sys
import logging
from parser import ArkTSParser

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('DeepProblemTest')


def test_deep_nested_classes():
    """测试深层嵌套类"""
    logger.info("=" * 80)
    logger.info("测试深层嵌套类")
    logger.info("=" * 80)
    
    test_code = '''
class Level1 {
    class Level2 {
        class Level3 {
            class Level4 {
                class Level5 {
                    method5() {}
                }
                method4() {}
            }
            method3() {}
        }
        method2() {}
    }
    method1() {}
}

class AnotherClass {
    someMethod() {
        this.callSomething();
    }
}
'''
    
    try:
        parser = ArkTSParser()
        entities = parser.parse_file(test_code, '/test/deep_nested.ets')
        
        logger.info(f"找到 {len(entities)} 个实体")
        for entity in entities:
            logger.info(f"  - {entity.name}: {len(entity.methods)} 个方法")
            
        return True
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        return False


def test_complex_comments():
    """测试复杂注释"""
    logger.info("=" * 80)
    logger.info("测试复杂注释")
    logger.info("=" * 80)
    
    test_code = '''
/* This is a multi-line comment
with class /* nested */ comment */
class /* inline comment */ MyClass /* another comment */ {
    // This is a line comment
    method1() {}
    
    /* Multi-line comment
    in the middle */
    method2() {}
}

// Another line comment
function testFunction() {
    // Comment
}
'''
    
    try:
        parser = ArkTSParser()
        entities = parser.parse_file(test_code, '/test/comments.ets')
        functions = parser.extract_standalone_functions(test_code)
        
        logger.info(f"找到 {len(entities)} 个类, {len(functions)} 个函数")
        for entity in entities:
            logger.info(f"  - {entity.name}: {len(entity.methods)} 个方法")
            
        return True
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        return False


def test_edge_cases():
    """测试各种边界情况"""
    logger.info("=" * 80)
    logger.info("测试各种边界情况")
    logger.info("=" * 80)
    
    test_cases = [
        ("空内容", ""),
        ("只有空格", "   \n  \t  "),
        ("只有注释", "// comment\n/* another */"),
        ("只有导入语句", "import { something } from 'module';\n"),
        ("空类", "class EmptyClass {}"),
        ("空函数", "function emptyFunc() {}"),
        ("类中有空方法", "class Test {\n    emptyMethod() {}\n}"),
    ]
    
    all_passed = True
    parser = ArkTSParser()
    
    for name, code in test_cases:
        logger.info(f"  测试: {name}")
        try:
            entities = parser.parse_file(code, f'/test/{name}.ets')
            functions = parser.extract_standalone_functions(code)
            logger.info(f"    ✓ 成功: {len(entities)} 个类, {len(functions)} 个函数")
        except Exception as e:
            logger.error(f"    ✗ 失败: {e}", exc_info=True)
            all_passed = False
    
    return all_passed


def test_method_calls_extraction():
    """测试方法调用提取"""
    logger.info("=" * 80)
    logger.info("测试方法调用提取")
    logger.info("=" * 80)
    
    test_code = '''
class TestClass {
    method1() {
        this.method2();
        this.method3();
        console.log('test');
        this.method2(); // duplicate
    }
    
    method2() {}
    
    method3() {
        this.method4();
    }
    
    method4() {}
}

function globalFunc() {
    anotherFunc();
}
'''
    
    try:
        parser = ArkTSParser()
        entities = parser.parse_file(test_code, '/test/calls.ets')
        
        logger.info(f"找到 {len(entities)} 个类")
        for entity in entities:
            logger.info(f"  - {entity.name}:")
            for method in entity.methods:
                logger.info(f"    * {method.name} -> calls: {method.calls}")
                
        return True
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        return False


def main():
    """主测试函数"""
    logger.info("开始深层次问题查找测试")
    logger.info("=" * 80)
    
    results = {}
    results['deep_nested'] = test_deep_nested_classes()
    results['complex_comments'] = test_complex_comments()
    results['edge_cases'] = test_edge_cases()
    results['method_calls'] = test_method_calls_extraction()
    
    logger.info("=" * 80)
    logger.info("测试结果汇总:")
    for test_name, passed in results.items():
        status = "通过" if passed else "失败"
        logger.info(f"  {test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        logger.info("✅ 所有深层次问题测试通过！")
        return 0
    else:
        logger.error("❌ 部分测试失败！")
        return 1


if __name__ == '__main__':
    sys.exit(main())

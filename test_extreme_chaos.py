#!/usr/bin/env python3
"""极端混乱场景测试 - 用于发现更深层次的问题"""

import os
import sys
import logging
from parser import ArkTSParser
from ark_analyzer_db import ArkAnalyzerDB
from ark_analyzer_runner import ArkAnalyzerRunner

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ExtremeChaosTest')

def test_extreme_chaos_project():
    """测试极端混乱项目"""
    logger.info("=" * 80)
    logger.info("开始测试极端混乱项目")
    logger.info("=" * 80)
    
    parser = ArkTSParser()
    total_classes = 0
    total_methods = 0
    total_functions = 0
    
    chaos_dir = '/workspace/extreme_chaos_project'
    if not os.path.exists(chaos_dir):
        logger.warning(f"极端混乱项目目录不存在: {chaos_dir}")
        return False
    
    ets_files = [f for f in os.listdir(chaos_dir) if f.endswith('.ets')]
    logger.info(f"找到 {len(ets_files)} 个测试文件")
    
    success_count = 0
    failed_files = []
    
    for i, filename in enumerate(ets_files):
        filepath = os.path.join(chaos_dir, filename)
        logger.info(f"[{i+1}/{len(ets_files)}] 解析文件: {filename}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            entities = parser.parse_file(content, filepath)
            functions = parser.extract_standalone_functions(content)
            
            total_classes += len(entities)
            for entity in entities:
                total_methods += len(entity.methods)
            total_functions += len(functions)
            
            logger.info(f"  成功解析: {len(entities)} 个类, {len(functions)} 个函数")
            success_count += 1
            
        except Exception as e:
            logger.error(f"  解析失败: {filename}, 错误: {e}", exc_info=True)
            failed_files.append((filename, str(e)))
    
    logger.info("=" * 80)
    logger.info(f"极端混乱项目测试完成:")
    logger.info(f"  成功解析: {success_count}/{len(ets_files)}")
    logger.info(f"  总计: {total_classes} 个类, {total_methods} 个方法, {total_functions} 个函数")
    
    if failed_files:
        logger.error(f"失败文件 ({len(failed_files)}):")
        for filename, error in failed_files:
            logger.error(f"  - {filename}: {error}")
        return False
    
    return True

def test_massive_chaos_project():
    """测试大规模混乱项目"""
    logger.info("=" * 80)
    logger.info("开始测试大规模混乱项目")
    logger.info("=" * 80)
    
    db = ArkAnalyzerDB(':memory:')
    db.initialize_schema()
    runner = ArkAnalyzerRunner('', db)
    
    massive_dir = '/workspace/massive_chaos_project'
    if not os.path.exists(massive_dir):
        logger.warning(f"大规模混乱项目目录不存在: {massive_dir}")
        return False
    
    try:
        logger.info(f"开始分析目录: {massive_dir}")
        
        # 直接使用 parser 进行测试，因为 runner 可能没有 analyze_directory 方法
        parser = ArkTSParser()
        total_classes = 0
        total_methods = 0
        total_functions = 0
        
        files_analyzed = 0
        
        for root, dirs, files in os.walk(massive_dir):
            for filename in files:
                if filename.endswith('.ets'):
                    filepath = os.path.join(root, filename)
                    files_analyzed += 1
                    
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    entities = parser.parse_file(content, filepath)
                    functions = parser.extract_standalone_functions(content)
                    
                    total_classes += len(entities)
                    for entity in entities:
                        total_methods += len(entity.methods)
                    total_functions += len(functions)
                    
                    if files_analyzed % 100 == 0:
                        logger.info(f"已分析 {files_analyzed} 个文件...")
        
        logger.info(f"分析完成:")
        logger.info(f"  分析文件数: {files_analyzed}")
        logger.info(f"  找到类数: {total_classes}")
        logger.info(f"  找到方法数: {total_methods}")
        logger.info(f"  找到函数数: {total_functions}")
        
        return True
        
    except Exception as e:
        logger.error(f"大规模混乱项目测试失败: {e}", exc_info=True)
        return False

def test_unicode_extreme():
    """测试极端 Unicode 场景"""
    logger.info("=" * 80)
    logger.info("开始测试极端 Unicode 场景")
    logger.info("=" * 80)
    
    parser = ArkTSParser()
    
    # 构造包含多种 Unicode 字符的复杂测试代码
    test_code = '''
@Entry
@Component
struct 中文组件 {
    build() {
        Column() {
            Text("こんにちは")
            this.한국어메서드()
            this.ไทยฟังก์ชัน()
        }
    }
    
    한국어메서드() {
        console.log("한국어")
    }
    
    ไทยฟังก์ชัน() {
        console.log("ไทย")
    }
}

function 日本語関数() {
    return "にほんご"
}

class РусскийКласс {
    русскийМетод() {
        console.log("Русский")
    }
}

class ΕλληνικήΤάξη {
    ελληνικήΜέθοδος() {
        console.log("Ελληνική")
    }
}

class عربيClass {
    عربيMethod() {
        console.log("عربي")
    }
}

class עבריתClass {
    עבריתMethod() {
        console.log("עברית")
    }
}
'''
    
    try:
        entities = parser.parse_file(test_code, '/test/unicode_extreme.ets')
        functions = parser.extract_standalone_functions(test_code)
        
        logger.info(f"极端 Unicode 测试成功:")
        logger.info(f"  找到 {len(entities)} 个类/结构")
        logger.info(f"  找到 {len(functions)} 个独立函数")
        
        for entity in entities:
            logger.info(f"  - {entity.name}: {len(entity.methods)} 个方法")
            for method in entity.methods:
                logger.info(f"    * {method.name}")
        
        for func in functions:
            logger.info(f"  - {func.name}")
        
        return True
        
    except Exception as e:
        logger.error(f"极端 Unicode 测试失败: {e}", exc_info=True)
        return False

def main():
    """主测试函数"""
    logger.info("开始极端混乱场景测试")
    logger.info("=" * 80)
    
    results = {}
    
    results['extreme_chaos'] = test_extreme_chaos_project()
    results['unicode_extreme'] = test_unicode_extreme()
    
    logger.info("=" * 80)
    logger.info("测试结果汇总:")
    for test_name, passed in results.items():
        status = "通过" if passed else "失败"
        logger.info(f"  {test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        logger.info("✅ 所有极端测试通过！")
        return 0
    else:
        logger.error("❌ 部分测试失败！")
        return 1

if __name__ == '__main__':
    sys.exit(main())

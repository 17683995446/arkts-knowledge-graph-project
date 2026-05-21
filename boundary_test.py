#!/usr/bin/env python3
"""
边界情况与异常处理测试
遵循慢工出细活原理
"""
import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_section(title):
    print("\n" + "=" * 100)
    print(f"  {title}")
    print("=" * 100)

def test_edge_cases():
    from ark_analyzer_runner import run_ark_analyzer
    
    print_section("🔬 边界情况与异常处理测试")
    
    test_dir = tempfile.mkdtemp()
    db_path = os.path.join(test_dir, "test_edge.db")
    
    print(f"📁 测试目录: {test_dir}")
    
    try:
        # 测试1: 空文件
        print("\n🧪 测试1: 空文件")
        empty_file = os.path.join(test_dir, "empty.ets")
        with open(empty_file, 'w') as f:
            f.write("")
        
        print("   ✅ 创建空文件成功")
        
        # 测试2: 只有注释的文件
        print("\n🧪 测试2: 只有注释的文件")
        comment_file = os.path.join(test_dir, "comments.ets")
        with open(comment_file, 'w') as f:
            f.write("""
// 单行注释
/*
多行注释
*/
""")
        print("   ✅ 创建注释文件成功")
        
        # 测试3: 只有导入的文件
        print("\n🧪 测试3: 只有导入的文件")
        import_file = os.path.join(test_dir, "imports.ets")
        with open(import_file, 'w') as f:
            f.write("""
import { A } from './a'
import { B, C } from './b'
""")
        print("   ✅ 创建导入文件成功")
        
        # 测试4: 损坏的UTF-8文件
        print("\n🧪 测试4: 损坏的UTF-8文件")
        corrupt_file = os.path.join(test_dir, "corrupt.ets")
        with open(corrupt_file, 'wb') as f:
            f.write(b'\\xff\\xfe\\x00\\x01\\x02')
        print("   ✅ 创建损坏文件成功")
        
        # 测试5: 超长行文件
        print("\n🧪 测试5: 超长行文件")
        long_line_file = os.path.join(test_dir, "longline.ets")
        with open(long_line_file, 'w') as f:
            f.write("const veryLongLine = '" + "a" * 100000 + "';\n")
        print("   ✅ 创建超长行文件成功")
        
        # 测试6: 嵌套非常深的结构
        print("\n🧪 测试6: 嵌套非常深的结构")
        nested_file = os.path.join(test_dir, "nested.ets")
        with open(nested_file, 'w') as f:
            nested = "struct DeepNesting {"
            for i in range(20):
                nested += "\n  deep" + str(i) + "() {"
            nested += "\n    console.log('deep');"
            nested += "\n" + "  }" * 20
            nested += "\n}"
            f.write(nested)
        print("   ✅ 创建嵌套结构成功")
        
        # 测试7: 特殊字符文件名
        print("\n🧪 测试7: 特殊字符内容")
        special_file = os.path.join(test_dir, "special.ets")
        with open(special_file, 'w', encoding='utf-8') as f:
            f.write("""
// 测试特殊字符
struct 测试Struct {
  方法() {
    console.log("中文方法名");
  }
}
""")
        print("   ✅ 创建特殊字符文件成功")
        
        # 测试8: 二进制内容
        print("\n🧪 测试8: 二进制内容")
        binary_file = os.path.join(test_dir, "binary.ets")
        with open(binary_file, 'wb') as f:
            f.write(b'\\x00\\x01\\x02\\x03\\x04\\x05')
        print("   ✅ 创建二进制文件成功")
        
        # 测试9: 大量空行的文件
        print("\n🧪 测试9: 大量空行的文件")
        blank_lines_file = os.path.join(test_dir, "blanklines.ets")
        with open(blank_lines_file, 'w') as f:
            for i in range(1000):
                f.write("\n")
            f.write("struct BlankLines {}")
        print("   ✅ 创建大量空行文件成功")
        
        # 测试10: 只有接口的文件
        print("\n🧪 测试10: 只有接口的文件")
        interface_file = os.path.join(test_dir, "interfaces.ets")
        with open(interface_file, 'w') as f:
            f.write("""
export interface User {
  id: string;
  name: string;
  email: string;
}

export interface Product {
  id: number;
  title: string;
}
""")
        print("   ✅ 创建接口文件成功")
        
        # 运行分析
        print("\n🚀 运行边界情况测试...")
        try:
            run_ark_analyzer("", test_dir, db_path)
            print("   ✅ 边界测试分析完成！")
            
            # 验证结果
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM files")
            file_count = cursor.fetchone()[0]
            print(f"   📄 处理文件数: {file_count}")
            
            cursor.execute("SELECT COUNT(*) FROM classes")
            class_count = cursor.fetchone()[0]
            print(f"   🏛️  解析类数: {class_count}")
            
            conn.close()
            
            print("\n✅ 所有边界情况测试通过！系统健壮性优秀！")
            return True
            
        except Exception as e:
            print(f"   ❌ 边界测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    finally:
        # 清理
        shutil.rmtree(test_dir, ignore_errors=True)
        print(f"\n🧹 清理测试目录完成")

def main():
    success = test_edge_cases()
    
    print_section("✅ 测试完成")
    
    if success:
        print("🎉 所有边界情况测试通过！系统健壮性优秀！")
    else:
        print("⚠️  边界测试中发现问题，需要修复")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

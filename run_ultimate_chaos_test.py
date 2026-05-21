#!/usr/bin/env python3
"""
运行终极混乱测试 - 简化日志版本
慢工出细活
"""
import os
import sys
import time
import sqlite3
import hashlib
from pathlib import Path
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def log(msg, level="INFO"):
    """详细的日志记录函数"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] [{level}] {msg}")

def print_section(title):
    log("=" * 80, "SECTION")
    log(f"  {title}", "SECTION")
    log("=" * 80, "SECTION")

def main():
    print_section("终极混乱深度压力测试开始")
    
    log("开始初始化...", "INFO")
    
    project_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ultimate_chaos_project")
    db_path = "ultimate_chaos_test.db"
    
    if os.path.exists(db_path):
        log(f"删除旧数据库: {db_path}", "INFO")
        os.remove(db_path)
    
    log("项目路径: " + project_path, "INFO")
    log("数据库路径: " + db_path, "INFO")
    
    # 导入模块
    from ark_analyzer_db import ArkAnalyzerDB
    from parser import ArkTSParser
    
    log("数据库初始化...", "INFO")
    db = ArkAnalyzerDB(db_path)
    db.initialize()
    
    log("解析器初始化...", "INFO")
    parser = ArkTSParser()
    
    # 收集文件
    log("收集文件...", "INFO")
    files = []
    for root, dirs, filenames in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in ('node_modules', 'build', '.git', 'dist')]
        for filename in filenames:
            if filename.endswith(('.ets', '.ts')) and not filename.endswith('.d.ts'):
                files.append(os.path.join(root, filename))
    
    log(f"共收集到 {len(files)} 个文件", "INFO")
    
    # 创建项目
    project_name = Path(project_path).name
    cursor = db.execute("SELECT id FROM projects WHERE name = ? ORDER BY analyzed_at DESC LIMIT 1", (project_name,))
    result = cursor.fetchone()
    
    if result:
        project_id = result[0]
        log(f"使用现有项目，ID: {project_id}", "INFO")
    else:
        cursor = db.execute("""
            INSERT INTO projects (name, path, analyzed_at) 
            VALUES (?, ?, ?)
        """, (project_name, project_path, int(time.time())))
        project_id = cursor.lastrowid
        db.commit()
        log(f"创建新项目，ID: {project_id}", "INFO")
    
    processed_count = 0
    skipped_count = 0
    error_count = 0
    
    log("开始处理文件...", "INFO")
    start_time = time.time()
    
    for i, file_path in enumerate(files):
        if (i + 1) % 25 == 0:
            elapsed = time.time() - start_time
            log(f"进度: {i+1}/{len(files)} ({(i+1)/len(files)*100:.1f}%), 已用 {elapsed:.1f}秒", "INFO")
        
        try:
            log(f"处理 {os.path.basename(file_path)}...", "DEBUG")
            
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            file_hash = hashlib.md5(content.encode()).hexdigest()
            
            cursor = db.execute("""
                SELECT hash FROM files 
                WHERE project_id = ? AND path = ?
            """, (project_id, file_path))
            result = cursor.fetchone()
            
            if result and result[0] == file_hash:
                skipped_count += 1
                continue
            
            if result:
                cursor = db.execute("""
                    SELECT id FROM files WHERE project_id = ? AND path = ?
                """, (project_id, file_path))
                file_id = cursor.fetchone()[0]
                
                db.execute("""
                    DELETE FROM calls WHERE caller_method_id IN (SELECT id FROM methods WHERE file_id = ?)
                """, (file_id,))
                
                db.execute("""
                    DELETE FROM calls WHERE callee_method_id IN (SELECT id FROM methods WHERE file_id = ?)
                """, (file_id,))
                
                db.execute("DELETE FROM methods WHERE file_id = ?", (file_id,))
                db.execute("DELETE FROM decorators WHERE file_id = ?", (file_id,))
                db.execute("DELETE FROM classes WHERE file_id = ?", (file_id,))
                db.execute("DELETE FROM namespaces WHERE file_id = ?", (file_id,))
                db.execute("DELETE FROM files WHERE id = ?", (file_id,))
                db.commit()
            
            line_count = content.count('\n') + 1
            cursor = db.execute("""
                INSERT INTO files (project_id, path, hash, line_count, analyzed_at) 
                VALUES (?, ?, ?, ?, ?)
            """, (project_id, file_path, file_hash, line_count, int(time.time())))
            file_id = cursor.lastrowid
            db.commit()
            
            entities = parser.parse_file(content, file_path)
            functions = parser.extract_standalone_functions(content)
            
            for entity in entities:
                class_signature = f"struct {entity.name}" if entity.flags else f"class {entity.name}"
                
                cursor = db.execute("""
                    INSERT INTO classes (project_id, name, signature, file_id, flags, start_line, end_line) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (project_id, entity.name, class_signature, file_id, entity.flags,
                      entity.start_line, entity.end_line))
                class_id = cursor.lastrowid
                db.commit()
                
                for decorator in entity.decorators:
                    db.execute("""
                        INSERT INTO decorators (project_id, class_id, name) 
                        VALUES (?, ?, ?)
                    """, (project_id, class_id, decorator))
                db.commit()
                
                for method in entity.methods:
                    method_signature = f"{method.name}({method.params})"
                    cursor = db.execute("""
                        INSERT INTO methods (project_id, name, signature, class_id, file_id, 
                                           params, start_line, end_line, is_constructor, is_static) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (project_id, method.name, method_signature, class_id, file_id,
                          method.params, method.start_line, method.end_line,
                          1 if method.name == 'constructor' else 0,
                          1 if method.is_static else 0))
                    method_id = cursor.lastrowid
                    db.commit()
                    
                    SKIP_FUNCTIONS = {
                        'console', 'log', 'error', 'warn', 'info', 'debug',
                        'Text', 'Button', 'Column', 'Row', 'List', 'ListItem',
                        'ForEach', 'if', 'else', 'switch', 'case',
                        'return', 'break', 'continue', 'push', 'pop', 'shift',
                        'unshift', 'slice', 'splice', 'find', 'findIndex',
                        'map', 'filter', 'reduce', 'forEach', 'some', 'every',
                        'includes', 'indexOf', 'join', 'split', 'toString',
                        'toUpperCase', 'toLowerCase', 'trim', 'substring',
                        'substr', 'replace', 'match', 'test', 'exec',
                        'setTimeout', 'setInterval', 'Promise', 'then', 'catch',
                        'finally', 'resolve', 'reject', 'all', 'race', 'any',
                        'get', 'set', 'has', 'delete', 'clear', 'keys',
                        'values', 'entries', 'for', 'while', 'do', 'try',
                        'new', 'typeof', 'instanceof', 'in', 'of', 'void',
                        'undefined', 'null', 'NaN', 'Infinity', 'super',
                        'this', 'self', 'fn', 'callback', 'Math', 'Date',
                        'parseInt', 'parseFloat', 'JSON', 'Number', 'String',
                        'Boolean', 'Array', 'Object'
                    }
                    
                    for callee_name in method.calls:
                        if callee_name in SKIP_FUNCTIONS:
                            continue
                        
                        cursor = db.execute("""
                            SELECT id FROM methods WHERE name = ? AND project_id = ? LIMIT 1
                        """, (callee_name, project_id))
                        callee_id = cursor.fetchone()[0] if cursor.fetchone() else None
                        
                        db.execute("""
                            INSERT INTO calls (project_id, caller_method_id, callee_method_name, callee_method_id, call_type) 
                            VALUES (?, ?, ?, ?, ?)
                        """, (project_id, method_id, callee_name, callee_id, 'call'))
                    db.commit()
            
            for func in functions:
                method_signature = f"function {func.name}({func.params})"
                cursor = db.execute("""
                    INSERT INTO methods (project_id, name, signature, file_id, params, start_line, end_line) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (project_id, func.name, method_signature, file_id,
                      func.params, func.start_line, func.end_line))
                method_id = cursor.lastrowid
                db.commit()
                
                for callee_name in func.calls:
                    if callee_name in SKIP_FUNCTIONS:
                        continue
                    
                    cursor = db.execute("""
                        SELECT id FROM methods WHERE name = ? AND project_id = ? LIMIT 1
                    """, (callee_name, project_id))
                    callee_id = cursor.fetchone()[0] if cursor.fetchone() else None
                    
                    db.execute("""
                        INSERT INTO calls (project_id, caller_method_id, callee_method_name, callee_method_id, call_type) 
                        VALUES (?, ?, ?, ?, ?)
                    """, (project_id, method_id, callee_name, callee_id, 'call'))
                db.commit()
            
            processed_count += 1
            
        except Exception as e:
            log(f"处理文件时异常: {str(e)}", "ERROR")
            import traceback
            log(traceback.format_exc(), "ERROR")
            error_count += 1
    
    # 更新时间
    db.execute("UPDATE projects SET analyzed_at = ? WHERE id = ?", (int(time.time()), project_id))
    db.commit()
    
    # 获取最终统计
    cursor = db.execute("SELECT COUNT(*) FROM files WHERE project_id = ?", (project_id,))
    file_count = cursor.fetchone()[0]
    
    cursor = db.execute("SELECT COUNT(*) FROM classes WHERE project_id = ?", (project_id,))
    class_count = cursor.fetchone()[0]
    
    cursor = db.execute("SELECT COUNT(*) FROM methods WHERE project_id = ?", (project_id,))
    method_count = cursor.fetchone()[0]
    
    cursor = db.execute("SELECT COUNT(*) FROM calls WHERE project_id = ?", (project_id,))
    call_count = cursor.fetchone()[0]
    
    elapsed = time.time() - start_time
    
    print_section("测试完成")
    
    log(f"总耗时: {elapsed:.1f}秒", "INFO")
    log(f"处理文件数: {processed_count}", "INFO")
    log(f"跳过文件数: {skipped_count}", "INFO")
    log(f"错误文件数: {error_count}", "INFO")
    log(f"最终文件数: {file_count}", "INFO")
    log(f"最终类数: {class_count}", "INFO")
    log(f"最终方法数: {method_count}", "INFO")
    log(f"最终调用数: {call_count}", "INFO")
    
    # 验证完整性
    log("验证数据完整性...", "INFO")
    
    cursor = db.execute("""
        SELECT COUNT(*) FROM classes c 
        WHERE c.file_id NOT IN (SELECT id FROM files)
    """)
    orphan_classes = cursor.fetchone()[0]
    
    cursor = db.execute("""
        SELECT COUNT(*) FROM methods m 
        WHERE m.file_id NOT IN (SELECT id FROM files)
    """)
    orphan_methods = cursor.fetchone()[0]
    
    log(f"孤立类数: {orphan_classes}", "INFO")
    log(f"孤立方法数: {orphan_methods}", "INFO")
    
    if orphan_classes == 0 and orphan_methods == 0 and error_count == 0:
        log("🎉 所有数据完整性验证通过！", "INFO")
        log("🎉 系统表现完美！", "INFO")
    else:
        log("⚠️ 发现一些问题需要处理", "WARN")
    
    db.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
终极混乱深度压力测试 - 慢工出细活
包含详细的日志记录功能
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

def get_file_hash(file_path):
    """获取文件哈希，带详细日志"""
    log(f"get_file_hash() 开始", "DEBUG")
    log(f"  输入文件路径: {file_path}", "DEBUG")
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
            log(f"  文件读取成功，长度: {len(content)} 字符", "DEBUG")
            
        file_hash = hashlib.md5(content.encode()).hexdigest()
        log(f"  哈希计算成功: {file_hash}", "DEBUG")
        
        log(f"get_file_hash() 返回: {file_hash}", "DEBUG")
        return file_hash
    except Exception as e:
        log(f"get_file_hash() 异常: {str(e)}", "ERROR")
        return None

def collect_files(project_path):
    """收集所有文件，带详细日志"""
    log("collect_files() 开始", "DEBUG")
    log(f"  项目路径: {project_path}", "DEBUG")
    
    files = []
    
    for root, dirs, filenames in os.walk(project_path):
        log(f"  遍历目录: {root}", "DEBUG")
        
        # 排除特定目录
        dirs[:] = [d for d in dirs if d not in ('node_modules', 'build', '.git', 'dist')]
        log(f"  过滤后的子目录: {dirs}", "DEBUG")
        
        for filename in filenames:
            if filename.endswith(('.ets', '.ts')) and not filename.endswith('.d.ts'):
                full_path = os.path.join(root, filename)
                files.append(full_path)
                log(f"    找到文件: {filename}", "TRACE")
    
    log(f"collect_files() 返回 {len(files)} 个文件", "DEBUG")
    return files

def check_existing_project(db, project_name):
    """检查项目是否存在，带详细日志"""
    log("check_existing_project() 开始", "DEBUG")
    log(f"  项目名称: {project_name}", "DEBUG")
    
    try:
        cursor = db.execute("SELECT id FROM projects WHERE name = ? ORDER BY analyzed_at DESC LIMIT 1", (project_name,))
        result = cursor.fetchone()
        
        if result:
            log(f"  找到现有项目，ID: {result[0]}", "DEBUG")
        else:
            log(f"  未找到现有项目", "DEBUG")
        
        log(f"check_existing_project() 返回: {result}", "DEBUG")
        return result[0] if result else None
        
    except Exception as e:
        log(f"check_existing_project() 异常: {str(e)}", "ERROR")
        return None

def create_project(db, project_name, project_path):
    """创建新项目，带详细日志"""
    log("create_project() 开始", "DEBUG")
    log(f"  项目名称: {project_name}", "DEBUG")
    log(f"  项目路径: {project_path}", "DEBUG")
    
    try:
        cursor = db.execute("""
            INSERT INTO projects (name, path, analyzed_at) 
            VALUES (?, ?, ?)
        """, (project_name, project_path, int(time.time())))
        
        project_id = cursor.lastrowid
        db.commit()
        
        log(f"  项目创建成功，ID: {project_id}", "DEBUG")
        log(f"create_project() 返回: {project_id}", "DEBUG")
        return project_id
        
    except Exception as e:
        log(f"create_project() 异常: {str(e)}", "ERROR")
        return None

def check_file_updated(db, project_id, file_path, file_hash):
    """检查文件是否有更新，带详细日志"""
    log("check_file_updated() 开始", "DEBUG")
    log(f"  项目ID: {project_id}", "DEBUG")
    log(f"  文件路径: {file_path}", "DEBUG")
    log(f"  文件哈希: {file_hash}", "DEBUG")
    
    try:
        cursor = db.execute("""
            SELECT hash FROM files 
            WHERE project_id = ? AND path = ?
        """, (project_id, file_path))
        
        result = cursor.fetchone()
        
        if result and result[0] == file_hash:
            log(f"  文件未变化，跳过", "DEBUG")
            log(f"check_file_updated() 返回: False (未更新)", "DEBUG")
            return False
        else:
            log(f"  文件已更新或新文件", "DEBUG")
            log(f"check_file_updated() 返回: True (需要更新)", "DEBUG")
            return True
            
    except Exception as e:
        log(f"check_file_updated() 异常: {str(e)}", "ERROR")
        return True

def delete_old_file_data(db, project_id, file_path):
    """删除旧的文件数据，带详细日志"""
    log("delete_old_file_data() 开始", "DEBUG")
    log(f"  项目ID: {project_id}", "DEBUG")
    log(f"  文件路径: {file_path}", "DEBUG")
    
    try:
        # 获取文件ID
        cursor = db.execute("""
            SELECT id FROM files WHERE project_id = ? AND path = ?
        """, (project_id, file_path))
        result = cursor.fetchone()
        
        if result:
            file_id = result[0]
            log(f"  文件ID: {file_id}", "DEBUG")
            
            # 删除调用
            log(f"  删除调用记录...", "DEBUG")
            db.execute("""
                DELETE FROM calls 
                WHERE caller_method_id IN (SELECT id FROM methods WHERE file_id = ?)
            """, (file_id,))
            
            db.execute("""
                DELETE FROM calls 
                WHERE callee_method_id IN (SELECT id FROM methods WHERE file_id = ?)
            """, (file_id,))
            
            # 删除方法
            log(f"  删除方法记录...", "DEBUG")
            db.execute("DELETE FROM methods WHERE file_id = ?", (file_id,))
            
            # 删除装饰器
            log(f"  删除装饰器记录...", "DEBUG")
            db.execute("DELETE FROM decorators WHERE file_id = ?", (file_id,))
            
            # 删除类
            log(f"  删除类记录...", "DEBUG")
            db.execute("DELETE FROM classes WHERE file_id = ?", (file_id,))
            
            # 删除命名空间
            log(f"  删除命名空间记录...", "DEBUG")
            db.execute("DELETE FROM namespaces WHERE file_id = ?", (file_id,))
            
            # 删除文件
            log(f"  删除文件记录...", "DEBUG")
            db.execute("DELETE FROM files WHERE id = ?", (file_id,))
            
            log(f"  旧数据删除成功", "DEBUG")
        
        log(f"delete_old_file_data() 完成", "DEBUG")
        
    except Exception as e:
        log(f"delete_old_file_data() 异常: {str(e)}", "ERROR")

def insert_file(db, project_id, file_path, file_hash, line_count):
    """插入文件记录，带详细日志"""
    log("insert_file() 开始", "DEBUG")
    log(f"  项目ID: {project_id}", "DEBUG")
    log(f"  文件路径: {file_path}", "DEBUG")
    log(f"  文件哈希: {file_hash}", "DEBUG")
    log(f"  行数: {line_count}", "DEBUG")
    
    try:
        cursor = db.execute("""
            INSERT INTO files (project_id, path, hash, line_count, analyzed_at) 
            VALUES (?, ?, ?, ?, ?)
        """, (project_id, file_path, file_hash, line_count, int(time.time())))
        
        file_id = cursor.lastrowid
        db.commit()
        
        log(f"  文件插入成功，ID: {file_id}", "DEBUG")
        log(f"insert_file() 返回: {file_id}", "DEBUG")
        return file_id
        
    except Exception as e:
        log(f"insert_file() 异常: {str(e)}", "ERROR")
        return None

def read_file_content(file_path):
    """读取文件内容，带详细日志"""
    log("read_file_content() 开始", "DEBUG")
    log(f"  文件路径: {file_path}", "DEBUG")
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
            log(f"  文件读取成功，长度: {len(content)} 字符", "DEBUG")
            log(f"read_file_content() 返回内容", "DEBUG")
            return content
            
    except Exception as e:
        log(f"read_file_content() 异常: {str(e)}", "ERROR")
        return ""

def strip_comments(content):
    """去除注释，带详细日志"""
    log("strip_comments() 开始", "DEBUG")
    log(f"  输入长度: {len(content)} 字符", "DEBUG")
    
    import re
    
    # 去除块注释
    content = re.sub(r'/\*[\s\S]*?\*/', '', content)
    log(f"  去除块注释后长度: {len(content)} 字符", "DEBUG")
    
    # 去除行注释
    content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
    log(f"  去除行注释后长度: {len(content)} 字符", "DEBUG")
    
    log(f"strip_comments() 返回处理后内容", "DEBUG")
    return content

def parse_file_with_logging(content, file_path, parser):
    """解析文件，带详细日志"""
    log("parse_file_with_logging() 开始", "DEBUG")
    log(f"  文件路径: {file_path}", "DEBUG")
    
    try:
        # 首先收集类名
        log(f"  开始收集类名...", "DEBUG")
        classes = parser.parse_file(content, file_path)
        class_names = set(c.name for c in classes)
        log(f"  收集到 {len(class_names)} 个类名", "DEBUG")
        
        # 然后解析
        log(f"  开始解析内容...", "DEBUG")
        entities = parser.parse_file(content, file_path)
        log(f"  解析到 {len(entities)} 个类/结构", "DEBUG")
        
        # 提取独立函数
        log(f"  开始提取独立函数...", "DEBUG")
        functions = parser.extract_standalone_functions(content)
        log(f"  提取到 {len(functions)} 个独立函数", "DEBUG")
        
        log(f"parse_file_with_logging() 返回结果", "DEBUG")
        return (entities, functions)
        
    except Exception as e:
        log(f"parse_file_with_logging() 异常: {str(e)}", "ERROR")
        return ([], [])

def store_class_with_logging(db, parsed_class, file_id, project_id):
    """存储类，带详细日志"""
    log("store_class_with_logging() 开始", "DEBUG")
    log(f"  类名: {parsed_class.name}", "DEBUG")
    log(f"  文件ID: {file_id}", "DEBUG")
    log(f"  项目ID: {project_id}", "DEBUG")
    
    try:
        class_signature = f"struct {parsed_class.name}" if parsed_class.flags else f"class {parsed_class.name}"
        
        log(f"  类签名: {class_signature}", "DEBUG")
        
        cursor = db.execute("""
            INSERT INTO classes (project_id, name, signature, file_id, flags, start_line, end_line, source_code) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (project_id, parsed_class.name, class_signature, file_id, parsed_class.flags, 
              parsed_class.start_line, parsed_class.end_line, None))
        
        class_id = cursor.lastrowid
        db.commit()
        
        log(f"  类插入成功，ID: {class_id}", "DEBUG")
        
        # 存储装饰器
        for decorator in parsed_class.decorators:
            log(f"    存储装饰器: {decorator}", "DEBUG")
            db.execute("""
                INSERT INTO decorators (project_id, class_id, name) 
                VALUES (?, ?, ?)
            """, (project_id, class_id, decorator))
        
        db.commit()
        log(f"  装饰器存储完成", "DEBUG")
        
        log(f"store_class_with_logging() 返回: {class_id}", "DEBUG")
        return class_id
        
    except Exception as e:
        log(f"store_class_with_logging() 异常: {str(e)}", "ERROR")
        return None

def store_method_with_logging(db, method, class_id, namespace_id, file_id, project_id):
    """存储方法，带详细日志"""
    log("store_method_with_logging() 开始", "DEBUG")
    log(f"  方法名: {method.name}", "DEBUG")
    log(f"  类ID: {class_id}", "DEBUG")
    log(f"  文件ID: {file_id}", "DEBUG")
    
    try:
        method_signature = f"{method.name}({method.params})"
        log(f"  方法签名: {method_signature}", "DEBUG")
        
        cursor = db.execute("""
            INSERT INTO methods (project_id, name, signature, class_id, namespace_id, file_id, 
                               params, return_type, flags, start_line, end_line, source_code, 
                               is_constructor, is_static) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (project_id, method.name, method_signature, class_id, namespace_id, file_id,
              method.params, method.return_type, 0, method.start_line, method.end_line, None,
              1 if method.name == 'constructor' else 0,
              1 if method.is_static else 0))
        
        method_id = cursor.lastrowid
        db.commit()
        
        log(f"  方法插入成功，ID: {method_id}", "DEBUG")
        log(f"store_method_with_logging() 返回: {method_id}", "DEBUG")
        return method_id
        
    except Exception as e:
        log(f"store_method_with_logging() 异常: {str(e)}", "ERROR")
        return None

def store_calls_with_logging(db, method, method_id, project_id):
    """存储调用关系，带详细日志"""
    log("store_calls_with_logging() 开始", "DEBUG")
    log(f"  方法名: {method.name}", "DEBUG")
    log(f"  方法ID: {method_id}", "DEBUG")
    log(f"  调用数量: {len(method.calls)}", "DEBUG")
    
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
    
    try:
        for callee_name in method.calls:
            if callee_name in SKIP_FUNCTIONS:
                log(f"  跳过已知函数: {callee_name}", "TRACE")
                continue
            
            log(f"  处理调用: {callee_name}", "DEBUG")
            
            # 尝试解析
            cursor = db.execute("""
                SELECT id FROM methods WHERE name = ? AND project_id = ? LIMIT 1
            """, (callee_name, project_id))
            
            callee_id = cursor.fetchone()[0] if cursor.fetchone() else None
            
            if callee_id:
                log(f"  找到被调用方ID: {callee_id}", "DEBUG")
            
            db.execute("""
                INSERT INTO calls (project_id, caller_method_id, callee_method_name, callee_method_id, call_type) 
                VALUES (?, ?, ?, ?, ?)
            """, (project_id, method_id, callee_name, callee_id, 'call'))
        
        db.commit()
        log(f"  调用关系存储完成", "DEBUG")
        log(f"store_calls_with_logging() 完成", "DEBUG")
        
    except Exception as e:
        log(f"store_calls_with_logging() 异常: {str(e)}", "ERROR")

def analyze_ultimate_chaos_project(project_path, db_path):
    """分析终极混乱项目，带详细日志"""
    print_section("终极混乱项目深度分析开始")
    
    log("分析开始", "INFO")
    log(f"项目路径: {project_path}", "INFO")
    log(f"数据库路径: {db_path}", "INFO")
    
    try:
        from ark_analyzer_db import ArkAnalyzerDB
        from parser import ArkTSParser
        
        log("初始化数据库...", "INFO")
        db = ArkAnalyzerDB(db_path)
        db.initialize()
        
        log("初始化解析器...", "INFO")
        parser = ArkTSParser()
        
        log("收集文件...", "INFO")
        files = collect_files(project_path)
        log(f"共收集到 {len(files)} 个文件", "INFO")
        
        project_name = Path(project_path).name
        
        log("检查或创建项目...", "INFO")
        project_id = check_existing_project(db, project_name)
        
        if project_id:
            log(f"使用现有项目，ID: {project_id}", "INFO")
        else:
            project_id = create_project(db, project_name, project_path)
        
        if not project_id:
            log("项目创建失败，退出", "ERROR")
            return False
        
        log(f"项目ID: {project_id}", "INFO")
        
        processed_count = 0
        skipped_count = 0
        error_count = 0
        
        log("开始处理文件...", "INFO")
        
        for i, file_path in enumerate(files):
            log(f"处理文件 {i+1}/{len(files)}: {os.path.basename(file_path)}", "INFO")
            
            try:
                log("读取文件...", "DEBUG")
                content = read_file_content(file_path)
                
                if not content:
                    log("文件内容为空，跳过", "WARN")
                    continue
                
                log("计算哈希...", "DEBUG")
                file_hash = get_file_hash(file_path)
                
                if not file_hash:
                    log("哈希计算失败", "ERROR")
                    error_count += 1
                    continue
                
                log("检查文件变化...", "DEBUG")
                needs_update = check_file_updated(db, project_id, file_path, file_hash)
                
                if not needs_update:
                    log("文件未变化，跳过", "INFO")
                    skipped_count += 1
                    continue
                
                log("删除旧数据...", "DEBUG")
                delete_old_file_data(db, project_id, file_path)
                
                log("插入文件记录...", "DEBUG")
                line_count = content.count('\n') + 1
                file_id = insert_file(db, project_id, file_path, file_hash, line_count)
                
                if not file_id:
                    log("文件插入失败", "ERROR")
                    error_count += 1
                    continue
                
                log("解析文件...", "DEBUG")
                entities, functions = parse_file_with_logging(content, file_path, parser)
                
                log(f"解析到 {len(entities)} 个类，{len(functions)} 个函数", "DEBUG")
                
                for entity in entities:
                    log(f"存储类: {entity.name}", "DEBUG")
                    class_id = store_class_with_logging(db, entity, file_id, project_id)
                    
                    if class_id:
                        for method in entity.methods:
                            log(f"  存储方法: {method.name}", "DEBUG")
                            method_id = store_method_with_logging(db, method, class_id, None, file_id, project_id)
                            
                            if method_id:
                                log(f"  存储调用关系...", "DEBUG")
                                store_calls_with_logging(db, method, method_id, project_id)
                
                for func in functions:
                    log(f"存储函数: {func.name}", "DEBUG")
                    method_id = store_method_with_logging(db, func, None, None, file_id, project_id)
                    
                    if method_id:
                        store_calls_with_logging(db, func, method_id, project_id)
                
                processed_count += 1
                log(f"文件处理完成，已处理: {processed_count}, 跳过: {skipped_count}, 错误: {error_count}", "INFO")
                
                if processed_count % 50 == 0:
                    log(f"进度: {processed_count}/{len(files)} 个文件已处理", "INFO")
                
            except Exception as e:
                log(f"处理文件时异常: {str(e)}", "ERROR")
                import traceback
                log(traceback.format_exc(), "ERROR")
                error_count += 1
        
        log(f"更新项目分析时间...", "DEBUG")
        db.execute("UPDATE projects SET analyzed_at = ? WHERE id = ?", (int(time.time()), project_id))
        db.commit()
        
        log("获取最终统计...", "INFO")
        cursor = db.execute("SELECT COUNT(*) FROM files WHERE project_id = ?", (project_id,))
        file_count = cursor.fetchone()[0]
        
        cursor = db.execute("SELECT COUNT(*) FROM classes WHERE project_id = ?", (project_id,))
        class_count = cursor.fetchone()[0]
        
        cursor = db.execute("SELECT COUNT(*) FROM methods WHERE project_id = ?", (project_id,))
        method_count = cursor.fetchone()[0]
        
        cursor = db.execute("SELECT COUNT(*) FROM calls WHERE project_id = ?", (project_id,))
        call_count = cursor.fetchone()[0]
        
        log(f"最终统计 - 文件: {file_count}, 类: {class_count}, 方法: {method_count}, 调用: {call_count}", "INFO")
        
        print_section("分析完成")
        log(f"分析完成！", "INFO")
        log(f"处理文件数: {processed_count}", "INFO")
        log(f"跳过文件数: {skipped_count}", "INFO")
        log(f"错误文件数: {error_count}", "INFO")
        log(f"最终文件数: {file_count}", "INFO")
        log(f"最终类数: {class_count}", "INFO")
        log(f"最终方法数: {method_count}", "INFO")
        log(f"最终调用数: {call_count}", "INFO")
        
        db.close()
        
        return True
        
    except Exception as e:
        log(f"分析过程中异常: {str(e)}", "ERROR")
        import traceback
        log(traceback.format_exc(), "ERROR")
        return False

def main():
    log("终极混乱深度压力测试开始", "INFO")
    
    project_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ultimate_chaos_project")
    db_path = "ultimate_chaos_test.db"
    
    if os.path.exists(db_path):
        log(f"删除旧数据库: {db_path}", "INFO")
        os.remove(db_path)
    
    success = analyze_ultimate_chaos_project(project_path, db_path)
    
    if success:
        log("测试成功完成！", "INFO")
        return 0
    else:
        log("测试失败！", "ERROR")
        return 1

if __name__ == "__main__":
    sys.exit(main())

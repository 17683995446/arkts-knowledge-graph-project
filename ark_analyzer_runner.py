"""ArkAnalyzer integration - runs analysis and stores results in SQLite."""
import os
import time
import hashlib
import logging
from typing import List, Dict, Optional
from pathlib import Path

from ark_analyzer_db import ArkAnalyzerDB
from parser import ArkTSParser, ParsedClass, ParsedMethod

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ArkAnalyzerRunner')


class ArkAnalyzerRunner:
    """Runs ArkAnalyzer and processes results."""
    
    def __init__(self, ark_analyzer_path: str, db: ArkAnalyzerDB):
        logger.debug(f"初始化 ArkAnalyzerRunner，ark_analyzer_path={ark_analyzer_path}")
        self.ark_analyzer_path = ark_analyzer_path
        self.db = db
        self.parser = ArkTSParser()
        self.project_id: Optional[int] = None

    def analyze_project(self, project_path: str, project_name: Optional[str] = None, incremental: bool = True) -> bool:
        """Analyze an ArkTS project and store results in SQLite."""
        if not project_name:
            project_name = Path(project_path).name
            
        logger.info(f"开始分析项目: {project_name}")
        logger.info(f"项目路径: {project_path}")
        logger.info(f"增量模式: {'启用' if incremental else '禁用'}")
        
        try:
            self.db.begin_transaction()
            
            # 获取或创建项目
            logger.debug("获取或创建项目记录")
            existing_project = self._get_existing_project(project_name)
            if existing_project:
                self.project_id = existing_project
                logger.info(f"使用现有项目 ID: {self.project_id}")
            else:
                self.project_id = self.db.insert_project(
                    name=project_name,
                    path=project_path,
                    analyzed_at=int(time.time())
                )
                logger.info(f"创建新的项目 ID: {self.project_id}")
            
            # 收集文件
            logger.debug("开始收集需要分析的文件")
            files_to_process = self._collect_files(project_path)
            logger.info(f"找到 {len(files_to_process)} 个文件需要分析")
            
            # 处理文件
            processed = 0
            skipped = 0
            for i, file_path in enumerate(files_to_process):
                if incremental and self._should_skip_file(file_path):
                    skipped += 1
                else:
                    logger.debug(f"处理文件 {i+1}/{len(files_to_process)}: {file_path}")
                    self._process_file(file_path)
                    processed += 1
                
                if (i + 1) % 10 == 0:
                    logger.info(f"  已处理 {i + 1}/{len(files_to_process)} 个文件 (跳过: {skipped})")
            
            logger.info(f"  文件处理完成: {len(files_to_process)} 个文件 (跳过: {skipped})")
            
            self.db.commit()
            
            # 更新项目分析时间
            logger.debug("更新项目分析时间")
            self.db.conn.execute(
                "UPDATE projects SET analyzed_at = ? WHERE id = ?",
                (int(time.time()), self.project_id)
            )
            self.db.commit()
            
            # 显示最终统计
            stats = self.db.get_project_stats(self.project_id)
            logger.info(f"\n项目分析完成!")
            logger.info(f"  文件数量: {stats['files']}")
            logger.info(f"  类数量: {stats['classes']}")
            logger.info(f"  方法数量: {stats['methods']}")
            logger.info(f"  调用关系: {stats['calls']}")
            logger.info(f"  增量更新: 跳过 {skipped} 个未变更文件")
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"项目分析过程中出错: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def _get_existing_project(self, project_name: str) -> Optional[int]:
        """获取已存在的项目ID"""
        logger.debug(f"查询已存在的项目: {project_name}")
        try:
            cursor = self.db.conn.execute(
                "SELECT id FROM projects WHERE name = ? ORDER BY analyzed_at DESC LIMIT 1",
                (project_name,)
            )
            result = cursor.fetchone()
            if result:
                logger.debug(f"找到项目 ID: {result[0]}")
            else:
                logger.debug(f"未找到项目: {project_name}")
            return result[0] if result else None
        except Exception as e:
            logger.warning(f"查询项目时出错: {e}")
            return None

    def _should_skip_file(self, file_path: str) -> bool:
        """检查文件是否有变化"""
        logger.debug(f"检查文件是否需要跳过: {file_path}")
        try:
            # 读取文件
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # 计算哈希
            file_hash = hashlib.md5(content.encode()).hexdigest()
            logger.debug(f"文件哈希: {file_hash}")
            
            # 查询数据库中的哈希
            cursor = self.db.conn.execute(
                "SELECT hash FROM files WHERE project_id = ? AND path = ?",
                (self.project_id, file_path)
            )
            result = cursor.fetchone()
            
            # 如果哈希相同，跳过
            if result and result[0] == file_hash:
                logger.debug(f"文件未变更，跳过: {file_path}")
                return True
            
            # 如果文件不存在或有变化，需要处理
            # 先删除旧记录
            if result:
                logger.debug(f"文件已变更，删除旧记录: {file_path}")
                self._delete_file_records(file_path)
            
            return False
            
        except Exception as e:
            logger.warning(f"检查文件时出错: {e}")
            return False

    def _delete_file_records(self, file_path: str):
        """删除文件相关的所有记录"""
        logger.debug(f"删除文件相关记录: {file_path}")
        try:
            # 获取文件ID
            cursor = self.db.conn.execute(
                "SELECT id FROM files WHERE project_id = ? AND path = ?",
                (self.project_id, file_path)
            )
            result = cursor.fetchone()
            if not result:
                logger.debug(f"未找到文件记录: {file_path}")
                return
            
            file_id = result[0]
            logger.debug(f"文件 ID: {file_id}")
            
            # 删除调用关系
            logger.debug("删除调用关系")
            self.db.conn.execute(
                "DELETE FROM calls WHERE caller_method_id IN (SELECT id FROM methods WHERE file_id = ?)",
                (file_id,)
            )
            self.db.conn.execute(
                "DELETE FROM calls WHERE callee_method_id IN (SELECT id FROM methods WHERE file_id = ?)",
                (file_id,)
            )
            
            # 删除方法
            logger.debug("删除方法记录")
            self.db.conn.execute(
                "DELETE FROM methods WHERE file_id = ?",
                (file_id,)
            )
            
            # 删除装饰器
            logger.debug("删除装饰器记录")
            self.db.conn.execute(
                "DELETE FROM decorators WHERE file_id = ?",
                (file_id,)
            )
            
            # 删除类
            logger.debug("删除类记录")
            self.db.conn.execute(
                "DELETE FROM classes WHERE file_id = ?",
                (file_id,)
            )
            
            # 删除命名空间
            logger.debug("删除命名空间记录")
            self.db.conn.execute(
                "DELETE FROM namespaces WHERE file_id = ?",
                (file_id,)
            )
            
            # 删除文件记录
            logger.debug("删除文件记录")
            self.db.conn.execute(
                "DELETE FROM files WHERE id = ?",
                (file_id,)
            )
            
            logger.debug(f"文件记录删除完成: {file_path}")
            
        except Exception as e:
            logger.error(f"删除文件记录时出错: {e}")

    def _collect_files(self, project_path: str) -> List[str]:
        """Collect all ArkTS/TypeScript files from the project."""
        logger.debug(f"开始收集项目文件: {project_path}")
        files = []
        project = Path(project_path)
        
        for root, dirs, filenames in os.walk(project):
            # Skip node_modules and build directories
            dirs[:] = [d for d in dirs if d not in (
                'node_modules', 'build', '.build', '.cxx', 'dist', 'target', '.git'
            )]
            
            for filename in filenames:
                if filename.endswith(('.ets', '.ts')) and not filename.endswith('.d.ts'):
                    files.append(os.path.join(root, filename))
        
        logger.debug(f"收集到 {len(files)} 个文件")
        return files

    def _process_file(self, file_path: str):
        """Process a single file and store its entities in the database."""
        logger.debug(f"处理文件: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
        except Exception as e:
            logger.warning(f"无法读取文件 {file_path}: {e}")
            return
        
        file_hash = hashlib.md5(content.encode()).hexdigest()
        line_count = content.count('\n') + 1
        logger.debug(f"文件哈希: {file_hash}, 行数: {line_count}")
        
        file_id = self.db.insert_file(
            project_id=self.project_id,
            path=file_path,
            hash_val=file_hash,
            line_count=line_count,
            analyzed_at=int(time.time())
        )
        
        if file_id is None:
            logger.debug("文件未变更，跳过处理")
            return
        
        logger.debug(f"文件 ID: {file_id}")
        
        entities = self.parser.parse_file(content, file_path)
        standalone_funcs = self.parser.extract_standalone_functions(content)
        
        logger.debug(f"找到 {len(entities)} 个类/结构，{len(standalone_funcs)} 个独立函数")
        
        for entity in entities:
            self._store_class(entity, file_id, file_path)
            
        for func in standalone_funcs:
            self._store_standalone_function(func, file_id, file_path)
        
        logger.debug(f"文件处理完成: {file_path}")
    
    def _store_class(self, entity: ParsedClass, file_id: int, file_path: str):
        """Store a parsed class/struct in the database."""
        logger.debug(f"存储类: {entity.name}")
        # Insert class
        class_id = self.db.insert_class(
            project_id=self.project_id,
            name=entity.name,
            signature=f"struct {entity.name}" if entity.flags else f"class {entity.name}",
            file_id=file_id,
            namespace_id=None,
            flags=entity.flags,
            start_line=entity.start_line,
            end_line=entity.end_line,
            source_code=None
        )
        logger.debug(f"类 ID: {class_id}")
        
        # Insert decorators
        for decorator in entity.decorators:
            logger.debug(f"存储装饰器: {decorator}")
            self.db.insert_decorator(
                project_id=self.project_id,
                class_id=class_id,
                method_id=None,
                name=decorator,
                args=None
            )
        
        # Insert methods and create relationships
        logger.debug(f"存储 {len(entity.methods)} 个方法")
        for method in entity.methods:
            method_id = self._store_method(method, class_id, None, file_id, file_path)
            self._store_method_calls(method, method_id)

    def _store_method(self, method: ParsedMethod, class_id: Optional[int], 
                     namespace_id: Optional[int], file_id: int, file_path: str) -> int:
        """Store a parsed method in the database."""
        logger.debug(f"存储方法: {method.name} (第 {method.start_line}-{method.end_line} 行)")
        return self.db.insert_method(
            project_id=self.project_id,
            name=method.name,
            signature=f"{method.name}({method.params})",
            class_id=class_id,
            namespace_id=namespace_id,
            file_id=file_id,
            params=method.params,
            return_type=method.return_type,
            flags=0,
            start_line=method.start_line,
            end_line=method.end_line,
            source_code=None,
            is_constructor=1 if method.name == 'constructor' else 0,
            is_static=1 if method.is_static else 0
        )

    def _store_method_calls(self, method: ParsedMethod, method_id: int):
        """Store all calls from a method."""
        # Skip known library functions that shouldn't be tracked
        SKIP_FUNCTIONS = {
            'console', 'log', 'error', 'warn', 'info', 'debug',
            'Text', 'Button', 'Column', 'Row', 'List', 
            'ListItem', 'ForEach', 'if', 'else', 'switch', 'case',
            'return', 'break', 'continue', 'push', 'pop', 'shift',
            'unshift', 'slice', 'splice', 'find', 'findIndex',
            'map', 'filter', 'reduce', 'forEach', 'some', 'every',
            'includes', 'indexOf', 'join', 'split', 'toString',
            'toUpperCase', 'toLowerCase', 'trim', 'substring',
            'substr', 'replace', 'match', 'test', 'exec',
            'setTimeout', 'setInterval', 'Promise', 'then', 'catch',
            'finally', 'resolve', 'reject', 'all', 'race', 'any',
            'get', 'set', 'has', 'delete', 'clear', 'keys',
            'values', 'entries', 'for...of', 'for...in', 'while',
            'do...while', 'try', 'catch', 'finally', 'throw',
            'new', 'typeof', 'instanceof', 'in', 'of', 'delete',
            'void', 'undefined', 'null', 'NaN', 'Infinity',
            'super', 'this', 'self', 'fn', 'callback'
        }
        
        logger.debug(f"存储方法 {method.name} 的调用关系 (共 {len(method.calls)} 个)")
        for callee_name in method.calls:
            # Skip known library functions
            if callee_name in SKIP_FUNCTIONS:
                continue
            
            # Try to resolve the callee method ID
            callee_method_id = self._resolve_callee_method_id(callee_name)
            logger.debug(f"存储调用关系: {method.name} -> {callee_name} (ID: {callee_method_id})")
            
            self.db.insert_call(
                project_id=self.project_id,
                caller_method_id=method_id,
                callee_method_name=callee_name,
                callee_signature=None,
                callee_method_id=callee_method_id,
                call_type='call'
            )

    def _resolve_callee_method_id(self, method_name: str) -> Optional[int]:
        """Try to resolve a method name to its database ID."""
        try:
            cursor = self.db.conn.execute(
                "SELECT id FROM methods WHERE name = ? AND project_id = ? LIMIT 1",
                (method_name, self.project_id)
            )
            result = cursor.fetchone()
            if result:
                logger.debug(f"解析到方法 ID: {result[0]} for {method_name}")
            else:
                logger.debug(f"未找到方法: {method_name}")
            return result[0] if result else None
        except Exception as e:
            logger.warning(f"解析方法时出错: {e}")
            return None

    def _store_standalone_function(self, func: ParsedMethod, file_id: int, file_path: str):
        """Store a standalone function in the database."""
        logger.debug(f"存储独立函数: {func.name}")
        method_id = self.db.insert_method(
            project_id=self.project_id,
            name=func.name,
            signature=f"function {func.name}({func.params})",
            class_id=None,
            namespace_id=None,
            file_id=file_id,
            params=func.params,
            return_type=func.return_type,
            flags=0,
            start_line=func.start_line,
            end_line=func.end_line,
            source_code=None,
            is_constructor=0,
            is_static=0
        )
        
        self._store_method_calls(func, method_id)


def run_ark_analyzer(ark_analyzer_path: str, project_path: str, db_path: str = "ark_graph.db") -> bool:
    """Main function to run analysis and populate database."""
    logger.info(f"开始运行 ArkAnalyzer，项目路径: {project_path}")
    # 不再删除数据库，支持增量更新
    db = ArkAnalyzerDB(db_path)
    db.initialize()
    
    runner = ArkAnalyzerRunner(ark_analyzer_path, db)
    result = runner.analyze_project(project_path)
    logger.info(f"ArkAnalyzer 运行完成，结果: {'成功' if result else '失败'}")
    return result

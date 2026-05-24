# 代码分层分析文档

## 1. 架构分层

### 1.1 分层结构

```
┌─────────────────────────────────────┐
│     用户接口层 (UI Layer)            │
│  (未来开发：Web界面、CLI、IDE插件)  │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│     业务逻辑层 (Business Logic)     │
│  - ArkAnalyzerRunner                │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│     数据访问层 (Data Access)        │
│  - ArkAnalyzerDB                    │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│     解析层 (Parser Layer)           │
│  - ArkTSParser                      │
└─────────────────────────────────────┘
```

### 1.2 模块依赖关系

- **ArkAnalyzerRunner** → ArkAnalyzerDB, ArkTSParser
- **ArkAnalyzerDB** → sqlite3 (外部依赖)
- **ArkTSParser** → re, logging (标准库)

### 1.3 调用链路

```
analyze_project()
  ↓
_collect_files()
  ↓
_process_file()
  ↓
parse_file() → _find_structs() → _parse_struct() → _extract_methods_from_body()
  ↓
extract_standalone_functions()
  ↓
_store_class() / _store_standalone_function()
  ↓
insert_class() / insert_method() / insert_call()
```

## 2. 核心模块详细分析

### 2.1 parser.py - 解析层

#### 职责
- 解析ArkTS/TypeScript源码
- 提取类、结构体、方法、函数
- 识别装饰器和调用关系
- 处理Unicode标识符

#### 核心类与方法

| 类/方法 | 职责 | 参数 | 返回值 |
|---------|------|------|--------|
| ArkTSParser | 主解析器 | 无 | 实例 |
| parse_file() | 解析整个文件 | content, file_path | List[ParsedClass] |
| extract_standalone_functions() | 提取独立函数 | content | List[ParsedMethod] |
| _strip_comments_and_map() | 去除注释并建立位置映射 | content | Tuple[str, List[int]] |
| _find_structs() | 查找类和结构体 | clean_content, full_content, pos_map | List[Tuple] |
| _parse_struct() | 解析单个类/结构体 | content, match_info, pos_map | ParsedClass |
| _extract_methods_from_body() | 从类体提取方法 | clean_body, full_body, body_pos_map, base_line, body_start | List[ParsedMethod] |

#### 正则表达式

- `method_pattern`: 匹配方法定义
- `struct_pattern`: 匹配类/结构体定义
- `function_pattern`: 匹配独立函数
- `call_pattern`: 匹配函数调用

#### 参数规则

- **文件路径**: 字符串，绝对路径
- **源码内容**: UTF-8编码的字符串
- **位置映射**: 整数列表，长度等于清理后内容长度
- **匹配信息**: 包含名称、行号、装饰器等信息的元组

#### 边界条件

- 空文件 → 返回空列表
- 文件只有注释 → 返回空列表
- 未闭合的括号 → 可能导致解析失败
- 超大文件 → 性能可能下降

### 2.2 ark_analyzer_db.py - 数据访问层

#### 职责
- SQLite数据库操作
- 存储和查询代码知识图谱
- 事务管理
- 索引优化

#### 核心表

| 表名 | 用途 | 关键字段 |
|------|------|----------|
| projects | 项目信息 | id, name, path, analyzed_at |
| files | 文件信息 | id, project_id, path, hash, line_count |
| classes | 类定义 | id, project_id, name, file_id, flags, start_line, end_line |
| methods | 方法定义 | id, project_id, name, class_id, params, return_type |
| calls | 调用关系 | id, project_id, caller_method_id, callee_method_name, callee_method_id |
| decorators | 装饰器信息 | id, project_id, class_id, method_id, name, args |
| namespaces | 命名空间 | id, project_id, name, file_id |
| fields | 字段 | id, project_id, name, class_id, type |
| imports | 导入关系 | id, project_id, file_id, import_path |
| exports | 导出关系 | id, project_id, file_id, export_name |

#### 核心方法

| 方法 | 职责 | 关键参数 |
|------|------|----------|
| initialize() | 初始化数据库连接和表 | 无 |
| begin_transaction() | 开始事务 | 无 |
| commit() | 提交事务 | 无 |
| rollback() | 回滚事务 | 无 |
| insert_project() | 插入项目 | name, path, analyzed_at |
| insert_file() | 插入文件 | project_id, path, hash_val, line_count |
| insert_class() | 插入类 | project_id, name, file_id, flags, start_line, end_line |
| insert_method() | 插入方法 | project_id, name, class_id, params, return_type |
| insert_call() | 插入调用关系 | project_id, caller_method_id, callee_method_name |
| query_class() | 查询类 | project_id, class_name |
| query_methods_by_class() | 查询类的所有方法 | class_id |
| get_project_stats() | 获取项目统计 | project_id |
| export_graph() | 导出知识图谱 | project_id |

#### 事务逻辑

- 每个文件处理前不单独开启事务
- `analyze_project()` 中开启一个大事务
- 成功时 `commit()`，失败时 `rollback()`

### 2.3 ark_analyzer_runner.py - 业务逻辑层

#### 职责
- 协调整个分析流程
- 增量更新处理
- 文件收集和处理
- 解析结果存储

#### 核心类与方法

| 类/方法 | 职责 |
|---------|------|
| ArkAnalyzerRunner | 主运行器 |
| analyze_project() | 分析整个项目 |
| _collect_files() | 收集项目文件 |
| _process_file() | 处理单个文件 |
| _store_class() | 存储类到数据库 |
| _store_method() | 存储方法到数据库 |
| _store_method_calls() | 存储调用关系 |
| _should_skip_file() | 检查文件是否需要跳过 |
| _delete_file_records() | 删除文件相关记录 |

#### 增量更新逻辑

1. 计算文件MD5哈希
2. 与数据库中的哈希比对
3. 如果相同，跳过该文件
4. 如果不同，删除旧记录，重新解析

## 3. 数据流向分析

### 3.1 完整数据流

```
源码文件
  ↓
读取内容 (UTF-8编码)
  ↓
去除注释 & 建立位置映射
  ↓
正则表达式匹配
  ↓
提取实体 (类/方法/函数)
  ↓
解析装饰器 & 计算标志位
  ↓
提取方法调用
  ↓
构建Python数据结构 (ParsedClass/ParsedMethod)
  ↓
存储到SQLite数据库
  ↓
建立索引
  ↓
可查询
```

### 3.2 状态变更

| 阶段 | 状态 | 描述 |
|------|------|------|
| 初始化 | 准备就绪 | 数据库连接，解析器实例化 |
| 分析中 | 处理中 | 正在遍历文件，解析，存储 |
| 完成 | 完成 | 所有文件处理完成，事务提交 |
| 失败 | 回滚 | 出错时回滚到初始状态 |

## 4. 隐藏隐性规则

1. **注释处理**: 注释在解析前被去除，但位置映射保留
2. **装饰器识别**: 只识别预定义的装饰器 (@Component, @Entry, @State)
3. **跳过列表**: 大量内置函数和关键字被跳过，不记录为调用
4. **Unicode支持**: 支持中文、日文、韩文、泰语等Unicode字符作为标识符
5. **哈希比较**: 使用MD5进行增量更新检测
6. **外键约束**: 启用了外键约束，但删除级联
7. **事务粒度**: 整个项目分析作为一个大事务

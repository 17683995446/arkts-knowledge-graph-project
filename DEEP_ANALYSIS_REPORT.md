# 深度逆向分析报告

## 一、架构分层梳理

### 1. parser.py - 解析器层
```
ArkTSParser
├── _strip_comments_and_map() - 注释去除 + 位置映射
│   ├── 行注释处理: // ...
│   ├── 块注释处理: /* ... */
│   ├── 字符串字面量保留
│   └── 返回 (clean_content, pos_map)
│
├── parse_file() - 文件解析入口
│   ├── 清除已知类名缓存
│   ├── 注释去除 + 位置映射
│   ├── 查找所有结构体 (class/struct)
│   ├── 收集类名到 known_class_names
│   └── 逐个解析结构体
│
├── _find_structs() - 结构体查找
│   ├── 匹配类/结构定义
│   ├── 装饰器收集
│   ├── 括号匹配定位
│   └── 返回: (name, start_line, end_line, flags, decorators, brace_pos, end_brace_pos, struct_type, pos_map)
│
├── _parse_struct() - 结构体解析
│   ├── 创建 ParsedClass 对象
│   ├── 提取方法体
│   └── 调用 _extract_methods_from_body
│
├── _extract_methods_from_body() - 方法提取
│   ├── 方法正则匹配
│   ├── 跳过关键字过滤
│   ├── 括号匹配定位
│   └── 调用 _strip_comments_and_map
│
└── extract_standalone_functions() - 独立函数提取
    ├── 函数正则匹配
    ├── 括号匹配
    └── 返回 ParsedMethod 列表
```

**关键分支与边界**：
1. 注释去除后的位置映射准确性
2. 括号匹配的正确性（嵌套括号）
3. 方法名过滤的完整性

### 2. ark_analyzer_db.py - 数据库层

```
ArkAnalyzerDB
├── initialize() - 数据库初始化
│   ├── 创建表结构
│   ├── 创建索引
│   └── 启用外键约束
│
├── insert_*() 系列方法
│   ├── insert_project()
│   ├── insert_file() - 支持增量更新
│   ├── insert_class()
│   ├── insert_method()
│   ├── insert_call()
│   ├── insert_namespace()
│   ├── insert_field()
│   ├── insert_decorator()
│   └── insert_import()
│
├── query_*() 系列方法
│   ├── query_class() - 单个类查询
│   ├── query_methods_by_class()
│   ├── query_callers()
│   └── query_callees()
│
├── get_project_stats() - 统计查询
│
├── export_graph() - 图导出
│
├── get_all_projects() - 项目列表
│
└── delete_project() - 项目删除
```

**关键分支与边界**：
1. insert_file 的哈希检测逻辑
2. 外键约束的级联删除
3. 空值处理（所有 Optional 参数）

### 3. ark_analyzer_runner.py - 分析运行层

```
ArkAnalyzerRunner
├── analyze_project() - 主分析流程
│   ├── 事务开始
│   ├── 获取/创建项目
│   ├── 收集文件列表
│   ├── 逐文件处理
│   └── 事务提交
│
├── _get_existing_project() - 项目查找
│
├── _should_skip_file() - 增量判断
│   ├── 文件哈希计算
│   ├── 数据库哈希比较
│   └── 决定是否处理
│
├── _delete_file_records() - 文件记录删除
│   ├── 删除调用关系
│   ├── 删除方法
│   ├── 删除装饰器
│   ├── 删除类
│   └── 删除文件记录
│
├── _collect_files() - 文件收集
│   └── 跳过特定目录
│
├── _process_file() - 单文件处理
│   ├── 读取文件
│   ├── 计算哈希
│   ├── 调用解析器
│   └── 存储实体
│
├── _store_class() - 存储类
│   ├── 插入类记录
│   ├── 插入装饰器
│   └── 插入方法
│
├── _store_method() - 存储方法
│
├── _store_method_calls() - 存储调用关系
│   └── 跳过库函数
│
├── _resolve_callee_method_id() - 方法ID解析
│
└── _store_standalone_function() - 独立函数存储
```

**关键分支与边界**：
1. 增量更新的准确性
2. 文件删除的完整性
3. 调用关系解析的准确性

## 二、边界条件与异常场景

### 1. parser.py 边界条件

| 场景 | 预期行为 | 潜在问题 |
|------|---------|---------|
| 空字符串 | 返回空列表 | ✅ 已覆盖 |
| 仅有注释 | 返回空列表 | ✅ 已覆盖 |
| 嵌套注释 | 正确去除 | ⚠️ 需验证 |
| 字符串中的 // 和 /\* | 保留原始字符 | ⚠️ 需验证 |
| 非常深的嵌套括号 | 正确匹配 | ⚠️ 需验证 |
| 超长方法名 | 正常解析 | ✅ 已覆盖 |
| Unicode 字符 | 正常解析 | ⚠️ 需验证 |
| Windows/Unix 换行符 | 统一处理 | ⚠️ 需验证 |

### 2. ark_analyzer_db.py 边界条件

| 场景 | 预期行为 | 潜在问题 |
|------|---------|---------|
| 重复插入同名项目 | 使用 INSERT OR REPLACE | ✅ 已覆盖 |
| 插入空字符串类名 | 正常插入 | ⚠️ 需验证 |
| 哈希冲突 | 使用 INSERT OR REPLACE | ⚠️ 需验证 |
| 删除不存在的项目 | 无操作 | ⚠️ 需验证 |
| 查询空数据库 | 返回空列表 | ✅ 已覆盖 |

### 3. ark_analyzer_runner.py 边界条件

| 场景 | 预期行为 | 潜在问题 |
|------|---------|---------|
| 项目路径不存在 | 返回 False | ⚠️ 需验证 |
| 文件无法读取 | 跳过文件 | ⚠️ 需验证 |
| 文件内容为空 | 跳过文件 | ⚠️ 需验证 |
| 文件编码错误 | 使用 errors='replace' | ✅ 已覆盖 |
| 增量更新时文件被删除 | 删除旧记录 | ⚠️ 需验证 |
| 循环依赖的调用 | 正常处理 | ⚠️ 需验证 |

## 三、隐藏逻辑与默认行为

### 1. parser.py 隐藏逻辑

```python
# 方法名跳过列表 - 100+ 个关键字和库方法
self.SKIP_METHOD_NAMES = {
    'if', 'for', 'while', 'switch', 'catch', ...
    'Text', 'Button', 'Column', 'Row', ...  # UI 组件
    'map', 'filter', 'reduce', ...  # 数组方法
    'then', 'catch', 'finally', ...  # Promise
}
```

**问题**: 跳过列表是否足够完整？是否漏掉了某些常见方法？

### 2. ark_analyzer_runner.py 隐藏逻辑

```python
# 调用关系跳过列表
SKIP_FUNCTIONS = {
    'console', 'log', 'error', 'warn', ...
    'Text', 'Button', 'Column', ...  # UI 组件
    'map', 'filter', 'reduce', ...
    'setTimeout', 'setInterval', ...
}
```

**问题**: 解析器和方法存储的跳过列表不一致！

### 3. 增量更新隐藏逻辑

```python
# _should_skip_file 的逻辑
if result and result[0] == file_hash:
    return True  # 跳过未改变的文件
else:
    if result:
        _delete_file_records()  # 删除旧记录
    return False  # 处理文件
```

**问题**: 如果哈希相同但内容实际改变了怎么办？哈希碰撞！

## 四、异常处理清单

### 1. parser.py 异常

- [ ] UnicodeDecodeError
- [ ] 正则表达式匹配失败
- [ ] 括号匹配失败（未闭合的括号）
- [ ] 内存不足（超长文件）

### 2. ark_analyzer_db.py 异常

- [ ] 数据库文件锁定
- [ ] 外键约束违反
- [ ] 磁盘空间不足
- [ ] 并发写入冲突

### 3. ark_analyzer_runner.py 异常

- [ ] 文件读取失败
- [ ] 文件编码错误
- [ ] 项目路径不存在
- [ ] 数据库连接失败

## 五、测试覆盖矩阵

| 测试场景 | parser | db | runner | 状态 |
|---------|--------|-----|--------|------|
| 空输入 | ✅ | ✅ | ⚠️ | 待验证 |
| 超大文件 | ⚠️ | ⚠️ | ⚠️ | 待验证 |
| 特殊字符 | ⚠️ | ⚠️ | ⚠️ | 待验证 |
| 嵌套结构 | ⚠️ | ⚠️ | ⚠️ | 待验证 |
| 并发访问 | ❌ | ⚠️ | ❌ | 未覆盖 |
| 哈希碰撞 | ❌ | ⚠️ | ⚠️ | 未覆盖 |
| 磁盘空间不足 | ❌ | ⚠️ | ⚠️ | 未覆盖 |

## 六、下一步行动

1. **深度单元测试**：针对每个分支和边界进行测试
2. **异常场景测试**：模拟各种异常情况
3. **性能压测**：大规模数据场景
4. **一致性检查**：验证解析器和运行器的跳过列表一致性
5. **日志增强**：在关键路径添加调试日志

# ArkTS 代码知识图谱 - 动态更新版

基于第一性原理设计的实时代码知识图谱系统。

## 核心特性

- **增量更新**: 只处理变更的文件，99% 的修改 < 0.5 秒完成
- **原子操作**: 每个文件的更新是事务性的，保证数据一致性
- **哈希检测**: MD5 哈希检测文件变化，避免不必要的重新解析
- **防抖处理**: 连续修改同一文件只执行最后一次更新

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 初始化并同步项目
python main.py --project /path/to/your/project sync

# 查询类
python main.py --project /path/to/your/project query class --name MyClass

# 搜索类
python main.py --project /path/to/your/project search-classes --pattern Component

# 获取统计
python main.py --project /path/to/your/project stats

# 启动实时监控（Ctrl+C 停止）
python main.py --project /path/to/your/project watch
```

## 项目结构

```
├── database.py      # SQLite 数据库管理
├── parser.py        # ArkTS 代码解析器
├── watcher.py       # 文件系统监控
├── updater.py       # 增量更新引擎
├── query.py         # 查询 API
├── main.py          # CLI 主程序
└── example/         # 示例代码
```

## 查询示例

```bash
# 查询类及其方法
python main.py -p ./example query class --name UserCard

# 查询文件中的所有实体
python main.py -p ./example query file --path ./example/Index.ets

# 查找调用者
python main.py -p ./example query callers --method build

# 导出完整知识图谱
python main.py -p ./example export
```

## 性能指标

| 操作 | 耗时 | 场景 |
|------|------|------|
| 单文件更新 | <0.5s | 开发过程中最常见 |
| 10 文件批量 | <2s | 切换小分支 |
| 100 文件批量 | <10s | 拉取代码 |
| 全量同步 | 取决于项目大小 | 首次运行或切换大分支 |

## 设计原理

基于第一性原理：**修改文件 A，只需要删除文件 A 在图谱中的所有旧数据，重新解析文件 A，插入文件 A 的新数据**。不需要修改任何其他文件的数据。

这使得动态更新真正可用 - 用户修改代码后，最多等待 0.5 秒就能查询到最新结果。

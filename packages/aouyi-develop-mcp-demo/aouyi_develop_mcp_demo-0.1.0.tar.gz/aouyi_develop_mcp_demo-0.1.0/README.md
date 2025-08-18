# 开发者工具 MCP 服务器

一个专为开发者设计的 MCP (Model Context Protocol) 服务器，提供常用的开发工具功能。

## 功能特性

### 🛠️ 工具 (Tools)
- **format_json**: JSON 格式化工具，美化 JSON 字符串
- **count_lines**: 文件统计工具，统计行数、字符数等信息
- **list_files**: 文件列表工具，列出目录下的文件并可按扩展名过滤

### 📄 资源 (Resources)
- **project://info**: 获取当前项目的基本信息

### 💡 提示词 (Prompts)
- **code_review_prompt**: 生成代码审查提示词

## 安装与运行

### 环境要求
- Python >= 3.13
- mcp[cli] >= 1.13.0

### 安装依赖
```bash
pip install mcp[cli]
```

### 运行服务器
```bash
python main.py
```

## 使用示例

### 格式化 JSON
```python
# 输入混乱的 JSON
format_json('{"name":"张三","age":25}')
# 输出格式化的 JSON
```

### 统计文件信息
```python
count_lines("main.py")
# 返回文件的行数、字符数等统计信息
```

### 列出文件
```python
list_files(".", ".py")
# 列出当前目录下所有 Python 文件
```

## 比赛信息

本项目参加**蓝耘元生代MCP广场：开启服务调用新旅程**比赛
- 分类：开发者工具
- 特点：简单实用，本地 stdio 运行
- 目标：为开发者提供便捷的日常开发工具

## 技术架构

- 基于 FastMCP 框架
- 使用 stdio 传输协议
- 支持工具、资源和提示词三种功能类型
- 轻量级设计，易于部署和使用

## 许可证

MIT License
# Web Tool MCP Server

一个基于FastMCP框架的Web工具MCP服务器，提供网页内容获取和搜索功能。

## 功能特性

- **网页内容获取**: 获取指定URL的网页内容
- **内容搜索**: 在网页内容中搜索特定关键词
- **HTML解析**: 自动解析HTML并提取文本内容
- **错误处理**: 完善的错误处理和超时机制

## 安装

### 从源码安装

```bash
# 克隆项目
git clone https://github.com/linview/sandbox_agent.git
cd sandbox_agent/mcp/web_tool

# 安装依赖
pip install -e .
```

### 从PyPI安装（发布后）

```bash
pip install web-tool-mcp-server
```

## 使用方法

### 命令行使用

```bash
# 直接运行
python -m web_tool.server

# 或使用安装的命令
web-tool-server
```

### 在Cursor中配置

在Cursor的MCP配置文件中添加：

```json
{
  "web-tools": {
    "command": "python",
    "args": ["-m", "web_tool.server"]
  }
}
```

或者如果通过pip安装：

```json
{
  "web-tools": {
    "command": "web-tool-server"
  }
}
```

## 可用工具

### 1. get_web_page

获取网页内容

**参数:**
- `url` (str): 要获取的网页URL

**返回:**
- 网页的标题和文本内容

**示例:**
```python
result = get_web_page("https://example.com")
```

### 2. search_web_content

在网页内容中搜索关键词

**参数:**
- `url` (str): 要搜索的网页URL
- `search_term` (str): 搜索关键词

**返回:**
- 包含关键词的上下文内容

**示例:**
```python
result = search_web_content("https://example.com", "python")
```

## 开发

### 项目结构

```
web_tool/
├── src/
│   └── web_tool/
│       ├── __init__.py
│       └── server.py
├── setup.py
├── pyproject.toml
└── README.md
```

### 本地开发

```bash
# 安装开发依赖
pip install -e .

# 运行测试
python -m web_tool.server

# 构建包
python -m build

# 检查包
twine check dist/*
```

## 依赖

- fastmcp >= 1.0.0
- pydantic >= 2.0.0
- requests >= 2.28.0
- beautifulsoup4 >= 4.11.0

## 许可证

MIT License

## 作者

linview (linview@gmail.com)

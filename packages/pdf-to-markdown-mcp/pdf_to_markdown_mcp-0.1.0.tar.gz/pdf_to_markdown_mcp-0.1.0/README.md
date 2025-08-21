# PDF转Markdown MCP服务器

这是一个基于Python的MCP (Model Context Protocol) 服务器，用于将PDF文件转换为Markdown格式。

## 功能特性

- 🚀 直接使用Python的`markitdown`库，性能更高
- 🔧 简单的API接口
- 📄 支持各种PDF格式
- 🛡️ 完整的错误处理

## 安装和使用

### 1. 安装依赖

```bash
cd /Users/fengjinchao/Desktop/mcp/skills/python/pdf-to-markdown
uv sync
```

### 2. Claude配置

在Claude的MCP配置中添加：

```json
{
  "pdf-to-markdown-python": {
    "name": "PDF转markdown(Python)",
    "type": "stdio",
    "description": "Python版本的PDF转markdown工具，性能更好",
    "isActive": true,
    "command": "uv",
    "args": ["--directory", "/Users/fengjinchao/Desktop/mcp/skills/python/pdf-to-markdown", "run", "pdf-to-markdown-mcp"]
  }
}
```

### 3. 使用工具

```json
{
  "name": "pdf-to-markdown",
  "arguments": {
    "filepath": "/path/to/your/document.pdf"
  }
}
```

## Python版本的优势

1. **更简单的实现**: 直接调用`markitdown.convert()`, 不需要子进程
2. **更好的性能**: 避免了进程间通信的开销
3. **更好的错误处理**: Python的异常处理更直观
4. **更少的依赖**: 不需要TypeScript构建工具链

## 代码结构

```
pdf-to-markdown/
├── pyproject.toml          # 项目配置
├── README.md              # 说明文档
└── pdf_to_markdown_mcp/   # 主要代码
    ├── __init__.py        # 包初始化
    └── server.py          # MCP服务器实现
```
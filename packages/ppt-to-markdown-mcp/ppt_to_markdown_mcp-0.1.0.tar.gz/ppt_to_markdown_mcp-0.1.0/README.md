# PPT转Markdown MCP服务器

这是一个基于Python的MCP (Model Context Protocol) 服务器，用于将PowerPoint文件转换为Markdown格式。

## 功能特性

- 🚀 直接使用Python的`markitdown`库，支持PowerPoint处理
- 📊 支持PowerPoint格式 (.pptx, .ppt)
- 🎯 支持幻灯片结构转换
- 📝 提取文本、图片描述、表格等内容
- 🔧 简单的API接口
- 🛡️ 完整的错误处理

## 安装和使用

### 1. 安装依赖

```bash
cd /Users/fengjinchao/Desktop/mcp/skills/python/ppt-to-markdown
uv sync
```

### 2. Claude配置

在Claude的MCP配置中添加：

```json
{
  "ppt-to-markdown-python": {
    "name": "PPT转markdown(Python)",
    "type": "stdio",
    "description": "Python版本的PPT转markdown工具，支持幻灯片结构",
    "isActive": true,
    "command": "uv",
    "args": ["--directory", "/Users/fengjinchao/Desktop/mcp/skills/python/ppt-to-markdown", "run", "ppt-to-markdown-mcp"]
  }
}
```

### 3. 使用工具

#### 基本用法
```json
{
  "name": "pptx-to-markdown",
  "arguments": {
    "filepath": "/path/to/your/presentation.pptx"
  }
}
```

#### 自定义选项
```json
{
  "name": "pptx-to-markdown", 
  "arguments": {
    "filepath": "/path/to/your/presentation.pptx",
    "include_slides": true
  }
}
```

## 支持的文件格式

- `.pptx` - PowerPoint 2007+ 格式
- `.ppt` - PowerPoint 97-2003 格式（通过markitdown支持）

## 转换特性

- ✅ **幻灯片结构**: 保持幻灯片的逻辑结构
- ✅ **文本内容**: 提取所有文本内容包括标题和正文
- ✅ **图片处理**: 提取图片描述和alt文本
- ✅ **表格支持**: 转换表格为Markdown表格格式
- ✅ **列表处理**: 保持项目符号和编号列表
- ✅ **格式保持**: 尽可能保持原有格式结构

## Python版本优势

1. **更好的Office文档支持**: Python在处理Office文档方面有丰富的库
2. **更直接的处理**: 无需子进程调用，直接API处理
3. **更好的错误处理**: Python异常处理更完善
4. **更强的扩展性**: 易于添加自定义处理逻辑
5. **更好的性能**: 避免进程间通信开销

## 代码结构

```
ppt-to-markdown/
├── pyproject.toml               # 项目配置
├── README.md                   # 说明文档
└── ppt_to_markdown_mcp/        # 主要代码
    ├── __init__.py            # 包初始化
    └── server.py              # MCP服务器实现
```
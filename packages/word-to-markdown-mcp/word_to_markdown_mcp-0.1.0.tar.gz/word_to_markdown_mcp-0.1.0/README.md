# Word转Markdown MCP服务器

这是一个基于Python的MCP (Model Context Protocol) 服务器，用于将Microsoft Word文件转换为Markdown格式。

## 功能特性

- 🚀 直接使用Python的`markitdown`库，支持Word文档处理
- 📄 支持Word格式 (.docx, .doc)
- 📝 保持文档结构和层次
- 🎨 支持格式转换（粗体、斜体、标题等）
- 📊 支持表格转换
- 🖼️ 支持图片信息提取
- 📋 支持列表结构
- 🔧 简单的API接口
- 🛡️ 完整的错误处理

## 安装和使用

### 1. 安装依赖

```bash
cd /Users/fengjinchao/Desktop/mcp/skills/python/word-to-markdown
uv sync
```

### 2. Claude配置

在Claude的MCP配置中添加：

```json
{
  "word-to-markdown-python": {
    "name": "Word转markdown(Python)",
    "type": "stdio",
    "description": "Word转markdown工具，支持文档结构和格式",
    "isActive": true,
    "command": "uv",
    "args": ["--directory", "/Users/fengjinchao/Desktop/mcp/skills/python/word-to-markdown", "run", "word-to-markdown-mcp"]
  }
}
```

### 3. 使用工具

#### 基本用法
```json
{
  "name": "docx-to-markdown",
  "arguments": {
    "filepath": "/path/to/your/document.docx"
  }
}
```

#### 自定义选项
```json
{
  "name": "docx-to-markdown", 
  "arguments": {
    "filepath": "/path/to/your/document.docx",
    "preserve_format": true,
    "extract_images": true
  }
}
```

## 支持的文件格式

- `.docx` - Word 2007+ 格式
- `.doc` - Word 97-2003 格式（通过markitdown支持）

## 转换特性

- ✅ **文档结构**: 保持标题层次和段落结构
- ✅ **文本格式**: 转换粗体、斜体、下划线等格式
- ✅ **标题**: 转换为对应级别的Markdown标题
- ✅ **列表**: 保持有序和无序列表结构
- ✅ **表格**: 转换为Markdown表格格式
- ✅ **图片**: 提取图片信息和描述
- ✅ **链接**: 保持超链接功能
- ✅ **引用**: 转换引用和脚注

## Python版本优势

1. **更好的Word文档支持**: Python在处理Office文档方面有成熟的库
2. **更精确的格式转换**: 直接处理文档对象模型
3. **更好的中文支持**: Python对Unicode和中文处理更完善
4. **更强的自定义能力**: 可以根据需要调整转换逻辑
5. **更好的性能**: 避免子进程调用开销
6. **更好的错误处理**: Python异常处理更完善

## 使用场景

- 📚 **文档迁移**: 将Word文档迁移到Markdown格式
- 📖 **内容发布**: 将Word文档发布到支持Markdown的平台
- 📝 **文档处理**: 批量处理Word文档内容
- 🔄 **格式转换**: 在不同文档格式间转换
- 📋 **内容提取**: 从Word文档中提取纯文本内容

## 代码结构

```
word-to-markdown/
├── pyproject.toml               # 项目配置
├── README.md                   # 说明文档
└── word_to_markdown_mcp/       # 主要代码
    ├── __init__.py            # 包初始化
    └── server.py              # MCP服务器实现
```
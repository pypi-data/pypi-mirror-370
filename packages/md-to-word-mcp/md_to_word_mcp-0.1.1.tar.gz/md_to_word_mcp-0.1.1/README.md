# md-to-word MCP Server

Markdown 转 Word 文档 MCP 服务器

## 功能特性

- ✅ 将 Markdown 文件转换为 Word 文档
- ✅ 支持自定义 Word 模板
- ✅ 模板管理功能
- ✅ Markdown 文件验证
- ✅ 示例文件创建
- ✅ 文件信息查看

## 安装和使用

### 1. 安装依赖

```bash
# 使用 uv
uv add pypandoc-binary mcp

# 或使用 pip
pip install pypandoc-binary mcp
```

### 2. 启动服务器

```bash
# 直接运行
python -m md_to_word_mcp

# 或使用模块方式
python src/md_to_word_mcp/server.py
```

### 3. 配置 Claude Desktop

在 Claude Desktop 的配置文件中添加：

```json
{
  "mcpServers": {
    "md-to-word": {
      "command": "python",
      "args": ["-m", "md_to_word_mcp"],
      "cwd": "/path/to/your/project"
    }
  }
}
```

## 可用工具

### 1. convert_md_to_word

将 Markdown 文件转换为 Word 文档。

**参数：**
- `input_file`: 输入的 Markdown 文件路径
- `output_file`: 输出的 Word 文件路径（可选）
- `template`: Word 模板文件路径（可选）
- `title`: 文档标题（可选）
- `author`: 文档作者（可选）

### 2. create_markdown_sample

创建示例 Markdown 文件。

**参数：**
- `filename`: 输出文件名（默认：sample.md）
- `content_type`: 内容类型（product_manual/technical_doc/user_guide/custom）
- `custom_content`: 自定义内容（当 content_type 为 custom 时）

### 3. list_templates

列出可用的 Word 模板。

### 4. validate_markdown

验证 Markdown 文件格式和内容。

**参数：**
- `file_path`: Markdown 文件路径

## 使用示例

在 Claude 中使用：

```
请帮我将 README.md 转换为 Word 文档
```

```
创建一个产品手册的示例文件
```

```
列出所有可用的模板
```

## 文件结构

```
md转word/
├── src/
│   └── md_to_word_mcp/
│       ├── __init__.py
│       ├── __main__.py
│       ├── server.py          # MCP 服务器
│       ├── converter.py       # 转换器
│       ├── template_manager.py # 模板管理器
│       └── utils.py           # 工具函数
├── pyproject.toml
├── batch_demo.py          # 原始示例脚本
├── product_manual_black.docx  # 默认模板
└── README.md
```

## 配置选项

可以通过修改 `server.py` 中的 `config` 对象来调整设置：

```python
config = {
    "default_template": "product_manual_black.docx",  # 默认模板
    "output_dir": "./output",                        # 输出目录
    "max_file_size": 50 * 1024 * 1024,              # 最大文件大小 (50MB)
    "supported_formats": [".md", ".markdown", ".txt"] # 支持的格式
}
```

## 注意事项

1. 确保 `product_manual_black.docx` 模板文件存在于项目根目录
2. 支持的输入格式：.md、.markdown、.txt
3. 输出格式：.docx
4. 模板格式：.docx、.dotx
5. 最大文件大小限制：50MB

## 问题排查

如果遇到问题，请检查：

1. 是否正确安装了 `pypandoc-binary`
2. 输入文件是否存在且可读
3. 模板文件是否存在且是有效的 Word 文档
4. 输出目录是否有写入权限

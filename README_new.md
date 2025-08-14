# Outliner - 智能文档大纲生成器

基于 Ollama 大语言模型的智能文档大纲生成工具，能够自动分析文档内容，提取章节标题，并生成结构化大纲。

## 🌟 主要特性

- **智能标题提取**：使用大语言模型自动提取章节标题
- **上下文感知**：利用记忆机制保持章节间的逻辑连贯性
- **批量处理**：支持一次性处理多个章节
- **长文档支持**：自动分割长文档为合适的章节
- **灵活配置**：支持调节模型参数（temperature、top_p、repeat_penalty）
- **ReAct风格提示**：支持多级标题大纲抽取（兼容原功能）

## 🚀 快速开始

### 安装依赖

```bash
pip install requests
```

### 准备工作

1. 安装并启动 Ollama 服务（默认端口 11434）
2. 拉取所需模型：

```bash
ollama pull qwen3:0.6b
ollama pull qwen3
```

### 基本使用

```python
from outliner.outliner import Outliner

# 创建实例
outliner = Outliner(model="qwen3:0.6b", endpoint="http://172.31.80.1:11434")

# 处理多个章节
chapters = [
    "第一章节内容...",
    "第二章节内容...",
    "第三章节内容..."
]

# 提取标题
titles = outliner.process_chapters(chapters)
print("提取的标题:", titles)

# 查看完整大纲
print(outliner.get_chapter_outline())
```

### 处理长文档

```python
# 读取长文档
with open('document.txt', 'r', encoding='utf-8') as f:
    long_text = f.read()

# 自动分割并提取标题
titles = outliner.process_text_to_chapters(long_text, max_chars=3000, overlap=200)

# 生成大纲
outline = outliner.get_chapter_outline()
```

## 🛠️ 命令行工具

### 使用示例脚本

```bash
python example_usage.py
```

### 使用文档大纲生成工具

```bash
# 基本用法
python document_outliner.py document.txt

# 自定义参数
python document_outliner.py document.txt --max-chars 2000 --overlap 100

# 保存大纲到文件
python document_outliner.py document.txt --output outline.md

# 使用不同模型
python document_outliner.py document.txt --model qwen2:7b --endpoint http://localhost:11434
```

### ReAct风格大纲提取（原功能）

```bash
# 基础版
python -m outliner.react_outliner path/to/input.txt -o outline.md \
    --model qwen3 --endpoint http://127.0.0.1:11434

# 2D滑窗 + 压缩版
python -m outliner.react_outliner_2d path/to/input.txt -o outline.md \
    --model qwen3:0.6b --endpoint http://127.0.0.1:11434 \
    --max-chars 2500 --overlap 300 --rows 2 --cols 3 --compress 0.5
```

## 📚 API 参考

### Outliner 类（新增功能）

#### 初始化参数

- `model`: 使用的AI模型名称（默认："qwen3:0.6b"）
- `endpoint`: Ollama服务端点（默认："http://172.31.80.1:11434"）

#### 主要方法

##### `process_chapters(chapters, chapter_level=1)`
批量处理章节并提取标题。

**参数：**
- `chapters`: 章节内容列表
- `chapter_level`: 章节层级（默认：1）

**返回：** 提取的标题列表

##### `process_text_to_chapters(text, max_chars=3000, overlap=200)`
将长文本分割为章节并提取标题。

**参数：**
- `text`: 要处理的长文本
- `max_chars`: 每个章节的最大字符数
- `overlap`: 章节间的重叠字符数

**返回：** 提取的标题列表

##### `add_to_memory(title, content, level=1)`
手动添加章节信息到记忆中。

##### `get_memory_summary(max_chapters=5)`
获取最近章节的摘要信息。

##### `get_chapter_outline()`
获取当前所有章节的大纲格式输出。

##### `clear_memory()`
清空章节记忆。

### 原有功能（ReAct风格）

```python
from outliner import outline_text, render_markdown

text = open("path/to/input.txt", "r", encoding="utf-8").read()
headings = outline_text(text, model="qwen3", endpoint="http://127.0.0.1:11434")
md = render_markdown(headings)
print(md)

# 2D 滑窗 + 压缩 + 页码
from outliner import Outline2DExtractor, Window2DConfig, render_markdown_with_page

text = open("path/to/input.txt", "r", encoding="utf-8").read()
cfg = Window2DConfig(max_chars=2500, overlap_chars=300, rows=2, cols=3, compress_ratio=0.5)
extractor = Outline2DExtractor(model="qwen3:0.6b", endpoint="http://127.0.0.1:11434")
headings = extractor.extract(text, cfg)
md = render_markdown_with_page(headings)
print(md)
```

## 🔧 配置说明

### repeat_penalty 参数配置

在代码中直接设置：
```python
outliner = Outliner()
response = outliner.chat(messages, repeat_penalty=1.2)
```

或通过 Modelfile 配置（详见 [README_repeat_penalty.md](README_repeat_penalty.md)）

### 模型参数调节

```python
# 在 chat 方法中调节参数
response = outliner.chat(
    messages, 
    temperature=0.2,    # 控制随机性 (0-2)
    top_p=0.9,         # 核采样参数 (0-1)
    repeat_penalty=1.1  # 重复惩罚 (>1.0减少重复)
)
```

## 💡 使用建议

1. **章节大小**：建议每个章节控制在 2000-4000 字符之间
2. **重叠设置**：设置适当的重叠（150-300字符）保证语义连续性
3. **模型选择**：根据需要选择合适的模型大小和性能
4. **批处理**：对于大量文档，建议分批处理避免内存占用过大

## 🐛 故障排除

### 常见问题

1. **连接失败**：检查 Ollama 服务是否正常运行
2. **模型未找到**：确保指定的模型已下载到 Ollama
3. **处理速度慢**：考虑使用更小的模型或调整章节大小
4. **标题质量差**：尝试调整 temperature 和 repeat_penalty 参数
5. **输出为空**：确认 Ollama 服务已启动且已拉取相应模型

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

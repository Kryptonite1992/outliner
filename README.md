Outliner (ReAct + Ollama + Qwen3)
=================================

基于本地 Ollama qwen3 模型的多级标题大纲抽取器，采用 ReAct 风格提示，把长文拆分遍历提取，并合并去重。
新增：2D 滑动窗口 + 压缩提取器，模型默认使用更轻量的 qwen3:0.6b。

特性
- 逐段落切分 + 上下文重叠，长文也可处理。
- LLM 仅返回 JSON（level/title），再合并去重。
- 输出 Markdown 形式的多级标题。

准备
1) 安装 Ollama（Linux）并启动服务（默认端口 11434）。
2) 拉取 qwen3 模型（或轻量版 qwen3:0.6b）：

```bash
ollama pull qwen3
ollama pull qwen3:0.6b
```

命令行用法（基础版）
```bash
python -m outliner.react_outliner path/to/input.txt -o outline.md \
	--model qwen3 --endpoint http://127.0.0.1:11434
```

命令行用法（2D 滑窗 + 压缩）
```bash
python -m outliner.react_outliner_2d path/to/input.txt -o outline.md \
	--model qwen3:0.6b --endpoint http://127.0.0.1:11434 \
	--max-chars 2500 --overlap 300 --rows 2 --cols 3 --compress 0.5
```

Python 用法
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

故障排查
- 若输出为空，确认 Ollama 服务已启动且已拉取 qwen3。
- 可调整 chunk 大小/重叠，在 `react_outliner.py` 的 `chunk_text` 中设置。
- 如果模型偶尔返回非 JSON，代码会尝试自动提取第一个 JSON 对象。

许可证
MIT


# 如何在 Ollama 中使用 repeat_penalty

## 方案一：API 调用中添加参数（已实现）
代码中已经添加了 `repeat_penalty` 参数支持，可以在调用时指定：

```python
# 使用较高的 repeat_penalty 减少重复
client.chat(messages, temperature=0.2, repeat_penalty=1.2)
```

## 方案二：使用 Modelfile 创建自定义模型

1. 使用提供的 Modelfile 创建自定义模型：
```bash
ollama create outliner-custom -f Modelfile
```

2. 在代码中使用自定义模型：
```python
client = Outliner(model="outliner-custom")
```

## repeat_penalty 参数说明：
- 值 > 1.0：减少重复内容（推荐 1.1-1.3）
- 值 = 1.0：不施加惩罚（默认）
- 值 < 1.0：增加重复内容

## 其他相关参数：
- `frequency_penalty`：OpenAI 风格的频率惩罚
- `presence_penalty`：OpenAI 风格的存在惩罚
- `repeat_penalty`：Ollama 原生的重复惩罚参数

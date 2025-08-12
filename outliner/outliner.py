import re
import requests

class Outliner:


    """
    用于访问 Ollama 0.6b 模型的简单客户端。
    """
    def __init__(self, model="qwen3:0.6b", endpoint="http://172.31.80.1:11434"):
        self.model = model
        self.endpoint = endpoint.rstrip("/")

    def chat(self, messages, temperature=0.1, top_p=0.9, repeat_penalty=1.1):
        """
        向 Ollama 0.6b 发送对话消息。
        messages: List[dict]，如 [{"role": "user", "content": "..."}]
        temperature: 控制随机性，0-2之间
        top_p: 核采样参数，0-1之间
        repeat_penalty: 重复惩罚，>1.0减少重复，<1.0增加重复，默认1.1
        返回字符串回复。
        """
        # 在最前面插入系统提示词，包含 /no_think 指令
        sys_prompt = {"role": "system", "content": ""}
        
        # 给用户消息添加 /no_think 前缀
        processed_messages = []
        for msg in messages:
            if msg["role"] == "user":
                content = msg["content"]
                if not content.startswith("/no_think"):
                    content = "/no_think " + content
                processed_messages.append({"role": "user", "content": content})
            else:
                processed_messages.append(msg)
        
        full_messages = [sys_prompt] + processed_messages
        url = f"{self.endpoint}/v1/chat/completions"
        payload = {
            "model": self.model,
            "messages": full_messages,
            "temperature": temperature,
            "top_p": top_p,
            "repeat_penalty": repeat_penalty
        }
        resp = requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        # 假设返回格式为 OpenAI 格式
        return data["choices"][0]["message"]["content"]




    def extract_paragraph_title(self, paragraph: str) -> str:
        """
        利用chat和内置prompt提取当前段落标题。
        """
        prompt = (
            "/no_think 你是一个文档结构分析专家。请为下列段落提炼一个简洁、准确的标题，只返回标题本身，不要多余内容。\n\n" + paragraph
        )
        messages = [
            {"role": "user", "content": prompt}
        ]
        reply = self.chat(messages, temperature=0.2, repeat_penalty=1.2)
        # 可根据需要做进一步清洗
        return reply.strip()

def remove_think_tags(text):
    """
    去除 <think>...</think> 标签及其中内容。
    """
    return re.sub(r'<think>[\s\S]*?</think>', '', text, flags=re.IGNORECASE)


# 只保留无错误的滑动窗口分块函数
def chunk_text(text: str, max_chars: int = 3000, overlap: int = 200) -> list:
    """
    基于字符滑动窗口分块，支持重叠。
    """
    if not text:
        return []
    chunks = []
    step = max_chars - overlap if max_chars > overlap else max_chars
    i = 0
    while i < len(text):
        chunk = text[i:i+max_chars]
        chunks.append(chunk)
        if i + max_chars >= len(text):
            break
        i += step
    return chunks


def test_ollama_client():
    """
    简单测试OutlinerOllamaClient，打印模型回复。
    """
    client = Outliner()
    messages = [
        {"role": "user", "content": "你好，介绍一下你自己。"}
    ]
    try:
        reply = client.chat(messages)
        print(remove_think_tags(reply))
        # print(remove_think_tags(reply))
    except Exception as e:
        print("请求失败:", e)


if __name__ == "__main__":
    test_ollama_client()

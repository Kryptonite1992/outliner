import re
import requests

class Outliner:
    def get_memory_count(self):
        """
        获取当前记忆中的章节数量。
        """
        return len(self.memory)
    def get_pre_memory(self, n=3):
        """
        获取 memory 中最近 n 条的内容（标题+内容），用于上下文提示。
        Args:
            n: 返回最近 n 条
        Returns:
            str: 拼接的内容字符串
        """
        if not self.memory:
            return ""
        selected = self.memory[-n:] if n > 0 else self.memory
        # 格式：标题: 内容
        return "\n\n".join([
            f"{item['title']}\n{item['content']}" for item in selected if item.get('title') or item.get('content')
        ])


    """
    用于访问 Ollama 0.6b 模型的简单客户端。
    """
    def __init__(self, configs=None, config_index=0):
        """
        configs: 配置列表，每个元素为dict，包含'model'和'endpoint'字段。
        config_index: 当前使用的配置索引。
        """
        # 你可以在这里注释/取消注释不同的配置
        if configs is None:
            configs = [
                {"model": "Qwen3-0___6B/", "endpoint": "http://127.0.0.1:30000"},
                # {"model": "llama3:8b", "endpoint": "http://127.0.0.1:11434"},
                # {"model": "other_model", "endpoint": "http://localhost:12345"},
            ]
        self.configs = configs
        self.config_index = config_index
        self.model = self.configs[self.config_index]["model"]
        self.endpoint = self.configs[self.config_index]["endpoint"].rstrip("/")
        self.memory = []  # 用于记录之前的章节信息
        self.pre_chunks = []  # 预先分块的内容，直接按顺序存储文本块

    def set_pre_chunks(self, text: str, max_chars: int = 3000, overlap: int = 200):
        """
        使用 chunk_text 对文本进行分块，并保存到 pre_chunks 属性。
        Args:
            text: 需要分块的原始文本
            max_chars: 每块最大字符数
            overlap: 块之间的重叠字符数
        """
        self.pre_chunks = chunk_text(text, max_chars=max_chars, overlap=overlap)

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



    def extract_paragraph_title(self, paragraph: str, use_context: bool = True) -> str:
        """
        利用chat和内置prompt提取当前段落标题。
        
        Args:
            paragraph: 要提取标题的段落
            use_context: 是否使用之前章节的上下文信息
        """
        context_info = ""
        if use_context and self.memory:
            # 获取 memory 中最后一条内容
            last_content = self.memory[-1]["content"] if self.memory and "content" in self.memory[-1] else ""
            if last_content:
                pre_mem = self.get_pre_memory(3)
                if pre_mem.strip():
                    context_info = f"\n\n【前文上下文】：\n{pre_mem}\n"
                else:
                    context_info = ""
        
        prompt = (
            "/no_think 你是一个标题抽取专家。如果下列段落中本身就有标题，请原封不动抽取该标题（必须与原文完全一致）；如果没有标题，不要生成新标题，直接返回空。只返回标题本身，不要多余内容。"
            + context_info
            + "\n\n【当前段落】:\n" + paragraph
        )
        messages = [
            {"role": "user", "content": prompt}
        ]
        reply = self.chat(messages, temperature=0.2, repeat_penalty=1.2)
        # 可根据需要做进一步清洗
        title = reply.strip()
        
        # 自动将提取的标题和段落添加到记忆中
        if use_context:
            self.add_to_memory(title, paragraph)
        
        return title

    def add_to_memory(self, title: str, content: str, level: int = 1, chunk_index: int = None):
        """
        添加章节信息到记忆中。
        Args:
            title: 章节标题
            content: 章节内容
            level: 章节层级（1为一级标题，2为二级标题等）
            chunk_index: 如果是 pre_chunks 分块，记录其在 pre_chunks 中的位置（索引）
        """
        chapter_info = {
            "title": title,
            "content": content,
            "level": level,
            "timestamp": len(self.memory) + 1,  # 简单的序号作为时间戳
        }
        if chunk_index is not None:
            chapter_info["chunk_index"] = chunk_index
        self.memory.append(chapter_info)

    def get_memory_summary(self):
        """
        利用大模型对所有memory中的标题进行整理归纳，输出更有层次的大纲。
        Returns:
            str: LLM整理后的标题大纲
        """
        if not self.memory:
            return "暂无章节记录。"

        # 收集所有标题
        all_titles = [chapter["title"] for chapter in self.memory if chapter["title"].strip()]
        if not all_titles:
            return "暂无有效标题。"

        titles_text = "\n".join(all_titles)
        prompt = (
            "/no_think 你是一个文档结构梳理专家。请根据下列标题集合，整理出更有层次和逻辑的大纲，只返回整理后的标题列表，不要多余解释。\n\n"
            f"【标题集合】：\n{titles_text}"
        )
        messages = [
            {"role": "user", "content": prompt}
        ]
        try:
            summary = self.chat(messages, temperature=0.1, repeat_penalty=1.1)
            return summary.strip()
        except Exception as e:
            return f"大模型整理失败: {e}"

    def process_chapters(self, chapters: list, chapter_level: int = 1, chunk_indices: list = None) -> list:
        """
        遍历所有章节，直接调用 extract_paragraph_title 提取标题，并将标题加到memory中。
        Args:
            chapters: 章节内容列表，每个元素是一个字符串（章节内容）
            chapter_level: 章节层级，默认为1（一级标题）
            chunk_indices: 可选，章节内容在 pre_chunks 中的索引列表
        Returns:
            list: 提取的标题列表
        """
        print(f"开始处理 {len(chapters)} 个章节...")
        for i, chapter_content in enumerate(chapters):
            if not chapter_content.strip():
                print(f"跳过空章节 {i+1}")
                continue
            print(f"正在处理第 {i+1} 个章节...")
            try:
                # 直接调用 extract_paragraph_title
                self.extract_paragraph_title(chapter_content)
                print(f"第 {i+1} 章节标题提取完成")
            except Exception as e:
                error_title = f"章节 {i+1} (提取失败)"
                print(f"第 {i+1} 章节标题提取失败: {e}")
                chunk_index = chunk_indices[i] if chunk_indices is not None and i < len(chunk_indices) else None
                self.add_to_memory(error_title, chapter_content, chapter_level, chunk_index=chunk_index)
        print(f"章节处理完成！")
        return self.get_memory_summary()


def remove_think_tags(text):
    """
    去除 <think>...</think> 标签及其中内容。
    """
    return re.sub(r'<think>[\s\S]*?</think>', '', text, flags=re.IGNORECASE)


# 只保留无错误的滑动窗口分块函数
def chunk_text(text: str, max_chars: int = 3000, overlap: int = 200) -> list:
    """
    只做滑动窗口分块，截取原文内容。
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
                self.add_to_memory(error_title, chapter_level)
    """
    client = Outliner()
    
    # 测试基本对话功能
    print("=== 测试基本对话功能 ===")
    messages = [
        {"role": "user", "content": "你好，介绍一下你自己。"}
    ]
    try:
        reply = client.chat(messages)
        print("模型回复:", remove_think_tags(reply))
    except Exception as e:
        print("请求失败:", e)
    
    # 测试批量章节处理功能
    print("\n=== 测试批量章节处理功能 ===")
    
    # 模拟一些带章节序号的内容
    sample_chapters = [
        "第1章 人工智能简介\n人工智能（Artificial Intelligence，AI）是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。该领域的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。人工智能从诞生以来，理论和技术日益成熟，应用领域也不断扩大。",
        "第2章 机器学习基础\n机器学习是人工智能的一个重要分支，它是一种通过算法使计算机系统能够自动学习和改进的技术。机器学习算法通过训练数据来构建数学模型，以便对新的数据做出预测或决策。常见的机器学习类型包括监督学习、无监督学习和强化学习。监督学习使用标记的训练数据，无监督学习从未标记的数据中发现模式，强化学习通过与环境交互来学习最优策略。",
        "第3章 深度学习\n深度学习是机器学习的一个子集，它模拟人脑神经网络的结构和功能。深度学习使用多层神经网络来学习数据的表示，这些网络能够自动提取特征并进行复杂的模式识别。深度学习在图像识别、语音识别、自然语言处理等领域取得了突破性进展。卷积神经网络（CNN）适用于图像处理，循环神经网络（RNN）适用于序列数据处理，变换器（Transformer）在自然语言处理中表现优异。",
        "第4章 自然语言处理\n自然语言处理（Natural Language Processing，NLP）是人工智能和计算语言学的一个分支，旨在让计算机能够理解、解释和生成人类语言。NLP涉及多个层面的语言分析，包括词法分析、句法分析、语义分析和语用分析。现代NLP技术广泛应用于机器翻译、情感分析、文本摘要、问答系统、聊天机器人等场景。近年来，基于深度学习的语言模型如GPT、BERT等取得了显著成果。"
    ]
    
    try:
        # 处理所有章节
        extracted_titles = client.process_chapters(sample_chapters)
        
        print(f"\n成功提取 {len(extracted_titles)} 个章节标题:")
        for i, title in enumerate(extracted_titles):
            print(f"{i+1}. {title}")
        
        print(f"\n当前memory中共有 {client.get_memory_count()} 个章节")
        
        # 显示完整大纲
        print("\n" + client.get_chapter_outline())
        
        # 测试长文本处理
        print("\n=== 测试长文本自动分割处理 ===")
        long_text = """
        云计算是一种基于互联网的计算方式，通过这种方式，共享的软硬件资源和信息可以按需提供给计算机和其他设备。
        云计算是继1980年代大型机到客户端-服务器的大转变之后的又一种巨变。云计算描述了一种基于互联网的新的IT服务
        增加、使用和交付模式，通常涉及通过互联网来提供动态易扩展且经常是虚拟化的资源。
        资源汇集起来，使用多租户模型为多个消费者服务。快速弹性使资源能够快速灵活地提供和释放。服务可测量性
        确保云系统能够自动控制和优化资源使用。
        
        云计算服务模式主要分为三种：基础设施即服务（IaaS）、平台即服务（PaaS）和软件即服务（SaaS）。
        IaaS提供虚拟化的计算基础设施，如虚拟机、存储和网络。PaaS提供应用程序开发和部署平台。
        SaaS直接提供完整的应用程序服务。这三种模式为不同需求的用户提供了灵活的选择。
        """
        
        # 清空之前的memory开始新测试
        client.clear_memory()
        print("已清空memory，开始测试长文本处理...")
        
        long_text_titles = client.process_text_to_chapters(long_text, max_chars=500, overlap=50)
        print(f"\n长文本处理完成，提取 {len(long_text_titles)} 个章节标题:")
        for i, title in enumerate(long_text_titles):
            print(f"{i+1}. {title}")
            
    except Exception as e:
        print("批量处理失败:", e)


if __name__ == "__main__":
    test_ollama_client()

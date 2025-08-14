#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from outliner.outliner import OllamaClient

def test_extract_paragraph_title():
    """
    测试 extract_paragraph_title 方法
    """
    client = OllamaClient()
    
    # 测试段落1：技术文档
    paragraph1 = """
    机器学习是人工智能的一个重要分支，它使计算机能够在没有明确编程的情况下学习和改进。
    通过算法和统计模型，机器学习系统可以分析大量数据，识别模式，并做出预测或决策。
    常见的机器学习类型包括监督学习、无监督学习和强化学习。
    """
    
    # 测试段落2：日常生活
    paragraph2 = """
    早晨起床后，我通常会先喝一杯温水，然后进行简单的晨练。
    晨练包括拉伸运动、慢跑和一些基础的力量训练。
    这个习惯让我一整天都充满活力，工作效率也有明显提升。
    """
    
    # 测试段落3：商业分析
    paragraph3 = """
    电子商务平台的用户体验设计直接影响转化率和客户满意度。
    优秀的用户界面应该简洁直观，购买流程要尽可能简化。
    同时，个性化推荐系统可以显著提高用户的购买意愿和平台粘性。
    """
    
    test_paragraphs = [
        ("技术文档段落", paragraph1),
        ("日常生活段落", paragraph2),
        ("商业分析段落", paragraph3)
    ]
    
    print("=== 测试 extract_paragraph_title 方法 ===\n")
    
    for desc, paragraph in test_paragraphs:
        print(f"测试 {desc}:")
        print(f"原始段落: {paragraph.strip()}")
        print("-" * 50)
        
        try:
            title = client.extract_paragraph_title(paragraph)
            print(f"提取的标题: {title}")
            print(f"标题长度: {len(title)} 字符")
        except Exception as e:
            print(f"提取标题失败: {e}")
        
        print("=" * 60)
        print()

if __name__ == "__main__":
    test_extract_paragraph_title()

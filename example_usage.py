#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Outliner使用示例 - 批量章节标题提取

这个示例展示如何使用Outliner类：
1. 处理多个章节内容
2. 自动提取标题
3. 利用memory功能保持上下文连贯性
4. 生成文档大纲
"""

from outliner.outliner import Outliner, remove_think_tags

def main():
    """主函数：演示Outliner的完整工作流程"""
    
    # 创建Outliner实例
    outliner = Outliner()
    
    # 示例章节内容
    chapters = [
        """
        项目背景与目标：本项目旨在开发一个智能文档大纲生成系统，能够自动分析长文档内容，
        提取关键信息，并生成结构化的章节标题。系统基于大语言模型技术，具备上下文理解能力，
        能够保证生成标题的连贯性和逻辑性。该系统将极大提高文档整理和结构化的效率。
        """,
        
        """
        技术架构设计：系统采用模块化架构，主要包括文本预处理模块、AI推理模块、记忆管理模块
        和输出格式化模块。文本预处理模块负责文档分割和清洗；AI推理模块基于Ollama框架，
        支持多种语言模型；记忆管理模块维护章节上下文信息；输出模块生成多种格式的大纲。
        """,
        
        """
        核心算法实现：系统实现了滑动窗口文本分割算法，确保章节间的语义连续性。标题提取算法
        结合了提示工程和上下文感知技术，能够根据前文内容调整当前章节的标题风格。记忆机制
        采用FIFO策略，动态维护最相关的上下文信息，避免信息过载。
        """,
        
        """
        测试与验证：通过对多种类型文档的测试，系统在技术文档、学术论文、商业报告等场景下
        均表现出良好的性能。标题提取准确率达到85%以上，生成的大纲结构清晰，层次分明。
        系统支持实时处理，单个章节的处理时间通常在2-5秒之间。
        """
    ]
    
    print("=" * 60)
    print("智能文档大纲生成系统 - 示例演示")
    print("=" * 60)
    
    try:
        # 处理所有章节
        print(f"\n正在处理 {len(chapters)} 个章节，请稍候...")
        titles = outliner.process_chapters(chapters)
        
        print(f"\n✅ 处理完成！成功提取 {len(titles)} 个标题")
        print("\n📋 提取的章节标题：")
        for i, title in enumerate(titles, 1):
            print(f"  {i}. {title}")
        
        # 显示完整大纲
        print("\n📖 完整文档大纲：")
        print(outliner.get_chapter_outline())
        
        # 显示memory状态
        print(f"\n💾 当前记忆状态：共存储 {outliner.get_memory_count()} 个章节")
        
        # 演示单独提取标题（利用已有上下文）
        print("\n🔍 演示单独章节标题提取（利用上下文）：")
        new_chapter = """
        未来发展规划：计划在下一个版本中加入多语言支持、实时协作功能和云端部署选项。
        同时将优化算法性能，减少处理时间，提高标题提取的准确性。预计在六个月内完成
        这些功能的开发和测试工作。
        """
        
        new_title = outliner.extract_paragraph_title(new_chapter, use_context=True)
        print(f"新章节标题：{new_title}")
        
        # 最终大纲
        print("\n📑 最终完整大纲：")
        print(outliner.get_chapter_outline())
        
    except Exception as e:
        print(f"❌ 处理过程中出现错误：{e}")
        print("请检查网络连接和Ollama服务状态")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
长文档大纲生成工具

用法：
python document_outliner.py input.txt [--max-chars 3000] [--overlap 200] [--output outline.md]
"""

import argparse
import sys
from pathlib import Path
from outliner.outliner import Outliner

def read_document(file_path):
    """读取文档文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ 读取文件失败：{e}")
        sys.exit(1)

def save_outline(outline, output_path):
    """保存大纲到文件"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(outline)
        print(f"✅ 大纲已保存到：{output_path}")
    except Exception as e:
        print(f"❌ 保存文件失败：{e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='智能文档大纲生成工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法：
  python document_outliner.py document.txt
  python document_outliner.py document.txt --max-chars 2000 --overlap 100
  python document_outliner.py document.txt --output my_outline.md
        """
    )
    
    parser.add_argument('input_file', help='输入文档文件路径')
    parser.add_argument('--max-chars', type=int, default=3000, 
                       help='每个章节的最大字符数（默认：3000）')
    parser.add_argument('--overlap', type=int, default=200,
                       help='章节间重叠字符数（默认：200）')
    parser.add_argument('--output', '-o', help='输出大纲文件路径（可选）')
    parser.add_argument('--model', default="qwen3:0.6b", 
                       help='使用的AI模型（默认：qwen3:0.6b）')
    parser.add_argument('--endpoint', default="http://172.31.80.1:11434",
                       help='Ollama服务端点（默认：http://172.31.80.1:11434）')
    
    args = parser.parse_args()
    
    # 检查输入文件
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ 输入文件不存在：{args.input_file}")
        sys.exit(1)
    
    print("=" * 60)
    print("智能文档大纲生成工具")
    print("=" * 60)
    print(f"📁 输入文件：{args.input_file}")
    print(f"🔧 章节大小：{args.max_chars} 字符")
    print(f"🔗 重叠大小：{args.overlap} 字符")
    print(f"🤖 AI模型：{args.model}")
    print(f"🌐 服务端点：{args.endpoint}")
    print("-" * 60)
    
    try:
        # 读取文档
        print("📖 正在读取文档...")
        document_text = read_document(args.input_file)
        print(f"✅ 文档读取完成，共 {len(document_text)} 字符")
        
        # 创建Outliner实例
        print("🚀 初始化AI大纲生成器...")
        outliner = Outliner(model=args.model, endpoint=args.endpoint)
        
        # 处理文档
        print("🔄 正在分析文档并生成大纲...")
        titles = outliner.process_text_to_chapters(
            document_text, 
            max_chars=args.max_chars, 
            overlap=args.overlap
        )
        
        # 生成大纲
        outline = outliner.get_chapter_outline()
        
        print("\n" + "=" * 60)
        print("📋 生成的文档大纲")
        print("=" * 60)
        print(outline)
        
        # 保存到文件（如果指定了输出路径）
        if args.output:
            # 添加更详细的大纲信息
            detailed_outline = f"""# 文档大纲

**原文件：** {args.input_file}
**生成时间：** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**章节数量：** {len(titles)}
**使用模型：** {args.model}

## 章节列表

"""
            for i, title in enumerate(titles, 1):
                detailed_outline += f"{i}. {title}\n"
            
            detailed_outline += f"\n## 详细大纲\n\n{outline}\n"
            
            save_outline(detailed_outline, args.output)
        
        print(f"\n🎉 处理完成！共生成 {len(titles)} 个章节标题")
        
    except KeyboardInterrupt:
        print("\n❌ 操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 处理过程中出现错误：{e}")
        print("请检查网络连接和Ollama服务状态")
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
测试 document_info 字段合并功能
"""

import asyncio
import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from design import call_autobots_sse_api, search_autobots_ai

async def test_document_info_merge():
    """测试 document_info 字段合并功能"""
    print("🧪 开始测试 document_info 字段合并功能...")
    print("=" * 60)
    
    # 测试用例 1: 使用默认值 (document_info=None)
    print("\n📋 测试用例 1: 使用默认值")
    print("-" * 30)
    try:
        result1 = await call_autobots_sse_api(
            keyword="测试默认文档信息",
            document_info=None  # 使用默认值
        )
        print("✅ 测试用例 1 通过 - 默认值处理正常")
    except Exception as e:
        print(f"❌ 测试用例 1 失败: {str(e)}")
    
    # 测试用例 2: 使用自定义 document_info
    print("\n📋 测试用例 2: 使用自定义文档信息")
    print("-" * 30)
    custom_doc_info = {
        'title': '自定义标题测试',
        'content': '这是自定义的文档内容\n包含多行文本'
    }
    try:
        result2 = await call_autobots_sse_api(
            keyword="测试自定义文档信息",
            document_info=custom_doc_info
        )
        print("✅ 测试用例 2 通过 - 自定义文档信息处理正常")
    except Exception as e:
        print(f"❌ 测试用例 2 失败: {str(e)}")
    
    # 测试用例 3: 使用部分字段的 document_info
    print("\n📋 测试用例 3: 使用部分字段")
    print("-" * 30)
    partial_doc_info = {
        'title': '只有标题的测试'
        # 缺少 content 字段，应该使用默认值
    }
    try:
        result3 = await call_autobots_sse_api(
            keyword="测试部分字段",
            document_info=partial_doc_info
        )
        print("✅ 测试用例 3 通过 - 部分字段处理正常")
    except Exception as e:
        print(f"❌ 测试用例 3 失败: {str(e)}")
    
    # 测试用例 4: 测试 MCP 工具函数
    print("\n📋 测试用例 4: 测试 MCP 工具函数")
    print("-" * 30)
    mcp_doc_info = {
        'title': 'MCP工具测试',
        'content': '测试MCP工具的文档信息合并功能'
    }
    try:
        result4 = await search_autobots_ai(
            keyword="测试MCP工具",
            document_info=mcp_doc_info
        )
        print("✅ 测试用例 4 通过 - MCP工具函数处理正常")
    except Exception as e:
        print(f"❌ 测试用例 4 失败: {str(e)}")
    
    print("\n🎉 所有测试用例执行完成！")
    print("=" * 60)

def main():
    """主函数"""
    try:
        asyncio.run(test_document_info_merge())
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试执行错误: {str(e)}")

if __name__ == "__main__":
    main()
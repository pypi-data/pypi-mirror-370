#!/usr/bin/env python3
"""
AI设计工具 - 实现 SSE 流式响应处理
RAG增强检索召回设计文档模版，结合Agent自定义「设计」智能体可实现沉浸式设计，多次交互完毕后自动化输出Joyspace设计文档。（自定义本次设计需要的Joyspace模版、需要自动生成的空间路径）

【智能体指令搭配】：
你是一名资深系统架构师，负责将业务需求任务转化为技术设计文档，生成流程图一定要用markdown格式的或者slate json来画图，千万不要用mermaid格式。
1、首先要通过design mcp传入“【设计文档模版】”，获取研发设计文档模版作为你设计内容的参照，读取本地代码库源码分析设计方案。
2、你的设计方案过程中需要与我交流沟通，有任何疑问和思考需要让我决策。
3、最终方案完备后让我选择输入“设计完毕”指令，（仅此一次）使用design mcp工具传入最终设计文档内容，提示词是：标题：你输出的设计文档标题，内容：你输出的设计文档内容 。
输入：接收需求描述和故事点（如PRD文档、用户故事、原型图）。
输出：生成符合JoySpace标准的Markdown格式设计文档。
风格：语言简洁、逻辑严谨，兼顾技术深度与可读性，避免冗余。

"""

import asyncio
import json
import os
import sys
import time
import uuid
from typing import Any, Optional

import httpx
from mcp.server.fastmcp import FastMCP

# 强制刷新输出缓冲
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# 设置环境变量强制输出
os.environ['PYTHONUNBUFFERED'] = '1'


def flush_print(*args, **kwargs):
    """带强制刷新的打印函数"""
    print(*args, **kwargs)
    sys.stdout.flush()


# Initialize FastMCP server
mcp = FastMCP("design")

# Autobots API 配置
AUTOBOTS_API_URL = "http://autobots-bk.jd.local/autobots/api/v1/searchAiSse"
DEFAULT_AGENT_ID = "26748"
DEFAULT_TOKEN = "97fbf17086584918ab25385acf74474b"
DEFAULT_ERP = "zhouyiru"

# 请求超时配置（300秒）
REQUEST_TIMEOUT = 300.0


def _validate_required_params(**params) -> Optional[str]:
    """
    验证必需参数的有效性
    
    Args:
        **params: 参数字典，键为参数名，值为参数值
    
    Returns:
        如果验证失败返回错误信息，否则返回 None
    """
    for param_name, param_value in params.items():
        if not param_value or not str(param_value).strip():
            return f"错误：{param_name}不能为空"
    return None


def _get_env_param(env_key: str, param_name: str) -> Optional[str]:
    """
    从环境变量获取参数值
    
    Args:
        env_key: 环境变量键名
        param_name: 参数名称（用于日志显示）
    
    Returns:
        环境变量值或 None
    """
    value = os.environ.get(env_key)
    flush_print(f"🔧 从环境变量{env_key}获取{param_name}: {value}")
    return value


async def call_autobots_sse_api(
    keyword: str,
    agent_id: str = DEFAULT_AGENT_ID,
    token: str = DEFAULT_TOKEN,
    erp: str = None,
    space_id: str = None,
    folder_id: str = None
) -> str:
    """
    AI设计工具
    
    Args:
        keyword: 查询关键词
        agent_id: Autobots 代理ID
        token: Autobots 访问令牌
        erp: 用户ERP（如果为None，将从环境变量erp获取）
        space_id: JoySpace 空间ID（如果为None，将从环境变量joySpaceId获取）
        folder_id: JoySpace 文件夹ID（如果为None，将从环境变量joyFolderId获取）
    
    Returns:
        完整的响应内容字符串
    """
    # 从环境变量获取参数（如果未提供）
    if erp is None:
        erp = _get_env_param('erp', 'erp')
    
    if space_id is None:
        space_id = _get_env_param('joySpaceId', 'space_id')
    
    if folder_id is None:
        folder_id = _get_env_param('joyFolderId', 'folder_id')
    
    # 验证必需参数
    validation_params = {
        '查询关键词': keyword,
        '代理ID': agent_id,
        '访问令牌': token,
        'erp': erp,
        'space_id': space_id,
        'folder_id': folder_id
    }
    
    error_msg = _validate_required_params(**validation_params)
    if error_msg:
        flush_print(f"❌ {error_msg}")
        return error_msg
    
    # 构建完整的查询关键词
    full_keyword = _build_full_keyword(keyword, space_id, folder_id)
    if full_keyword.startswith("❌"):
        return full_keyword
    
    # 生成请求ID和跟踪ID
    trace_id = str(uuid.uuid4())
    req_id = str(int(time.time() * 1000))
    
    # 构建HTTP请求头和请求体
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "autobots-agent-id": agent_id.strip(),
        "autobots-token": token.strip()
    }
    
    payload = {
        "traceId": trace_id,
        "reqId": req_id,
        "erp": erp.strip(),
        "keyword": full_keyword
    }
    
    # 打印请求信息
    _log_request_info(keyword, full_keyword, payload, headers)
    
    # 发送HTTP POST请求并处理SSE流式响应
    return await _process_sse_response(headers, payload)


def _build_full_keyword(keyword: str, space_id: str, folder_id: str) -> str:
    """
    构建完整的查询关键词
    
    Args:
        keyword: 原始关键词
        space_id: 空间ID
        folder_id: 文件夹ID
    
    Returns:
        完整的查询关键词或错误信息
    """
    keyword_prefix = f"帮我在空间（{space_id}）的文件夹（{folder_id}）里面创建文档，标题和内容是：{keyword}"
    
    # 检测是否包含设计文档模版关键词
    if "【设计文档模版】" in keyword:
        template_name = os.environ.get('templateName')
        if template_name and template_name.strip():
            full_keyword = f"获取{template_name}的文档模版"
            flush_print(f"🔧 检测到设计文档模版请求，templateName: {template_name}")
            flush_print(f"🔧 full_keyword已替换为: {full_keyword}")
            return full_keyword
        else:
            error_msg = "❌ 错误：检测到【设计文档模版】关键词，但环境变量templateName未设置或为空"
            flush_print(error_msg)
            return error_msg
    
    return keyword_prefix + "\n" + keyword.strip()


def _log_request_info(keyword: str, full_keyword: str, payload: dict, headers: dict):
    """记录请求信息"""
    flush_print(f"🤖 正在调用 Autobots API...")
    flush_print(f"🌐 接口地址：{AUTOBOTS_API_URL}")
    flush_print(f"🔍 原始查询关键词：{keyword}")
    flush_print(f"🔍 完整查询关键词：{full_keyword}")
    flush_print(f"📋 请求参数：{json.dumps(payload, ensure_ascii=False, indent=2)}")
    flush_print(f"📋 请求头信息：{json.dumps(headers, ensure_ascii=False, indent=2)}")


async def _process_sse_response(headers: dict, payload: dict) -> str:
    """
    处理SSE流式响应
    
    Args:
        headers: 请求头
        payload: 请求体
    
    Returns:
        完整的响应内容字符串或错误信息
    """
    response_content = ""  # 改为字符串，只保留最后一次响应
    
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        try:
            async with client.stream(
                "POST",
                AUTOBOTS_API_URL,
                headers=headers,
                json=payload
            ) as response:
                
                # 检查HTTP状态码
                flush_print(f"📊 HTTP状态码：{response.status_code}")
                
                if response.status_code != 200:
                    error_msg = f"HTTP错误：状态码 {response.status_code}"
                    flush_print(f"❌ {error_msg}")
                    return error_msg
                
                # 逐行读取SSE流式响应
                flush_print("📡 开始接收SSE流式响应...")
                flush_print("-" * 50)
                
                async for line in response.aiter_lines():
                    if line and line.strip():
                        flush_print(f"📨 接收到数据：{line}")
                        response_content = line  # 只保留最后一次响应，覆盖之前的内容
                
                flush_print("-" * 50)
                flush_print("✅ SSE流式响应接收完成")
                
        except httpx.TimeoutException:
            error_msg = f"❌ 请求超时（{REQUEST_TIMEOUT}秒）"
            flush_print(error_msg)
            return error_msg
        except httpx.HTTPStatusError as e:
            error_msg = f"❌ HTTP错误：状态码 {e.response.status_code}"
            flush_print(error_msg)
            flush_print(f"📄 错误响应：{e.response.text}")
            return error_msg
        except httpx.RequestError as e:
            error_msg = f"❌ 请求错误：{str(e)}"
            flush_print(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"❌ 未知错误：{str(e)}"
            flush_print(error_msg)
            return error_msg
    
    # 处理并返回最后一次响应内容
    if response_content:
        flush_print(f"📄 最终响应内容：")
        flush_print(response_content)
        return response_content
    else:
        error_msg = "❌ 未接收到任何响应数据"
        flush_print(error_msg)
        return error_msg


@mcp.tool()
async def ai_design(
    keyword: str,
    agent_id: str = DEFAULT_AGENT_ID,
    token: str = DEFAULT_TOKEN,
    erp: str = None,
    space_id: str = None,
    folder_id: str = None
) -> str:
    """
    AI设计工具（SSE 流式响应）
    
    Args:
        erp: 用户ERP
        space_id: JoySpace设计文档的空间ID（必须）
        folder_id: JoySpace设计文档的文件夹ID（必须）
        templateName: 设计文档模版名称（可选，需要联系zhouyiru知识库投喂）
    """
    # 验证输入参数
    if not keyword or not keyword.strip():
        return "错误：查询关键词不能为空"
    
    # 调用API并获取结果
    result = await call_autobots_sse_api(
        keyword=keyword.strip(),
        agent_id=agent_id or DEFAULT_AGENT_ID,
        token=token or DEFAULT_TOKEN,
        erp=erp,
        space_id=space_id,
        folder_id=folder_id
    )
    
    # 格式化返回结果
    if result.startswith("错误：") or result.startswith("❌"):
        return f"""❌ AI设计失败！
🔍 查询关键词: {keyword}
🤖 代理ID: {agent_id or DEFAULT_AGENT_ID}
👤 用户ERP: {erp}
❌ 错误信息: {result}
💡 建议: 请检查网络连接、API配置或联系管理员"""
    else:
        return f"""✅ AI设计成功！
🔍 查询关键词: {keyword}
🤖 代理ID: {agent_id or DEFAULT_AGENT_ID}
👤 用户ERP: {erp}
📄 搜索结果:
{result}"""


@mcp.prompt()
async def sse_response_filter() -> str:
    """
    SSE流式响应过滤提示词
    
    用于指导在调用call_autobots_sse_api创建设计文档时，
    SSE模式中间过程的响应不用返回用户，判断到最后完成了返回最后一次结果即可。
    """
    return """在处理call_autobots_sse_api接口SSE流式响应时，请遵循以下规则：

1. **中间过程响应处理**：
   - SSE流式响应的中间过程数据不需要返回给用户
   - 只有当检测到响应完成时，才返回最终结果
   - 避免向用户展示过多的中间状态信息

2. **完成状态判断**：
   - 监听SSE流的结束信号
   - 当接收到完整的响应数据后，进行最终处理
   - 确保返回的是完整、有意义的最终结果

3. **用户体验优化**：
   - 减少不必要的中间信息输出
   - 提供清晰、简洁的最终结果
   - 保持响应的专业性和可读性

4. **错误处理**：
   - 如果在SSE过程中发生错误，及时返回错误信息
   - 确保用户能够了解操作的最终状态
   - 提供有用的错误诊断信息

请在调用call_autobots_sse_api时应用这些原则，确保用户获得最佳的交互体验。"""


async def interactive_mode():
    """交互式模式 - 允许用户直接操作 Autobots API"""
    flush_print("🤖 欢迎使用 AI设计工具！")
    flush_print("=" * 50)
    
    while True:
        flush_print("\n📋 请选择操作：")
        flush_print("1. AI 搜索查询")
        flush_print("2. 启动 MCP 服务器模式")
        flush_print("3. 退出程序")
        
        try:
            choice = input("\n请输入选项 (1-3): ").strip()
            
            if choice == "1":
                await search_interactive()
            elif choice == "2":
                flush_print("🚀 启动 MCP 服务器模式...")
                flush_print("💡 提示：需要退出交互式模式来启动 MCP 服务器")
                flush_print("🔄 请使用 'uv run design.py --mcp' 命令直接启动 MCP 服务器")
                flush_print("⚠️ 或者选择退出程序，然后重新运行")
                break
            elif choice == "3":
                flush_print("👋 再见！")
                break
            else:
                flush_print("❌ 无效选项，请输入 1-3")
                
        except KeyboardInterrupt:
            flush_print("\n👋 程序已退出")
            break
        except Exception as e:
            flush_print(f"❌ 发生错误：{str(e)}")


async def search_interactive():
    """交互式AI搜索"""
    flush_print("\n🔍 AI 搜索查询")
    flush_print("-" * 30)
    
    try:
        keyword = input("请输入查询关键词: ").strip()
        if not keyword:
            flush_print("❌ 查询关键词不能为空")
            return
            
        agent_id = input(f"请输入代理ID (默认: {DEFAULT_AGENT_ID}): ").strip()
        if not agent_id:
            agent_id = DEFAULT_AGENT_ID
            
        token = input(f"请输入访问令牌 (默认: {DEFAULT_TOKEN}): ").strip()
        if not token:
            token = DEFAULT_TOKEN
            
        erp = input(f"请输入用户ERP (默认: {DEFAULT_ERP}): ").strip()
        if not erp:
            erp = DEFAULT_ERP
        
        flush_print("\n🚀 开始AI搜索...")
        result = await call_autobots_sse_api(
            keyword=keyword,
            agent_id=agent_id,
            token=token,
            erp=erp
        )
        
        if not result.startswith("错误：") and not result.startswith("❌"):
            flush_print("\n🎉 AI搜索完成！")
        else:
            flush_print("\n❌ AI搜索失败")
            
    except KeyboardInterrupt:
        flush_print("\n⏹️ 操作已取消")
    except Exception as e:
        flush_print(f"\n❌ 发生错误：{str(e)}")


def show_help():
    """显示帮助信息"""
    flush_print(f"""🎯 AI设计工具使用说明

运行模式：
  uv run design.py                    # 交互式模式
  uv run design.py --mcp             # 直接启动 MCP 服务器
  uv run design.py --help            # 显示帮助信息

交互式模式功能：
  1. AI 搜索查询 - 通过交互式界面进行AI搜索
  2. 启动 MCP 服务器 - 切换到 MCP 服务器模式
  3. 退出程序

MCP 服务器模式：
  - 通过 stdio 传输运行
  - 等待 MCP 客户端连接
  - 提供 search_autobots_ai 工具

API 配置：
  - 接口地址: {AUTOBOTS_API_URL}
  - 默认代理ID: {DEFAULT_AGENT_ID}
  - 默认令牌: {DEFAULT_TOKEN}
  - 默认ERP: {DEFAULT_ERP}
  - 请求超时: {REQUEST_TIMEOUT}秒""")


def main_sync():
    """同步主函数，处理 MCP 服务器启动"""
    flush_print("🔧 AI设计工具启动中...")
    
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ['--help', '-h']:
            show_help()
        elif arg == '--mcp':
            flush_print("🚀 启动 MCP 服务器模式...")
            # 直接使用正确的 FastMCP 启动方式，避免事件循环冲突
            mcp.run(transport='stdio')
        else:
            flush_print(f"❌ 未知参数: {arg}")
            show_help()
    else:
        # 默认交互式模式需要异步运行
        try:
            asyncio.run(interactive_mode())
        except KeyboardInterrupt:
            flush_print("\n👋 程序已退出")
        except Exception as e:
            flush_print(f"❌ 交互式模式运行错误：{str(e)}")


if __name__ == "__main__":
    try:
        main_sync()
    except KeyboardInterrupt:
        flush_print("\n👋 程序已退出")
    except Exception as e:
        flush_print(f"❌ 程序运行错误：{str(e)}")
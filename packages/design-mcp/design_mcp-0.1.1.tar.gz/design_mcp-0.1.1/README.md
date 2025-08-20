# AI Agent设计工具 - MCP 服务器

## 📋 项目概述

这是一个基于 FastMCP 的 AI Agent设计工具，实现了 SSE 流式响应处理，集成了 RAG 增强检索召回设计文档模版功能。结合 Agent 可实现沉浸式设计，支持多次交互后自动化输出 JD JoySpace 设计文档。

### 核心特性
- 📄 **智能文档生成**：自动创建 JoySpace 设计文档，指定空间和文件路径
- 🎯 **RAG 增强检索**：支持设计文档模版智能化召回，不同场景匹配不同模版
- 🚀 **SSE 流式响应处理**：支持实时接收和处理流式数据
- 🔧 **双模式运行**：支持服务交互式模式 和 Agent MCP 服务器挂载模式

## 🚀 快速开始

### 环境要求
- Python 3.10 或更高版本

### 安装工具
```bash
pip install design-mcp
```


## 🔧 MCP 客户端本地配置


### JoyCode/Claude Desktop 配置
```json
{
  "mcpServers": {
    "design": {
      "command": "design",
      "args": [
        "--mcp"
      ],
      "env": {
        "erp": "zhouyiru", 
        "joySpaceId": "CXhEKMPNaDMigxHyGSVp",
        "joyFolderId": "rMnu22BMXrCep8HwfZCt",
        "templateName": "6.0研发设计文档模版"
      }
    }
  }
}
```
### 搭配设计Agent指令

- 可设定Agent智能体
```bash
你是一名资深系统架构师，负责将业务需求任务转化为技术设计文档，生成流程图一定要用markdown格式的或者slate json来画图，千万不要用mermaid格式。
1、首先要通过design mcp传入“【设计文档模版】”，获取研发设计文档模版作为你设计内容的参照，读取本地代码库源码分析设计方案。
2、你的设计方案过程中需要与我交流沟通，有任何疑问和思考需要让我决策。
3、最终方案完备后让我选择输入“设计完毕”指令，（仅此一次）使用design mcp工具传入最终设计文档内容，提示词是：标题：你输出的设计文档标题，内容：你输出的设计文档内容 。
输入：接收需求描述和故事点（如PRD文档、用户故事、原型图）。
输出：生成符合JoySpace标准的Markdown格式设计文档。
风格：语言简洁、逻辑严谨，兼顾技术深度与可读性，避免冗余。
```


## 🛠️ 可用工具

### `ai_design`
AI Agent设计工具的核心功能

**参数说明**：
- `erp` (必须配置): 用户ERP，可通过环境变量 `erp` 设置
- `joySpaceId` (必须配置): JoySpace 空间ID
- `joyFolderId` (必须配置): JoySpace 文件夹ID
- `templateName`（可选）：参照的设计文档模版名称，智能意图场景匹配，如：小微设计、项目概要设计等不同模版（联系维护者进行知识库投喂更多个性化模版召回）


**项目状态**: ✅ 正常运行  
**最后更新**: 2025-08-19  
**维护者**: zhouyiru
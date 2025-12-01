"""
MCP服务器实现
将黄历AI Agent功能暴露为MCP工具
"""
import asyncio
import json
import os
import sys
import re
from typing import Any, Sequence

# 必须在导入其他模块之前设置工作目录
# 获取脚本所在目录（项目根目录）并切换工作目录
_script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_script_dir)

from dotenv import load_dotenv

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    # 如果mcp包不可用，尝试使用mcp-python-sdk
    try:
        from mcp_python_sdk.server import Server
        from mcp_python_sdk.server.stdio import stdio_server
        from mcp_python_sdk.types import Tool, TextContent
    except ImportError:
        # 如果都不可用，使用简化的实现
        print("警告：未找到MCP SDK，请安装：pip install mcp", file=sys.stderr)
        sys.exit(1)

import agents.question as agent_question
import agents.calander as agent_calander
from pkg.sqlite.sqlite import init_db


# 初始化服务器
app = Server("cardcaptor-calendar")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    列出所有可用的工具
    """
    return [
        Tool(
            name="get_calendar_info",
            description="获取指定日期的黄历信息。支持相对日期（今天、明天、后天等）或具体日期（YYYY-MM-DD格式）。",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "日期，可以是相对日期（今天、明天、后天等）或具体日期（YYYY-MM-DD格式）",
                    },
                    "force_refresh": {
                        "type": "boolean",
                        "description": "是否强制从API获取最新数据，忽略缓存。默认为false",
                        "default": False,
                    },
                },
                "required": ["date"],
            },
        ),
        Tool(
            name="answer_calendar_question",
            description="回答关于黄历的问题。可以询问某日期的宜忌、吉时、方位等信息。",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "用户关于黄历的问题，可以包含相对日期（今天、明天等）或具体日期",
                    },
                    "force_refresh": {
                        "type": "boolean",
                        "description": "是否强制从API获取最新数据，忽略缓存。默认为false",
                        "default": False,
                    },
                },
                "required": ["question"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> Sequence[TextContent]:
    """
    处理工具调用
    """
    if arguments is None:
        arguments = {}

    try:
        if name == "get_calendar_info":
            date = arguments.get("date", "")
            force_refresh = arguments.get("force_refresh", False)
            
            if not date:
                return [TextContent(
                    type="text",
                    text="错误：必须提供日期参数"
                )]
            
            # 解析日期，将相对日期转换为具体日期
            parsed_question = agent_question.parse_question(f"查询{date}的黄历信息")
            
            # 从解析后的问题中提取日期
            date_match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', parsed_question)
            if not date_match:
                date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', parsed_question)
                if not date_match:
                    return [TextContent(
                        type="text",
                        text=f"无法解析日期：{date}。请使用相对日期（今天、明天等）或具体日期（YYYY-MM-DD格式）"
                    )]
            
            year = int(date_match.group(1))
            month = int(date_match.group(2))
            day = int(date_match.group(3))
            
            # 获取黄历信息
            calendar_info = agent_calander.get_calander_info(year, month, day, force_refresh=force_refresh)
            
            return [TextContent(
                type="text",
                text=calendar_info
            )]
        
        elif name == "answer_calendar_question":
            question = arguments.get("question", "")
            force_refresh = arguments.get("force_refresh", False)
            
            if not question:
                return [TextContent(
                    type="text",
                    text="错误：必须提供问题参数"
                )]
            
            # 解析问题，将相对日期转换为具体日期
            parsed_question = agent_question.parse_question(question)
            
            # 检查是否包含日期信息
            if "无法从问题中提取日期信息" in parsed_question or "请输入具体的时间日期" in parsed_question:
                return [TextContent(
                    type="text",
                    text=parsed_question
                )]
            
            # 回答问题
            answer = agent_calander.answer_question(parsed_question, force_refresh=force_refresh)
            
            return [TextContent(
                type="text",
                text=answer
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f"未知工具：{name}"
            )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"处理工具调用时出错：{str(e)}"
        )]


async def main():
    """
    MCP服务器主函数
    """
    # 加载环境变量
    env_path = os.path.join(_script_dir, "configs", ".env")
    if os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path)
    else:
        # 尝试从项目根目录加载
        load_dotenv()
    
    # 初始化数据库
    init_db()
    
    # 使用stdio传输运行服务器
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())


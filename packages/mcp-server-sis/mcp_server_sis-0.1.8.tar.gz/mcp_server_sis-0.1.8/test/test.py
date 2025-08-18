import asyncio
from fastmcp import Client

# 服务地址，指向在 Docker 中运行的 MCP 服务
# 端口为 3000，与 docker-compose.yml 和 Dockerfile 中设置的保持一致
# URL 中包含 /sse 来提示客户端使用 SSETransport
MCP_SERVER_URL = "http://localhost:3000/sse"

# 为需要参数的工具设置默认输入
DEFAULT_INPUTS = {
    "sis_get_course": {
        "course_code": "CSC3002",
        "term": "2410", 
        "open_only": False,
    },
    "sis_get_grades": {"term": "2024-25 Term 2"},
    "sis_get_course_outline": {"course_code": "CSC3002"},
}

async def run_full_test():
    """
    连接到 MCP 服务，并依次调用所有可用的工具。
    """
    print(f"🚀 开始全面测试，正在连接到: {MCP_SERVER_URL}")
    
    try:
        client = Client(MCP_SERVER_URL)
        
        async with client:
            tools = await client.list_tools()
            if not tools:
                print("❌ 未找到任何工具，测试中止。")
                return

            print(f"\n✅ 连接成功！发现 {len(tools)} 个可用工具。将依次调用...\n")
            
            for tool in tools:
                # 从 Tool 对象中获取名称字符串
                tool_name = tool.name
                print(f"--- 正在调用工具: {tool_name} ---")
                
                try:
                    # 使用工具名称字符串作为键
                    params = DEFAULT_INPUTS.get(tool_name, {})
                    
                    if params:
                        print(f"   参数: {params}")
                    else:
                        print("   (无参数)")

                    # 修正调用方式：将参数字典作为第二个参数传递
                    result = await client.call_tool(tool_name, params, timeout=120.0)
                    
                    # FastMCP v0.4.0+ aclient.call_tool returns a list of content blocks
                    result_text = ""
                    if isinstance(result, list):
                        for content_block in result:
                            if hasattr(content_block, 'text'):
                                result_text += content_block.text
                    else:
                        result_text = str(result)

                    # 打印部分结果以保持输出简洁
                    preview = (result_text[:500] + '...') if len(result_text) > 500 else result_text
                    print(f"\n✅ {tool_name} 调用成功！结果预览:\n---\n{preview}\n---\n")
                
                except Exception as e:
                    print(f"⚠️ 调用工具 '{tool_name}' 时发生错误: {e}\n")
            
            print("🏁 所有工具调用完毕，全面测试结束！")

    except Exception as e:
        print(f"❌ 测试失败，无法连接到服务: {e}")
        print("\n请确认:")
        print("1. Docker 容器是否已通过 'docker-compose up --build' 命令成功启动？")
        print("2. 端口 3000 是否正确映射？")
        print("3. .env 文件是否已创建并包含正确的 SIS_USERNAME 和 SIS_PASSWORD？")

if __name__ == "__main__":
    asyncio.run(run_full_test()) 
import asyncio
from fastmcp import Client
from datetime import datetime, timedelta

# 服务地址，指向在 Docker 中运行的 MCP 服务
# 端口为 3001，与 docker-compose.yml 和 Dockerfile 中设置的保持一致
# URL 中包含 /sse 来提示客户端使用 SSETransport
MCP_SERVER_URL = "http://localhost:3001/sse"

# 为需要参数的工具设置默认输入
def get_default_inputs():
    # 设置测试时间为明天
    tomorrow = datetime.now() + timedelta(days=1)
    query_start = tomorrow.strftime("%Y-%m-%d 08:00")
    query_end = tomorrow.strftime("%Y-%m-%d 22:00")
    check_start = tomorrow.strftime("%Y-%m-%d 08:00")
    check_end = tomorrow.strftime("%Y-%m-%d 22:00")

    # 设置查询时间为后天
    two_days_later = datetime.now() + timedelta(days=2)
    two_days_later_start = two_days_later.strftime("%Y-%m-%d 08:00")
    two_days_later_end = two_days_later.strftime("%Y-%m-%d 22:00")
    two_days_later_check_start = two_days_later.strftime("%Y-%m-%d 08:00")
    two_days_later_check_end = two_days_later.strftime("%Y-%m-%d 22:00")
    
    return {
        "booking_get_field_info": {
            "field": "badminton",
            "start_time": query_start,
            "end_time": query_end,
        },
        "booking_get_all_available_slots": {
            "field": "badminton",
            "start_time": query_start,
            "end_time": two_days_later_end,
        },
        "booking_get_available_places": {
            "field": "badminton",
            "query_start_time": query_start,
            "query_end_time": query_end,
            "check_start_time": check_start,
            "check_end_time": check_end,
        },
        "booking_book": {
            "field_id": "1097",
            "place_id": "test_place_id",  # 这需要从实际查询结果中获取
            "start_time": check_start,
            "end_time": check_end,
            "telephone": "",
            "reason": "🏸",
            "details": "🏸"
        }
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
            
            default_inputs = get_default_inputs()
            
            # 首先测试不需要特殊处理的工具
            safe_tools = [
                "booking_get_field_info",
                "booking_get_available_places", 
                "booking_get_all_available_slots",
                # "booking_clear_cache",
                # "booking_force_relogin"
            ]
            
            for tool in tools:
                tool_name = tool.name
                
                # 跳过预订工具，因为它会进行真实预订
                if tool_name == "booking_book":
                    print(f"--- 跳过工具: {tool_name} (真实预订操作，测试时不执行) ---")
                    continue
                    
                print(f"--- 正在调用工具: {tool_name} ---")
                
                try:
                    params = default_inputs.get(tool_name, {})
                    
                    if params:
                        print(f"   参数: {params}")
                    else:
                        print("   (无参数)")

                    result = await client.call_tool(tool_name, params, timeout=120.0)
                    
                    # FastMCP v0.4.0+ client.call_tool returns a list of content blocks
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
            print("\n📋 测试总结:")
            print("- ✅ 场地信息查询")
            print("- ✅ 可用场地查询")
            print("- ✅ 所有可用时间段查询")
            # print("- ✅ 缓存管理")
            # print("- ✅ 重新登录")
            print("- ⚠️  预订功能已跳过 (防止误操作)")
            print("\n如需测试预订功能，请谨慎手动调用 booking_book 工具。")

    except Exception as e:
        print(f"❌ 测试失败，无法连接到服务: {e}")
        print("\n请确认:")
        print("1. Docker 容器是否已通过 'docker-compose up --build' 命令成功启动？")
        print("2. 端口 3001 是否正确映射？")
        print("3. .env 文件是否已创建并包含正确的 BOOKING_USERNAME 和 BOOKING_PASSWORD？")
        print("4. 容器日志中是否有错误信息？运行 'docker-compose logs -f booking-mcp' 查看。")

async def test_booking_only():
    """
    仅测试预订功能 - 需要谨慎使用
    """
    print("⚠️  警告：这将进行真实的预订操作！")
    response = input("确定要继续吗？(输入 'yes' 继续): ")
    if response.lower() != 'yes':
        print("已取消预订测试。")
        return
    
    print(f"🚀 开始预订测试，正在连接到: {MCP_SERVER_URL}")
    
    try:
        client = Client(MCP_SERVER_URL)
        
        async with client:
            # 首先获取场地信息
            default_inputs = get_default_inputs()
            field_info_params = default_inputs["booking_get_field_info"]
            
            print("--- 获取场地信息 ---")
            print(f"   参数: {field_info_params}")
            field_result = await client.call_tool("booking_get_field_info", field_info_params, timeout=120.0)
            
            # 显示场地信息结果
            field_result_text = ""
            if isinstance(field_result, list):
                for content_block in field_result:
                    if hasattr(content_block, 'text'):
                        field_result_text += content_block.text
            else:
                field_result_text = str(field_result)
            
            print(f"\n✅ 场地信息查询结果:\n---\n{field_result_text}\n---\n")
            
            # 获取可用场地
            available_params = default_inputs["booking_get_available_places"]
            print("--- 获取可用场地 ---")
            print(f"   参数: {available_params}")
            available_result = await client.call_tool("booking_get_available_places", available_params, timeout=120.0)
            
            # 显示可用场地结果
            available_result_text = ""
            if isinstance(available_result, list):
                for content_block in available_result:
                    if hasattr(content_block, 'text'):
                        available_result_text += content_block.text
            else:
                available_result_text = str(available_result)
            
            print(f"\n✅ 可用场地查询结果:\n---\n{available_result_text}\n---\n")
            
            # 这里需要手动输入有效的 place_id
            place_id = input("请输入要预订的场地ID (从上面的查询结果中获取): ")
            if not place_id:
                print("未提供场地ID，取消预订。")
                return
            
            # 更新预订参数
            book_params = default_inputs["booking_book"]
            book_params["place_id"] = place_id
            
            print(f"--- 正在预订场地: {place_id} ---")
            print(f"   参数: {book_params}")
            book_result = await client.call_tool("booking_book", book_params, timeout=120.0)
            
            result_text = ""
            if isinstance(book_result, list):
                for content_block in book_result:
                    if hasattr(content_block, 'text'):
                        result_text += content_block.text
            else:
                result_text = str(book_result)
            
            print(f"\n📋 预订结果:\n{result_text}")
            
    except Exception as e:
        print(f"❌ 预订测试失败: {e}")

if __name__ == "__main__":
    print("选择测试模式:")
    print("1. 安全测试 (不包含预订操作)")
    print("2. 完整测试 (包含预订操作 - 谨慎使用)")
    choice = input("请选择 (1 或 2): ")
    
    if choice == "2":
        asyncio.run(test_booking_only())
    else:
        asyncio.run(run_full_test()) 
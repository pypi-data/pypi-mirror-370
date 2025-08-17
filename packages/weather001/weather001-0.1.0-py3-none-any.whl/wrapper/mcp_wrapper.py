import requests
import sys

from fastmcp import FastMCP

from common.Response import Response
from weather import get_weather

mcp = FastMCP("天气获取小工具")


def get_weather_data(location):
    # 这里是向国家气象局API发送请求的代码
    # 响应数据将从API返回
    return get_weather(location)


def format_weather_data(resp: Response) -> str:
    # 这里是格式化天气数据的代码
    if resp.is_success:
        data = resp.data
        return f"{data['城市']} {data['天气状况']} {data['温度']} {data['湿度']} {data['风速']}"
    else:
        return "无法获取天气信息"


@mcp.tool("获取天气")
def get_current_weather(location: str):
    """获取当前位置的天气情况"""
    weather_data = get_weather_data(location)
    return format_weather_data(weather_data)


def main():
    """程序入口点"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("天气获取小工具")
        print("使用方法:")
        print("  weather001              # 运行MCP服务器")
        print("  weather001 --help       # 显示帮助信息")
        return
    
    # 运行MCP服务器
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
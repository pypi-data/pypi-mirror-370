from typing import Optional
import asyncio
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
from gusantong.sina.sina import Sina
from gusantong.eastmoney.eastmoney import Eastmoney
from gusantong.wallstreetcn.wallstreetcn import Wallstreetcn
from gusantong.jin10.jin10 import Jin10
from gusantong.data.price import Price
from gusantong.gelonghui.gelonghui import GeLongHui
from gusantong.zhitongcaijing.zhitongcaijing import Zhitongcaijing


server = Server("mcp-gusantong")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    列出可用的工具。
    每个工具使用 JSON Schema 验证来指定其参数。
    """
    return [
        types.Tool(
            name="live_news",
            description="获取全球实时财经新闻数据",
            inputSchema={
                "type": "object",
                "properties": {

                },
            },
        ),
        types.Tool(
            name="hk_roll_news",
            description="获取港股实时新闻",
            inputSchema={
                "type": "object",
                "properties": {

                },
            },
        ),
        types.Tool(
            name="us_roll_news",
            description="获取美股实时新闻",
            inputSchema={
                "type": "object",
                "properties": {

                },
            },
        ),
        types.Tool(
            name="us_target_price",
            description="获取美股调整价格",
            inputSchema={
                "type": "object",
                "properties": {

                },
            },
        ),
        types.Tool(
            name="hk_target_price",
            description="获取港股调整价格",
            inputSchema={
                "type": "object",
                "properties": {

                },
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
        name: str, arguments: Optional[dict]
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    处理工具执行请求。
    工具可以获取财经新闻数据并通知客户端变更。
    """
    if name == "live_news":
        data_list = await live_news()
        final_list: list = []
        for data in data_list:
            final_list.append(types.TextContent(
                type="text",
                text=data
            ))
        return final_list
    elif name == "hk_roll_news":
        data_list = await hk_roll_news()
        final_list: list = []
        for data in data_list:
            final_list.append(types.TextContent(
                type="text",
                text=data
            ))
        return final_list
    elif name == "us_roll_news":
        data_list = await us_roll_news()

        final_list: list = []
        for data in data_list:
            final_list.append(types.TextContent(
                type="text",
                text=data
            ))
        return final_list
    elif name == "us_target_price":
        data_list = await us_target_price()

        final_list: list = []
        for data in data_list:
            final_list.append(types.TextContent(
                type="text",
                text=data
            ))
        return final_list
    elif name == "hk_target_price":
        data_list = await hk_target_price()

        final_list: list = []
        for data in data_list:
            final_list.append(types.TextContent(
                type="text",
                text=data
            ))
        return final_list
    else:
        raise ValueError(f"未知工具: {name}")


async def hk_roll_news() -> list:
    """
    Name:
        获取港股滚动新闻。
    Description:
        获取港股滚动新闻。
    """

    final_list: list = []

    """ 新浪 """
    sina = Sina()
    sina_data_list = await sina.hk_roll_news()
    final_list.extend(sina_data_list)

    """ 华尔街 """
    wallstreetcn = Wallstreetcn()
    wallstreetcn_data_list = await wallstreetcn.hk_roll_news()
    final_list.extend(wallstreetcn_data_list)

    """ 金十数据 """
    jin10 = Jin10()
    jin10_data_list = await jin10.hk_roll_news()
    final_list.extend(jin10_data_list)

    """ 格隆汇 """
    geLongHui = GeLongHui()
    geLongHui_data_list = await geLongHui.hk_roll_news()
    final_list.extend(geLongHui_data_list)

    """ 智通财经 """
    zhitongcaijing = Zhitongcaijing()
    zhitongcaijing_data_list = await zhitongcaijing.hk_roll_news()
    final_list.extend(zhitongcaijing_data_list)

    return final_list

async def us_roll_news() -> list:
    """
    Name:
        获取美股滚动新闻。
    Description:
        获取美股滚动新闻。
    """

    final_list: list = []

    """ 新浪 """
    sina = Sina()
    sina_data_list = await sina.us_roll_news()
    final_list.extend(sina_data_list)

    """ 华尔街 """
    wallstreetcn = Wallstreetcn()
    wallstreetcn_data_list = await wallstreetcn.us_roll_news()
    final_list.extend(wallstreetcn_data_list)

    """ 金十数据 """
    jin10 = Jin10()
    jin10_data_list = await jin10.us_roll_news()
    final_list.extend(jin10_data_list)

    """ 格隆汇 """
    geLongHui = GeLongHui()
    geLongHui_data_list = await geLongHui.us_roll_news()
    final_list.extend(geLongHui_data_list)

    """ 智通财经 """
    zhitongcaijing = Zhitongcaijing()
    zhitongcaijing_data_list = await zhitongcaijing.us_roll_news()
    final_list.extend(zhitongcaijing_data_list)

    return final_list

async def live_news() -> list:
    """
    Name:
        获取全球实时财经新闻。
    Description:
        获取全球实时财经新闻
    """

    final_list: list = []

    """ 新浪 """
    sina = Sina()
    sina_data_list = await sina.live_news()
    final_list.extend(sina_data_list)

    """ 东方财富 """
    eastmoney = Eastmoney()
    eastmoney_data_list = await eastmoney.live_news()
    final_list.extend(eastmoney_data_list)


    return final_list


async def us_target_price():
    final_list: list = []

    """ 金十数据 """
    price = Price()
    price_data_list = await price.us_roll_news()
    final_list.extend(price_data_list)

    return final_list

async def hk_target_price():
    final_list: list = []

    """ 金十数据 """
    price = Price()
    price_data_list = await price.hk_roll_news()
    final_list.extend(price_data_list)

    return final_list

async def main():
    # 使用标准输入/输出流运行服务器
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-gusantong",
                server_version="1.0.3",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


# 如果你想连接到自定义客户端,这是必需的
if __name__ == "__main__":
    asyncio.run(main())
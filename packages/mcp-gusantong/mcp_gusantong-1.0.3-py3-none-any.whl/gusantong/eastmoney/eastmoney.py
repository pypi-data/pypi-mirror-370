import asyncio
import aiohttp
import ssl
import certifi
import json
import logging
import random
import time
from urllib.parse import urlencode
from gusantong.utils.user_agent_util import UserAgent

ssl_context = ssl.create_default_context(cafile=certifi.where())

logger = logging.getLogger("mcp-gusantong")
logger.setLevel("DEBUG")


class Eastmoney:

    async def live_news(self) -> list:
        """
        Name:
            获取全球实时财经新闻。
        Description:
            获取7*24小时全球实时财经新闻直播数据，支持分页查询
        返回:
            JSON字符串，包含所有新闻数据
        """

        all_news: list = []
        page_size: int = 50
        max_page: int = 1
        final_list: list = []

        logger.info("获取数据开始")
        await live_news_fetch_page(page_size, max_page, all_news)
        logger.info("数据获取完成")

        for item in all_news:
            final_list.append(item['summary'])

        logger.info(f"获取全球实时财经新闻共提取了 {len(final_list)} 条新闻摘要")
        return final_list


async def live_news_fetch_page(page_size: int = 50, max_page: int = 1, all_news: list = []):
    """
    获取分页数据

    参数:
        tag_id: 标签 ID  0：全部 10：A股 1:宏观 3:公司 4:数据 5:市场 102:国际 6:观点 7:央行 8:其他
        page: 起始页码，默认为1
        page_size: 每页数量，默认为20
        max_page: 最大抓取页数，1表示只抓取当前页
        all_news: 所有新闻列表
    返回:
        所有新闻列表
    """

    base_url = "https://np-weblist.eastmoney.com/comm/web/getFastNewsList"

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        headers = {"User-Agent": UserAgent.get_random_from_pool()}
        page = 1
        req_trace = int(time.time() * 1000)
        time_ = int(time.time() * 1000)
        sortEnd: str = ""
        while page <= max_page:
            # 随机延迟防止被封
            delay = random.uniform(1.0, 5.0)
            logger.info(f"等待 {delay:.2f} 秒后获取第 {page} 页数据")
            await asyncio.sleep(delay)

            params = {
                "client": "web",
                "biz": "web_724",
                "fastColumn": 102,
                "sortEnd": sortEnd,
                "pageSize": page_size,
                "req_trace": req_trace,
                "_": time_
            }

            url = f"{base_url}?{urlencode(params)}"
            logger.info(f"请求地址: {url}")

            try:
                # 发送HTTP请求
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=60)) as response:
                    # 检查HTTP状态码
                    response.raise_for_status()
                    # 解析JSON数据
                    data = await response.json()

                    # 处理数据
                    result = await live_news_handle_data(data)

                    # 检查错误
                    news_list = result["news_list"]
                    if not news_list:
                        break

                    # 添加到总列表
                    all_news.extend(news_list)

                    logger.info(f"成功获取第 {page} 页，共 {len(all_news)} 条新闻")
                    # 继续下一页
                    sortEnd = result["sortEnd"]
                    page += 1
            except aiohttp.ClientError as e:
                logger.error(f"网络请求失败: {str(e)}")
            except json.JSONDecodeError as e:
                logger.error(f"响应数据不是有效的JSON格式: {str(e)}")
            except Exception as e:
                logger.error(f"获取数据失败: {str(e)}")


async def live_news_handle_data(data: dict) -> dict:
    """
    处理API返回的数据，提取feed列表

    参数:
        data: API返回的原始JSON数据
    返回:
        处理后的新闻数据
    """
    try:
        # 检查状态码
        if data.get("code") != "1":
            logger.error("API返回非零状态码")
            return {"news_list": [], "sortEnd": ""}

        # 提取feed列表和分页信息
        fastNewsList = data.get("data", {}).get("fastNewsList", [])
        sortEnd = data.get("data", {}).get("sortEnd", "")

        # 返回数据和分页信息
        return {
            "news_list": fastNewsList,
            "sortEnd": sortEnd
        }
    except Exception as e:
        logger.error(f"数据处理失败: {str(e)}")
        return {"news_list": [], "sortEnd": ""}

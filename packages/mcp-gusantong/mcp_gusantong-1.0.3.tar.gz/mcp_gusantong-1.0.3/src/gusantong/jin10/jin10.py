import asyncio
import aiohttp
import ssl
import certifi
import json
import logging
import random
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from gusantong.utils.user_agent_util import UserAgent

logger = logging.getLogger("mcp-gusantong")
logger.setLevel("DEBUG")

ssl_context = ssl.create_default_context(cafile=certifi.where())


class Jin10:

    async def hk_roll_news(self) -> list:
        """
        Name:
            获取港股滚动新闻。
        Description:
            获取港股滚动新闻。
        """
        channel: str = '2'
        return await query_data(channel);

    async def us_roll_news(self) -> list:
        """
        Name:
            获取美股滚动新闻。
        Description:
            获取美股滚动新闻。
        """
        channel: str = '1'
        return await query_data(channel);


async def query_data(channel: str = '1'):
    max_page: int = 3
    all_news: list = []
    final_list: list = []

    logger.info("获取数据开始")
    await roll_news_fetch_page(channel, max_page, all_news)
    logger.info("获取数据完成")

    for item in all_news:
        if item["data"] and item["type"] == 0:
            final_list.append(BeautifulSoup(item["data"]["content"], 'html.parser').get_text())
    logger.info(f"获取新闻共提取了 {len(final_list)} 条新闻快讯")
    return final_list


async def roll_news_fetch_page(channel, max_page, all_news):
    """
    获取分页数据

    参数:
        channel: 渠道
        max_page: 最大抓取页数，1表示只抓取当前页
        all_news: 所有新闻列表
    返回:
        所有新闻列表
    """
    base_url = "https://flash-api.ushknews.com/get_flash_list_with_channel"
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Origin": "https://www.ushknews.com",
            "Referer": "https://www.ushknews.com/",
            "X-App-Id": "brCYec5s1ova317e",
            "X-Version": "1.0.0",
            "User-Agent": UserAgent.get_random_from_pool()
        }
        max_time: str = ''
        page = 1
        while page <= max_page:
            # 随机延迟防止被封
            delay = random.uniform(1.0, 5.0)
            logger.info(f"等待 {delay:.2f} 秒后获取第 {page} 页数据")
            await asyncio.sleep(delay)

            params = {
                "channel": '',
            }
            if len(max_time) != 0:
                params["max_time"] = max_time

            url = f"{base_url}?{urlencode(params)}"

            try:
                # 发送HTTP请求
                logger.info(f"请求URL: {url}")
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=60)) as response:
                    response.raise_for_status()  # 检查HTTP状态码

                    # 解析JSON数据
                    data = await response.json()

                    # 检查API状态码
                    if data.get("status") != 200:
                        logger.warning(f"第 {page} 页返回状态码异常")
                        break

                    # 处理数据
                    feed_list = data.get("data", [])
                    if not feed_list:
                        logger.info(f"第 {page} 页无数据，停止获取")
                        break

                    # 添加到总列表
                    all_news.extend(feed_list)
                    logger.info(f"成功获取第 {page} 页，共 {len(feed_list)} 条新闻")

                    # 继续下一页
                    page += 1
                    max_time = feed_list[-1].get("time", "")
            except aiohttp.ClientError as e:
                logger.error(f"网络请求失败: {str(e)}")
                break
            except json.JSONDecodeError as e:
                logger.error(f"响应数据不是有效的JSON格式: {str(e)}")
                break
            except asyncio.TimeoutError:
                logger.error(f"请求超时: {url}")
                break
            except Exception as e:
                logger.error(f"获取数据失败: {str(e)}")
                break

import asyncio
import aiohttp
import ssl
import certifi
import json
import logging
import random
from datetime import datetime
from urllib.parse import urlencode
from gusantong.utils.user_agent_util import UserAgent

logger = logging.getLogger("mcp-gusantong")
logger.setLevel("DEBUG")

ssl_context = ssl.create_default_context(cafile=certifi.where())

now = datetime.now()
year, month = now.year, now.month
first_day = datetime(year, month, 1).strftime("%Y-%m-%d")

class Price:

    async def hk_roll_news(self) -> list:
        """
        Name:
            获取港股价格调整。
        Description:
            获取港股价格调整。
        """

        category: str = 'hk'
        result_list: list = []
        indicator_list: list = [
            {'id': 1744, 'name': '快手(01024.HK)'},
            {'id': 1100, 'name': '腾讯控股(00700.HK)'},
            {'id': 1648, 'name': '泡泡玛特(09992.HK)'},
            {'id': 1467, 'name': '山东黄金(01787.HK)'},
            {'id': 1453, 'name': '网易(09999.HK)'},
            {'id': 2363, 'name': '腾讯音乐(01698.HK)'},
            {'id': 1306, 'name': '小米集团(01810.HK)'},
            {'id': 1358, 'name': '石药集团(01093.HK)'},
            {'id': 1306, 'name': '小米集团(01810.HK)'},
            {'id': 1468, 'name': '新华保险(01336.HK)'},
            {'id': 1312, 'name': '美团(03690.HK)'},
            {'id': 1125, 'name': '比亚迪股份(01211.HK)'},
            {'id': 1813, 'name': '小鹏汽车(09868.HK)'},
            {'id': 1478, 'name': '翰森制药(03692.HK)'},
            {'id': 1100, 'name': '腾讯控股(00700.HK)'},
            {'id': 1539, 'name': '药明生物(02269.HK)'},
            {'id': 1422, 'name': '阿里巴巴(09988.HK)'},
            {'id': 2195, 'name': '百度(09888.HK)'},
            {'id': 1489, 'name': '金蝶国际(00268.HK)'},
            {'id': 1165, 'name': '渣打集团(02888.HK)'},
            {'id': 1085, 'name': '比亚迪电子(00285.HK)'},
            {'id': 1386, 'name': '药明康德(02359.HK)'},
            {'id': 1781, 'name': '哔哩哔哩(09626.HK)'},
            {'id': 1127, 'name': '友邦保险(01299.HK)'},
            {'id': 1453, 'name': '网易(09999.HK)'},
            {'id': 1141, 'name': '周大福(01929.HK)'},
            {'id': 1452, 'name': '京东(09618.HK)'},
            {'id': 1156, 'name': '舜宇光学科技(02382.HK)'},
            {'id': 1324, 'name': '阿里健康(00241.HK))'}
        ]
        for indicator in indicator_list:
            final_list = await query_data(category, indicator)
            result_list.extend(final_list)

        return result_list

    async def us_roll_news(self) -> list:
        """
        Name:
            获取美股价格调整。
        Description:
            获取美股价格调整。
        """

        category: str = 'us'
        result_list: list = []
        indicator_list: list = [
            {'id': 1185, 'name': '苹果(AAPL.O)'},
            {'id': 1189, 'name': '亚马逊(AMZN.O)'},
            {'id': 1217, 'name': '波音(BA.N)'},
            {'id': 1190, 'name': 'Meta Platforms(META.O)'},
            {'id': 1188, 'name': '微软(MSFT.O)'},
            {'id': 1506, 'name': '默沙东(MRK.N)'},
            {'id': 1222, 'name': '英伟达(NVDA.O)'},
            {'id': 1239, 'name': '星巴克(SBUX.O)'},
            {'id': 1258, 'name': '特斯拉(TSLA.O)'},
            {'id': 1226, 'name': '高通(QCOM.O)'},
            {'id': 1768, 'name': 'Coinbase(COIN.O)'},
            {'id': 1208, 'name': '可口可乐(KO.N)'},
            {'id': 1220, 'name': '麦当劳(MCD.N)'},
            {'id': 1195, 'name': '美国银行(BAC.N)'},
            {'id': 1238, 'name': '奈飞(NFLX.O)'},
            {'id': 1213, 'name': '百事(PEP.O)'},
            {'id': 1207, 'name': '甲骨文(ORCL.N)'},
            {'id': 1303, 'name': 'AMD(AMD.O)'},
            {'id': 1394, 'name': 'Uber(UBER.N)'},
            {'id': 1038, 'name': '京东(JD.O)'},
            {'id': 1023, 'name': '阿里巴巴(BABA.N)'}
        ]

        for indicator in indicator_list:
            final_list = await query_data(category, indicator)
            result_list.extend(final_list)

        return result_list


async def query_data(category: str = 'us', indicator: dict = {}):
    limit: int = 20
    max_page: int = 1
    all_news: list = []
    final_list: list = []

    logger.info("获取数据开始")
    await roll_news_fetch_page(category, indicator, limit, max_page, all_news)
    logger.info("获取数据完成")

    context = []
    for item in all_news:
        dt = datetime.strptime(item["pub_time"], "%Y-%m-%d %H:%M:%S")
        date = dt.strftime("%Y-%m-%d")
        if date >= first_day:
            # 机构名称
            institution = item["institution"]
            # 目标价
            previous_target_price = item["previous_target_price"]
            latest_target_price = item["latest_target_price"]
            context.append(
                f'机构名称:{institution}调整{indicator["name"]}目标价格从{previous_target_price}美元到{latest_target_price}美元\n')


    if len(context) != 0:
        final_list.append("".join(context))

    logger.info(f"获取新闻共提取了 {len(final_list)} 条新闻快讯")
    return final_list


async def roll_news_fetch_page(category, indicator, limit, max_page, all_news):
    """
    获取分页数据

    参数:
        category: 渠道
        max_page: 最大抓取页数，1表示只抓取当前页
        all_news: 所有新闻列表
    返回:
        所有新闻列表
    """
    base_url = "https://calendar-api.ushknews.com/getWebTargetPriceList"
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Origin": "https://www.ushknews.com",
            "Referer": "https://www.ushknews.com/",
            "X-App-Id": "BNsiR9uq7yfW0LVz",
            "X-Version": "1.0.0",
            "User-Agent": UserAgent.get_random_from_pool()
        }

        date: str = ''
        page: int = 1
        offset: int = 0
        while page <= max_page:
            # 随机延迟防止被封
            delay = random.uniform(1.0, 2.0)
            logger.info(f"等待 {delay:.2f} 秒后获取第 {page} 页数据")
            await asyncio.sleep(delay)

            params = {
                "category": category,
                "limit": limit,
                "indicator_id": indicator['id']
            }
            if len(date) != 0:
                params["date"] = date
                params["offset"] = offset

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
                    feed_list = data.get("data").get("list")
                    if not feed_list:
                        logger.info(f"第 {page} 页无数据，停止获取")
                        break

                    # 添加到总列表
                    all_news.extend(feed_list)
                    logger.info(f"成功获取第 {page} 页，共 {len(feed_list)} 条新闻")

                    # 继续下一页
                    page += 1
                    offset = data.get("data").get("offset")
                    dt = datetime.strptime(feed_list[-1].get("pub_time"), "%Y-%m-%d %H:%M:%S")
                    date = dt.strftime("%Y-%m-%d")
                    if date < first_day:
                        break
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

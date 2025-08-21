import hashlib
import time
from urllib.parse import urlparse, parse_qs, urlencode

# def get(url, data=None):
#     if data is None:
#         data = {}
#     data['platform'] = 'web'
#
#     # 获取 URL 中的查询参数
#     getDataData = getQueryData(url)
#
#     # 合并参数（URL 参数会覆盖 data 中的同名参数）
#     all_params = {**data, **getDataData}
#
#     # 生成 token
#     token = tokenCrypto(all_params)
#
#     # 构建最终的 URL
#     parsed_url = urlparse(url)
#     query_params = parse_qs(parsed_url.query)
#     query_params['token'] = token
#
#     # 重建查询字符串
#     new_query_string = urlencode(query_params, doseq=True)
#     # 重建完整 URL
#     final_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{new_query_string}"
#     return final_url
#
#
# def getQueryData(url):
#     parsed = urlparse(url)
#     if not parsed.query:
#         return {}
#
#     # 将查询参数转换为字典
#     query_params = parse_qs(parsed.query)
#
#     # 将列表值转换为单个值（取最后一个值）
#     result = {}
#     for key, values in query_params.items():
#         result[key] = values[-1] if values else ''
#
#     return result
#
#
# def tokenCrypto(params):
#     params['platform'] = 'web'
#     # 合并参数（URL 参数会覆盖 data 中的同名参数）
#     # 对参数按键进行排序
#     sorted_params = sorted(params.items(), key=lambda x: x[0])
#
#     # 构建参数字符串
#     param_string = '&'.join([f"{key}={value}" for key, value in sorted_params])
#
#     # 计算 SHA1 哈希
#     sha1_hash = hashlib.sha1(param_string.encode('utf-8')).hexdigest()
#     return sha1_hash

class TokenCrypto:

    @staticmethod
    def tokenCrypto(params):
        params['platform'] = 'web'
        # 对参数按键进行排序
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        # 构建参数字符串
        param_string = '&'.join([f"{key}={value}" for key, value in sorted_params])
        # 计算 SHA1 哈希
        sha1_hash = hashlib.sha1(param_string.encode('utf-8')).hexdigest()
        return sha1_hash


# if __name__ == '__main__':
#     base_url = "https://www.zhitongcaijing.com/immediately/content-list.html"
#
#     params = {
#         "last_update_time": int(time.time()),
#         "platform": "web",
#         "type": "usstock"
#     }
#     params['token'] = TokenCrypto.tokenCrypto(params)
#     url = f"{base_url}?{urlencode(params)}"
#     print(url)



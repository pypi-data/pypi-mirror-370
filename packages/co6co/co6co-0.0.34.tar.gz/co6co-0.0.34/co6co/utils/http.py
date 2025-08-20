# -*- coding:utf-8 -*-

import requests


# 禁用安全请求警告 不验证 verify=False
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

"""
使用socks代理方法
pip install PySocks

import socket
import socks
import requests

socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
socket.socket = socks.socksocket
print(requests.get('http://ip-api.com/json').text)

"""


def download(url, timeout: int | tuple | None = None, proxy: str | dict = None, header_dict: dict = None, verify: bool = True) -> (int, bytes):
    """
    return : http.status,bytes
    """
    # requests.utils.requote_uri(url) #url 编码
    response = get(url, timeout, proxy, header_dict, verify)
    return (response.status_code, response.content)


def get(url, timeout: int | tuple | None = None, proxy: str | dict = None, header_dict: dict = None, verify: bool = True) -> requests.Response:
    """
    proxy: 
        # pip install requests[socks] 
        proxy = {'http': 'socks5://127.0.0.1:1080', 'https': 'socks5://127.0.0.1:1080'} 
    """
    proxies = {}
    if proxy != None and isinstance(proxy, str):
        proxies = {'http': f'http://{proxy}', 'https': f'https://{proxy}'}
    elif proxy != None and isinstance(proxy, dict):

        proxies = proxy
    else:
        proxies = None
    headers = {
        # "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        # "Accept-Encoding":"gzip, deflate, br",
        # "Accept-Language":"zh-CN,zh;q=0.9",
        # "Cache-Control":"no-cache",
        # "Pragma":"no-cache",
        # "Sec-Ch-Ua":'"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        # "Sec-Ch-Ua-Mobile":"?0",
        # "Sec-Ch-Ua-Platform":'"Windows"',
        # "Sec-Fetch-Dest":"document",
        # "Sec-Fetch-Mode":"navigate",
        # "Sec-Fetch-Site":"none",
        # "Sec-Fetch-User":"?1",
        # "Upgrade-Insecure-Requests":"1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        # 'User-Agent':'BaiduSipder'
    }
    if header_dict != None:
        headers.update(header_dict)
    if timeout == None:
        timeout = (5, 15)
    resp = requests.get(url, headers=headers, timeout=timeout,
                        allow_redirects=True, proxies=proxies, verify=verify)
    if len(resp.history) > 0:  # 存在302 跳转
        location_url = resp.history[len(
            resp.history) - 1].headers.get('Location')
        resp = requests.get(location_url, headers=headers,
                            timeout=(15, 30), proxies=proxies)
        return resp
    return resp

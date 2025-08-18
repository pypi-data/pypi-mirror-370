import random
import time
import httpx
from httpx import Limits
from httpx_socks import AsyncProxyTransport
from ..API.api import PROXY_API_URL

_working_proxy = None
_working_proxy_timestamp = 0
_PROXY_CACHE_DURATION = 300  

DEFAULT_HEADERS = {
    "User-Agent": "WaifuPython/1.0 akoushik88@gmail.com"
}

Connection = Limits(max_keepalive_connections=200, max_connections=1000)

client = httpx.AsyncClient(
    timeout=15.0,
    follow_redirects=True,
    limits=Connection,
    headers=DEFAULT_HEADERS
)

def get_random_proxy() -> str:
    try:
        response = httpx.get(PROXY_API_URL, timeout=10)
        response.raise_for_status()
        proxies = response.text.strip().splitlines()
        if proxies:
            top_proxies = proxies[:10]
            selected = random.choice(top_proxies)
            return selected
    except Exception as e:
        print(f"Error fetching proxies: {e}")
    return ""

def get_working_proxy() -> str:
    global _working_proxy, _working_proxy_timestamp
    now = time.time()
    if _working_proxy and (now - _working_proxy_timestamp) < _PROXY_CACHE_DURATION:
        return _working_proxy
    new_proxy = get_random_proxy()
    if new_proxy:
        _working_proxy = new_proxy
        _working_proxy_timestamp = now
    return _working_proxy

def get_dynamic_client(use_proxy: bool = False) -> httpx.AsyncClient:
    if use_proxy:
        proxy_url = get_working_proxy()
        if proxy_url:
            transport = AsyncProxyTransport.from_url(proxy_url)
            return httpx.AsyncClient(
                transport=transport,
                timeout=15.0,
                follow_redirects=True,
                limits=Connection,
                headers=DEFAULT_HEADERS
            )
    return client

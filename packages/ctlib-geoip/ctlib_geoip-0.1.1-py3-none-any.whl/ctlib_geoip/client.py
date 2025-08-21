"""
同步GeoIP客户端实现
"""
import ipaddress
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Union

import httpx

from .base import BaseGeoIPClient
from .constants import DEFAULT_TTL, DEFAULT_CACHE_LEN, DEFAULT_MAX_RETRIES, DEFAULT_MAX_WAIT_TIME, DataSource
from .models import GeoIP
from .types import Unset, SourceType, TTLType

logger = logging.getLogger(__name__)


class GeoIPClient(BaseGeoIPClient):
    """同步GeoIP客户端"""

    def __init__(
        self,
        url: str,
        source: Union[DataSource, str, None] = None,
        ttl: int = DEFAULT_TTL,
        cache_len: int = DEFAULT_CACHE_LEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        max_wait_time: int = DEFAULT_MAX_WAIT_TIME,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        初始化同步GeoIP客户端
        
        Args:
            url: GeoIP服务地址
            source: 数据源
            ttl: 数据有效期（秒）
            cache_len: 缓存最大条数
            max_retries: 最大重试次数
            max_wait_time: 最长等待时间（秒）
            headers: HTTP请求头
        """
        super().__init__(
            url=url,
            source=source,
            ttl=ttl,
            cache_len=cache_len,
            max_retries=max_retries,
            max_wait_time=max_wait_time,
            headers=headers,
        )

        self.http_client = httpx.Client(
            timeout=httpx.Timeout(30.0),
            headers=self.headers,
            follow_redirects=True
        )

    def lookup(
        self,
        ip: Union[str, ipaddress.IPv4Address],
        source: SourceType = Unset,
        ttl: TTLType = Unset,
        **extra,
    ) -> Optional[GeoIP]:
        """
        查询IP地址
        
        Args:
            ip: IP地址
            source: 数据源，Unset表示使用Client设置/默认值，None表示不携带该参数
            ttl: TTL，Unset表示使用Client设置/默认值, None表示不携带该参数
            
        Returns:
            GeoIP对象，如果查询失败则返回None
        """
        try:
            ipaddress.IPv4Address(ip)
        except ipaddress.AddressValueError as e:
            logger.error(f"无效的IPv4地址: {e}")
            return None

        ip = str(ip)
        if source is Unset:
            source = self.source
        if ttl is Unset:
            ttl = self.ttl
        ttl_delta = timedelta(seconds=ttl)

        now = datetime.now(timezone.utc)
        try:
            # 尝试从缓存获取
            cached_result = self.cache_manager.get(ip)
            if cached_result:
                if source:
                    if cached_geoip := cached_result.get(source):
                        if cached_geoip.updated_at + ttl_delta > now:
                            return cached_geoip
                cached_geoip = max(cached_result.values(), key=lambda x: x.updated_at)
                if cached_geoip.updated_at + ttl_delta > now:
                    return cached_geoip

            url = self._build_url(ip, source, ttl, **extra)
            result = self._fetch_from_api(url, ip)
            if result:
                if cached_result:
                    cached_result[result.source] = result
                else:
                    self.cache_manager.set(ip, {result.source: result})
                logger.debug(f"API查询成功，已缓存: {ip}")
                return result

        except Exception as e:
            logger.error(f"查询IP失败: {ip}, 错误: {e}")
            return None

        return None

    def _fetch_from_api(self, url: str, ip: str) -> Optional[GeoIP]:
        """
        从API获取数据

        Args:
            url: 请求URL地址
            ip: 查询IP地址

        Returns:
            GeoIP对象，如果失败则返回None
        """
        headers = self.headers.copy()
        logger.debug(f"请求API: {url}")

        for attempt in range(1, self.max_retries + 1):
            try:
                response = self._make_request(url, headers)
                result = self._parse_response(response)
                logger.debug(f"API请求成功: {ip}")
                return result

            except Exception as e:
                logger.warning(f"API请求失败 (第{attempt}次): {ip}, 错误: {e}")

                if attempt < self.max_retries:
                    self._handle_request_error(e, attempt)
                else:
                    logger.error(f"API请求最终失败: {ip}, 错误: {e}")
                    return None
        return None

    def _make_request(self, url: str, headers: dict) -> httpx.Response:
        """
        发送HTTP请求

        Args:
            url: 请求URL
            headers: 请求头

        Returns:
            HTTP响应
        """
        return self.http_client.get(url, headers=headers)

    def close(self) -> None:
        """关闭客户端，释放资源"""
        if hasattr(self, 'http_client'):
            self.http_client.close()
        logger.debug("同步GeoIP客户端已关闭")

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()

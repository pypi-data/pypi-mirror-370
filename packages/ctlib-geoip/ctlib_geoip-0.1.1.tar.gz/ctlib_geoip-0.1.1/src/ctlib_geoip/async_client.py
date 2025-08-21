"""
异步GeoIP客户端实现
"""

import asyncio
import ipaddress
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Union

import httpx

from .base import BaseGeoIPClient
from .constants import DEFAULT_TTL, DEFAULT_CACHE_LEN, DEFAULT_MAX_RETRIES, DEFAULT_MAX_WAIT_TIME, DataSource
from .exceptions import GeoIPError, GeoIPNetworkError
from .models import GeoIP
from .types import Unset, SourceType, TTLType

logger = logging.getLogger(__name__)


class AsyncGeoIPClient(BaseGeoIPClient):
    """异步GeoIP客户端"""

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
        初始化异步GeoIP客户端
        
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

        # 创建异步HTTP客户端
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            headers=self.headers,
            follow_redirects=True
        )

    async def lookup(
        self,
        ip: Union[str, ipaddress.IPv4Address],
        source: SourceType = Unset,
        ttl: TTLType = Unset,
        **extra
    ) -> Optional[GeoIP]:
        """
        异步查询IP地址
        
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
            result = await self._fetch_from_api(url, ip)
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

    async def _fetch_from_api(self, url: str, ip: str) -> Optional[GeoIP]:
        """
        从API异步获取数据
        
        Args:
            url: 请求URL地址
            ip: 查询IP地址

        Returns:
            GeoIP对象，如果失败则返回None
        """
        headers = self.headers.copy()
        logger.debug(f"异步请求API: {url}")

        for attempt in range(1, self.max_retries + 1):
            try:
                response = await self._make_request(url, headers)
                result = self._parse_response(response)
                logger.debug(f"异步API请求成功: {ip}")
                return result

            except Exception as e:
                logger.warning(f"异步API请求失败 (第{attempt}次): {ip}, 错误: {e}")

                if attempt < self.max_retries:
                    await self._handle_request_error_async(e, attempt)
                else:
                    logger.error(f"异步API请求最终失败: {ip}, 错误: {e}")
                    return None

        return None

    async def _make_request(self, url: str, headers: dict) -> httpx.Response:
        """
        发送异步HTTP请求
        
        Args:
            url: 请求URL
            headers: 请求头
            
        Returns:
            HTTP响应
        """
        return await self.http_client.get(url, headers=headers)

    async def _handle_request_error_async(self, error: Exception, attempt: int) -> None:
        """
        异步处理请求错误
        
        Args:
            error: 错误对象
            attempt: 重试次数
            
        Raises:
            GeoIPNetworkError: 网络错误
        """
        if attempt >= self.max_retries:
            logger.error(f"异步请求失败，已达到最大重试次数: {error}")
            if isinstance(error, httpx.RequestError):
                raise GeoIPNetworkError(f"异步网络请求失败: {error}")
            else:
                raise GeoIPError(f"异步请求失败: {error}")

        wait_time = self._calculate_wait_time(attempt)
        logger.warning(f"异步请求失败，{wait_time}秒后重试 (第{attempt}次): {error}")
        await asyncio.sleep(wait_time)

    async def close(self) -> None:
        """关闭异步客户端，释放资源"""
        if hasattr(self, 'http_client'):
            await self.http_client.aclose()
        logger.debug("异步GeoIP客户端已关闭")

    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()

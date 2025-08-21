"""
基础客户端抽象类
"""
import ipaddress
import logging
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, Union
from urllib.parse import urlsplit, parse_qs, urlencode

import httpx

from .cache import CacheManager
from .constants import DEFAULT_TTL, DEFAULT_CACHE_LEN, DEFAULT_MAX_RETRIES, DEFAULT_MAX_WAIT_TIME, DataSource
from .exceptions import GeoIPError, GeoIPNetworkError, GeoIPAPIError, GeoIPValidationError
from .models import GeoIP, APIResponse
from .types import SourceType, TTLType, Unset

logger = logging.getLogger(__name__)


class BaseGeoIPClient(ABC):
    """GeoIP客户端基础抽象类"""

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
        初始化GeoIP客户端
        
        Args:
            url: GeoIP服务地址, eg: https://geoip.example.com/api/{ip}?key=value
            source: 数据源
            ttl: 数据有效期（秒）
            cache_len: 缓存最大条数
            max_retries: 最大重试次数
            max_wait_time: 最长等待时间（秒）
            headers: HTTP请求头
        """
        if not url:
            raise GeoIPError("url参数不能为空")

        if not url.startswith("http"):
            url = f"https://{url}"
        self.url = url

        self.source = source
        self.ttl = ttl
        self.max_retries = max_retries
        self.max_wait_time = max_wait_time
        self.headers = headers or {}
        self.cache_manager = CacheManager[Dict[str, GeoIP]](maxsize=cache_len)

        logger.debug(f"初始化GeoIP客户端: url={url}, source={source}, ttl={ttl}")

    def _build_url(self, ip: str, source: Union[DataSource, str, None], ttl: Optional[int], **extra) -> str:
        """
        构建请求URL
        
        Args:
            ip: IP地址
            source: 数据源
            ttl: 数据有效期
            
        Returns:
            完整的请求URL
        """
        url = self.url.format(ip=ip, source=source, ttl=ttl, **extra)

        parts = urlsplit(url)
        qs = parse_qs(parts.query)
        if source is None:
            qs.pop("source", None)
        else:
            qs["source"] = [source]

        if ttl is None:
            qs.pop("ttl", None)
        else:
            qs["ttl"] = [str(ttl)]

        url = parts._replace(query=urlencode(qs, doseq=True)).geturl()
        return url

    @staticmethod
    def _should_retry(status_code: int) -> bool:
        """
        判断是否应该重试
        
        Args:
            status_code: HTTP状态码
            
        Returns:
            是否应该重试
        """
        # 5xx错误和网络错误应该重试
        return status_code >= 500

    def _calculate_wait_time(self, attempt: int) -> float:
        """
        计算等待时间（指数退避）
        
        Args:
            attempt: 重试次数（从1开始）
            
        Returns:
            等待时间（秒）
        """
        wait_time = min(2 ** (attempt - 1), self.max_wait_time)
        return wait_time

    @abstractmethod
    def lookup(
        self,
        ip: Union[str, ipaddress.IPv4Address],
        source: SourceType = Unset,
        ttl: TTLType = Unset,
        **extra
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
        raise NotImplementedError

    @abstractmethod
    def _make_request(self, url: str, headers: Dict[str, str]) -> httpx.Response:
        """
        发送HTTP请求（抽象方法）
        
        Args:
            url: 请求URL
            headers: 请求头
            
        Returns:
            HTTP响应
        """
        pass

    @staticmethod
    def _parse_response(response: httpx.Response) -> GeoIP:
        """
        解析API响应
        
        Args:
            response: HTTP响应
            
        Returns:
            GeoIP对象
            
        Raises:
            GeoIPAPIError: API响应错误
            GeoIPValidationError: 数据验证错误
        """
        try:
            # 检查HTTP状态码
            response.raise_for_status()

            # 解析JSON响应
            data = response.json()
            logger.debug(f"API响应: {data}")

            # 验证响应格式
            api_response = APIResponse(**data)

            if not api_response.is_success():
                raise GeoIPAPIError(
                    f"API请求失败: {api_response.msg}",
                    status_code=response.status_code,
                    response_body=response.text
                )

            return api_response.data

        except httpx.HTTPStatusError as e:
            raise GeoIPAPIError(
                f"HTTP请求失败: {e.response.status_code}",
                status_code=e.response.status_code,
                response_body=e.response.text
            )
        except ValueError as e:
            raise GeoIPValidationError(f"响应数据格式错误: {e}")
        except Exception as e:
            raise GeoIPError(f"解析响应失败: {e}")

    def _handle_request_error(self, error: Exception, attempt: int) -> None:
        """
        处理请求错误
        
        Args:
            error: 错误对象
            attempt: 重试次数
            
        Raises:
            GeoIPNetworkError: 网络错误
        """
        if attempt >= self.max_retries:
            logger.error(f"请求失败，已达到最大重试次数: {error}")
            if isinstance(error, httpx.RequestError):
                raise GeoIPNetworkError(f"网络请求失败: {error}")
            else:
                raise GeoIPError(f"请求失败: {error}")

        wait_time = self._calculate_wait_time(attempt)
        logger.warning(f"请求失败，{wait_time}秒后重试 (第{attempt}次): {error}")
        time.sleep(wait_time)

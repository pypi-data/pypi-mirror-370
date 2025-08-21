"""
常量定义
"""

from enum import Enum
from typing import Final


class DataSource(str, Enum):
    """
    预定义的数据源
    """
    IPINFO = "ipinfo.io"
    IP_API = "ip-api.com"
    IP_SB = "ip.sb"
    IPLOCATE = "iplocate.io"


# 默认配置常量
DEFAULT_TTL: Final[int] = 60 * 60 * 24 * 30  # 30天
DEFAULT_CACHE_LEN: Final[int] = 256
DEFAULT_MAX_RETRIES: Final[int] = 3
DEFAULT_MAX_WAIT_TIME: Final[int] = 10  # 秒

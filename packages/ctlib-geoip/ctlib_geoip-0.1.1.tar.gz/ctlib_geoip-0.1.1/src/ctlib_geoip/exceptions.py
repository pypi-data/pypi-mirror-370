"""
异常定义
"""

from typing import Optional


class GeoIPError(Exception):
    """GeoIP基础异常类"""
    
    def __init__(self, message: str, details: Optional[str] = None) -> None:
        self.message = message
        self.details = details
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class GeoIPNetworkError(GeoIPError):
    """网络相关异常"""
    pass


class GeoIPAPIError(GeoIPError):
    """API响应异常"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_body: Optional[str] = None) -> None:
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message, f"Status: {status_code}, Response: {response_body}")


class GeoIPCacheError(GeoIPError):
    """缓存相关异常"""
    pass


class GeoIPValidationError(GeoIPError):
    """数据验证异常"""
    pass


class GeoIPConfigError(GeoIPError):
    """配置相关异常"""
    pass

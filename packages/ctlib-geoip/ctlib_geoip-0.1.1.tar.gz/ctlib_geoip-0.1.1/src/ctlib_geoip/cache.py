"""
缓存管理模块
"""

from typing import Optional, TypeVar, Generic

from cachetools import LRUCache

from .exceptions import GeoIPCacheError

T = TypeVar("T")


class CacheManager(Generic[T]):
    """缓存管理器"""

    def __init__(self, maxsize: int = 256) -> None:
        """
        初始化缓存管理器
        
        Args:
            maxsize: 缓存最大条数
        """
        self.cache = LRUCache(maxsize=maxsize)

    def get(self, key: str) -> Optional[T]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在或已过期则返回None
        """
        try:
            return self.cache.get(key)
        except Exception as e:
            raise GeoIPCacheError(f"获取缓存失败: {e}")

    def set(self, key: str, value: T) -> None:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
        """
        try:
            self.cache[key] = value
        except Exception as e:
            raise GeoIPCacheError(f"设置缓存失败: {e}")

    def delete(self, key: str) -> None:
        """
        删除缓存值
        
        Args:
            key: 缓存键
        """
        try:
            if key in self.cache:
                del self.cache[key]
        except Exception as e:
            raise GeoIPCacheError(f"删除缓存失败: {e}")

    def clear(self) -> None:
        """清空所有缓存"""
        try:
            self.cache.clear()
        except Exception as e:
            raise GeoIPCacheError(f"清空缓存失败: {e}")

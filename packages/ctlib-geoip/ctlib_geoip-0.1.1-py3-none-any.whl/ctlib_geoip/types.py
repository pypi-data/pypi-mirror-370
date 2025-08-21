from typing import Union
from .constants import DataSource


class UnsetType:
    """
    特殊标记类，用于表示使用客户端创建时的默认参数
    """

    def __str__(self) -> str:
        return "Unset"


Unset = UnsetType()

SourceType = Union[DataSource, str, None, UnsetType]
TTLType = Union[int, None, UnsetType]

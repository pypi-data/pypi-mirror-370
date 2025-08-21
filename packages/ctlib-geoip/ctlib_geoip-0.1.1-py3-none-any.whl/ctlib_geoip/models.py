"""
数据模型定义
"""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Union

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
DATA_PATH = Path(__file__).parent / "data"


class GeoIP(BaseModel):
    """GeoIP数据模型"""

    ip: str = Field(description="IP地址")
    country: str = Field(description="国家代码", examples=["CN", "US"])
    region: str = Field(description="地区")
    city: str = Field(description="城市")
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(microsecond=0),
        description="数据获取时间"
    )
    source: str = Field(description="数据来源")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class GeoInfo(BaseModel):
    name: Optional[str] = None
    country: str
    region: Optional[str] = None
    city: Optional[str] = None
    detail: Optional[str] = None
    geo_id: Optional[int] = None
    geo_code: Optional[str] = None

    @classmethod
    def _find(cls, key: str, value: Union[str, int]) -> Optional['GeoInfo']:
        if key == "geo_code":
            country, _ = value.split("-", 1)
            fs = [DATA_PATH / f"GEO_{country}.jsonl"]
        else:
            fs = list(DATA_PATH.rglob("GEO_*.jsonl"))
        for f in fs:
            with f.open("r") as fp:
                for line in fp:
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    if data[key] == value:
                        return cls(**data)
        logger.error(f"No GeoInfo found for {key}={value}")
        return None

    @classmethod
    def from_geo_id(cls, geo_id: int):
        return cls._find("geo_id", geo_id)

    @classmethod
    def from_geo_code(cls, geo_code: str):
        return cls._find("geo_code", geo_code)

    @classmethod
    def from_name(cls, name: str):
        return cls._find("name", name)


class APIResponse(BaseModel):
    """API响应模型"""

    code: int = Field(description="响应状态码")
    data: Optional[GeoIP] = Field(description="响应数据")
    msg: str = Field(description="响应消息")

    def is_success(self) -> bool:
        """检查响应是否成功"""
        return self.code == 0 and self.data is not None

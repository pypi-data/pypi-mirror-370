from typing import Optional, Dict

from .models import GeoIP, GeoInfo


class GeoTree:
    def __init__(self, *geos: Optional[GeoInfo]):
        # 三层嵌套 dict: country -> region -> city -> True
        self.root: Dict[str, dict] = {}
        if geos:
            for geo in geos:
                self.add(geo)

    def add(self, geo: Optional[GeoInfo]):
        """添加一条 Geo"""
        if not geo:
            return
        node = self.root
        # 处理 country
        node = node.setdefault(geo.country, {})

        # 处理 region
        if geo.region is None:
            node["_flag"] = True
            return
        node = node.setdefault(geo.region, {})

        # 处理 city
        if geo.city is None:
            node["_flag"] = True
            return
        node[geo.city] = True  # 最终标记

    def contains(self, geoip: GeoIP) -> bool:
        """判断是否包含 GeoIP"""
        country = geoip.country
        region = geoip.region.strip() or None
        city = geoip.city.strip() or None

        node = self.root.get(country)
        if not node:
            return False

        # 检查 country
        if node.get("_flag"):
            return True

        # 如果没有 region 信息，则无法继续匹配
        if not region:
            return False

        node = node.get(region)
        if not node:
            return False

        # 检查 region
        if node.get("_flag"):
            return True

        # 如果没有 city 信息，则无法继续匹配
        if not city:
            return False

        # 检查 city
        return city in node

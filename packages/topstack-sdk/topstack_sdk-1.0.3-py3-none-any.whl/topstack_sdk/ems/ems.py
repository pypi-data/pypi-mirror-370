"""
能源管理 API 实现
"""

from typing import List, Optional
from ..client import TopStackClient, Response

class EmsApi:
    """能源管理 API 客户端"""
    
    def __init__(self, client: TopStackClient):
        """
        初始化能源管理 API
        
        Args:
            client: TopStack 客户端实例
        """
        self.client = client
    
    def query_meters(self, **params):
        """查询电表"""
        return self.client.post("/ems/open_api/v1/meter/query", params)
    
    def get_meter_detail(self, meter_id: str):
        """获取电表详情"""
        return self.client.post("/ems/open_api/v1/meter/detail", {"id": meter_id})
    
    def query_sectors(self, **params):
        """查询部门"""
        return self.client.post("/ems/open_api/v1/sector/query", params)
    
    def get_sector_detail(self, sector_id: str):
        """获取部门详情"""
        return self.client.post("/ems/open_api/v1/sector/detail", {"id": sector_id})
    
    def query_subentries(self, **params):
        """查询分项"""
        return self.client.post("/ems/open_api/v1/subentry/query", params)
    
    def get_subentry_detail(self, subentry_id: str):
        """获取分项详情"""
        return self.client.post("/ems/open_api/v1/subentry/detail", {"id": subentry_id}) 
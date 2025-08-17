"""
资产管理 API 实现
"""

from typing import List, Optional
from ..client import TopStackClient, Response

class AssetApi:
    """资产管理 API 客户端"""
    
    def __init__(self, client: TopStackClient):
        """
        初始化资产管理 API
        
        Args:
            client: TopStack 客户端实例
        """
        self.client = client
    
    def query_work_orders(self, **params):
        """查询工单"""
        return self.client.get("/asset/open_api/v1/alert_work_order", params)
    
    def get_work_order_detail(self, work_order_id: str):
        """获取工单详情"""
        return self.client.get(f"/asset/open_api/v1/alert_work_order/{work_order_id}") 
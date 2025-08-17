"""
告警 API 实现
"""

from typing import List, Optional
from ..client import TopStackClient, Response

class AlertApi:
    """告警 API 客户端"""
    
    def __init__(self, client: TopStackClient):
        """
        初始化告警 API
        
        Args:
            client: TopStack 客户端实例
        """
        self.client = client
    
    def query_alert_levels(self):
        """查询告警级别"""
        return self.client.get("/alert/open_api/v1/alert_level")
    
    def query_alert_types(self):
        """查询告警类型"""
        return self.client.get("/alert/open_api/v1/alert_type")
    
    def query_alert_records(self, **params):
        """查询告警记录"""
        return self.client.get("/alert/open_api/v1/alert_record", params) 
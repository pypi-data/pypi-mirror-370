"""
IoT API 实现
"""

from typing import List, Union, Dict, Any
from datetime import datetime
from ..client import TopStackClient, Response
from .models import (
    FindLastRequest, FindLastResponse,
    FindLastBatchRequest, FindLastBatchResponse,
    SetValueRequest, HistoryRequest, HistoryResponse
)

class IotApi:
    """IoT API 客户端"""
    
    def __init__(self, client: TopStackClient):
        """
        初始化 IoT API
        
        Args:
            client: TopStack 客户端实例
        """
        self.client = client
    
    def find_last(self, device_id: str, point_id: str) -> FindLastResponse:
        """
        查询单测点实时值
        
        Args:
            device_id: 设备ID
            point_id: 测点ID
            
        Returns:
            FindLastResponse: 测点实时值
        """
        request = FindLastRequest(device_id=device_id, point_id=point_id)
        response = self.client.post(
            "/iot/open_api/v1/data/findLast",
            request.dict(by_alias=True),
            FindLastResponse
        )
        return response.data
    
    def find_last_batch(self, points: List[Dict[str, str]]) -> List[FindLastResponse]:
        """
        批量查询多测点实时值
        
        Args:
            points: 测点列表，每个元素包含 device_id 和 point_id
            
        Returns:
            List[FindLastResponse]: 测点实时值列表
        """
        # 构建请求数据
        request_data = []
        for point in points:
            request_data.append({
                "deviceID": point["device_id"],
                "pointID": point["point_id"]
            })
        
        response = self.client.post(
            "/iot/open_api/v1/data/findLastBatch",
            request_data,
            FindLastResponse
        )
        # 处理响应数据，确保返回列表格式
        if isinstance(response.data, list):
            return response.data
        elif response.data is not None:
            return [response.data]
        else:
            return []
    
    def set_value(self, device_id: str, point_id: str, value: str) -> None:
        """
        设置测点值（控制指令下发）
        
        Args:
            device_id: 设备ID
            point_id: 测点ID
            value: 要设置的值
        """
        request = SetValueRequest(device_id=device_id, point_id=point_id, value=value)
        self.client.post("/iot/open_api/v1/data/setValue", request.dict(by_alias=True))
    
    def query_history(
        self,
        points: List[Dict[str, str]],
        start: datetime,
        end: datetime,
        aggregation: str = "last",
        interval: str = "10s",
        fill: str = "null",
        offset: int = 0,
        limit: int = 5000,
        order: str = "asc"
    ) -> HistoryResponse:
        """
        查询历史数据
        
        Args:
            points: 测点列表，每个元素包含 device_id 和 point_id
            start: 开始时间
            end: 结束时间
            aggregation: 聚合方式
            interval: 时间间隔
            fill: 填充方式
            offset: 偏移量
            limit: 限制数量
            order: 排序方式
            
        Returns:
            HistoryResponse: 历史数据
        """
        # 构建测点列表
        point_requests = []
        for point in points:
            point_requests.append(FindLastRequest(
                device_id=point["device_id"],
                point_id=point["point_id"]
            ))
        
        request = HistoryRequest(
            points=point_requests,
            start=start,
            end=end,
            aggregation=aggregation,
            interval=interval,
            fill=fill,
            offset=offset,
            limit=limit,
            order=order
        )
        
        response = self.client.post(
            "/iot/open_api/v1/data/query",
            request.dict(by_alias=True),
            HistoryResponse
        )
        return response.data 
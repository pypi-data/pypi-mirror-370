"""
设备管理 API 实现
"""

from typing import List, Optional
from ...client import TopStackClient, Response
from .models import (
    QueryRequest, QueryResponse,
    PropsQueryResponse, PointQueryRequest, PointQueryResponse
)

class DeviceApi:
    """设备管理 API 客户端"""
    
    def __init__(self, client: TopStackClient):
        """
        初始化设备管理 API
        
        Args:
            client: TopStack 客户端实例
        """
        self.client = client
    
    def query(
        self,
        search: Optional[str] = None,
        gateway_id: Optional[str] = None,
        type_id: Optional[str] = None,
        connect_mode: Optional[str] = None,
        data_channel_id: Optional[str] = None,
        custom_channel_id: Optional[str] = None,
        state: Optional[str] = None,
        user_group_id: Optional[str] = None,
        empty: Optional[bool] = None,
        group_id: Optional[str] = None,
        page_num: int = 1,
        page_size: int = 10
    ) -> QueryResponse:
        """
        查询设备
        
        Args:
            search: 名称或标识关键字
            gateway_id: 所属网关
            type_id: 所属模型
            connect_mode: 接入方式
            data_channel_id: 所属数据通道ID
            custom_channel_id: 所属自定义通道ID
            state: 状态
            user_group_id: 用户组ID
            empty: 是否查询未关联设备
            group_id: 所属设备分组
            page_num: 当前页
            page_size: 每页数量
            
        Returns:
            QueryResponse: 设备查询结果
        """
        request = QueryRequest(
            search=search,
            gateway_id=gateway_id,
            type_id=type_id,
            connect_mode=connect_mode,
            data_channel_id=data_channel_id,
            custom_channel_id=custom_channel_id,
            state=state,
            user_group_id=user_group_id,
            empty=empty,
            group_id=group_id,
            page_num=page_num,
            page_size=page_size
        )
        
        response = self.client.get(
            "/iot/open_api/v1/device/query",
            request.dict(by_alias=True, exclude_none=True),
            QueryResponse
        )
        return response.data
    
    def query_props(self, device_id: str) -> List[dict]:
        """
        查询设备属性
        
        Args:
            device_id: 设备ID
            
        Returns:
            List[dict]: 设备属性列表
        """
        response = self.client.get(
            f"/iot/open_api/v1/device/{device_id}/props",
            response_model=PropsQueryResponse
        )
        # 处理 RootModel 响应
        if response.data is not None:
            return response.data.root if hasattr(response.data, 'root') else response.data
        return []
    
    def query_points(
        self,
        search: Optional[str] = None,
        device_id: Optional[str] = None,
        type: Optional[str] = None,
        order: Optional[str] = None,
        page_num: int = 1,
        page_size: int = 10
    ) -> PointQueryResponse:
        """
        查询设备测点
        
        Args:
            search: 搜索关键字
            device_id: 设备ID
            type: 测点类型
            order: 排序方式
            page_num: 当前页
            page_size: 每页数量
            
        Returns:
            PointQueryResponse: 测点查询结果
        """
        request = PointQueryRequest(
            search=search,
            device_id=device_id,
            type=type,
            order=order,
            page_num=page_num,
            page_size=page_size
        )
        
        response = self.client.get(
            "/iot/open_api/v1/device_point/query",
            request.dict(by_alias=True, exclude_none=True),
            PointQueryResponse
        )
        return response.data 
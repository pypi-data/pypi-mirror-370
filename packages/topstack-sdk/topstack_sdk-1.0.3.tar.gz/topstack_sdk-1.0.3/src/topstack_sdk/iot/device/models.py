"""
设备管理数据模型
"""

from typing import List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, RootModel

class QueryRequest(BaseModel):
    """设备查询请求"""
    search: Optional[str] = Field(None, description="名称或标识关键字")
    gateway_id: Optional[str] = Field(None, alias="gatewayID", description="所属网关")
    type_id: Optional[str] = Field(None, alias="typeID", description="所属模型")
    connect_mode: Optional[str] = Field(None, alias="connectMode", description="接入方式：direct、gateway、custom")
    data_channel_id: Optional[str] = Field(None, alias="dataChannelID", description="所属数据通道ID")
    custom_channel_id: Optional[str] = Field(None, alias="customChannelID", description="所属自定义通道ID")
    state: Optional[str] = Field(None, description="状态 true 表示在线, false 表示离线")
    user_group_id: Optional[str] = Field(None, alias="userGroupID", description="用户组ID")
    empty: Optional[bool] = Field(None, description="true 表示查询未关联任何通道或网关的设备")
    group_id: Optional[str] = Field(None, alias="groupID", description="所属设备分组")
    page_num: Optional[int] = Field(1, alias="pageNum", description="当前页，起始值为 1, 默认为 1")
    page_size: Optional[int] = Field(10, alias="pageSize", description="每页数量，默认为 10")

class DeviceItem(BaseModel):
    """设备项"""
    id: str = Field(..., description="设备ID")
    code: str = Field(..., description="设备代码")
    name: str = Field(..., description="设备名称")
    description: Optional[str] = Field(None, description="设备描述")
    gateway_id: Optional[str] = Field(None, alias="gatewayID", description="网关ID")
    gateway_name: Optional[str] = Field(None, alias="gatewayName", description="网关名称")
    type_id: Optional[str] = Field(None, alias="typeID", description="类型ID")
    type_name: Optional[str] = Field(None, alias="typeName", description="类型名称")
    group_id: Optional[str] = Field(None, alias="groupID", description="分组ID")
    group_name: Optional[str] = Field(None, alias="groupName", description="分组名称")
    template: bool = Field(False, description="是否为模板")
    address: Optional[str] = Field(None, description="地址")
    idle_timeout: Optional[int] = Field(None, alias="idleTimeout", description="空闲超时")
    connect_mode: str = Field(..., alias="connectMode", description="连接模式")
    user_group_id: Optional[str] = Field(None, alias="userGroupID", description="用户组ID")
    user_group_name: Optional[str] = Field(None, alias="userGroupName", description="用户组名称")
    data_channel_id: Optional[str] = Field(None, alias="dataChannelID", description="数据通道ID")
    data_channel_name: Optional[str] = Field(None, alias="dataChannelName", description="数据通道名称")
    custom_channel_id: Optional[str] = Field(None, alias="customChannelID", description="自定义通道ID")
    custom_channel_name: Optional[str] = Field(None, alias="customChannelName", description="自定义通道名称")
    state: int = Field(..., description="状态：0表示在线，1表示离线")
    state_change_time: Optional[datetime] = Field(None, alias="stateChangeTime", description="状态变更时间")
    created_at: Optional[datetime] = Field(None, alias="createdAt", description="创建时间")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt", description="更新时间")
    has_props: bool = Field(False, alias="hasProps", description="是否有属性")
    manual_gi: bool = Field(False, alias="manualGI", description="手动地理信息")
    longitude: Optional[float] = Field(None, description="经度")
    latitude: Optional[float] = Field(None, description="纬度")
    longitude_point_id: Optional[str] = Field(None, alias="longitudePointID", description="经度测点ID")
    latitude_point_id: Optional[str] = Field(None, alias="latitudePointID", description="纬度测点ID")

class QueryResponse(BaseModel):
    """设备查询响应"""
    total: int = Field(..., description="总数")
    items: List[DeviceItem] = Field(..., description="设备列表")

class PropertyItem(BaseModel):
    """属性项"""
    property_id: str = Field(..., alias="id", description="属性ID")
    property_type: str = Field(..., alias="type", description="属性类型")
    name: str = Field(..., description="属性名称")
    description: Optional[str] = Field(None, description="属性描述")
    value: Optional[str] = Field(None, description="属性值")

class PropsQueryResponse(RootModel[List[PropertyItem]]):
    """属性查询响应"""
    model_config = {"title": "PropsQueryResponse", "description": "属性列表"}

class PointQueryRequest(BaseModel):
    """测点查询请求"""
    search: Optional[str] = Field(None, description="搜索关键字")
    device_id: Optional[str] = Field(None, alias="deviceID", description="设备ID")
    type: Optional[str] = Field(None, description="测点类型")
    order: Optional[str] = Field(None, description="排序方式")
    page_num: Optional[int] = Field(1, alias="pageNum", description="当前页")
    page_size: Optional[int] = Field(10, alias="pageSize", description="每页数量")

class PointItem(BaseModel):
    """测点项"""
    point_id: str = Field(..., alias="pointID", description="测点ID")
    name: str = Field(..., description="测点名称")
    type: str = Field(..., description="测点类型：int double string bool array float time")
    access_mode: str = Field(..., alias="accessMode", description="读写类型：只读(r)、只写(w)、读写(rw)")
    order_number: int = Field(..., alias="orderNumber", description="排序号")
    description: Optional[str] = Field(None, description="测点描述")
    group: Optional[str] = Field(None, description="测点分组")
    unit: Optional[str] = Field(None, description="计量单位")
    format: Optional[str] = Field(None, description="格式化")
    edge: bool = Field(False, description="是否只在边缘侧使用")
    is_array: bool = Field(False, alias="isArray", description="是否为数组")
    generator: Optional[str] = Field(None, description="模拟器函数")

class PointQueryResponse(BaseModel):
    """测点查询响应"""
    total: int = Field(..., description="总数")
    items: List[PointItem] = Field(..., description="测点列表") 
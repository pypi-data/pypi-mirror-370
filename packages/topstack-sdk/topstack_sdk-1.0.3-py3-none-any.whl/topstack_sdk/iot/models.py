"""
IoT 模块数据模型
"""

from typing import Any, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, RootModel

class FindLastRequest(BaseModel):
    """查询单测点实时值请求"""
    device_id: str = Field(..., alias="deviceID", description="设备ID")
    point_id: str = Field(..., alias="pointID", description="测点ID")

class FindLastResponse(BaseModel):
    """查询单测点实时值响应"""
    device_id: str = Field(..., alias="deviceID", description="设备ID")
    point_id: str = Field(..., alias="pointID", description="测点ID")
    value: Any = Field(None, description="测点值")
    quality: int = Field(0, description="数据质量：0表示正常，1表示离线，2表示无效")
    timestamp: datetime = Field(..., description="时间戳")

class FindLastBatchRequest(RootModel[List[FindLastRequest]]):
    """批量查询多测点实时值请求"""
    model_config = {"title": "FindLastBatchRequest", "description": "测点列表"}

class FindLastBatchResponse(RootModel[List[FindLastResponse]]):
    """批量查询多测点实时值响应"""
    model_config = {"title": "FindLastBatchResponse", "description": "测点数据列表"}

class SetValueRequest(BaseModel):
    """设置测点值请求"""
    device_id: str = Field(..., alias="deviceID", description="设备ID")
    point_id: str = Field(..., alias="pointID", description="测点ID")
    value: str = Field(..., description="要设置的值")

class HistoryValue(BaseModel):
    """历史数据值"""
    value: Optional[Any] = Field(None, description="值")
    first: Optional[Any] = Field(None, description="第一个值")
    last: Optional[Any] = Field(None, description="最后一个值")
    max: Optional[Any] = Field(None, description="最大值")
    min: Optional[Any] = Field(None, description="最小值")
    mean: Optional[Any] = Field(None, description="平均值")
    median: Optional[Any] = Field(None, description="中位数")
    sum: Optional[Any] = Field(None, description="总和")
    count: Optional[Any] = Field(None, description="计数")
    spread: Optional[Any] = Field(None, description="范围")
    stddev: Optional[Any] = Field(None, description="标准差")
    time: datetime = Field(..., description="时间")

class HistoryResult(BaseModel):
    """历史数据结果"""
    device_id: str = Field(..., alias="deviceID", description="设备ID")
    point_id: str = Field(..., alias="pointID", description="测点ID")
    values: List[HistoryValue] = Field(..., description="历史数据值列表")

class HistoryRequest(BaseModel):
    """查询历史数据请求"""
    points: List[FindLastRequest] = Field(..., description="测点列表")
    start: datetime = Field(..., description="开始时间")
    end: datetime = Field(..., description="结束时间")
    aggregation: str = Field("last", description="聚合方式：first,last,min,max,mean")
    interval: str = Field("5s", description="时间间隔")
    fill: str = Field("null", description="填充方式：null,previous")
    offset: int = Field(0, ge=0, description="偏移量")
    limit: int = Field(5000, ge=0, le=5000, description="限制数量")
    order: str = Field("asc", description="排序方式：asc,desc")

class HistoryResponse(BaseModel):
    """查询历史数据响应"""
    results: List[HistoryResult] = Field(..., description="历史数据结果列表") 
import json
import logging
import asyncio
from datetime import datetime
from typing import Callable, Optional, Any, Dict, Union
import nats
from nats.aio.client import Client as NATSClient
from nats.aio.subscription import Subscription


class NatsConfig:
    """NATS 配置类"""
    
    def __init__(self, addr: str, token: str = None, username: str = None, password: str = None):
        self.addr = addr
        self.token = token
        self.username = username
        self.password = password


class PointData:
    """测点数据结构"""
    
    def __init__(self, device_id: str = None, point_id: str = None, value: Any = None, 
                 quality: int = None, timestamp: datetime = None, status: int = None,
                 device_type_id: str = None, project_id: str = None, gateway_id: str = None,
                 not_save: bool = False):
        self.device_id = device_id
        self.point_id = point_id
        self.value = value
        self.quality = quality  # 1 表示离线，2 表示无效
        self.timestamp = timestamp
        self.status = status  # 0 表示正常，> 0 表示越上限，< 0 表示越下限
        self.device_type_id = device_type_id
        self.project_id = project_id
        self.gateway_id = gateway_id
        self.not_save = not_save
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PointData':
        """从字典创建 PointData 对象"""
        timestamp = None
        if 'timestamp' in data and data['timestamp']:
            if isinstance(data['timestamp'], str):
                timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
            elif isinstance(data['timestamp'], (int, float)):
                timestamp = datetime.fromtimestamp(data['timestamp'] / 1000)
        
        return cls(
            device_id=data.get('deviceID'),
            point_id=data.get('pointID'),
            value=data.get('value'),
            quality=data.get('quality'),
            timestamp=timestamp,
            status=data.get('status'),
            device_type_id=data.get('deviceTypeID'),
            project_id=data.get('projectID'),
            gateway_id=data.get('gatewayID'),
            not_save=data.get('notSave', False)
        )


class GatewayState:
    """网关状态数据结构"""
    
    def __init__(self, sn: str = None, name: str = None, project_id: str = None,
                 gateway_id: str = None, state: int = None, timestamp: datetime = None):
        self.sn = sn
        self.name = name
        self.project_id = project_id
        self.gateway_id = gateway_id
        self.state = state  # 0: 离线， 1：在线
        self.timestamp = timestamp
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GatewayState':
        """从字典创建 GatewayState 对象"""
        timestamp = None
        if 'timestamp' in data and data['timestamp']:
            if isinstance(data['timestamp'], str):
                timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
            elif isinstance(data['timestamp'], (int, float)):
                timestamp = datetime.fromtimestamp(data['timestamp'] / 1000)
        
        return cls(
            sn=data.get('sn'),
            name=data.get('name'),
            project_id=data.get('projectID'),
            gateway_id=data.get('gatewayID'),
            state=data.get('state'),
            timestamp=timestamp
        )


class DeviceState:
    """设备状态数据结构"""
    
    def __init__(self, project_id: str = None, gateway_id: str = None, device_id: str = None,
                 state: int = None, timestamp: datetime = None):
        self.project_id = project_id
        self.gateway_id = gateway_id
        self.device_id = device_id
        self.state = state  # 0: 离线， 1：在线
        self.timestamp = timestamp
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeviceState':
        """从字典创建 DeviceState 对象"""
        timestamp = None
        if 'timestamp' in data and data['timestamp']:
            if isinstance(data['timestamp'], str):
                timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
            elif isinstance(data['timestamp'], (int, float)):
                timestamp = datetime.fromtimestamp(data['timestamp'] / 1000)
        
        return cls(
            project_id=data.get('projectID'),
            gateway_id=data.get('gatewayID'),
            device_id=data.get('deviceID'),
            state=data.get('state'),
            timestamp=timestamp
        )


class ChannelState:
    """数据通道状态数据结构"""
    
    def __init__(self, project_id: str = None, gateway_id: str = None, channel_id: str = None,
                 running: bool = None, connected: bool = None, timestamp: datetime = None,
                 gateway_name: str = None, channel_name: str = None):
        self.project_id = project_id
        self.gateway_id = gateway_id
        self.channel_id = channel_id
        self.running = running
        self.connected = connected
        self.timestamp = timestamp
        self.gateway_name = gateway_name
        self.channel_name = channel_name
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChannelState':
        """从字典创建 ChannelState 对象"""
        timestamp = None
        if 'timestamp' in data and data['timestamp']:
            if isinstance(data['timestamp'], str):
                timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
            elif isinstance(data['timestamp'], (int, float)):
                timestamp = datetime.fromtimestamp(data['timestamp'] / 1000)
        
        return cls(
            project_id=data.get('projectID'),
            gateway_id=data.get('gatewayID'),
            channel_id=data.get('channelID'),
            running=data.get('running'),
            connected=data.get('connected'),
            timestamp=timestamp,
            gateway_name=data.get('gatewayName'),
            channel_name=data.get('channelName')
        )


class AlertInfo:
    """告警信息数据结构"""
    
    def __init__(self, alert_id: str = None, status: str = None, created_at: datetime = None,
                 recovered_at: datetime = None, handled_at: datetime = None, expired_at: datetime = None,
                 handler: str = None, order_created: bool = None, edge: bool = None, title: str = None,
                 content: str = None, remark: str = None, rule_template_id: str = None, trigger_id: str = None,
                 mode: str = None, compare_mode: str = None, compare_value: str = None, duration: int = None,
                 input_value: str = None, point_id: str = None, dead_band: float = None, diff: float = None,
                 project_id: str = None, device_id: str = None, alert_type_id: str = None, alert_level_id: str = None,
                 rule_name: str = None, alert_type_name: str = None, alert_type_code: str = None,
                 alert_level_code: str = None, alert_level_color: str = None, alert_level_name: str = None,
                 device_name: str = None, point_name: str = None, device_type_id: str = None,
                 device_group_id: str = None, device_attr: Dict[str, Any] = None):
        self.alert_id = alert_id
        self.status = status
        self.created_at = created_at
        self.recovered_at = recovered_at
        self.handled_at = handled_at
        self.expired_at = expired_at
        self.handler = handler
        self.order_created = order_created
        self.edge = edge
        self.title = title
        self.content = content
        self.remark = remark
        self.rule_template_id = rule_template_id
        self.trigger_id = trigger_id
        self.mode = mode
        self.compare_mode = compare_mode
        self.compare_value = compare_value
        self.duration = duration
        self.input_value = input_value
        self.point_id = point_id
        self.dead_band = dead_band
        self.diff = diff
        self.project_id = project_id
        self.device_id = device_id
        self.alert_type_id = alert_type_id
        self.alert_level_id = alert_level_id
        self.rule_name = rule_name
        self.alert_type_name = alert_type_name
        self.alert_type_code = alert_type_code
        self.alert_level_code = alert_level_code
        self.alert_level_color = alert_level_color
        self.alert_level_name = alert_level_name
        self.device_name = device_name
        self.point_name = point_name
        self.device_type_id = device_type_id
        self.device_group_id = device_group_id
        self.device_attr = device_attr or {}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AlertInfo':
        """从字典创建 AlertInfo 对象"""
        def parse_datetime(value):
            if not value:
                return None
            if isinstance(value, str):
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            elif isinstance(value, (int, float)):
                return datetime.fromtimestamp(value / 1000)
            return None
        
        return cls(
            alert_id=data.get('id'),
            status=data.get('status'),
            created_at=parse_datetime(data.get('createdAt')),
            recovered_at=parse_datetime(data.get('recoveredAt')),
            handled_at=parse_datetime(data.get('handledAt')),
            expired_at=parse_datetime(data.get('expiredAt')),
            handler=data.get('handler'),
            order_created=data.get('orderCreated'),
            edge=data.get('edge'),
            title=data.get('title'),
            content=data.get('content'),
            remark=data.get('remark'),
            rule_template_id=data.get('ruleTemplateID'),
            trigger_id=data.get('triggerID'),
            mode=data.get('mode'),
            compare_mode=data.get('compareMode'),
            compare_value=data.get('compareValue'),
            duration=data.get('duration'),
            input_value=data.get('inputValue'),
            point_id=data.get('pointID'),
            dead_band=data.get('deadBand'),
            diff=data.get('diff'),
            project_id=data.get('projectID'),
            device_id=data.get('deviceID'),
            alert_type_id=data.get('alertTypeID'),
            alert_level_id=data.get('alertLevelID'),
            rule_name=data.get('ruleName'),
            alert_type_name=data.get('alertTypeName'),
            alert_type_code=data.get('alertTypeCode'),
            alert_level_code=data.get('alertLevelCode'),
            alert_level_color=data.get('alertLevelColor'),
            alert_level_name=data.get('alertLevelName'),
            device_name=data.get('deviceName'),
            point_name=data.get('pointName'),
            device_type_id=data.get('deviceTypeID'),
            device_group_id=data.get('deviceGroupID'),
            device_attr=data.get('deviceAttr', {})
        ) 


class NatsBus:
    """NATS 消息总线"""
    
    def __init__(self, conn: NATSClient):
        self.conn = conn
        self.logger = logging.getLogger(__name__)
    
    async def close(self):
        """关闭连接"""
        if self.conn:
            await self.conn.close()
    
    async def subscribe_point_data(self, project_id: str, device_id: str, point_id: str,
                                 callback: Callable[[PointData], None]) -> Subscription:
        """订阅设备测点数据"""
        topic = self._realtime_point_topic(project_id, device_id, point_id)
        
        async def message_handler(msg):
            try:
                data = json.loads(msg.data.decode())
                point_data = PointData.from_dict(data)
                if asyncio.iscoroutinefunction(callback):
                    await callback(point_data)
                else:
                    callback(point_data)
            except Exception as e:
                self.logger.error(f"解析实时测点数据错误: {e}")
        
        return await self.conn.subscribe(topic, cb=message_handler)
    
    async def subscribe_device_type_data(self, project_id: str, device_type_id: str, point_id: str,
                                       callback: Callable[[PointData], None]) -> Subscription:
        """订阅同设备模型下的测点数据"""
        topic = self._realtime_point_topic_v2(project_id, device_type_id, "*", point_id)
        
        async def message_handler(msg):
            try:
                data = json.loads(msg.data.decode())
                point_data = PointData.from_dict(data)
                if asyncio.iscoroutinefunction(callback):
                    await callback(point_data)
                else:
                    callback(point_data)
            except Exception as e:
                self.logger.error(f"解析实时测点数据错误: {e}")
        
        return await self.conn.subscribe(topic, cb=message_handler)
    
    async def subscribe_device_state(self, project_id: str, device_id: str,
                                   callback: Callable[[DeviceState], None]) -> Subscription:
        """订阅设备状态数据"""
        topic = self._device_state_topic(project_id, device_id)
        
        async def message_handler(msg):
            try:
                data = json.loads(msg.data.decode())
                device_state = DeviceState.from_dict(data)
                if asyncio.iscoroutinefunction(callback):
                    await callback(device_state)
                else:
                    callback(device_state)
            except Exception as e:
                self.logger.error(f"解析设备状态数据错误: {e}")
        
        return await self.conn.subscribe(topic, cb=message_handler)
    
    async def subscribe_gateway_state(self, project_id: str,
                                    callback: Callable[[GatewayState], None]) -> Subscription:
        """订阅网关状态数据"""
        topic = self._gateway_state_topic(project_id, "*")
        
        async def message_handler(msg):
            try:
                data = json.loads(msg.data.decode())
                gateway_state = GatewayState.from_dict(data)
                if asyncio.iscoroutinefunction(callback):
                    await callback(gateway_state)
                else:
                    callback(gateway_state)
            except Exception as e:
                self.logger.error(f"解析网关状态数据错误: {e}")
        
        return await self.conn.subscribe(topic, cb=message_handler)
    
    async def subscribe_channel_state(self, project_id: str,
                                    callback: Callable[[ChannelState], None]) -> Subscription:
        """订阅数据通道状态数据"""
        topic = self._channel_state_topic(project_id, "*")
        
        async def message_handler(msg):
            try:
                data = json.loads(msg.data.decode())
                channel_state = ChannelState.from_dict(data)
                if asyncio.iscoroutinefunction(callback):
                    await callback(channel_state)
                else:
                    callback(channel_state)
            except Exception as e:
                self.logger.error(f"解析数据通道状态数据错误: {e}")
        
        return await self.conn.subscribe(topic, cb=message_handler)
    
    async def subscribe_alert_info(self, project_id: str,
                                 callback: Callable[[AlertInfo], None]) -> Subscription:
        """订阅全部告警消息"""
        topic = self._alert_topic(project_id)
        
        async def message_handler(msg):
            try:
                data = json.loads(msg.data.decode())
                alert_info = AlertInfo.from_dict(data)
                if asyncio.iscoroutinefunction(callback):
                    await callback(alert_info)
                else:
                    callback(alert_info)
            except Exception as e:
                self.logger.error(f"解析告警信息数据错误: {e}")
        
        return await self.conn.subscribe(topic, cb=message_handler)
    
    async def subscribe_device_alert_info(self, project_id: str, device_id: str,
                                        callback: Callable[[AlertInfo], None]) -> Subscription:
        """订阅设备告警信息"""
        topic = self._device_alert_topic(project_id, device_id)
        
        async def message_handler(msg):
            try:
                data = json.loads(msg.data.decode())
                alert_info = AlertInfo.from_dict(data)
                if asyncio.iscoroutinefunction(callback):
                    await callback(alert_info)
                else:
                    callback(alert_info)
            except Exception as e:
                self.logger.error(f"解析告警信息数据错误: {e}")
        
        return await self.conn.subscribe(topic, cb=message_handler)
    
    # Topic 生成方法
    def _realtime_point_topic_v2(self, project_id: str, device_type_id: str, device_id: str, point_id: str) -> str:
        return f"iot.platform.device.datas.{project_id}.{device_type_id}.{device_id}.{point_id}"
    
    def _realtime_point_topic(self, project_id: str, device_id: str, point_id: str) -> str:
        return self._realtime_point_topic_v2(project_id, "*", device_id, point_id)
    
    def _channel_state_topic(self, project_id: str, channel_id: str) -> str:
        return f"iot.platform.channel.state.{project_id}.{channel_id}"
    
    def _gateway_state_topic(self, project_id: str, gateway_id: str) -> str:
        return f"iot.platform.gateway.state.{project_id}.{gateway_id}"
    
    def _device_state_topic(self, project_id: str, device_id: str) -> str:
        return f"iot.platform.device.state.{project_id}.{device_id}"
    
    def _alert_topic(self, project_id: str) -> str:
        return f"iot.platform.alert.{project_id}.>"
    
    def _device_alert_topic(self, project_id: str, device_id: str) -> str:
        if not device_id:
            device_id = "not_device"
        return f"iot.platform.alert.{project_id}.{device_id}"


async def create_nats_bus(config: NatsConfig, **options) -> NatsBus:
    """创建 NATS 总线实例"""
    opts = {}
    
    # 更新配置
    opts.update(options)
    
    # 设置认证信息
    if config.token:
        opts['token'] = config.token
    
    if config.username and config.password:
        opts['user'] = config.username
        opts['password'] = config.password
    
    try:
        nc = await nats.connect(config.addr, **opts)
        return NatsBus(nc)
    except Exception as e:
        raise Exception(f"创建 NATS 连接错误: {e}") 
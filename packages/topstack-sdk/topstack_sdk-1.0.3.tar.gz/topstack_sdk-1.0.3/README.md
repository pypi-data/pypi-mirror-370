# TopStack Python SDK

TopStack Python SDK 是一个用于与 TopStack 平台交互的 Python 客户端库，提供了完整的 API 封装和便捷的使用接口。

## 功能特性

- 🚀 **完整的 API 支持** - 支持 IoT、告警、资产管理、能源管理等所有模块
- 🔧 **易于使用** - 简洁的 API 设计，快速上手
- 🛡️ **类型安全** - 使用 Pydantic 进行数据验证
- 📦 **标准包结构** - 采用现代 Python 包结构，支持 src 布局
- 🧪 **完整测试** - 包含单元测试和集成测试
- 📚 **详细文档** - 提供完整的使用示例和 API 文档
- 🔄 **实时数据** - 支持 NATS 消息总线，实时接收设备数据、状态和告警信息
- 🔐 **安全认证** - 支持 AppID/AppSecret 认证，自动令牌管理和刷新

## 项目结构

```
topstack-sdk-python/
├── LICENSE
├── pyproject.toml          # 项目配置
├── README.md              # 项目说明
├── src/                   # 源代码目录
│   └── topstack_sdk/      # SDK 包
│       ├── __init__.py
│       ├── client.py      # 核心客户端
│       ├── alert/         # 告警模块
│       ├── asset/         # 资产管理模块
│       ├── datav/         # 数据可视化模块
│       ├── ems/           # 能源管理模块
│       ├── iot/           # IoT 模块
│       └── nats.py        # NATS 消息总线模块
├── tests/                 # 测试目录
│   ├── __init__.py
│   ├── test_client.py
│   └── test_iot.py
├── examples/              # 示例代码
│   ├── basic_usage.py
│   └── nats_example.py   # NATS 消息总线示例
└── scripts/               # 工具脚本
    ├── explore_apis.py
    └── diagnose_connection.py
```

## 认证方式

TopStack Python SDK 使用 AppID/AppSecret 认证方式：

```python
from topstack_sdk import TopStackClient

# 使用 AppID/AppSecret 认证方式
client = TopStackClient(
    base_url="http://localhost:8000",
    app_id="your-app-id",
    app_secret="your-app-secret"
)
```

**认证方式说明：**
- **AppID/AppSecret 认证**：通过获取访问令牌进行认证，支持令牌自动刷新，适合企业级应用
- 自动调用 `/open_api/v1/auth/access_token` 接口获取访问令牌
- 访问令牌自动缓存，并在过期前5分钟自动刷新
- 所有 API 调用自动携带 Bearer 令牌进行认证

## 快速开始

### 安装

#### 从 PyPI 安装（推荐）

```bash
pip install topstack-sdk
```

#### 本地安装

```bash
# 克隆仓库
git clone https://github.com/topstack/topstack-sdk-python.git
cd topstack-sdk-python

# 开发模式安装（推荐）
pip install -e .
```

### 基本使用

```python
from topstack_sdk import TopStackClient
from topstack_sdk.iot import IotApi

# 创建客户端
client = TopStackClient(
    base_url="http://localhost:8000",
    app_id="your-app-id",
    app_secret="your-app-secret"
)

# 使用 IoT API
iot_api = IotApi(client)

# 查询实时数据
data = iot_api.find_last_data("device-id", "point-id")
print(f"当前值: {data.data['value']}")

# 查询设备列表
devices = client.get("/iot/open_api/v1/device/query")
print(f"设备数量: {len(devices.data.items)}")
```

## API 模块

### IoT 模块

```python
from topstack_sdk.iot import IotApi

iot_api = IotApi(client)

# 查询单点实时数据
data = iot_api.find_last_data("device-id", "point-id")

# 批量查询实时数据
points = [{"deviceID": "dev1", "pointID": "point1"}]
batch_data = iot_api.find_last_batch_data(points)

# 设置点位值
iot_api.set_value("device-id", "point-id", 123.45)

# 查询历史数据
history = iot_api.query_history_data(
    points=[{"deviceID": "dev1", "pointID": "point1"}],
    start="2023-01-01T00:00:00Z",
    end="2023-01-01T23:59:59Z"
)
```

### 告警模块

```python
from topstack_sdk.alert import AlertApi

alert_api = AlertApi(client)

# 查询告警级别
alert_levels = alert_api.query_alert_levels()

# 查询告警类型
alert_types = alert_api.query_alert_types()

# 查询告警记录
alert_records = alert_api.query_alert_records(
    start="2023-01-01T00:00:00Z",
    end="2023-01-01T23:59:59Z",
    pageNum=1,
    pageSize=10
)
```

### 资产管理模块

```python
from topstack_sdk.asset import AssetApi

asset_api = AssetApi(client)

# 查询工单
work_orders = asset_api.query_work_orders(pageSize=10, pageNum=1)

# 获取工单详情
work_order_detail = asset_api.get_work_order_detail("work-order-id")
```

### 能源管理模块

```python
from topstack_sdk.ems import EmsApi

ems_api = EmsApi(client)

# 查询电表
meters = ems_api.query_meters(pageNum=1, pageSize=10)

# 查询用能单元
sectors = ems_api.query_sectors(pageNum=1, pageSize=10)
```

### NATS 消息总线模块

```python
import asyncio
from topstack_sdk import NatsConfig, create_nats_bus

# 创建 NATS 配置
config = NatsConfig(
    addr="nats://localhost:4222",  # NATS 服务器地址
    token="your_token_here",       # 认证令牌（可选）
    username="your_username",       # 用户名（可选）
    password="your_password"        # 密码（可选）
)

async def point_data_handler(point_data):
    """处理测点数据"""
    print(f"收到测点数据: 设备={point_data.device_id}, 测点={point_data.point_id}, 值={point_data.value}")

async def device_state_handler(device_state):
    """处理设备状态数据"""
    status = "在线" if device_state.state == 1 else "离线"
    print(f"设备状态变化: 设备={device_state.device_id}, 状态={status}")

async def alert_info_handler(alert_info):
    """处理告警信息"""
    print(f"收到告警: ID={alert_info.alert_id}, 标题={alert_info.title}")

async def main():
    # 创建 NATS 总线
    nats_bus = await create_nats_bus(config)
    
    # 订阅设备测点数据
    point_sub = await nats_bus.subscribe_point_data(
        "project_id", "device_id", "point_id", point_data_handler
    )
    
    # 订阅设备状态数据
    device_state_sub = await nats_bus.subscribe_device_state(
        "project_id", "device_id", device_state_handler
    )
    
    # 订阅告警信息
    alert_sub = await nats_bus.subscribe_alert_info(
        "project_id", alert_info_handler
    )
    
    # 保持连接运行
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        # 取消订阅并关闭连接
        await point_sub.unsubscribe()
        await device_state_sub.unsubscribe()
        await alert_sub.unsubscribe()
        await nats_bus.close()

# 运行
asyncio.run(main())
```

#### 支持的消息类型

- **设备测点数据** (`PointData`): 实时设备测点值
- **设备状态数据** (`DeviceState`): 设备在线/离线状态
- **网关状态数据** (`GatewayState`): 网关在线/离线状态
- **数据通道状态** (`ChannelState`): 数据通道运行状态
- **告警信息** (`AlertInfo`): 实时告警消息

#### 订阅方法

```python
# 订阅设备测点数据
await nats_bus.subscribe_point_data(project_id, device_id, point_id, callback)

# 订阅同设备模型下的测点数据
await nats_bus.subscribe_device_type_data(project_id, device_type_id, point_id, callback)

# 订阅设备状态数据
await nats_bus.subscribe_device_state(project_id, device_id, callback)

# 订阅网关状态数据
await nats_bus.subscribe_gateway_state(project_id, callback)

# 订阅数据通道状态数据
await nats_bus.subscribe_channel_state(project_id, callback)

# 订阅全部告警消息
await nats_bus.subscribe_alert_info(project_id, callback)

# 订阅设备告警信息
await nats_bus.subscribe_device_alert_info(project_id, device_id, callback)
```

## 开发

### 运行测试

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=src/topstack_sdk --cov-report=html
```

### 代码格式化

```bash
# 格式化代码
black src/ tests/

# 排序导入
isort src/ tests/
```

### 类型检查

```bash
# 运行类型检查
mypy src/
```

## 发布到 PyPI

### 构建包

```bash
# 安装构建工具
pip install build twine

# 构建包
python -m build
```

### 发布

```bash
# 检查包
python -m twine check dist/*

# 发布到测试 PyPI
python -m twine upload --repository testpypi dist/*

# 发布到正式 PyPI
python -m twine upload dist/*
```

## 本地使用（不发布到 PyPI）

### 方法一：直接使用源码

```bash
# 克隆仓库
git clone https://github.com/topstack/topstack-sdk-python.git
cd topstack-sdk-python

# 开发模式安装
pip install -e .

# 在代码中使用
python examples/basic_usage.py
```

### 方法二：开发模式安装

```bash
# 在 SDK 目录下执行
pip install -e .
```

### 方法三：构建本地包

```bash
# 构建包
python -m build

# 安装本地包
pip install dist/topstack_sdk-1.0.0-py3-none-any.whl
```

## 配置

### 环境变量

```bash
export TOPSTACK_BASE_URL="http://localhost:8000"
export TOPSTACK_API_KEY="your-api-key"
export TOPSTACK_PROJECT_ID="your-project-id"
```

### 配置文件

```python
# config.py
TOPSTACK_CONFIG = {
    "base_url": "http://localhost:8000",
    "api_key": "your-api-key",
    "project_id": "your-project-id"
}
```

## 故障排除

### 常见问题

1. **模块找不到**
   ```bash
   # 检查 Python 路径
   python -c "import sys; print('\n'.join(sys.path))"
   
   # 检查模块是否可导入
   python -c "import topstack_sdk; print('SDK 导入成功')"
   ```

2. **依赖问题**
   ```bash
   # 检查依赖
   pip list | grep -E "(requests|pydantic|python-dateutil)"
   
   # 重新安装依赖
   pip install . --force-reinstall
   ```

3. **API 端点问题**
   ```bash
   # 运行 API 探索脚本
   python scripts/explore_apis.py
   
   # 运行连接诊断
   python scripts/diagnose_connection.py
   ```

## 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 支持

- 📧 邮箱：support@topstack.com
- 🐛 问题反馈：[GitHub Issues](https://github.com/topstack/topstack-sdk-python/issues)
- 📖 文档：[GitHub Wiki](https://github.com/topstack/topstack-sdk-python/wiki) 
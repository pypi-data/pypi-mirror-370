"""
TopStack SDK IoT 模块测试
"""

import pytest
from unittest.mock import Mock, patch
from topstack_sdk import TopStackClient
from topstack_sdk.iot import IotApi


class TestIotApi:
    """IoT API 测试类"""

    def setup_method(self):
        """设置测试环境"""
        self.client = TopStackClient(
            base_url="http://localhost:8000",
            api_key="test-api-key",
            project_id="test-project"
        )
        self.iot_api = IotApi(self.client)

    @patch.object(TopStackClient, 'post')
    def test_find_last_data(self, mock_post):
        """测试查询单点实时数据"""
        # 模拟响应
        mock_response = Mock()
        mock_response.data = {
            "deviceID": "test-device",
            "pointID": "test-point",
            "value": 123.45,
            "quality": 0,
            "timestamp": "2023-01-01T00:00:00Z"
        }
        mock_post.return_value = mock_response
        
        result = self.iot_api.find_last_data("test-device", "test-point")
        
        # 验证请求
        mock_post.assert_called_once_with(
            "/iot/open_api/v1/data/findLast",
            {"deviceID": "test-device", "pointID": "test-point"}
        )
        
        assert result.data["deviceID"] == "test-device"
        assert result.data["pointID"] == "test-point"
        assert result.data["value"] == 123.45

    @patch.object(TopStackClient, 'post')
    def test_find_last_batch_data(self, mock_post):
        """测试批量查询实时数据"""
        # 模拟响应
        mock_response = Mock()
        mock_response.data = [
            {
                "deviceID": "test-device-1",
                "pointID": "test-point-1",
                "value": 100,
                "quality": 0,
                "timestamp": "2023-01-01T00:00:00Z"
            },
            {
                "deviceID": "test-device-2",
                "pointID": "test-point-2",
                "value": 200,
                "quality": 0,
                "timestamp": "2023-01-01T00:00:00Z"
            }
        ]
        mock_post.return_value = mock_response
        
        points = [
            {"deviceID": "test-device-1", "pointID": "test-point-1"},
            {"deviceID": "test-device-2", "pointID": "test-point-2"}
        ]
        
        result = self.iot_api.find_last_batch_data(points)
        
        # 验证请求
        mock_post.assert_called_once_with(
            "/iot/open_api/v1/data/findLastBatch",
            points
        )
        
        assert len(result.data) == 2
        assert result.data[0]["deviceID"] == "test-device-1"
        assert result.data[1]["deviceID"] == "test-device-2"

    @patch.object(TopStackClient, 'post')
    def test_set_value(self, mock_post):
        """测试设置点位值"""
        # 模拟响应
        mock_response = Mock()
        mock_response.data = {"success": True}
        mock_post.return_value = mock_response
        
        result = self.iot_api.set_value("test-device", "test-point", 123.45)
        
        # 验证请求
        mock_post.assert_called_once_with(
            "/iot/open_api/v1/data/setValue",
            {
                "deviceID": "test-device",
                "pointID": "test-point",
                "value": 123.45
            }
        )
        
        assert result.data["success"] is True

    @patch.object(TopStackClient, 'post')
    def test_batch_set_value(self, mock_post):
        """测试批量设置点位值"""
        # 模拟响应
        mock_response = Mock()
        mock_response.data = {"success": True}
        mock_post.return_value = mock_response
        
        values = {
            "test-device-1": {"test-point-1": 100},
            "test-device-2": {"test-point-2": 200}
        }
        
        result = self.iot_api.batch_set_value(values)
        
        # 验证请求
        mock_post.assert_called_once_with(
            "/iot/open_api/v1/data/batchSetValue",
            values
        )
        
        assert result.data["success"] is True

    @patch.object(TopStackClient, 'post')
    def test_query_history_data(self, mock_post):
        """测试查询历史数据"""
        # 模拟响应
        mock_response = Mock()
        mock_response.data = {
            "results": [
                {
                    "deviceID": "test-device",
                    "pointID": "test-point",
                    "values": [
                        {"value": 100, "time": "2023-01-01T00:00:00Z"},
                        {"value": 200, "time": "2023-01-01T01:00:00Z"}
                    ]
                }
            ]
        }
        mock_post.return_value = mock_response
        
        query_params = {
            "points": [{"deviceID": "test-device", "pointID": "test-point"}],
            "start": "2023-01-01T00:00:00Z",
            "end": "2023-01-01T23:59:59Z"
        }
        
        result = self.iot_api.query_history_data(**query_params)
        
        # 验证请求
        mock_post.assert_called_once_with(
            "/iot/open_api/v1/data/query",
            query_params
        )
        
        assert len(result.data["results"]) == 1
        assert len(result.data["results"][0]["values"]) == 2 
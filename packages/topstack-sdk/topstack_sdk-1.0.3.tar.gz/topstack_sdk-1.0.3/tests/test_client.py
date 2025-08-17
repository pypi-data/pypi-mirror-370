"""
TopStack SDK 客户端测试
"""

import pytest
from unittest.mock import Mock, patch
from topstack_sdk import TopStackClient


class TestTopStackClient:
    """TopStack 客户端测试类"""

    def test_client_initialization(self):
        """测试客户端初始化"""
        client = TopStackClient(
            base_url="http://localhost:8000",
            api_key="test-api-key",
            project_id="test-project"
        )
        
        assert client.base_url == "http://localhost:8000"
        assert client.api_key == "test-api-key"
        assert client.project_id == "test-project"

    def test_client_headers(self):
        """测试请求头设置"""
        client = TopStackClient(
            base_url="http://localhost:8000",
            api_key="test-api-key",
            project_id="test-project"
        )
        
        expected_headers = {
            "X-API-KEY": "test-api-key",
            "X-ProjectID": "test-project",
            "Content-Type": "application/json"
        }
        
        assert client.headers == expected_headers

    @patch('requests.get')
    def test_get_request(self, mock_get):
        """测试 GET 请求"""
        # 模拟响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "data": []}
        mock_get.return_value = mock_response
        
        client = TopStackClient(
            base_url="http://localhost:8000",
            api_key="test-api-key",
            project_id="test-project"
        )
        
        response = client.get("/test/endpoint")
        
        # 验证请求
        mock_get.assert_called_once_with(
            "http://localhost:8000/test/endpoint",
            headers=client.headers,
            timeout=30
        )
        
        assert response.data == []

    @patch('requests.post')
    def test_post_request(self, mock_post):
        """测试 POST 请求"""
        # 模拟响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "data": {"id": "123"}}
        mock_post.return_value = mock_response
        
        client = TopStackClient(
            base_url="http://localhost:8000",
            api_key="test-api-key",
            project_id="test-project"
        )
        
        data = {"name": "test"}
        response = client.post("/test/endpoint", data)
        
        # 验证请求
        mock_post.assert_called_once_with(
            "http://localhost:8000/test/endpoint",
            headers=client.headers,
            json=data,
            timeout=30
        )
        
        assert response.data["id"] == "123"

    @patch('requests.get')
    def test_error_handling(self, mock_get):
        """测试错误处理"""
        # 模拟错误响应
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.reason = "Not Found"
        mock_response.text = '{"code": "404", "msg": "Resource not found"}'
        mock_response.json.return_value = {"code": "404", "msg": "Resource not found"}
        mock_get.return_value = mock_response
        
        client = TopStackClient(
            base_url="http://localhost:8000",
            api_key="test-api-key",
            project_id="test-project"
        )
        
        with pytest.raises(Exception) as exc_info:
            client.get("/test/endpoint")
        
        assert "HTTP 404" in str(exc_info.value)
        assert "Resource not found" in str(exc_info.value) 
# test_v2_client.py
import json
import pytest
import responses
import hmac
import hashlib
import time
from unittest.mock import patch
from clients import V2Client
from auth import V2AuthProvider
from config import config

class TestV2Client:
    @pytest.fixture(autouse=True)
    def setup_config(self):
        """显式配置测试用AK/SK"""
        # 保存原始配置
        self.original_base_url = config.BASE_URLS['V2']
        self.original_ak = getattr(config, 'V2_ACCESS_KEY', None)
        self.original_sk = getattr(config, 'V2_SECRET_KEY', None)

        # 设置测试配置
        config.BASE_URLS['V2'] = "https://api.v2.example.com"
        config.V2_ACCESS_KEY = "test_ak"
        config.V2_SECRET_KEY = "test_sk"

        yield

        # 恢复原始配置
        config.BASE_URLS['V2'] = self.original_base_url
        if self.original_ak: config.V2_ACCESS_KEY = self.original_ak
        if self.original_sk: config.V2_SECRET_KEY = self.original_sk

    @pytest.fixture
    def client(self):
        return V2Client()

    @responses.activate
    def test_create_experiment_success(self, client):
        """测试成功创建实验"""
        # Mock响应配置
        mock_url = f"{config.BASE_URLS['V2']}/openapi/v2/apps/123/experiments"
        responses.add(
            responses.POST,
            mock_url,
            json={"code": 200, "data": {"experiment_id": 456}},
            status=200
        )

        # 构造符合文档要求的参数
        params = {
            "app_id": 123,
            "name": "体验优化实验V2",
            "mode": 1,
            "endpoint_type": 1,
            "duration": 14,
            "major_metric": "click_rate",
            "metrics": ["click_rate", "conversion"],
            "versions": [
                {
                    "type": 0,
                    "name": "对照组",
                    "weight": 0.5,
                    "config": {"feature_flag": True}
                },
                {
                    "type": 1,
                    "name": "实验组",
                    "weight": 0.5
                }
            ],
            "layer_info": {
                "layer_id": -1,
                "version_resource": 0.7
            }
        }

        # 执行测试
        response = client.create_experiment(params)

        # 验证响应透传
        assert response == {"code": 200, "data": {"experiment_id": 456}}

        # 验证请求头
        request = responses.calls[0].request
        assert "X-Access-Key" in request.headers
        assert "X-Signature" in request.headers

        # 验证请求体结构
        request_body = json.loads(request.body)
        assert request_body["name"] == "体验优化实验V2"
        assert len(request_body["versions"]) == 2

    def test_create_experiment_missing_required_fields(self, client):
        """测试缺少必填字段"""
        invalid_params = {
            "app_id": 123,
            "name": "测试实验",
            # 缺少mode字段
            "endpoint_type": 1,
            "duration": 14,
            "major_metric": "m1",
            "metrics": ["m1"],
            "versions": []
        }

        response = client.create_experiment(invalid_params)
        assert response["code"] == 400
        assert "mode" in response["message"]

    @responses.activate
    def test_get_experiment_details(self, client):
        """测试获取实验详情"""
        mock_url = f"{config.BASE_URLS['V2']}/openapi/v2/apps/123/experiments/456/details"
        responses.add(
            responses.GET,
            mock_url,
            json={"code": 200, "data": {"status": 1}}
        )

        response = client.get_experiment_details({
            "app_id": 123,
            "experiment_id": 456
        })

        assert response["data"]["status"] == 1

class TestV2AuthProvider:
    def test_auth_headers_generation(self):
        """单独测试认证头生成"""
        with patch("time.time") as mock_time:
            mock_time.return_value = 1717257600  # 固定时间戳

            provider = V2AuthProvider()
            provider.ak = "test_ak"
            provider.sk = "test_sk"

            expected_sign = hmac.new(
                key=b"test_sk",
                msg=b"1717257600\ntest_ak",
                digestmod=hashlib.sha256
            ).hexdigest()

            headers = provider.get_headers()

            assert headers == {
                "X-Access-Key": "test_ak",
                "X-Timestamp": "1717257600",
                "X-Signature": expected_sign
            }
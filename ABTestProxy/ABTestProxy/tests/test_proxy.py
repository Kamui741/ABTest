'''
Author: ChZheng
Date: 2025-02-19 05:21:50
LastEditTime: 2025-02-19 05:22:37
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/ABTestProxy/ABTestProxy/tests/test_proxy.py
'''
import unittest
from unittest.mock import MagicMock
from clients.proxy import ABTestProxy

class TestABTestProxy(unittest.TestCase):
    def setUp(self):
        self.mock_v1_client = MagicMock()
        self.mock_mapper = MagicMock()
        self.proxy = ABTestProxy(self.mock_v1_client, self.mock_mapper)

    def test_request_transformation(self):
        """测试请求参数转换流程"""
        # 配置映射规则
        self.mock_mapper.load_mapping.return_value = {
            "flight_name": "name",
            "app": "app_id"
        }

        # 执行代理方法
        v2_request = {
            "name": "New Experiment",
            "app_id": 1001,
            "extra_param": "test"
        }
        self.proxy.create_experiment(v2_request)

        # 验证映射器调用
        self.mock_mapper.transform.assert_called_with(v2_request, {
            "flight_name": "name",
            "app": "app_id"
        })

    def test_error_handling(self):
        """测试异常处理机制"""
        self.mock_v1_client.create_experiment.side_effect = Exception("Test error")

        response = self.proxy.create_experiment({})
        self.assertEqual(response["code"], 500)
        self.assertIn("Test error", response["message"])
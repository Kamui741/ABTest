'''
Author: ChZheng
Date: 2025-02-19 05:21:50
LastEditTime: 2025-02-19 05:22:54
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/ABTestProxy/ABTestProxy/tests/test_helpers.py
'''
import unittest
from unittest.mock import patch
from api.helpers import send_request

class TestRequestHelpers(unittest.TestCase):
    @patch('requests.request')
    def test_successful_request(self, mock_request):
        """测试正常请求流程"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'code': 200}
        mock_request.return_value = mock_response

        result = send_request("GET", "http://test.url")
        self.assertEqual(result['code'], 200)

    @patch('requests.request')
    def test_retry_mechanism(self, mock_request):
        """测试会话失效后的重试逻辑"""
        mock_request.side_effect = [
            MagicMock(json=lambda: {'code': 401}),  # 首次失败
            MagicMock(json=lambda: {'code': 200})   # 重试成功
        ]

        result = send_request("GET", "http://test.url")
        self.assertEqual(result['code'], 200)
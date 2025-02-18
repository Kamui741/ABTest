'''
Author: ChZheng
Date: 2025-02-19 05:21:50
LastEditTime: 2025-02-19 05:22:31
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/ABTestProxy/ABTestProxy/tests/test_v1_client.py
'''
import unittest
from unittest.mock import MagicMock
from clients.v1_client import V1Client
from auth import SessionManager

class TestV1Client(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock(spec=SessionManager)
        self.client = V1Client(self.mock_session)

    def test_create_experiment_params(self):
        """测试实验创建参数传递"""
        self.mock_session.get_valid_session.return_value = "valid_session"

        # 执行创建方法
        self.client.create_experiment(
            flight_name="Test",
            duration=30,
            app_id=1001
        )

        # 验证核心参数
        self.mock_session.post.assert_called_with(
            "http://28.4.136.142/api/step1",
            json={
                "flight_name": "Test",
                "duration": 30,
                "hash_strategy": "ssid",
                # ...其他预期参数
            }
        )

    def test_report_generation(self):
        """测试报告生成参数处理"""
        self.client.get_report(
            app_id=1001,
            flight_id=2001,
            report_type="day",
            start_ts=1672502400,
            end_ts=1675084800
        )

        # 验证时间参数转换
        self.mock_session.get.assert_called_with(
            "https://28.4.136.142/datatester/api/v2/app/1001/flight/2001/rich-metric-report",
            params={
                "report_type": "day",
                "start_ts": 1672502400,
                "end_ts": 1675084800,
                "traceData": ""
            }
        )
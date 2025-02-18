'''
Author: ChZheng
Date: 2025-02-19 05:21:50
LastEditTime: 2025-02-19 05:22:47
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/ABTestProxy/ABTestProxy/tests/test_api_core.py
'''
import unittest
from unittest.mock import patch
from api.core import create_experiment

class TestExperimentCreation(unittest.TestCase):
    @patch('api.core.post_data')
    def test_full_creation_flow(self, mock_post):
        """测试完整四步创建流程"""
        # 配置各步骤模拟响应
        mock_post.side_effect = [
            {'data': {'draft_id': 'DRAFT_123'}},  # Step1
            {'success': True},                    # Step2
            {'success': True},                    # Step3
            {'data': {'flight_id': 789}}          # Step4
        ]

        result = create_experiment(
            flight_name="Full Test",
            duration=30,
            hash_strategy="user_id",
            app_id=1001
        )

        self.assertEqual(result['data']['flight_id'], 789)
        self.assertEqual(mock_post.call_count, 4)

    @patch('api.core.post_data')
    def test_step_failure_handling(self, mock_post):
        """测试步骤失败处理"""
        mock_post.side_effect = [
            {'data': {'draft_id': 'DRAFT_123'}},
            None,  # Step2失败
            {'success': True},
            {'data': {'flight_id': 789}}
        ]

        result = create_experiment(...)
        self.assertIsNone(result)
'''
Author: ChZheng
Date: 2025-02-19 05:21:50
LastEditTime: 2025-02-19 05:22:15
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/ABTestProxy/ABTestProxy/tests/test_auth.py
'''
import unittest
from unittest.mock import patch, Mock
from auth import SessionManager
import os

class TestSessionManager(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_session.txt"
        self.login_url = "http://mock.login"
        self.test_url = "http://mock.test"

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    @patch('requests.post')
    def test_new_session_creation(self, mock_post):
        """测试首次运行无session文件时的登录流程"""
        # 配置模拟登录响应
        mock_response = Mock()
        mock_response.cookies = {'sessionid': 'new_session_123'}
        mock_response.json.return_value = {'code': 200}
        mock_post.return_value = mock_response

        manager = SessionManager(self.login_url, self.test_file)
        sessionid = manager.load_sessionid()

        self.assertEqual(sessionid, 'new_session_123')
        self.assertTrue(os.path.exists(self.test_file))

    @patch('requests.get')
    def test_session_validation(self, mock_get):
        """测试会话有效性验证"""
        # 配置有效会话响应
        mock_response = Mock()
        mock_response.json.return_value = {'code': 200}
        mock_get.return_value = mock_response

        manager = SessionManager(self.login_url, self.test_file)
        self.assertTrue(manager.validate_session('valid_session', self.test_url))

    @patch('requests.get')
    def test_invalid_session_recovery(self, mock_get):
        """测试失效会话的自动恢复"""
        # 第一次验证失败
        mock_get.side_effect = [
            Mock(json=Mock(return_value={'code': 401})),  # 无效会话
            Mock(json=Mock(return_value={'code': 200}))   # 重新登录后有效
        ]

        manager = SessionManager(self.login_url, self.test_file)
        sessionid = manager.get_valid_session(self.test_url)

        self.assertIsNotNone(sessionid)
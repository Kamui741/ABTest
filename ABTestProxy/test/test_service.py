'''
Author: ChZheng
Date: 2025-03-06 06:29:39
LastEditTime: 2025-03-06 07:33:27
LastEditors: ChZheng
Description:
FilePath: /ABTest/ABTestProxy/test/test_service.py
'''
import pytest
from src.service import ABTestService

def test_seamless_version_switch():
    from src.service import ABTestService
    from unittest.mock import MagicMock

    service = ABTestService()

    # Mock组件
    mock_v2_client = MagicMock()
    mock_v2_client.create_experiment.return_value = {"code": 200}
    service.clients['V2'] = mock_v2_client

    mock_v1_adapter = MagicMock()
    mock_v1_adapter.convert_create_experiment_request.return_value = {"converted": True}
    service.adapters['V1'] = mock_v1_adapter

    # 测试V1路径
    service.create_experiment({"version": "V1", "name": "test"})
    mock_v1_adapter.convert_create_experiment_request.assert_called_once()

    # 测试V2路径
    service.create_experiment({"version": "V2", "name": "test"})
    mock_v2_client.create_experiment.assert_called_once()
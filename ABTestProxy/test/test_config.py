'''
Author: ChZheng
Date: 2025-03-06 06:29:39
LastEditTime: 2025-03-06 07:02:05
LastEditors: ChZheng
Description:
FilePath: /ABTest/ABTestProxy/test/test_config.py
'''
import pytest
import os
from src.config import config

def test_config_overrides(monkeypatch):
    monkeypatch.setenv('V1_BASE_URL', 'http://v1.test')
    monkeypatch.setenv('V2_AK', 'test_ak_123')

    from src.config import config
    config._reload()

    assert config.BASE_URLS['V1'] == 'http://v1.test'
    assert config.V2_ACCESS_KEY == 'test_ak_123'

def test_complex_endpoint():
    from src.config import config
    path = config.get_endpoint(
        version='V2',
        name='modify_status',
        app_id=123,
        experiment_id=456,
        action='stop'
    )
    assert path == "openapi/v2/apps/123/experiments/456/stop"
'''
Author: ChZheng
Date: 2025-03-06 07:02:29
LastEditTime: 2025-03-06 07:02:30
LastEditors: ChZheng
Description:
FilePath: /ABTest/ABTestProxy/test/test_auth.py
'''
import pytest
import hmac
import hashlib
from unittest.mock import patch

def test_v1_session_persistence(tmp_path):
    from src.auth import V1AuthProvider
    import os

    # 设置临时会话文件
    session_file = tmp_path / "session.txt"
    os.environ['V1_SESSION_FILE'] = str(session_file)

    provider = V1AuthProvider()
    provider._save_sessionid("test_session_123")

    assert provider._load_sessionid() == "test_session_123"
    assert session_file.read_text().strip() == "test_session_123"

def test_v2_signature_consistency():
    from src.auth import V2AuthProvider
    import time

    fixed_time = 1672531200  # 2023-01-01 00:00:00
    with patch('time.time', return_value=fixed_time):
        provider = V2AuthProvider()
        provider.ak = "test_ak"
        provider.sk = "test_sk"

        expected = hmac.new(
            b"test_sk",
            f"{fixed_time*1000}\ntest_ak".encode(),
            hashlib.sha256
        ).hexdigest()

        assert provider.get_headers()['X-Signature'] == expected
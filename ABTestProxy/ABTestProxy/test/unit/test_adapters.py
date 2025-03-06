'''
Author: ChZheng
Date: 2025-03-06 09:30:11
LastEditTime: 2025-03-06 17:15:57
LastEditors: ChZheng
Description:
FilePath: /ABTest/ABTestProxy/ABTestProxy/test/test_adapters.py
'''
# test_adapters.py
from adapters import V1Adapter, V2Adapter

def test_v1_request_conversion():
    """测试V1到V2的请求参数转换"""
    v2_params = {
        "name": "Test Exp",
        "duration": 7,
        "major_metric": "metric1",
        "versions": [
            {"name": "Control", "weight": 50},
            {"name": "Variant", "weight": 50}
        ]
    }

    converted = V1Adapter.convert_create_experiment_request(v2_params)

    # 验证字段映射
    assert converted["flight_name"] == "Test Exp"
    assert converted["duration"] == 7
    assert "hash_strategy" in converted
    assert len(converted["versions"]) == 2

def test_v1_response_conversion():
    """测试V1到V2的响应转换"""
    v1_response = {
        "flight_id": "f123",
        "status": "RUNNING",
        "created_at": "2024-05-01"
    }

    converted = V1Adapter.convert_create_experiment_response(v1_response)

    assert converted["data"]["experiment_id"] == "f123"
    assert "created_at" in converted["data"]

def test_v2_passthrough():
    """测试V2透传逻辑"""
    original = {"key": "value"}
    assert V2Adapter.convert_request(original) == original
    assert V2Adapter.convert_response(original) == original



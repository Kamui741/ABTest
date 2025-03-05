'''
Author: ChZheng
Date: 2025-03-06 06:29:39
LastEditTime: 2025-03-06 07:02:54
LastEditors: ChZheng
Description:
FilePath: /ABTest/ABTestProxy/test/test_adapters.py
'''
import pytest
from src.adapters import V1Adapter, V2Adapter

class TestV1Adapters:
    @pytest.mark.parametrize("input_data,expected", [
        (
            {"name": "test", "duration": 7},
            {"flight_name": "test", "hash_strategy": "ssid", "duration": 7}
        ),
        (
            {"versions": [{"weight": 0.3}]},
            {"versions": [{"weight": 30}]}
        )
    ])
    def test_create_conversion(self, input_data, expected):
        from src.adapters import V1Adapter
        assert V1Adapter.convert_create_experiment_request(input_data) == expected

class TestV2Adapters:
    def test_passthrough_logic(self):
        from src.adapters import V2Adapter
        data = {"complex": {"nested": [1,2,3]}}
        assert V2Adapter.convert_request(data) == data
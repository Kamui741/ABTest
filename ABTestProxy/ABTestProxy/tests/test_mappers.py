'''
Author: ChZheng
Date: 2025-02-19 05:21:50
LastEditTime: 2025-02-19 05:22:22
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/ABTestProxy/ABTestProxy/tests/test_mappers.py
'''
import unittest
from mappers import SimpleMapper
import tempfile
import json

class TestSimpleMapper(unittest.TestCase):
    def test_basic_field_mapping(self):
        """测试基础字段映射"""
        mapper = SimpleMapper()
        data = {"user": {"name": "Alice", "age": 30}}
        mapping = {
            "username": "user.name",
            "user_age": "user.age"
        }

        result = mapper.transform(data, mapping)
        self.assertEqual(result, {
            "username": "Alice",
            "user_age": 30
        })

    def test_nested_structure(self):
        """测试嵌套结构映射"""
        mapper = SimpleMapper()
        data = {
            "payload": {
                "items": [
                    {"id": 1, "value": "A"},
                    {"id": 2, "value": "B"}
                ]
            }
        }
        mapping = {
            "elements": {
                "path": "payload.items",
                "mapping": {
                    "element_id": "id",
                    "content": "value"
                }
            }
        }

        result = mapper.transform(data, mapping)
        self.assertEqual(result["elements"], [
            {"element_id": 1, "content": "A"},
            {"element_id": 2, "content": "B"}
        ])

    def test_default_values(self):
        """测试默认值处理"""
        mapper = SimpleMapper()
        data = {"settings": {}}
        mapping = {
            "retry_count": "settings.retry||3",
            "timeout": "settings.timeout||30"
        }

        result = mapper.transform(data, mapping)
        self.assertEqual(result["retry_count"], 3)
        self.assertEqual(result["timeout"], 30)
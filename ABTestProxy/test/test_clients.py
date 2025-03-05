'''
Author: ChZheng
Date: 2025-03-06 06:29:39
LastEditTime: 2025-03-06 07:32:01
LastEditors: ChZheng
Description:
FilePath: /ABTest/ABTestProxy/test/test_clients.py
'''
import pytest
import requests_mock
from src.clients import V1Client, V2Client
from src.helpers import post_data
from src.adapters import V1Adapters, V2Adapters

class TestV1Client:
    def test_multistep_creation(mocker):
        from src.clients import V1Client
        from src.helpers import post_data

        client = V1Client()
        mocker.patch.object(client, 'base_url', 'http://v1.test')

        with requests_mock.Mocker() as m:
            m.post("http://v1.test/api/step1", json={"data": {"draft_id": "D001"}})
            m.post("http://v1.test/api/step2", json={"data": {}})
            m.post("http://v1.test/api/step3", json={"data": {}})
            m.post("http://v1.test/api/step4", json={"data": {"id": 123}})

            result = client.create_experiment({
                "flight_name": "test",
                "app_id": 456,
                "duration": 7
            })

            assert result['data']['id'] == 123
            assert m.call_count == 4

class TestV2Client:
    def test_version_building():
        from src.clients import V2Client
        client = V2Client()

        versions = client._build_versions([
            {"type": 0, "name": "Control"},
            {"type": 1, "name": "Test", "weight": 0.6}
        ])

        assert len(versions) == 2
        assert versions[0]['weight'] == 0.5  # 默认均分
        assert versions[1]['weight'] == 0.5
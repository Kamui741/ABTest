# tests/test_clients.py
import responses
from clients import V1Client, V2Client
import pytest

def test_v1_client_creation():
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "https://v1-server/api/step1",
            json={"data": {"draft_id": "d1"}}
        )
        client = V1Client()
        result = client.create_experiment({
            "flight_name": "测试实验",
            "duration": 7,
            "app_id": 123
        })
        assert "draft_id" in result.get("data", {})

def test_v2_signature_generation():
    client = V2Client()
    headers = client._get_auth_headers()
    assert "X-Access-Key" in headers
    assert "X-Signature" in headers
# test_clients.py
import responses
from clients import V1Client, V2Client

def test_v1_full_workflow():
    """测试V1客户端完整四步创建流程"""
    with responses.RequestsMock() as rsps:
        # 模拟四个步骤的响应
        rsps.add(responses.POST, "https://v1-api/step1", json={"data": {"draft_id": "d1"}})
        rsps.add(responses.POST, "https://v1-api/step2", json={"status": "ok"})
        rsps.add(responses.POST, "https://v1-api/step3", json={"version_id": "v1"})
        rsps.add(responses.POST, "https://v1-api/step4", json={"flight_id": "f123"})

        client = V1Client()
        result = client.create_experiment({
            "flight_name": "test",
            "duration": 7,
            "app_id": 123
        })

        assert result["flight_id"] == "f123"
        assert len(rsps.calls) == 4  # 验证四个步骤

def test_v2_signature_generation():
    """测试V2签名头生成"""
    client = V2Client()
    with patch("time.time", return_value=1717257600):
        headers = client._get_auth_headers()

        # 验证签名算法
        expected_sign = hmac.new(
            key=config.V2_SECRET_KEY.encode(),
            msg=f"1717257600\n{config.V2_ACCESS_KEY}".encode(),
            digestmod=hashlib.sha256
        ).hexdigest()

        assert headers["X-Timestamp"] == "1717257600"
        assert headers["X-Signature"] == expected_sign

def test_v2_url_building():
    """测试V2端点路径生成"""
    client = V2Client()

    test_cases = [
        ("create_experiment", {"app_id": 123},
         "/openapi/v2/apps/123/experiments"),
        ("get_details", {"app_id": 123, "experiment_id": 456},
         "/openapi/v2/apps/123/experiments/456/details"),
        ("modify_status", {"app_id": 123, "experiment_id": 456, "action": "stop"},
         "/openapi/v2/apps/123/experiments/456/stop")
    ]

    for endpoint, params, expected_path in test_cases:
        url = client._build_url(endpoint, **params)
        assert expected_path in url

# test_adapters.py
from adapters import V1Adapter, V2Adapter

# def test_v1_request_conversion():
#     """测试V1到V2的请求参数转换"""
#     v2_params = {
#         "name": "Test Exp",
#         "duration": 7,
#         "major_metric": "metric1",
#         "versions": [
#             {"name": "Control", "weight": 50},
#             {"name": "Variant", "weight": 50}
#         ]
#     }

#     converted = V1Adapter.convert_create_experiment_request(v2_params)

#     # 验证字段映射
#     assert converted["flight_name"] == "Test Exp"
#     assert converted["duration"] == 7
#     assert "hash_strategy" in converted
#     assert len(converted["versions"]) == 2

# def test_v1_response_conversion():
#     """测试V1到V2的响应转换"""
#     v1_response = {
#         "flight_id": "f123",
#         "status": "RUNNING",
#         "created_at": "2024-05-01"
#     }

#     converted = V1Adapter.convert_create_experiment_response(v1_response)

#     assert converted["data"]["experiment_id"] == "f123"
#     assert "created_at" in converted["data"]

def test_v2_passthrough():
    """测试V2透传逻辑"""
    original = {"key": "value"}
    assert V2Adapter.convert_request(original) == original
    assert V2Adapter.convert_response(original) == original


# test_app.py
from fastapi.testclient import TestClient
from app import app
import pytest

client = TestClient(app)

# ----------- 实验管理 -----------
@pytest.mark.parametrize("version", ["V1", "V2"])
def test_create_experiment(version):
    """测试双版本创建实验"""
    response = client.post(
        f"/openapi/v2/apps/123/experiments?version={version}",
        json={
            "name": "用户体验测试",
            "duration": 14,
            "major_metric": "click_rate",
            "metrics": ["click_rate", "conversion"],
            "versions": [
                {"name": "对照组", "weight": 50},
                {"name": "实验组", "weight": 50}
            ]
        }
    )
    assert response.status_code == 200
    assert "experiment_id" in response.json()["data"]

def test_get_experiment_details():
    """测试获取实验详情"""
    # 先创建实验
    create_res = client.post(...)
    exp_id = create_res.json()["data"]["experiment_id"]

    response = client.get(
        f"/openapi/v1/apps/123/experiment/{exp_id}/details?version=V2"
    )
    assert response.json()["data"]["status"] == "RUNNING"

# ----------- 实验分析 -----------
@pytest.mark.parametrize("report_type,expected", [
    ("day", "daily_report"),
    ("hour", "hourly_report"),
    ("five_minute", "realtime_report")
])
def test_generate_reports(report_type, expected):
    """测试不同粒度报告生成"""
    response = client.get(
        f"/openapi/v1/apps/123/experiment/456/metrics",
        params={
            "report_type": report_type,
            "start_ts": "1717171200",
            "end_ts": "1717257600",
            "version": "V1"
        }
    )
    assert expected in response.json()["data"]

# ----------- 状态管理 -----------
def test_launch_experiment():
    response = client.put(
        "/openapi/v2/apps/123/experiments/456/launch?version=V2"
    )
    assert response.json()["message"] == "Experiment launched"

def test_stop_experiment():
    response = client.put(
        "/openapi/v2/apps/123/experiments/456/stop?version=V1"
    )
    assert "stopped_at" in response.json()["data"]

# ----------- 资源管理 -----------
def test_list_metrics_pagination():
    """测试指标列表分页"""
    response = client.get(
        "/openapi/v2/apps/123/metrics",
        params={
            "page": 2,
            "page_size": 5,
            "version": "V2"
        }
    )
    data = response.json()["data"]
    assert len(data["items"]) == 5
    assert data["page"] == 2

def test_search_mutex_groups():
    """测试互斥组搜索"""
    response = client.get(
        "/openapi/v2/apps/123/layers",
        params={
            "keyword": "核心实验",
            "version": "V1"
        }
    )
    assert all("核心实验" in g["name"] for g in response.json()["data"]["items"])

# test_app.py
from fastapi.testclient import TestClient
from app import app
import pytest

client = TestClient(app)

# ----------- 实验管理 -----------
@pytest.mark.parametrize("version", ["V1", "V2"])
def test_create_experiment(version):
    """测试双版本创建实验"""
    response = client.post(
        f"/openapi/v2/apps/123/experiments?version={version}",
        json={
            "name": "用户体验测试",
            "duration": 14,
            "major_metric": "click_rate",
            "metrics": ["click_rate", "conversion"],
            "versions": [
                {"name": "对照组", "weight": 50},
                {"name": "实验组", "weight": 50}
            ]
        }
    )
    assert response.status_code == 200
    assert "experiment_id" in response.json()["data"]

def test_get_experiment_details():
    """测试获取实验详情"""
    # 先创建实验
    create_res = client.post(...)
    exp_id = create_res.json()["data"]["experiment_id"]

    response = client.get(
        f"/openapi/v1/apps/123/experiment/{exp_id}/details?version=V2"
    )
    assert response.json()["data"]["status"] == "RUNNING"

# ----------- 实验分析 -----------
@pytest.mark.parametrize("report_type,expected", [
    ("day", "daily_report"),
    ("hour", "hourly_report"),
    ("five_minute", "realtime_report")
])
def test_generate_reports(report_type, expected):
    """测试不同粒度报告生成"""
    response = client.get(
        f"/openapi/v1/apps/123/experiment/456/metrics",
        params={
            "report_type": report_type,
            "start_ts": "1717171200",
            "end_ts": "1717257600",
            "version": "V1"
        }
    )
    assert expected in response.json()["data"]

# ----------- 状态管理 -----------
def test_launch_experiment():
    response = client.put(
        "/openapi/v2/apps/123/experiments/456/launch?version=V2"
    )
    assert response.json()["message"] == "Experiment launched"

def test_stop_experiment():
    response = client.put(
        "/openapi/v2/apps/123/experiments/456/stop?version=V1"
    )
    assert "stopped_at" in response.json()["data"]

# ----------- 资源管理 -----------
def test_list_metrics_pagination():
    """测试指标列表分页"""
    response = client.get(
        "/openapi/v2/apps/123/metrics",
        params={
            "page": 2,
            "page_size": 5,
            "version": "V2"
        }
    )
    data = response.json()["data"]
    assert len(data["items"]) == 5
    assert data["page"] == 2

def test_search_mutex_groups():
    """测试互斥组搜索"""
    response = client.get(
        "/openapi/v2/apps/123/layers",
        params={
            "keyword": "核心实验",
            "version": "V1"
        }
    )
    assert all("核心实验" in g["name"] for g in response.json()["data"]["items"])


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
    from auth import V1AuthProvider
    import os

    # 设置临时会话文件
    session_file = tmp_path / "session.txt"
    os.environ['V1_SESSION_FILE'] = str(session_file)

    provider = V1AuthProvider()
    provider._save_sessionid("test_session_123")

    assert provider._load_sessionid() == "test_session_123"
    assert session_file.read_text().strip() == "test_session_123"

def test_v2_signature_consistency():
    from auth import V2AuthProvider
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


# test_service.py
from unittest.mock import Mock, patch
from service import ABTestService
import pytest

def test_version_auto_detection():
    """测试版本自动选择逻辑"""
    service = ABTestService()

    # 测试显式指定V1
    service._setup_components({"version": "V1"})
    assert isinstance(service._client, V1Client)

    # 测试默认V2
    service._setup_components({})
    assert isinstance(service._client, V2Client)

def test_create_flow_with_mock():
    """模拟完整创建流程"""
    mock_client = Mock()
    mock_adapter = Mock()

    # 配置Mock返回值
    mock_adapter.convert_create_experiment_request.return_value = {"v1_format": True}
    mock_client.create_experiment.return_value = {"code": 200, "data": {"flight_id": "f123"}}
    mock_adapter.convert_create_experiment_response.return_value = {"code":200, "data": {"experiment_id": "exp123"}}

    # 注入Mock对象
    service = ABTestService()
    service._client = mock_client
    service._adapter = mock_adapter

    # 执行测试
    result = service.create_experiment({"version": "V1", "name": "test"})

    # 验证调用链
    mock_adapter.convert_create_experiment_request.assert_called_once()
    mock_client.create_experiment.assert_called_once()
    assert result["data"]["experiment_id"] == "exp123"

@pytest.mark.parametrize("method,params", [
    ("get_experiment_details", {"experiment_id": 456}),
    ("generate_report", {"report_type": "day"}),
    ("modify_experiment_status", {"action": "launch"}),
    ("list_available_metrics", {"page": 1}),
    ("list_mutex_groups", {"need_page": 0})
])
def test_all_service_methods(method, params):
    """测试所有服务方法"""
    service = ABTestService()
    func = getattr(service, method)
    with patch.object(service, '_client') as mock_client:
        mock_client.method.return_value = {"code": 200}
        result = func({"version": "V2", **params})
        assert result["code"] == 200

'''
Author: ChZheng
Date: 2025-03-06 09:30:11
LastEditTime: 2025-03-06 17:20:42
LastEditors: ChZheng
Description:
FilePath: /ABTest/ABTestProxy/ABTestProxy/test/test_integration.py
'''
# test_integration.py
import docker
import time

import pytest

@pytest.fixture(scope="module")
def mock_servers():
    """启动V1/V2模拟服务器"""
    client = docker.from_env()

    # 启动V1模拟服务
    v1_container = client.containers.run(
        "wiremock/wiremock",
        ports={"8080/tcp": 8080},
        detach=True
    )

    # 启动V2模拟服务
    v2_container = client.containers.run(
        "wiremock/wiremock",
        ports={"8081/tcp": 8081},
        detach=True
    )

    time.sleep(5)  # 等待服务启动
    yield
    v1_container.stop()
    v2_container.stop()

def test_full_v1_workflow(mock_servers):
    """测试V1完整流程"""
    # 配置V1 Mock规则
    configure_v1_endpoints()

    # 创建实验
    create_res = client.post(
        "/openapi/v2/apps/123/experiments?version=V1",
        json={...}
    )
    exp_id = create_res.json()["data"]["experiment_id"]

    # 查询详情
    detail_res = client.get(f"/openapi/v1/apps/123/experiment/{exp_id}/details?version=V1")
    assert detail_res.json()["data"]["status"] == "RUNNING"

    # 生成报告
    report_res = client.get(f"/openapi/v1/apps/123/experiment/{exp_id}/metrics?...")
    assert "daily_report" in report_res.json()["data"]

    # 停止实验
    stop_res = client.put(f"/openapi/v2/apps/123/experiments/{exp_id}/stop?version=V1")
    assert stop_res.json()["code"] == 200

def configure_v1_endpoints():
    """配置V1 Mock端点规则"""
    # 示例：配置创建实验的四个步骤
    setup_step("/step1", {"draft_id": "d1"})
    setup_step("/step2", {"status": "ok"})
    setup_step("/step3", {"version_id": "v1"})
    setup_step("/step4", {"flight_id": "f123"})

def setup_step(path, response):
    requests.post(
        "http://localhost:8080/__admin/mappings",
        json={
            "request": {"method": "POST", "urlPath": path},
            "response": {"status": 200, "jsonBody": response}
        }
    )
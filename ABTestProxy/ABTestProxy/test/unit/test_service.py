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
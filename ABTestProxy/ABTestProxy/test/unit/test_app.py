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
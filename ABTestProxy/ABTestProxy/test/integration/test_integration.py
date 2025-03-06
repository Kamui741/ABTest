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
import pytest
import requests
from src.config import config
from src.service import ABTestService


BASE_URL = "http://localhost:8000"

@pytest.mark.integration
class TestV1Features:
    """V1版本六接口全流程测试"""

    @pytest.fixture
    def experiment_id(self):
        # 创建V1实验并返回ID
        res = requests.post(
            f"{BASE_URL}/openapi/v2/apps/123/experiments",
            params={"version": "V1"},
            json={
                "flight_name": "v1_test",
                "duration": 7,
                "app_id": 123
            }
        )
        return res.json()['data']['flight_id']

    def test_all_features(self, experiment_id):
        # 1. 获取详情
        detail_res = requests.get(
            f"{BASE_URL}/openapi/v1/apps/123/experiment/{experiment_id}/details",
            params={"version": "V1"}
        )
        assert detail_res.json()['data']['flight_name'] == "v1_test"

        # 2. 生成报告
        report_res = requests.get(
            f"{BASE_URL}/openapi/v1/apps/123/experiment/{experiment_id}/metrics",
            params={
                "version": "V1",
                "report_type": "day",
                "start_ts": "1672502400",
                "end_ts": "1672588800"
            }
        )
        assert 'calculation_results' in report_res.json()['data']

        # 3. 修改状态
        status_res = requests.put(
            f"{BASE_URL}/openapi/v2/apps/123/experiments/{experiment_id}/stop",
            params={"version": "V1"}
        )
        assert status_res.json()['code'] == 200

        # 4. 指标列表
        metric_res = requests.get(
            f"{BASE_URL}/openapi/v2/apps/123/metrics",
            params={"version": "V1"}
        )
        assert isinstance(metric_res.json()['data'], list)

        # 5. 互斥组列表
        group_res = requests.get(
            f"{BASE_URL}/openapi/v2/apps/123/layers",
            params={"version": "V1"}
        )
        assert 'available_traffic' in group_res.json()['data'][0]

        # 6. 验证状态变更
        final_detail = requests.get(
            f"{BASE_URL}/openapi/v1/apps/123/experiment/{experiment_id}/details",
            params={"version": "V1"}
        )
        assert final_detail.json()['data']['status'] == 0

@pytest.mark.integration
class TestV2Features:
    """V2版本六接口全流程测试"""

    @pytest.fixture
    def experiment_id(self):
        # 创建V2实验并返回ID
        res = requests.post(
            f"{BASE_URL}/openapi/v2/apps/456/experiments",
            params={"version": "V2"},
            json={
                "name": "v2_test",
                "mode": 1,
                "duration": 14,
                "major_metric": 1001,
                "metrics": [1001],
                "versions": [{"type": 0}]
            }
        )
        return res.json()['data']

    def test_all_features(self, experiment_id):
        # 1. 获取详情
        detail_res = requests.get(
            f"{BASE_URL}/openapi/v1/apps/456/experiment/{experiment_id}/details",
            params={"version": "V2"}
        )
        assert detail_res.json()['data']['name'] == "v2_test"

        # 2. 生成报告
        report_res = requests.get(
            f"{BASE_URL}/openapi/v1/apps/456/experiment/{experiment_id}/metrics",
            params={
                "version": "V2",
                "report_type": "hour",
                "start_ts": "1672502400",
                "end_ts": "1672588800"
            }
        )
        assert 'user_data' in report_res.json()['data']

        # 3. 修改状态
        status_res = requests.put(
            f"{BASE_URL}/openapi/v2/apps/456/experiments/{experiment_id}/launch",
            params={"version": "V2"}
        )
        assert status_res.json()['code'] == 200

        # 4. 指标列表
        metric_res = requests.get(
            f"{BASE_URL}/openapi/v2/apps/456/metrics",
            params={"version": "V2"}
        )
        assert 'page' in metric_res.json()['data']

        # 5. 互斥组列表
        group_res = requests.get(
            f"{BASE_URL}/openapi/v2/apps/456/layers",
            params={"version": "V2"}
        )
        assert 'type' in group_res.json()['data'][0]

        # 6. 验证状态变更
        final_detail = requests.get(
            f"{BASE_URL}/openapi/v1/apps/456/experiment/{experiment_id}/details",
            params={"version": "V2"}
        )
        assert final_detail.json()['data']['status'] == 1
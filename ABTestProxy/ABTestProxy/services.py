'''
Author: ChZheng
Date: 2025-02-25 15:53:17
LastEditTime: 2025-02-25 15:55:52
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/ABTestProxy/ABTestProxy/services.py
'''
# ---------------------- services.py ----------------------
from interfaces import IExperimentService

class V1ProxyService(IExperimentService):
    def __init__(self, client: V1Client):
        self.client = client

    def create_experiment(self, name: str, app_id: int, metrics: list) -> dict:
        # V1参数转换
        v1_params = {
            "flight_name": name,
            "app_id": app_id,
            "metric_list": [{"name": m.upper()} for m in metrics]
        }

        response = self.client.post('experiment', 'create', v1_params)

        # 转换为统一格式
        return {
            'id': response['flight_id'],
            'name': name,
            'status': 'created' if response['success'] else 'failed'
        }

    def get_details(self, experiment_id: str) -> dict:
        raw = self.client.get('experiment', 'detail', {'id': experiment_id})
        return {
            'id': experiment_id,
            'versions': [g['group_name'] for g in raw.get('groups', [])],
            'status': raw.get('status')
        }

    def generate_report(self, experiment_id: str, start: int, end: int) -> dict:
        # 类似转换逻辑...
        pass

class V2DirectService(IExperimentService):
    def __init__(self, client: V2Client):
        self.client = client

    def create_experiment(self, name: str, app_id: int, metrics: list) -> dict:
        return self.client.post('experiment', 'create', {
            'name': name,
            'app_id': app_id,
            'metrics': metrics
        })

    def get_details(self, experiment_id: str) -> dict:
        return self.client.get('experiment', 'detail', {'id': experiment_id})

    def generate_report(self, experiment_id: str, start: int, end: int) -> dict:
        return self.client.post('report', '', {
            'experiment_id': experiment_id,
            'start': start,
            'end': end
        })

class ServiceFactory:
    @staticmethod
    def create(session: SessionManager) -> IExperimentService:
        if RUNTIME_MODE == 'V1':
            return V1ProxyService(V1Client(session))
        return V2DirectService(V2Client(session))
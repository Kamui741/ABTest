'''
Author: ChZheng
Date: 2025-02-25 19:36:47
LastEditTime: 2025-02-26 07:33:28
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/ABTestProxy/ABTestProxy/config.py
'''
# ---------------------- config.py ----------------------
import os

class ABTestConfig:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._reload()
        return cls._instance

    @classmethod
    def _reload(cls):
        # 基础配置
        cls.SESSION_FILE = os.getenv('SESSION_FILE', 'session.txt')
        cls.LOGIN_URL = os.getenv('LOGIN_URL', 'https://28.4.136.142/api/login')
        cls.USERNAME = os.getenv("USERNAME", "admin")
        cls.PASSWORD = os.getenv("PASSWORD", "admin123")

        # V2认证配置
        cls.V2_ACCESS_KEY = os.getenv("V2_ACCESS_KEY")
        cls.V2_SECRET_KEY = os.getenv("V2_SECRET_KEY")

        # 版本配置
        cls.RUNTIME_MODE = os.getenv('RUNTIME_MODE', 'V1')  # V1/V2
        cls.BASE_URLS = {
            'V1': 'https://28.4.136.142/datatester/api/v1',
            'V2': 'https://28.4.136.142/datatester/api/v2'
        }
        cls.API_ENDPOINTS = {
            'create_experiment': {
                'V1': 'experiment/create',
                'V2': 'openapi/v2/apps/{app_id}/experiments'
            },
            'get_details': {
                'V1': 'experiment/detail',
                'V2': 'openapi/v2/apps/{app_id}/experiments/{experiment_id}'
            },
            'generate_report': {
                'V1': 'report/generate',
                'V2': 'openapi/v2/apps/{app_id}/experiments/{experiment_id}/metrics'
            },
            'modify_status': {
                'V1': 'experiment/status',
                'V2': 'openapi/v2/apps/{app_id}/experiments/{experiment_id}/{action}'
            },
            'list_metrics': {
                'V1': 'metrics',
                'V2': 'openapi/v2/apps/{app_id}/metrics'
            },
            'list_groups': {
                'V1': 'groups',
                'V2': 'openapi/v2/apps/{app_id}/layers'
            }
        }

    @property
    def current_base_url(self):
        return self.BASE_URLS[self.RUNTIME_MODE]

    def get_endpoint(self, name: str, **params) -> str:
        template = self.API_ENDPOINTS[name][self.RUNTIME_MODE]
        return template.format(**params)

config = ABTestConfig()
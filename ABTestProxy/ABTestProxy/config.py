'''
Author: ChZheng
Date: 2025-02-25 19:36:47
LastEditTime: 2025-03-06 10:41:59
LastEditors: ChZheng
Description:
FilePath: /ABTest/ABTestProxy/src/config.py
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
        cls.V1_SESSION_FILE = os.getenv('SESSION_FILE', 'session.txt')
        cls.V1_LOGIN_URL = os.getenv('LOGIN_URL', 'https://28.4.136.142/api/login')
        cls.V1_USERNAME = os.getenv("USERNAME")
        cls.V1_PASSWORD = os.getenv("PASSWORD")
        cls.V1_TARGET_URL = os.getenv('TARGET_URL', 'https://28.4.136.142')

        # V2认证配置
        cls.V2_ACCESS_KEY = os.getenv("V2_ACCESS_KEY")
        cls.V2_SECRET_KEY = os.getenv("V2_SECRET_KEY")


        cls.BASE_URLS = {
            'V1': os.getenv('V1_BASE_URL', 'https://28.4.136.142'),
            'V2': os.getenv('V2_BASE_URL', 'https://default-v2.example.com')
        }
        cls.API_ENDPOINTS = {
            'create_experiment': {
                'V1': 'experiment/create',
                'V2': 'openapi/v2/apps/{app_id}/experiments'
            },
            'get_details': {
                'V1': 'experiment/detail',
                'V2': 'openapi/v2/apps/{app_id}/experiments/{experiment_id}/details'
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


    def get_endpoint(self, version: str, name: str, **params) -> str:
        """动态获取端点路径"""
        return self.API_ENDPOINTS[name][version].format(**params)

config = ABTestConfig()
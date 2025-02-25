# config.py 增强版
import os
from typing import Literal

# 版本配置
RUNTIME_MODE: Literal['V1', 'V2'] = os.getenv('RUNTIME_MODE', 'V1')

# 认证配置
V1_SESSION_FILE = os.getenv('V1_SESSION_FILE', 'v1_session.txt')
V2_AK = os.getenv("V2_ACCESS_KEY")
V2_SK = os.getenv("V2_SECRET_KEY")

# 服务端点
API_ENDPOINTS = {
    'V1': {
        'experiment': {
            'create': 'https://28.4.136.142/datatester/api/v1/experiment',
            'detail': 'https://28.4.136.142/datatester/api/v1/experiment/{id}',
            'status': 'https://28.4.136.142/datatester/api/v1/experiment/{id}/status'
        },
        'report': 'https://28.4.136.142/datatester/api/v1/report',
        'metric': 'https://28.4.136.142/datatester/api/v1/metric',
        'layer': 'https://28.4.136.142/datatester/api/v1/layer'
    },
    'V2': {
        'experiment': {
            'create': 'https://28.4.136.142/openapi/v2/apps/{app_id}/experiments',
            'detail': 'https://28.4.136.142/openapi/v2/apps/{app_id}/experiments/{experiment_id}',
            'launch': 'https://28.4.136.142/openapi/v2/apps/{app_id}/experiments/{experiment_id}/launch',
            'stop': 'https://28.4.136.142/openapi/v2/apps/{app_id}/experiments/{experiment_id}/stop'
        },
        'report': 'https://28.4.136.142/openapi/v2/apps/{app_id}/experiments/{experiment_id}/metrics',
        'metric': 'https://28.4.136.142/openapi/v2/apps/{app_id}/metrics',
        'layer': 'https://28.4.136.142/openapi/v2/apps/{app_id}/layers'
    }
}

# 基础配置
LOGIN_URL = os.getenv('LOGIN_URL', 'https://28.4.136.142/api/login')
USERNAME = os.getenv("USERNAME", "admin")
PASSWORD = os.getenv("PASSWORD", "admin123")
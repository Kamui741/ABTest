'''
Author: ChZheng
Date: 2025-02-12 04:40:30
LastEditTime: 2025-02-12 04:51:33
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/api/qushu/api/services.py
'''
# project/api/services.py
from typing import Dict
from core.config import AppConfig
from core.mapper import FieldMapper
from .clients import V1Client, V2Client
from core.exceptions import ConfigurationError

class ABTestService:
    """AB测试业务服务"""

    def __init__(self):
        self.mapper = FieldMapper()
        self.v1_client = V1Client()
        self.v2_client = V2Client()

        if AppConfig.V1_ADAPTER_MODE not in ["proxy", "direct"]:
            raise ConfigurationError("Invalid V1_ADAPTER_MODE")

    def create_experiment(self, request_data: Dict) -> Dict:
        """创建实验入口"""
        if AppConfig.USE_V2_DIRECT:
            return self.v2_client.create_experiment(request_data)

        if AppConfig.V1_ADAPTER_MODE == "proxy":
            return self._proxy_v1_request(request_data)

        return self.v1_client.create_experiment(request_data)

    def _proxy_v1_request(self, data: Dict) -> Dict:
        """代理模式请求处理"""
        mapped_request = self.mapper.map_fields(
            data,
            "create_experiment",
            "request"
        )
        v1_response = self.v1_client.create_experiment(mapped_request)
        return self.mapper.map_fields(
            v1_response,
            "create_experiment",
            "response"
        )
'''
Author: ChZheng
Date: 2025-03-05 15:12:03
LastEditTime: 2025-03-10 16:46:07
LastEditors: ChZheng
Description:
FilePath: /ABTest/ABTestProxy/ABTestProxy/service.py
'''
# ---------------------- service.py ----------------------
from config import config
from clients import V1Client, V2Client
from adapters import V1Adapter, V2Adapter
from typing import Dict
class ABTestService:
    def __init__(self):
        self._version = 'V2'  # 默认版本
        self._clients = {'v1': V1Client(), 'v2': V2Client()}
        self._adapters = {'v1': V1Adapter(), 'v2': V2Adapter()}
    def _setup_components(self, params: Dict):
        """统一初始化组件"""
        version = params.get('version', self._version).upper()
        if version not in ['v1', 'v2']:
            raise ValueError(f"Invalid version: {version}")
        print(f"当前版本: {version}, 适配器类型: {type(self._adapters[version])}")  # 调试输出
        self._client = self._clients[version]
        self._adapter = self._adapters[version]
        return self

    def create_experiment(self, params: Dict) -> Dict:
        self._setup_components(params)
        converted_params = self._adapter.convert_create_experiment_request(params)
        raw_response = self._client.create_experiment(converted_params)
        return self._adapter.convert_create_experiment_response(raw_response)

    def get_experiment_details(self, params: Dict) -> Dict:
        self._setup_components(params)
        converted_params = self._adapter.convert_get_experiment_details_request(params)
        raw_response = self._client.get_experiment_details(converted_params)
        return self._adapter.convert_get_experiment_details_response(raw_response)

    def generate_report(self, params: Dict) -> Dict:
        self._setup_components(params)
        converted_params = self._adapter.convert_generate_report_request(params)
        raw_response = self._client.generate_report(converted_params)
        return self._adapter.convert_generate_report_response(raw_response)

    def modify_experiment_status(self, params: Dict) -> Dict:
        self._setup_components(params)
        converted_params = self._adapter.convert_modify_experiment_status_request(params)
        raw_response = self._client.modify_experiment_status(converted_params)
        return self._adapter.convert_modify_experiment_status_response(raw_response)

    def list_available_metrics(self, params: Dict) -> Dict:
        self._setup_components(params)
        converted_params = self._adapter.convert_list_available_metrics_request(params)
        raw_response = self._client.list_available_metrics(converted_params)
        return self._adapter.convert_list_available_metrics_response(raw_response)

    def list_mutex_groups(self, params: Dict) -> Dict:
        self._setup_components(params)
        converted_params = self._adapter.convert_list_mutex_groups_request(params)
        raw_response = self._client.list_mutex_groups(converted_params)
        return self._adapter.convert_list_mutex_groups_response(raw_response)
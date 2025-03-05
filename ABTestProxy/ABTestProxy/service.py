'''
Author: ChZheng
Date: 2025-03-05 15:12:03
LastEditTime: 2025-03-05 15:12:04
LastEditors: ChZheng
Description:
FilePath: /ABTest/ABTestProxy/service.py
'''
# ---------------------- service.py ----------------------
from config import config
from clients import V1Client, V2Client
from adapters import V1Adapter, V2Adapter
from typing import Dict
class ABTestService:
    """统一服务入口"""
    def __init__(self):
        self.client = self._get_client()
        self.adapter = self._get_adapter()

    def _get_client(self):
        return V1Client() if config.RUNTIME_MODE == 'V1' else V2Client()

    def _get_adapter(self):
        return V1Adapter() if config.RUNTIME_MODE == 'V1' else V2Adapter()


    def create_experiment(self, params: Dict) -> Dict:
        converted_params = self.adapter.convert_create_experiment_request(params)
        raw_response = self.client.create_experiment(converted_params)
        return self.adapter.convert_create_experiment_response(raw_response)

    def get_experiment_details(self, params: Dict) -> Dict:
        converted_params = self.adapter.convert_get_experiment_details_request(params)
        raw_response = self.client.get_experiment_details(converted_params)
        return self.adapter.convert_get_experiment_details_response(raw_response)

    def generate_report(self, params: Dict) -> Dict:
        converted_params = self.adapter.convert_generate_report_request(params)
        raw_response = self.client.generate_report(converted_params)
        return self.adapter.convert_generate_report_response(raw_response)

    def modify_experiment_status(self, params: Dict) -> Dict:
        converted_params = self.adapter.convert_modify_experiment_status_request(params)
        raw_response = self.client.modify_experiment_status(converted_params)
        return self.adapter.convert_modify_experiment_status_response(raw_response)

    def list_available_metrics(self, params: Dict) -> Dict:
        converted_params = self.adapter.convert_list_available_metrics_request(params)
        raw_response = self.client.list_available_metrics(converted_params)
        return self.adapter.convert_list_available_metrics_response(raw_response)

    def list_mutex_groups(self, params: Dict) -> Dict:
        converted_params = self.adapter.convert_list_mutex_groups_request(params)
        raw_response = self.client.list_mutex_groups(converted_params)
        return self.adapter.convert_list_mutex_groups_response(raw_response)
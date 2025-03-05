'''
Author: ChZheng
Date: 2025-02-26 06:22:35
LastEditTime: 2025-03-05 15:14:33
LastEditors: ChZheng
Description:
FilePath: /ABTest/ABTestProxy/proxy.py
'''
# ---------------------- proxy.py ----------------------
from typing import Dict, Any
from interfaces import IApiClient, IAdapter  # 假设已有这些接口定义

class ABTestProxy:
    """增强的代理服务"""

    def __init__(self, client: IApiClient, adapter: IAdapter):
        """
        初始化代理服务
        :param client: 具体版本的客户端实例（V1Client/V2Client）
        :param adapter: 协议适配器实例
        """
        self.client = client
        self.adapter = adapter

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
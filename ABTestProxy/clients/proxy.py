'''
Author: ChZheng
Date: 2025-02-13 14:33:49
LastEditTime: 2025-02-18 15:21:59
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/ABTestProxy/ABTestProxy/clients/proxy.py
'''

# # ================== 客户端模块 ==================
# [ABTestProxy/clients/proxy.py]
# |- ABTestProxy
#    |- _create_proxy_method

import inspect
from typing import Dict
class ABTestProxy:
    # 显式声明V2到V1的映射关系（Key: V2接口名, Value: V1方法名）
    _API_MAPPINGS = {
        'create_experiment': 'create_experiment',
        'get_experiment_details': 'get_flight_config',
        'generate_report': 'get_experiment_report',
        'modify_experiment_status': 'update_flight_status',
        'list_available_metrics': 'get_metric_list',
        'list_mutex_groups': 'get_mutex_group_list'
    }

    def __init__(self, v1_client, mapper):
        self.v1_client = v1_client
        self.mapper = mapper

        # 动态注册所有接口方法
        for v2_method, v1_method in self._API_MAPPINGS.items():
            setattr(self, v2_method, self._create_proxy_method(v1_method))

    def _create_proxy_method(self, v1_method_name: str):
        """创建代理方法工厂"""
        def proxy_method(v2_request: Dict) -> Dict:
            try:
                # 加载字段映射配置（使用V2方法名）
                req_map = self.mapper.load_mapping(v2_method_name, 'request')
                res_map = self.mapper.load_mapping(v2_method_name, 'response')

                # 转换请求参数
                v1_params = self.mapper.transform(v2_request, req_map)

                # 调用V1方法
                v1_response = getattr(self.v1_client, v1_method_name)(**v1_params)

                # 转换响应结果
                return {
                    "code": 200,
                    "message": "success",
                    "data": self.mapper.transform(v1_response.get('data', {}), res_map)
                }
            except Exception as e:
                return {
                    "code": 500,
                    "message": f"代理处理错误: {str(e)}",
                    "data": None
                }

        # 获取当前V2方法名（通过闭包捕获）
        v2_method_name = inspect.currentframe().f_back.f_locals['v2_method']
        proxy_method.__name__ = v2_method_name
        return proxy_method
'''
Author: ChZheng
Date: 2025-02-26 06:57:14
LastEditTime: 2025-02-28 17:12:54
LastEditors: ChZheng
Description:
FilePath: /ABTest/ABTestProxy/ABTestProxy/adapters.py
'''
# ---------------------- adapters.py ----------------------
from interfaces import IAdapter
from typing import Dict
class V1Adapter(IAdapter):
    """增强的V1协议适配器"""

    @staticmethod
    def convert_create_experiment_request(params: Dict) -> Dict:
        """V1->V2 创建实验参数转换"""
        return {
            "flight_name" : params["name"],
            "duration":params["duration"],
            "hash_strategy":"ssid",
            "app_id":params["app_id"],
        }

    @staticmethod
    def convert_create_experiment_response(response: Dict) -> Dict:
        """V2->V1 创建实验响应转换"""
        return response

    @staticmethod
    def convert_get_experiment_details_request(params: Dict) -> Dict:
        """V1->V2 查询实验详情参数转换"""
        return {
            "flight_id": params["experiment_id"],
            "is_duplicate": False
        }

    @staticmethod
    def convert_get_experiment_details_response(response: Dict) -> Dict:

        return {
            "code":200,
            "data": {
                "id": 3799,
                "name": "实时指标报告测试",
                "start_ts": "2020-07-08 11:39:02",
                "end_ts": "2021-07-08 11:39:02",
                "owner": "203870",
                "description": "",
                "status": 1,
                "type": "client",
                "mode": 1,
                "layer": {
                "name": "互斥组1",
                "status": 1,
                "description": "LS的测试场景五实验时创建时默认层",
                "type": "NULL"
                },
                "version_resource": 1.0,
                "versions": [
                {
                    "id": 8572,
                    "name": "对照版本",
                    "type": 0,
                    "config": {
                    "hello12341": False
                    },
                    "description": "",
                    "weight": 30
                },
                ...
                ],
                "metrics": [
                {
                    "id": 10065,
                    "name": "测试指标",
                    "metric_description": "测试指标描述",
                    "type": "major",
                    "support_conf": True,
                    "offline": False,
                    "dsl": {
                    "queries": [
                        {
                        "show_label": "A",
                        "event_type": "origin",
                        "show_name": "活跃均次（pv/au）",
                        "event_name": "predefine_pageview",
                        "filters": [
                            {
                            "property_operation": "!=",
                            "property_type": "event_param",
                            "property_name": "title",
                            "property_values": [
                                "这是一个title"
                            ]
                            }
                        ]
                        },
                        ...
                    ],
                    "event_relation": "A*1"
                    },
                    "composed": False
                }
                ],
                "features": {
                "id": -1,
                "name": "",
                "key": ""
                },
                "filter": "",
                "whitelist": [
                {
                    "对照版本": [
                    {
                        "ssids": ["bbc33321-4352-4b95-91d1-lishanlishanlishan"],
                        "id": 81,
                        "is_deleted": False,
                        "name": "李珊",
                        "description": "",
                        "tags": []
                    }
                    ]
                }
                ]
            },
            "message": "success"
        }



    @staticmethod
    def _convert_status(v2_status: str) -> int:
        """V2状态码转V1状态码"""
        status_map = {
            "RUNNING": 1,
            "STOPPED": 0,
            "DRAFT": 4
        }
        return status_map.get(v2_status, -1)

    @staticmethod
    def convert_generate_report_request(params: Dict) -> Dict:
        """V1->V2 报告请求转换"""
        return {
            "flight_id": params["id"],
            "metrics": params["metrics"],
            "start_time": params["start_time"],
            "end_time": params["end_time"]
        }
    @staticmethod
    def convert_generate_report_response(response: Dict) -> Dict:
        """V2->V1 报告响应转换"""
        return response

    @staticmethod
    def convert_modify_experiment_status_request(params: Dict) -> Dict:
        """V1->V2 修改实验状态请求转换"""
        return {
            "flight_id": params["id"],
            "status": params["status"]
        }
    @staticmethod
    def convert_modify_experiment_status_response(response: Dict) -> Dict:
        """V2->V1 修改实验状态响应转换"""
        return response
    @staticmethod
    def convert_list_available_metrics_request(params: Dict) -> Dict:
        """V1->V2 查询可用指标请求转换"""
        return params
    @staticmethod
    def convert_list_available_metrics_response(response: Dict) -> Dict:
        """V2->V1 查询可用指标响应转换"""
        return response
    def convert_list_mutex_groups_request(params: Dict) -> Dict:
        """V1->V2 查询互斥组请求转换"""
        return params
    def convert_list_mutex_groups_response(response: Dict) -> Dict:
        """V2->V1 查询互斥组响应转换"""
        return response


class V2Adapter(IAdapter):
    """V2透传适配器"""
    @staticmethod
    def convert_request(params: Dict) -> Dict:
        return params

    @staticmethod
    def convert_response(response: Dict) -> Dict:
        return response
'''
Author: ChZheng
Date: 2025-02-26 06:57:14
LastEditTime: 2025-03-06 17:19:24
LastEditors: ChZheng
Description:
FilePath: /ABTest/ABTestProxy/ABTestProxy/adapters.py
'''
# ---------------------- adapters.py ----------------------

from typing import Dict
class V1Adapter():
    """增强的V1协议适配器"""

    @staticmethod
    def convert_create_experiment_request(params: Dict) -> Dict:
        """V1->V2 创建实验参数转换"""
        params["hash_strategy"] = "ssid"
        return params

    @staticmethod
    def convert_create_experiment_response(response: Dict) -> Dict:
        """V2->V1 创建实验响应转换"""
        return response

    @staticmethod
    def convert_get_experiment_details_request(params: Dict) -> Dict:
        """V1->V2 查询实验详情参数转换"""
        params["is_duplicate"] = False
        return params

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
                # ...
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
    def convert_generate_report_request(params: Dict) -> Dict:
        """V1->V2 报告请求转换"""
        params["trace_data"] = params.get("trace_data", "")
        return params
    @staticmethod
    def convert_generate_report_response(response: Dict) -> Dict:
        """V2->V1 报告响应转换"""
        return {
        "code": 200,
        "data": {
            "report_type": "day", # 报告类型,day:天 hour:小时 five_minute:5分钟
            "versions": [
            {
                "id": 8572, # 版本ID
                "name": "对照版本", # 版本名称
                "config": {
                "hello12341": False
                },
                "type": 0, # 版本类型,0:对照版本 1:实验版本
                "weight": 0  # 版本权重
            },
            ],
            "metrics": [
            {
                "id": 10065,
                "name": "测试指标",
                "metric_description": "测试指标描述",
                "type": "major", # 指标类型,major:核心 normal:普通
                "support_conf": true,
                "offline": False,
                "composed": False
            },
            ...
            ],
            "start_ts": 1594179542, # 实验开始时间
            "end_ts": 1597247999, # 实验结束时间
            "user_data": {
            "8572": 415248, # 实验总进组人数
            "8573": 415261
            },
            "calculation_results": {
            "10013": { # 指标ID
                "8572": { # 实验版本ID,以下类似数字代表该实验相对于另一实验计算得出的值
                "m": 1.367, #
                "p": {
                    "8573": -1 # -1为不存在,小于0.05则置信
                },
                "change": 0.09640731971910832, # 变化值
                "change_rate": {
                    "8573": -0.00053 # 变化率
                },
                "conf_interval": {
                    "8573": [0,0] # 置信区间
                },
                "half_interval": {
                    "8573": 0 # 置信区间中点
                },
                "confidence": {
                    "8573": 3 # 置信情况,1:正向 2:负向 3:不置信 4:新开实验
                            # 5:数据待更新 6:置信度无法计算 7:没有用户进组 8:已暂停
                },
                "mde": 0.012623757553642818 # 最小观测差值MDE(minimum detectable effect)
                },
                # ...
            },
            # ...
            }
        },
        "message": "success"
        }



    @staticmethod
    def convert_modify_experiment_status_request(params: Dict) -> Dict:
        """V1->V2 修改实验状态请求转换"""
        return {
            "flight_id": params["experiment_id"],
            "action": params["action"]
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
        params["need_default"] = False
        return params
    def convert_list_mutex_groups_response(response: Dict) -> Dict:
        """V2->V1 查询互斥组响应转换"""
        return response


class V2Adapter():
    """V2透传适配器"""
    @staticmethod
    def convert_request(params: Dict) -> Dict:
        return params

    @staticmethod
    def convert_response(response: Dict) -> Dict:
        return response
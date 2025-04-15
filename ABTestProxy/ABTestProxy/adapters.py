'''
Author: ChZheng
Date: 2025-02-26 06:57:14
LastEditTime: 2025-03-10 10:48:19
LastEditors: ChZheng
Description:
FilePath: /ABTest/ABTestProxy/ABTestProxy/adapters.py
'''
import time
# ---------------------- adapters.py ----------------------

from typing import Dict


class V1Adapter():
    """增强的V1协议适配器"""

    def convert_create_experiment_request(self, params: Dict) -> Dict:
        """V1->V2 创建实验参数转换"""
        params["hash_strategy"] = "ssid"
        return params

    def convert_create_experiment_response(self, response: Dict) -> Dict:
        """V2->V1 创建实验响应转换"""
        return response

    def convert_get_experiment_details_request(self, params: Dict) -> Dict:
        """V1->V2 查询实验详情参数转换"""
        params["is_duplicate"] = False
        return params

    def convert_get_experiment_details_response(self, response: Dict) -> Dict:
        if response["code"]==200
            return response
        return {
            "code": 200,
            "data": {
                "id":response["data"]["id"],
                "name": response["data"]["flight_name"],
                "start_ts": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(response["data"]["start_time"])),
                "end_ts": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(response["data"]["end_time"])),
                "owner": response["data"]["owner"],
                "description": response["data"]["description"],
                "status": response["data"]["status"],
                "type": "client",
                "mode": response["data"]["mode"],
                "layer":{
                    "name": response["data"]["layer_info"]["layer_name"],
                    "status": response["data"]["layer_info"]["layer_status"],
                    "description": "",
                    "type": response["data"]["layer_info"]["type"],
                },
                "version_resource": response["data"]["version_resource"],
                "versions":[
                    {
                        "id": v["id"],
                        "name": v["name"],
                        "type": v["type"],
                        "config": v["config"],
                        "description": v["description"],
                        "weight": v["weight"],
                    }
                for v in response["data"]["versions"]
                ],
                "metrics":[
                    {
                        "id": m["metrics"][0]["id"],
                        "name": m["metrics"][0]["name"],
                        "metric_description": m["metrics"][0]["description"],
                        "type": m["metrics"][0]["type"],

                    }
                for m in response["data"]["metrics"]
                ],
                "whitelist":[

                ],
            },
            "message":"success"
        }

    def convert_generate_report_request(self, params: Dict) -> Dict:
        """V1->V2 报告请求转换"""
        params["trace_data"] = params.get("trace_data", "")
        return params

    def convert_generate_report_response(self, response: Dict) -> Dict:
        """V2->V1 报告响应转换"""
        return response

    def convert_modify_experiment_status_request(self, params: Dict) -> Dict:
        """V1->V2 修改实验状态请求转换"""
        return {
            "flight_id": params["experiment_id"],
            "action": params["action"]
        }

    def convert_modify_experiment_status_response(self, response: Dict) -> Dict:
        """V2->V1 修改实验状态响应转换"""
        return response

    def convert_list_available_metrics_request(self, params: Dict) -> Dict:
        """V1->V2 查询可用指标请求转换"""
        return params

    def convert_list_available_metrics_response(self, response: Dict) -> Dict:
        """V2->V1 查询可用指标响应转换"""
        return response

    def convert_list_mutex_groups_request(self, params: Dict) -> Dict:
        """V1->V2 查询互斥组请求转换"""
        params["need_default"] = False
        return params

    def convert_list_mutex_groups_response(self, response: Dict) -> Dict:
        """V2->V1 查询互斥组响应转换"""
        return response


class V2Adapter():
    """V2透传适配器"""

    def convert_create_experiment_request(self, params: Dict) -> Dict:
        """V2不需要转换，直接透传"""
        return params

    def convert_create_experiment_response(self, response: Dict) -> Dict:
        return response

    def convert_get_experiment_details_request(self, params: Dict) -> Dict:
        return params

    def convert_get_experiment_details_response(self, response: Dict) -> Dict:
        return response

    def convert_generate_report_request(self, params: Dict) -> Dict:
        return params

    def convert_generate_report_response(self, response: Dict) -> Dict:
        return response

    def convert_modify_experiment_status_request(self, params: Dict) -> Dict:
        return params

    def convert_modify_experiment_status_response(self, response: Dict) -> Dict:
        return response

    def convert_list_available_metrics_request(self, params: Dict) -> Dict:
        return params

    def convert_list_available_metrics_response(self, response: Dict) -> Dict:
        return response

    def convert_list_mutex_groups_request(self, params: Dict) -> Dict:
        return params

    def convert_list_mutex_groups_response(self, response: Dict) -> Dict:
        return response

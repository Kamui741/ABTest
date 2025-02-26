'''
Author: ChZheng
Date: 2025-02-26 06:57:14
LastEditTime: 2025-02-26 07:45:23
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/ABTestProxy/ABTestProxy/adapters.py
'''
# ---------------------- adapters.py ----------------------
class V1Adapter(IAdapter):
    """增强的V1协议适配器"""

    @staticmethod
    def convert_create_request(params: Dict) -> Dict:
        """V1->V2 创建实验参数转换"""
        return {
            "app_id": params["app_id"],
            "name": params["flight_name"],  # 字段名转换
            "mode": 1,  # 固定值
            "endpoint_type": params.get("endpoint_type", 1),
            "duration": params["duration"],
            "major_metric": params["major_metric"],
            "metrics": params["metrics"],
            "versions": [{
                "type": v["type"],
                "name": v["name"],
                "config": v["config"]
            } for v in params["versions"]],
            "layer_info": params.get("layer_info")
        }

    @staticmethod
    def convert_create_response(response: Dict) -> Dict:
        """V2->V1 创建实验响应转换"""
        return {
            "code": response.get("code", 200),
            "message": response.get("message", "success"),
            "data": response.get("data")  # 直接返回V2的实验ID
        }

    @staticmethod
    def convert_detail_response(response: Dict) -> Dict:
        """V2->V1 详情响应转换"""
        v2_data = response.get("data", {})
        return {
            "id": v2_data.get("id"),
            "name": v2_data.get("name"),
            "status": v2_data.get("status"),
            "versions": [{
                "id": v["id"],
                "name": v["name"],
                "type": v["type"]
            } for v in v2_data.get("versions", [])]
        }

    @staticmethod
    def convert_report_response(response: Dict) -> Dict:
        """V2->V1 报告响应转换"""
        v2_data = response.get("data", {})
        return {
            "calculation_results": v2_data.get("calculation_results", {}),
            "metrics": [{
                "id": m["id"],
                "name": m["name"]
            } for m in v2_data.get("metrics", [])]
        }

    @staticmethod
    def convert_metric_response(response: Dict) -> Dict:
        """V2->V1 指标列表响应转换"""
        v2_data = response.get("data", {})
        return {
            "metrics": [{
                "id": m["id"],
                "name": m["name"],
                "is_required": 0 if m.get("is_support_major", False) else 1,
                "metric_type": m.get("type", "normal"),
                "description": m.get("description", "")
            } for m in v2_data.get("metrics", [])],
            "page_info": {
                "current_page": v2_data.get("page", {}).get("current_page", 1),
                "total_pages": v2_data.get("page", {}).get("total_page", 1),
                "total_items": v2_data.get("page", {}).get("total_items", 0)
            }
        }

    @staticmethod
    def convert_group_response(response: Dict) -> Dict:
        """V2->V1 互斥组列表响应转换"""
        v2_data = response.get("data", [])
        return {
            "groups": [{
                "id": g["id"],
                "name": g["name"],
                "available_traffic": g.get("available_traffic", 0),
                "layer_type": "client" if g.get("type") == "client" else "server",
                "description": g.get("description", "")
            } for g in v2_data],
            "page_info": {
                "current_page": 1,  # V2分页参数需根据实际返回补充
                "total_pages": 1,
                "total_items": len(v2_data)
            }
        }

class V2Adapter(IAdapter):
    """V2透传适配器"""
    @staticmethod
    def convert_request(params: Dict) -> Dict:
        return params

    @staticmethod
    def convert_response(response: Dict) -> Dict:
        return response
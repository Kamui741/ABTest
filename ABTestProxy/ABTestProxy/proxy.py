'''
Author: ChZheng
Date: 2025-02-26 06:22:35
LastEditTime: 2025-02-26 07:19:01
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/ABTestProxy/ABTestProxy/proxy.py
'''
# ---------------------- proxy.py ----------------------
class ABTestProxy:
    """增强的代理服务"""

    def create_experiment(self, params: Dict) -> Dict:
        converted_params = self.adapter.convert_create_request(params)
        raw_response = self.client.create_experiment(converted_params)
        return self.adapter.convert_create_response(raw_response)

    def get_experiment_details(self, params: Dict) -> Dict:
        exp_id = params["experiment_id"]
        raw_response = self.client.get_experiment_details(exp_id)
        return self.adapter.convert_detail_response(raw_response)

    def generate_report(self, params: Dict) -> Dict:
        converted_params = {
            "app_id": params["app_id"],
            "experiment_id": params["experiment_id"],
            "report_type": params["report_type"],
            "start_ts": params["start_ts"],
            "end_ts": params["end_ts"]
        }
        raw_response = self.client.generate_report(converted_params)
        return self.adapter.convert_report_response(raw_response)

    def modify_experiment_status(self, params: Dict) -> Dict:
        return self.client.modify_experiment_status(
            params["experiment_id"],
            params["action"]
        )

    def list_available_metrics(self, params: Dict) -> Dict:
        raw_response = self.client.list_available_metrics(params)
        return {
            "metrics": [{
                "id": m["id"],
                "name": m["name"]
            } for m in raw_response.get("data", {}).get("metrics", [])]
        }

    def list_mutex_groups(self, params: Dict) -> Dict:
        raw_response = self.client.list_mutex_groups(params)
        return {
            "groups": [{
                "id": g["id"],
                "name": g["name"]
            } for g in raw_response.get("data", [])]
        }
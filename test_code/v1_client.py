'''
Author: ChZheng
Date: 2025-02-26 08:51:59
LastEditTime: 2025-03-13 10:04:08
LastEditors: ChZheng
Description:
FilePath: /ABTest/test_code/v1_client.py
'''
# ---------------------- clients/v1_client.py ----------------------

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class V1Client(IApiClient):
    """V1客户端完整实现"""
    base_url = config.BASE_URLS['V1']
    def create_experiment(self, params: Dict) -> Dict:
        """创建实验（参数需适配V1格式）"""
        flight_name=params['flight_name']
        duration=params['duration']
        hash_strategy=params.get('hash_strategy', 'ssid')
        app_id=params['app_id']
        """
        创建实验的完整流程,包含四次连续的 POST 请求。
        """
        # Step 1: 初始化实验草稿
        step1_url = f"{self.base_url}/api/step1"
        step1_payload = {
            "flight_name": flight_name,
            "duration": duration,
            "hash_strategy": hash_strategy,
            "expiration_remind": True,
            "longrun_remind": True,
            "report_mode": 0,
            "mode": 1,
            "app": app_id
        }
        step1_response = post_data(step1_url, json_data=step1_payload)
        if not step1_response:
            logger.error(" 第一步请求失败")
            return None
        draft_id = step1_response.get("data",{}).get("draft_id")

        # Step 2: 配置实验指标
        step2_url = f"{self.base_url}/api/step2"
        step2_payload = {
            "major_metric": "1545",
            "metrics": "1545",
            "app": app_id,
            "draft_id": draft_id
        }
        step2_response = post_data(step2_url, json_data=step2_payload)
        if not step2_response:
            logger.error(" 第二步请求失败")
            return None

        # Step 3: 配置实验版本
        version_control_id = str(uuid.uuid4())
        version_experiment_id = str(uuid.uuid4())
        step3_url = f"{self.base_url}/api/step3"
        step3_payload = {
            "versions": f"""[{{"type": 0, "id": "{version_control_id}", "label": "对照版本", "name":"对照版本","users":[],"weight":50,"config":{{"3":"3"}}}},{{"type": 1, "id": "{version_experiment_id}", "label": "实验版本", "name":"实验版本","users":[],"weight":50,"config":{{"3":"3"}}}}""",
            "app": app_id,
            "draft_id": draft_id
        }
        step3_response = post_data(step3_url, json_data=step3_payload)
        if not step3_response:
            logger.error(" 第三步请求失败")
            return None

        # Step 4: 提交实验草稿
        step4_url = f"{self.base_url}/api/step4"
        step4_payload = {
            "skip_verification": False,
            "is_start": True,
            "distribute": True,
            "versions": f"""[{{"type": 0, "id": "{version_control_id}", "label": "对照版本", "name":"对照版本","users":[],"weight":50,"config":{{"3":"3"}}}},{{"type": 1, "id": "{version_experiment_id}", "label": "实验版本", "name":"实验版本","users":[],"weight":50,"config":{{"3":"3"}}}}""",
            "filter_rule":"[]",
            "layer_info":f"""{{"layer_id": -1,"version_resource":1}}""",
            "app": app_id,
            "draft_id": draft_id,
            "version_freeze_status":0
        }
        step4_response = post_data(step4_url, json_data=step4_payload)
        if not step4_response:
            logger.error(" 第四步请求失败")
            return None

        return step4_response


    def get_experiment_details(self, params: Dict) -> Dict:
        """获取实验详情"""
        flight_id=params["flight_id"]
        is_duplicate=params["is_duplicate"]
        url = f"{self.base_url}/datatester/api/v2/flight/view"
        params = {
            "flight_id": flight_id,
            "is_duplicate": str(is_duplicate).lower()
        }
        return fetch_data(url, params=params)

    def generate_report(self, params: Dict) -> Dict:
        """生成实验报告"""

        app_id=params['app_id'],
        flight_id=params['flight_id'],
        report_type=params['report_type'],
        start_ts=params['start_ts'],
        end_ts=params['end_ts'],
        trace_data=params['trace_data']

        url = f"{self.base_url}/datatester/api/v2/flight/view"
        params = {
            "app_id": app_id,
            "flight_id": flight_id,
            "report_type": report_type,
            "start_ts": start_ts,
            "end_ts": end_ts,
            "trace_data": trace_data
            }
        return fetch_data(url, params=params)

    def modify_experiment_status(self, params: Dict) -> Dict:
        """修改实验状态"""

        flight_id=params['flight_id'],
        action=params['action']
        if action not in ["launch", "stop"]:
            logger.error(" Invalid action. Use 'launch' or 'stop'.")

        url = f"{self.base_url}/datatester/api/v2/flight/{action}"
        payload = {"flight_id": flight_id}
        return put_data(url, json_data=payload)

    def list_available_metrics(self, params: Dict) -> Dict:
        """获取指标列表"""

        app_id=params['app_id'],
        keyword=params.get('keyword', ''),
        status=params.get('status', 1),
        is_required=params.get('is_required', -1),
        need_page=params.get('need_page', 1),
        page_size=params.get('page_size', 10)

        url = f"{self.base_url}/datatester/api/v2/app/{app_id}/metric/list"
        params = {
            "keyword": keyword,
            "status": status,
            "is_required": is_required,
            "need_page": need_page,
            "page_size": page_size
        }
        return fetch_data(url, params=params)

    def list_mutex_groups(self, params: Dict) -> Dict:
        """获取互斥组列表"""

        app_id=params['app_id'],
        keyword=params.get('keyword', ''),
        status=params.get('status', 1),
        need_page=params.get('need_page', 1),
        page_size=params.get('page_size', 10),
        page=params.get('page', 1),
        need_default=params.get('need_default', False)

        url = f"{self.base_url}/datatester/api/v2/app/{app_id}/layer/list"
        params = {
            "keyword": keyword,
            "status": status,
            "need_page": need_page,
            "page_size": page_size,
            "page": page,
            "need_default": str(need_default).lower()
        }
        return fetch_data(url, params=params)

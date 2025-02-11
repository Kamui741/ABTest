import requests
import os
import logging
from typing import Optional, Dict, Any

import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

login_url = "http://localhost:8000/api/v1/login"
target_url = "http://localhost:8000/api/v1/target"
username = os.getenv("USERNAME", "admin")
password = os.getenv("PASSWORD", "admin123")

session_file = "sessionid.txt"

class SessionManager:
    def __init__(self, login_url: str, session_file: str):
        self.login_url = login_url
        self.session_file = session_file

    def save_sessionid(self, sessionid: str):
        with open(self.session_file, "w") as f:
            f.write(sessionid)
        logger.info(f"Session ID saved to {self.session_file}")

    def load_sessionid(self) -> Optional[str]:
        if not os.path.exists(self.session_file):
            logger.warning(f"Session ID file {self.session_file} not found,     attempting to log in.")
            return self.login()  # 直接登录并获取新的 sessionid

        try:
            with open(self.session_file, "r") as f:
                sessionid = f.read().strip()
                logger.info(f"Session ID loaded from {self.session_file}")
                return sessionid
        except Exception as e:
            logger.error(f"❌ Error loading session ID file: {e}")
            return self.login()  # 读取失败时重新登录

    def _handle_response(self, response: requests.Response) -> Optional[Dict[str, Any]]:
        """ 统一处理 HTTP 响应 """
        try:
            response_data = response.json()
        except requests.JSONDecodeError:
            logger.error(f"❌ Failed to parse JSON response from {response.url}")
            return None

        if response.status_code == 200 and response_data.get("code") == 200:
            logger.info(f"✅ Request to {response.url} succeeded")
            return response_data
        else:
            logger.error(f"❌ Request failed, status: {response.status_code}, message: {response_data.get('message', 'Unknown error')}")
            return None

    def login(self) -> Optional[str]:
        """ 登录并获取 session ID """
        try:
            response = requests.post(self.login_url, json={"email": username, "password": password})
            response_data = self._handle_response(response)
            if response_data:
                sessionid = response.cookies.get("sessionid")
                if sessionid:
                    self.save_sessionid(sessionid)
                    return sessionid
                logger.warning("Login successful but session ID not found in response cookies")
        except requests.RequestException as e:
            logger.error(f"❌ Login request failed: {e}")
        return None

    def validate_session(self, sessionid: str, test_url: str) -> bool:
        """ 验证 session ID 是否有效 """
        headers = {"Cookie": f"sessionid={sessionid}"}
        try:
            response = requests.get(test_url, headers=headers)
            return bool(self._handle_response(response))
        except requests.RequestException as e:
            logger.error(f"❌ Failed to validate session: {e}")
            return False

    def get_valid_session(self, test_url: str) -> Optional[str]:
        """ 获取有效的 session ID """
        sessionid = self.load_sessionid()
        if sessionid and self.validate_session(sessionid, test_url):
            return sessionid
        return self.login()

def send_request(method: str, url: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None):
    """ 发送 HTTP 请求 """
    session_manager = SessionManager(login_url, session_file)
    sessionid = session_manager.get_valid_session(target_url)
    if not sessionid:
        logger.error("❌ Failed to get a valid session")
        return None

    headers = {"Cookie": f"sessionid={sessionid}"}
    if json_data:
        headers["Content-Type"] = "application/json"

    try:
        response = requests.request(method, url, headers=headers, data=data, json=json_data, params=params)
        return session_manager._handle_response(response)
    except requests.RequestException as e:
        logger.error(f"❌ Error occurred while making {method} request: {e}")
        return None

def fetch_data(url: str, params: Optional[Dict[str, Any]] = None):
    return send_request("GET", url, params=params)

def post_data(url: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None):
    return send_request("POST", url, data=data, json_data=json_data)

def put_data(url: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None):
    return send_request("PUT", url, data=data, json_data=json_data)

#######功能函数########
def create_experiment(flight_name: str, duration: int, hash_strategy: str, app_id: int) -> Optional[Dict[str, Any]]:
    """
    创建实验的完整流程，包含四次连续的 POST 请求。
    """

    # Step 1: 初始化实验草稿
    step1_url = "http://28.4.136.142/api/step1"
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
        logger.error("❌ 第一步请求失败")
        return None
    draft_id = step1_response.get("data",{}).get("draft_id")

    # Step 2: 配置实验指标
    step2_url = "http://28.4.136.142/api/step2"
    step2_payload = {
        "major_metric": "1545",
        "metrics": "1545",
        "app": app_id,
        "draft_id": draft_id
    }
    step2_response = post_data(step2_url, json_data=step2_payload)
    if not step2_response:
        logger.error("❌ 第二步请求失败")
        return None

    # Step 3: 配置实验版本
    version_control_id = str(uuid.uuid4())
    version_experiment_id = str(uuid.uuid4())
    step3_url = "http://28.4.136.142/api/step3"
    step3_payload = {
        "versions": f"""[{{"type": 0, "id": "{version_control_id}", "label": "对照版本", "name":"对照版本"，"users":[],"weight":50,"config":{{"3":"3"}}}},{{"type": 1, "id": "{version_experiment_id}", "label": "实验版本", "name":"实验版本"，"users":[],"weight":50,"config":{{"3":"3}}}}""",
        "app": app_id,
        "draft_id": draft_id
    }
    step3_response = post_data(step3_url, json_data=step3_payload)
    if not step3_response:
        logger.error("❌ 第三步请求失败")
        return None

    # Step 4: 提交实验草稿
    step4_url = "http://28.4.136.142/api/step4"
    step4_payload = {
        "skip_verificationh": False,
        "is_start": True,
        "distribute": True,
        "versions": f"""[{{"type": 0, "id": "{version_control_id}", "label": "对照版本", "name":"对照版本"，"users":[],"weight":50,"config":{{"3":"3"}}}},{{"type": 1, "id": "{version_experiment_id}", "label": "实验版本", "name":"实验版本"，"users":[],"weight":50,"config":{{"3":"3}}}}""",
        "filter_rule":"[]",
        "layer_info":f"""{{"layer_id": -1,"version_resource":1}}""",
        "app": app_id,
        "draft_id": draft_id,
        "version_freeze_status":0
    }
    step4_response = post_data(step4_url, json_data=step4_payload)
    if not step4_response:
        logger.error("❌ 第四步请求失败")
        return None

    return step4_response

def get_flight_config(flight_id: int, is_duplicate: bool = False):
    """ 获取实验配置 """
    url = f"https://28.4.136.142/datatester/api/v2/flight/view"
    params = {"flight_id": flight_id, "is_duplicate": str(is_duplicate).lower()}
    return fetch_data(url, params=params)


def get_metric_list(app_id: int, keyword: str = "", status: int = 1, is_required: int = -1, need_page: int = 1, page_size: int = 10):
    """ 获取指标列表 """
    url = f"https://28.4.136.142/datatester/api/v2/app/{app_id}/metric/list"
    params = {
        "keyword": keyword,
        "status": status,
        "is_required": is_required,
        "need_page": need_page,
        "page_size": page_size
    }
    return fetch_data(url, params=params)


def update_flight_status(flight_id: int, action: str):
    """ 修改实验状态 (启动/停止) """
    if action not in ["launch", "stop"]:
        logger.error("❌ Invalid action. Use 'launch' or 'stop'.")
        return None

    url = f"https://28.4.136.142/datatester/api/v2/flight/{action}"
    payload = {"flight_id": flight_id}
    return put_data(url, json_data=payload)


def get_experiment_report(app_id: int, flight_id: int, report_type: str, start_ts: int, end_ts: int, trace_data: str):
    """ 计算实验指标并返回指标报告 """
    url = f"https://28.4.136.142/datatester/api/v2/app/{app_id}/flight/{flight_id}/rich-metric-report"
    params = {
        "report_type": report_type,
        "start_ts": start_ts,
        "end_ts": end_ts,
        "traceData": trace_data
    }
    return fetch_data(url, params=params)


def get_mutex_group_list(app_id: int, keyword: str = "", status: int = 1, need_page: int = 1, page_size: int = 10, page: int = 1, need_default: bool = False):
    """ 获取互斥组列表 """
    url = f"https://28.4.136.142/datatester/api/v2/app/{app_id}/layer/list"
    params = {
        "keyword": keyword,
        "status": status,
        "need_page": need_page,
        "page_size": page_size,
        "page": page,
        "need_default": str(need_default).lower()
    }
    return fetch_data(url, params=params)


# 接口代理层程序


if __name__ == "__main__":
    # GET 请求示例
    get_url = "http://28.4.136.142/api/example_get"
    get_params = {"param1": "value1", "param2": "value2"}
    response = fetch_data(get_url, params=get_params)

    # POST 请求示例
    post_url = "http://28.4.136.142/api/example_post"
    post_json = {"key1": "value1", "key2": "value2"}
    response = post_data(post_url, json_data=post_json)

    # PUT 请求示例
    put_url = "http://28.4.136.142/api/example_put"
    put_json = {"update_key": "new_value"}
    response = put_data(put_url, json_data=put_json)

    #创建实验
    response    = create_experiment("abtest11",7,"ssid",10000305)

    # 获取实验配置 url get
    # https://28.4.136.142/datatester/api/v2/flight/view?flight_id=705&is_duplicate=false
    # 获取指标列表 get
    # https://28.4.136.142/datatester/api/v2/app/10000305/metric/list?keyword=&status=1&is_required=-1&need_page=1&page_size=10
    #修改实验状态 put
    # https://28.4.136.142/datatester/api/v2/flight/launch   payload = {"flight_id": 705}
    # https://28.4.136.142/datatester/api/v2/flight/stop   payload = {"flight_id": 705}

    #计算实验指标并返回指标报告
    # https://28.4.136.142/datatester/api/v2/app/10000305/flight/705/rich-metric-report?report_type=five_minute&start_ts=1704166400&end_ts=1704252800&traceData=cf19f8e8-9c5d-4e8a-9e6d-9a8e8e8e8e8e
    #获取互斥组列表
    # https://28.4.136.142/datatester/api/v2/app/10000305/layer/list?keyword=&status=1&need_page=1&page_size=10&page=1&need_default=false

    print(response)

    # 获取实验配置
    config = get_flight_config(flight_id=705)
    print(config)

    # 获取指标列表
    metrics = get_metric_list(app_id=10000305)
    print(metrics)

    # 启动实验
    response = update_flight_status(flight_id=705, action="launch")
    print(response)

    # 计算实验指标
    report = get_experiment_report(
        app_id=10000305,
        flight_id=705,
        report_type="five_minute",
        start_ts=1704166400,
        end_ts=1704252800,
        trace_data="cf19f8e8-9c5d-4e8a-9e6d-9a8e8e8e8e8e"
    )
    print(report)

    # 获取互斥组列表
    mutex_groups = get_mutex_group_list(app_id=10000305)
    print(mutex_groups)
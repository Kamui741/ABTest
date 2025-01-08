import requests
import os
import logging
import uuid
from typing import Optional, Dict, Any

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
logger = logging.getLogger(__name__)

# 配置
login_url = "http://28.4.136.142/api/auth/login"
target_url = "http://28.4.136.142/api/target_endpoint"
session_file = "sessionid.txt"
username = os.getenv("USERNAME", "your_username")
password = os.getenv("PASSWORD", "your_password")


class SessionManager:
    def __init__(self, login_url: str, session_file: str):
        self.login_url = login_url
        self.session_file = session_file

    def save_sessionid(self, sessionid: str) -> None:
        """保存 sessionid 到文件"""
        with open(self.session_file, "w") as f:
            f.write(sessionid)
        logger.info(f"Session ID 已保存到文件: {self.session_file}")

    def load_sessionid(self) -> Optional[str]:
        """从文件加载 sessionid"""
        if os.path.exists(self.session_file):
            with open(self.session_file, "r") as f:
                sessionid = f.read().strip()
                logger.info(f"从文件加载 Session ID: {sessionid}")
                return sessionid
        logger.warning("Session 文件不存在，需要重新登录")
        return None

    def login(self) -> Optional[str]:
        """登录系统并获取 sessionid"""
        try:
            response = requests.post(self.login_url, json={"username": username, "password": password})
            if response.status_code == 200:
                sessionid = response.cookies.get("sessionid")
                if sessionid:
                    logger.info(f"登录成功，Session ID: {sessionid}")
                    self.save_sessionid(sessionid)
                    return sessionid
                else:
                    logger.warning("登录成功，但未找到 Session ID")
            else:
                logger.error(f"登录失败，状态码: {response.status_code}, 响应: {response.text}")
        except requests.RequestException as e:
            logger.error(f"登录请求异常: {e}")
        return None

    def validate_session(self, sessionid: str, test_url: str) -> bool:
        """验证 sessionid 是否有效"""
        try:
            headers = {"Cookie": f"sessionid={sessionid}"}
            response = requests.get(test_url, headers=headers)
            if response.status_code == 200:
                logger.info("Session ID 有效")
                return True
            elif response.status_code == 401:
                logger.warning("Session ID 已失效")
                return False
            else:
                logger.error(f"验证 Session ID 失败，状态码: {response.status_code}")
        except requests.RequestException as e:
            logger.error(f"验证 Session ID 请求异常: {e}")
        return False

    def get_valid_session(self, test_url: str) -> Optional[str]:
        """获取有效的 sessionid"""
        sessionid = self.load_sessionid()
        if sessionid and self.validate_session(sessionid, test_url):
            return sessionid
        logger.warning("Session ID 无效或不存在，尝试重新登录")
        return self.login()


def fetch_data(url: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """使用有效的 Session ID 获取数据"""
    session_manager = SessionManager(login_url, session_file)
    sessionid = session_manager.get_valid_session(target_url)
    if not sessionid:
        logger.error("无法获取有效的 Session ID")
        return None

    headers = {"Cookie": f"sessionid={sessionid}"}
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            logger.info("数据请求成功")
            return response.json()
        else:
            logger.error(f"数据请求失败，状态码: {response.status_code}, 响应: {response.text}")
    except requests.RequestException as e:
        logger.error(f"请求异常: {e}")
    return None


def post_data_with_session(url: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """使用有效的 Session ID 发送 POST 请求"""
    session_manager = SessionManager(login_url, session_file)
    sessionid = session_manager.get_valid_session(target_url)
    if not sessionid:
        logger.error("无法获取有效的 Session ID")
        return None

    headers = {"Cookie": f"sessionid={sessionid}"}
    if json_data:
        headers["Content-Type"] = "application/json"

    try:
        response = requests.post(url, headers=headers, data=data, json=json_data)
        if response.status_code == 200:
            logger.info("数据提交成功")
            return response.json()
        else:
            logger.error(f"数据提交失败，状态码: {response.status_code}, 响应: {response.text}")
    except requests.RequestException as e:
        logger.error(f"请求异常: {e}")
    return None


def create_experiment(flight_name: str, duration: int, hash_strategy: str, app_id: int) -> Optional[Dict[str, Any]]:
    """
    创建实验的完整流程，包含四次连续的 POST 请求
    """
    try:
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
        step1_response = post_data_with_session(step1_url, json_data=step1_payload)
        if not step1_response:
            logger.error("❌ 第一步请求失败")
            return None
        draft_id = step1_response.get("draft_id")

        # Step 2: 配置实验指标
        step2_url = "http://28.4.136.142/api/step2"
        step2_payload = {
            "major_metric": "1545",
            "metrics": "1545",
            "app": app_id,
            "draft_id": draft_id
        }
        post_data_with_session(step2_url, json_data=step2_payload)

        # Step 3: 配置实验版本
        version_control_id = str(uuid.uuid4())
        version_experiment_id = str(uuid.uuid4())
        step3_url = "http://28.4.136.142/api/step3"
        step3_payload = {
            "versions": f"""[{{"type": 0, "id": "{version_control_id}", "label": "对照版本", "name":"对照版本"，"users":[],"weight":50,"config":{{"3":"3"}}}},{{"type": 1, "id": "{version_experiment_id}", "label": "实验版本", "name":"实验版本"，"users":[],"weight":50,"config":{{"3":"3}}}}""",
            "app": app_id,
            "draft_id": draft_id
        }
        post_data_with_session(step3_url, json_data=step3_payload)

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
        return post_data_with_session(step4_url, json_data=step4_payload)
    except Exception as e:
        logger.error(f"实验创建异常: {e}")
        return None



# 功能 1: 创建实验
def create_experiment_v3(app_id: int, name: str, duration: int, versions: List[Dict[str, Any]], major_metric: int, metrics: List[int]) -> Optional[Dict[str, Any]]:
    """
    创建一个编程实验
    """
    url = f"http://28.4.136.142/openapi/v3/apps/{app_id}/experiments"
    payload = {
        "name": name,
        "duration": duration,
        "versions": versions,
        "major_metric": major_metric,
        "metrics": metrics,
        "mode": 1,
        "endpoint_type": 0,
        "layer_info": {"layer_id": -1, "version_resource": 1}
    }
    return post_data_with_session(url, json_data=payload)


# 功能 2: 获取实验详情
def get_experiment_details(app_id: int, experiment_id: int) -> Optional[Dict[str, Any]]:
    """
    获取实验详情
    """
    url = f"http://28.4.136.142/openapi/v3/apps/{app_id}/experiments/{experiment_id}"
    return fetch_data(url)


# 功能 3: 修改实验信息
def update_experiment(app_id: int, experiment_id: int, update_data: Dict[str, Any], method: str = "PATCH") -> Optional[Dict[str, Any]]:
    """
    修改实验信息 (PATCH 或 PUT)
    """
    url = f"http://28.4.136.142/openapi/v3/apps/{app_id}/experiments/{experiment_id}"
    if method.upper() == "PATCH":
        return post_data_with_session(url, json_data=update_data)
    elif method.upper() == "PUT":
        return post_data_with_session(url, json_data=update_data)
    else:
        logger.error("无效的修改方法")
        return None


# 功能 4: 获取实验报告
def get_experiment_report(app_id: int, experiment_id: int, metrics: List[int], start_ts: int, end_ts: int) -> Optional[Dict[str, Any]]:
    """
    获取实验的报告数据
    """
    url = f"http://28.4.136.142/openapi/v3/apps/{app_id}/experiments/{experiment_id}/metric_report"
    payload = {"metrics": metrics, "start_ts": start_ts, "end_ts": end_ts}
    return post_data_with_session(url, json_data=payload)


# 功能 5: 删除指标
def delete_metric(app_id: int, metric_id: int) -> Optional[Dict[str, Any]]:
    """
    删除指定指标
    """
    url = f"http://28.4.136.142/openapi/v3/apps/{app_id}/metrics/{metric_id}"
    session_manager = SessionManager(login_url, session_file)
    sessionid = session_manager.get_valid_session(target_url)
    if not sessionid:
        logger.error("无法获取有效的 Session ID")
        return None

    headers = {"Cookie": f"sessionid={sessionid}"}
    try:
        response = requests.delete(url, headers=headers)
        if response.status_code == 200:
            logger.info("指标删除成功")
            return response.json()
        else:
            logger.error(f"删除指标失败，状态码: {response.status_code}, 响应: {response.text}")
    except requests.RequestException as e:
        logger.error(f"删除指标请求异常: {e}")
    return None


# 主函数测试
if __name__ == "__main__":
    # 示例调用: 创建实验
    versions = [
        {"type": 0, "name": "对照组", "label": "对照组", "weight": 50, "config": {"key1": "value1"}, "users": []},
        {"type": 1, "name": "实验组", "label": "实验组", "weight": 50, "config": {"key1": "value2"}, "users": []},
    ]
    metrics = [100940, 100941, 100942]
    experiment = create_experiment_v3(12345, "测试实验", 14, versions, 100942, metrics)
    print("创建实验返回:", experiment)

    # 示例调用: 获取实验详情
    details = get_experiment_details(12345, 67890)
    print("实验详情:", details)

    # 示例调用: 修改实验
    updated = update_experiment(12345, 67890, {"name": "修改后的实验名称", "duration": 7})
    print("修改实验返回:", updated)

    # 示例调用: 获取实验报告
    report = get_experiment_report(12345, 67890, metrics, 1708822800, 1713801599)
    print("实验报告:", report)

    # 示例调用: 删除指标
    deleted = delete_metric(12345, 100940)
    print("删除指标返回:", deleted)
'''
Author: ChZheng
Date: 2025-01-17 17:47:22
LastEditTime: 2025-02-07 15:10:26
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/api/requestnew.py
'''
import requests
import os
import logging
import uuid
from typing import Optional, Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

login_url = "http://localhost:8000/api/v1/login"
target_url = "http://localhost:8000/api/v1/target"
username = os.getenv("USERNAME","admin")
password = os.getenv("PASSWORD","admin123")

session_file= "sessionid.txt"

class SessionManager:
    def __init__(self, login_url: str, session_file: str) :
        self.login_url = login_url
        self.session_file = session_file
    def save_sessionid(self, sessionid: str):
        with open(self.session_file, "w") as f:
            f.write(sessionid)
        logger.info(f"Session ID saved to {self.session_file}")
    def load_sessionid(self):
        if os.path.exists(self.session_file):
            with open(self.session_file, "r") as f:
                sessionid = f.read()
                logger.info(f"Session ID loaded from {self.session_file}")
                return sessionid
        logger.warning(f"Session ID file {self.session_file} not found")
        return None

    def login(self):
        response = requests.post(self.login_url, json={"email":username, "password":password})
        if response.status_code == 200:
            sessionid = response.cookies.get("sessionid")
            if sessionid:
                logger.info(f"Login successful, session ID: {sessionid}")
                self.save_sessionid(sessionid)
                return sessionid
            else:
                logger.worning("Login successful but session ID not found in response cookies")
        else:
            logger.warning(f"Login failed with status code {response.status_code}")
        return None
    def validate_session(self, sessionid: str,test_url: str):
        headers = {"Cookie": f"sessionid={sessionid}"}
        response = requests.get(test_url, headers=headers)
        if response.status_code != 200:
            logger.error(f"login session is invalid, status code: {response.status_code}"
            return False
        response_data = response.json()
        if response_data.get("code")==200
            logger.info("login session is valid")
            return True
        else:
            logger.error(f"login session is invalid, response code: {response_data.get('code')},message:{response_data.get('message')}"}# decode the response data to a dictionary
            return False

    def get_valid_session(self, test_url: str):
        sessionid = self.load_sessionid()
        if sessionid and self.validate_session(sessionid, test_url):
            return sessionid
        else:
            sessionid = self.login()
            if sessionid:
                return sessionid
            else:
                logger.error("Failed to get a valid session")
                return None

    def fetch_data(url:str,params:Optional[Dict[str, Any]]=None):
        session_manager = SessionManager(login_url, session_file)
        sessionid = session_manager.get_valid_session(test_url)
        if not sessionid:
            logger.error("Failed to get a valid session")
            return None

        headers = {"Cookie": f"sessionid={sessionid}"}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            logging.info(f"Successfully fetched data from {url}")
            return response.json()
        else :
            logging.error(f"Failed to fetch data from {url}, status code: {response.status_code}")
            return None
    def post_data(url:str,data:Optional[Dict[str, Any]]=None,json_data:Optional[Dict[str, Any]]=None):
        session_manager = SessionManager(login_url, session_file)
        sessionid = session_manager.get_valid_session(test_url)
        if not sessionid:
            logger.error("Failed to get a valid session")
            return None

        headers = {"Cookie": f"sessionid={sessionid}"}
        if json_data:
            headers["Content-Type"] = "application/json"

        response = requests.post(url, headers=headers, data=data, json=json_data)
        if response.status_code == 200:
            logging.info(f"Successfully posted data to {url}")
            return response.json()
        else :
            logging.error(f"Failed to post data to {url}, status code: {response.status_code}")
            return None
    def put_data(url:str,data:Optional[Dict[str, Any]]=None,json_data:Optional[Dict[str, Any]]=None):
        session_manager = SessionManager(login_url, session_file)
        sessionid = session_manager.get_valid_session(test_url)
        if not sessionid:
            logger.error("Failed to get a valid session")
            return None

        headers = {"Cookie": f"sessionid={sessionid}"}
        if json_data:

            headers["Content-Type"] = "application/json"
        response = requests.put(url, headers=headers, data=data, json=json_data)
        if response.status_code == 200:
            logging.info(f"Successfully posted data to {url}")
            return response.json()
        else :
            logging.error(f"Failed to post data to {url}, status code: {response.status_code}")
            return None

    def create_experiment(flight_name: str, duration: int, hash_strategy: str, app_id: int) -> Optional[Dict[str, Any]]:
    """
    创建实验的完整流程，包含四次连续的 POST 请求
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


if __name__ == "__main__":
    # get
    url = "http://28.4.136.142/api/example_get"
    params = {"param1": "value1", "param2": "value2"}

    response = perform_request("GET", url, params=params)
    # response 已经是成功响应的字典数据（或 None），无需再手动检查。
    # post
    url = "http://28.4.136.142/api/example_post"
    json_data = {"key1": "value1", "key2": "value2"}

    response = perform_request("POST", url, json_data=json_data)
    # put
    url = "http://28.4.136.142/api/example_put"
    json_data = {"update_key": "new_value"}

    response = perform_request("PUT", url, json_data=json_data)


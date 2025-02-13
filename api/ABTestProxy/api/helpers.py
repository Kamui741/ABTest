'''
Author: ChZheng
Date: 2025-02-13 14:35:07
LastEditTime: 2025-02-13 17:10:47
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/api/ABTestProxy/api/helpers.py
'''

# [ABTestProxy/api/helpers.py]
# |- send_request
# |- fetch_data
# |- post_data
# |- put_data

import requests
from typing import Optional, Dict, Any
from ..auth import SessionManager
def send_request(method: str, url: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None):
    """发送HTTP请求"""
    session_manager = SessionManager(login_url, session_file)
    sessionid = session_manager.get_valid_session(target_url)
    if not sessionid:
        logger.error(" Failed to get a valid session")
        return None

    headers = {"Cookie": f"sessionid={sessionid}"}
    if json_data:
        headers["Content-Type"] = "application/json"

    try:
        response = requests.request(method, url, headers=headers, data=data, json=json_data, params=params)
        return session_manager._handle_response(response)
    except requests.RequestException as e:
        logger.error(f" Error occurred while making {method} request: {e}")
        return None

def fetch_data(url: str, params: Optional[Dict[str, Any]] = None):
    """发送GET请求"""
    return send_request("GET", url, params=params)

def post_data(url: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None):
    """发送POST请求"""
    return send_request("POST", url, data=data, json_data=json_data)

def put_data(url: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None):
    """发送PUT请求"""
    return send_request("PUT", url, data=data, json_data=json_data)

'''
Author: ChZheng
Date: 2025-02-13 14:35:07
LastEditTime: 2025-02-26 17:13:39
LastEditors: ChZheng
Description:
FilePath: /ABTest/ABTestProxy/ABTestProxy/api/helpers.py
'''
# api/helpers.py
import requests
import logging
import hmac
import hashlib
import time
from typing import Optional, Dict, Any, Union
from auth import SessionManager, V2AuthProvider
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




def send_request(
    method: str,
    url: str,
    params: Optional[Dict] = None,
    data: Optional[Dict] = None,
    json_data: Optional[Dict] = None,
    auth_type: str = 'v1'
) -> Optional[Dict]:
    """多版本兼容请求方法"""
    headers = {}

    # V1认证流程
    if auth_type == 'v1':
        session_manager = SessionManager(config.LOGIN_URL, config.SESSION_FILE)
        sessionid = session_manager.get_valid_session(config.BASE_URLS['V1'])
        headers = {"Cookie": f"sessionid={sessionid}"}

    # V2认证流程
    elif auth_type == 'v2':
        headers.update(V2AuthProvider.get_auth_headers())

    # 智能设置Content-Type
    if json_data and "Content-Type" not in headers:
        headers["Content-Type"] = "application/json"

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            json=json_data,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        logger.error(f"请求失败: {e.response.status_code} {e.response.text}")
        return {"code": e.response.status_code, "message": "API请求错误"}
    except Exception as e:
        logger.error(f"请求异常: {str(e)}")
        return None

# 保持原有快捷方法（新增auth_type参数）
def fetch_data(url: str, params: Optional[Dict] = None, auth_type: str = 'v1') -> Optional[Dict]:
    return send_request('GET', url, params=params, auth_type=auth_type)

def post_data(url: str, json_data: Optional[Dict] = None, auth_type: str = 'v1') -> Optional[Dict]:
    return send_request('POST', url, json_data=json_data, auth_type=auth_type)

def put_data(url: str, json_data: Optional[Dict] = None, auth_type: str = 'v1') -> Optional[Dict]:
    return send_request('PUT', url, json_data=json_data, auth_type=auth_type)
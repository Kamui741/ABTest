'''
Author: ChZheng
Date: 2025-02-13 14:35:07
LastEditTime: 2025-03-06 05:26:54
LastEditors: ChZheng
Description:
FilePath: /ABTest/ABTestProxy/ABTestProxy/helpers.py
'''
#helpers.py
import requests
import logging
import hmac
import hashlib
import time
from typing import Optional, Dict, Any, Union
from auth import V1AuthProvider, V2AuthProvider
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_auth_headers(auth_type: str) -> Dict:
    """统一认证头生成"""
    if auth_type == 'v1':
        provider = V1AuthProvider(config.LOGIN_URL, config.SESSION_FILE)
        sessionid = provider.get_valid_session(config.BASE_URLS['V1'])
        return {"Cookie": f"sessionid={sessionid}"}

    if auth_type == 'v2':
        return V2AuthProvider.generate_headers()

    return {}

def send_request(
    method: str,
    url: str,
    auth_type: str,  # 改为必填参数
    params: Optional[Dict] = None,
    json_data: Optional[Dict] = None
) -> Optional[Dict]:
    """优化后的请求方法"""
    headers = get_auth_headers(auth_type)
    headers.setdefault("Content-Type", "application/json")

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json_data,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        logger.error(f"请求失败[{auth_type}]: {e.response.status_code}")
        return {"code": e.response.status_code, "message": str(e)}
    except Exception as e:
        logger.error(f"请求异常[{auth_type}]: {str(e)}")
        return None

# 保持原有快捷方法（新增auth_type参数）
def fetch_data(url: str, params: Optional[Dict] = None, auth_type: str = 'v1') -> Optional[Dict]:
    return send_request('GET', url, params=params, auth_type=auth_type)

def post_data(url: str, json_data: Optional[Dict] = None, auth_type: str = 'v1') -> Optional[Dict]:
    return send_request('POST', url, json_data=json_data, auth_type=auth_type)

def put_data(url: str, json_data: Optional[Dict] = None, auth_type: str = 'v1') -> Optional[Dict]:
    return send_request('PUT', url, json_data=json_data, auth_type=auth_type)
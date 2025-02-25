'''
Author: ChZheng
Date: 2025-02-25 15:52:53
LastEditTime: 2025-02-25 15:52:54
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/ABTestProxy/ABTestProxy/clients.py
'''
# ---------------------- clients.py ----------------------
import requests
from auth import SessionManager
from config import API_ENDPOINTS, RUNTIME_MODE

class BaseClient:
    def __init__(self, session: SessionManager):
        self.session = session
        self.endpoints = API_ENDPOINTS[RUNTIME_MODE]

    def _build_url(self, service: str, endpoint: str, **params) -> str:
        return self.endpoints[service][endpoint].format(**params)

class V1Client(BaseClient, IApiClient):
    def post(self, service: str, endpoint: str, data: dict) -> dict:
        url = self._build_url(service, endpoint)
        return self._v1_request('POST', url, data)

    def get(self, service: str, endpoint: str, params: dict) -> dict:
        url = self._build_url(service, endpoint)
        return self._v1_request('GET', url, params)

    def _v1_request(self, method: str, url: str, data: dict):
        # V1特有请求逻辑
        sessionid = self.session.get_valid_session(url)
        headers = {"Cookie": f"sessionid={sessionid}"}
        response = requests.request(method, url, json=data, headers=headers)
        return self._parse_v1_response(response)

    def _parse_v1_response(self, response):
        # V1响应解析逻辑
        if response.status_code == 200:
            return response.json()['data']
        return {'error': f'V1 API error: {response.text}'}

class V2Client(BaseClient, IApiClient):
    def post(self, service: str, endpoint: str, data: dict) -> dict:
        url = self._build_url(service, endpoint)
        return requests.post(url, json=data).json()

    def get(self, service: str, endpoint: str, params: dict) -> dict:
        url = self._build_url(service, endpoint, **params)
        return requests.get(url).json()
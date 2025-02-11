# project/api/clients.py
import requests
from typing import Optional, Dict
from core.config import AppConfig
from core.auth import SessionManager
from core.exceptions import APIClientError

class BaseAPIClient:
    """API客户端基类"""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session_mgr = SessionManager()

    def _send_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Dict:
        """统一请求方法"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        session_id = self.session_mgr.get_valid_session()

        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                headers={"Cookie": f"sessionid={session_id}"},
                params=params,
                json=json_data,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise APIClientError(f"Request to {url} failed: {str(e)}") from e

class V1Client(BaseAPIClient):
    """一期服务客户端"""

    def __init__(self):
        super().__init__(AppConfig.V1_BASE_URL)

    def create_experiment(self, payload: Dict) -> Dict:
        return self._send_request("POST", "/api/experiments", json_data=payload)

    def get_experiment(self, experiment_id: str) -> Dict:
        return self._send_request("GET", f"/api/experiments/{experiment_id}")

class V2Client(BaseAPIClient):
    """二期服务客户端"""

    def __init__(self):
        super().__init__(AppConfig.V2_BASE_URL)

    def create_experiment(self, payload: Dict) -> Dict:
        return self._send_request("POST", "/openapi/v2/experiments", json_data=payload)
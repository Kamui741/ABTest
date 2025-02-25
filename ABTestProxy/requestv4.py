# ------------ config.py ------------
import os
from typing import Literal

# 版本配置
RUNTIME_MODE: Literal['V1', 'V2'] = os.getenv('RUNTIME_MODE', 'V1')

# 认证配置
V1_SESSION_FILE = os.getenv('SESSION_FILE', 'session.txt')
V1_LOGIN_URL = os.getenv('LOGIN_URL', 'https://28.4.136.142/api/login')
V2_AK = os.getenv("V2_AK")
V2_SK = os.getenv("V2_SK")

# 服务端点
API_ENDPOINTS = {
    'V1': {
        'experiment': {
            'create': '/datatester/api/v1/flight/create',
            'detail': '/datatester/api/v1/flight/{flight_id}',
            'status': '/datatester/api/v2/flight/{action}'
        },
        'report': '/datatester/api/v1/report',
        'metric': '/datatester/api/v2/app/{app_id}/metric/list',
        'layer': '/datatester/api/v2/app/{app_id}/layer/list'
    },
    'V2': {
        'experiment': {
            'create': '/openapi/v2/apps/{app_id}/experiments',
            'detail': '/openapi/v1/apps/{app_id}/experiment/{experiment_id}/details',
            'launch': '/openapi/v2/apps/{app_id}/experiments/{experiment_id}/launch/',
            'stop': '/openapi/v2/apps/{app_id}/experiments/{experiment_id}/stop/'
        },
        'report': '/openapi/v1/apps/{app_id}/experiment/{experiment_id}/metrics',
        'metric': '/openapi/v2/apps/{app_id}/metrics',
        'layer': '/openapi/v2/apps/{app_id}/layers'
    }
}

BASE_URL = "https://28.4.136.142"
# ------------ auth.py ------------
import requests
import logging
from typing import Optional

class AuthManager:
    """统一认证管理"""
    def __init__(self):
        self.v1_session = requests.Session()
        self.v2_credentials = None

    def v1_login(self, username: str, password: str) -> bool:
        """V1版本登录"""
        try:
            response = self.v1_session.post(
                V1_LOGIN_URL,
                json={"email": username, "password": password}
            )
            return response.status_code == 200
        except Exception as e:
            logging.error(f"V1登录失败: {str(e)}")
            return False

    def set_v2_credentials(self, ak: str, sk: str):
        """设置V2认证信息"""
        self.v2_credentials = (ak, sk)

# ------------ clients.py ------------
import requests
import time
import hashlib
import hmac
from urllib.parse import urlparse

class BaseClient:
    def __init__(self, auth: AuthManager):
        self.auth = auth
        self.base_url = BASE_URL

class V1Client(BaseClient):
    """V1版本客户端实现"""
    def create_experiment(self, params: dict) -> dict:
        url = f"{self.base_url}{API_ENDPOINTS['V1']['experiment']['create']}"
        response = self.auth.v1_session.post(url, json=params)
        return self._parse_response(response)

    def _parse_response(self, response):
        if response.status_code == 200:
            return response.json()
        return {"code": response.status_code, "message": "V1 API Error"}

class V2Client(BaseClient):
    """V2版本客户端实现（带签名认证）"""
    def _generate_signature(self, method: str, path: str, body: str = "") -> str:
        """生成V2版本请求签名"""
        ak, sk = self.auth.v2_credentials
        timestamp = str(int(time.time()))
        nonce = hashlib.sha256(timestamp.encode()).hexdigest()[:8]
        message = f"{method}\n{path}\n{timestamp}\n{nonce}\n{body}"
        signature = hmac.new(sk.encode(), message.encode(), hashlib.sha256).hexdigest()
        return f"{ak}:{timestamp}:{nonce}:{signature}"

    def _request(self, method: str, endpoint: str, params: dict, data: dict = None) -> dict:
        """统一请求方法"""
        full_url = f"{self.base_url}{endpoint}"
        parsed = urlparse(full_url)
        path = parsed.path

        # 生成签名头
        body_str = "" if not data else json.dumps(data, separators=(',', ':'))
        signature = self._generate_signature(method.upper(), path, body_str)

        headers = {
            "Authorization": f"ABTest {signature}",
            "Content-Type": "application/json"
        }

        response = requests.request(
            method,
            full_url,
            params=params,
            json=data,
            headers=headers
        )

        if response.status_code == 401:
            raise ABTestException(401, "认证失败，请检查AK/SK配置")

        return response.json()

    def create_experiment(self, app_id: int, data: dict) -> dict:
        endpoint = API_ENDPOINTS['V2']['experiment']['create'].format(app_id=app_id)
        return self._request("POST", endpoint, {}, data)

    def update_status(self, app_id: int, experiment_id: int, action: str) -> dict:
        endpoint = API_ENDPOINTS['V2']['experiment'][action].format(
            app_id=app_id,
            experiment_id=experiment_id
        )
        return self._request("PUT", endpoint, {})

# ------------ services.py ------------
from typing import Dict, Any

class ExperimentService:
    def __init__(self, client: BaseClient):
        self.client = client

class V1ExperimentService(ExperimentService):
    """V1版本服务实现"""
    def create(self, params: Dict) -> Dict:
        # 参数转换
        v1_params = {
            "flight_name": params["name"],
            "app_id": params["app_id"],
            "duration": params["duration"],
            "hash_strategy": "ssid",
            "metrics": ",".join(map(str, params["metrics"]))
        }
        return self.client.create_experiment(v1_params)

class V2ExperimentService(ExperimentService):
    """V2版本服务实现"""
    def create(self, params: Dict) -> Dict:
        required_fields = ["name", "app_id", "metrics", "versions"]
        if any(field not in params for field in required_fields):
            raise ABTestException(400, "缺少必要参数")

        return self.client.create_experiment(
            app_id=params["app_id"],
            data={
                "name": params["name"],
                "mode": 1,
                "endpoint_type": params.get("endpoint_type", 1),
                "duration": params["duration"],
                "major_metric": params["metrics"][0],
                "metrics": params["metrics"],
                "versions": params["versions"],
                "layer_info": params.get("layer_info", {"layer_id": -1})
            }
        )

# ------------ exception.py ------------
class ABTestException(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")

# ------------ factory.py ------------
class ServiceFactory:
    @staticmethod
    def create_service(auth: AuthManager) -> ExperimentService:
        if RUNTIME_MODE == 'V1':
            return V1ExperimentService(V1Client(auth))
        else:
            if not auth.v2_credentials:
                raise ABTestException(500, "V2模式需要配置AK/SK")
            return V2ExperimentService(V2Client(auth))

# ------------ main.py ------------
def main():
    # 初始化认证
    auth = AuthManager()

    if RUNTIME_MODE == 'V1':
        if not auth.v1_login(USERNAME, PASSWORD):
            raise ABTestException(401, "V1登录失败")
    else:
        auth.set_v2_credentials(V2_AK, V2_SK)

    # 创建服务实例
    service = ServiceFactory.create_service(auth)

    # 创建实验示例
    try:
        params = {
            "name": "新用户引导实验V2",
            "app_id": 1001,
            "duration": 30,
            "metrics": [29806],
            "versions": [
                {
                    "type": 0,
                    "name": "对照组",
                    "config": {"feature_flag": "control"}
                },
                {
                    "type": 1,
                    "name": "实验组",
                    "config": {"feature_flag": "experiment"}
                }
            ]
        }
        result = service.create(params)
        print("实验创建成功:", result)

    except ABTestException as e:
        print(f"操作失败: {e.code} - {e.message}")

if __name__ == "__main__":
    main()
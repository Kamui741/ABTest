'''
Author: ChZheng
Date: 2025-02-26 06:57:14
LastEditTime: 2025-04-16 09:13:25
LastEditors: ChZheng
Description:
FilePath: /code/code/ABTest/ABTestProxy/requestv4.py
'''
import time
# ---------------------- adapters.py ----------------------

from typing import Dict


class V1Adapter():
    """增强的V1协议适配器"""

    def convert_create_experiment_request(self, params: Dict) -> Dict:
        """V1->V2 创建实验参数转换"""
        params["hash_strategy"] = "ssid"
        return params

    def convert_create_experiment_response(self, response: Dict) -> Dict:
        """V2->V1 创建实验响应转换"""
        return response

    def convert_get_experiment_details_request(self, params: Dict) -> Dict:
        """V1->V2 查询实验详情参数转换"""
        params["is_duplicate"] = False
        return params

    def convert_get_experiment_details_response(self, response: Dict) -> Dict:
        if response["code"]==200
            return response
        return {
            "code": 200,
            "data": {
                "id":response["data"]["id"],
                "name": response["data"]["flight_name"],
                "start_ts": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(response["data"]["start_time"])),
                "end_ts": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(response["data"]["end_time"])),
                "owner": response["data"]["owner"],
                "description": response["data"]["description"],
                "status": response["data"]["status"],
                "type": "client",
                "mode": response["data"]["mode"],
                "layer":{
                    "name": response["data"]["layer_info"]["layer_name"],
                    "status": response["data"]["layer_info"]["layer_status"],
                    "description": "",
                    "type": response["data"]["layer_info"]["type"],
                },
                "version_resource": response["data"]["version_resource"],
                "versions":[
                    {
                        "id": v["id"],
                        "name": v["name"],
                        "type": v["type"],
                        "config": v["config"],
                        "description": v["description"],
                        "weight": v["weight"],
                    }
                for v in response["data"]["versions"]
                ],
                "metrics":[
                    {
                        "id": m["metrics"][0]["id"],
                        "name": m["metrics"][0]["name"],
                        "metric_description": m["metrics"][0]["description"],
                        "type": m["metrics"][0]["type"],

                    }
                for m in response["data"]["metrics"]
                ],
                "whitelist":[

                ],
            },
            "message":"success"
        }

    def convert_generate_report_request(self, params: Dict) -> Dict:
        """V1->V2 报告请求转换"""
        params["trace_data"] = params.get("trace_data", "")
        return params

    def convert_generate_report_response(self, response: Dict) -> Dict:
        """V2->V1 报告响应转换"""
        return response

    def convert_modify_experiment_status_request(self, params: Dict) -> Dict:
        """V1->V2 修改实验状态请求转换"""
        return {
            "flight_id": params["experiment_id"],
            "action": params["action"]
        }

    def convert_modify_experiment_status_response(self, response: Dict) -> Dict:
        """V2->V1 修改实验状态响应转换"""
        return response

    def convert_list_available_metrics_request(self, params: Dict) -> Dict:
        """V1->V2 查询可用指标请求转换"""
        return params

    def convert_list_available_metrics_response(self, response: Dict) -> Dict:
        """V2->V1 查询可用指标响应转换"""
        return response

    def convert_list_mutex_groups_request(self, params: Dict) -> Dict:
        """V1->V2 查询互斥组请求转换"""
        params["need_default"] = False
        return params

    def convert_list_mutex_groups_response(self, response: Dict) -> Dict:
        """V2->V1 查询互斥组响应转换"""
        return response


class V2Adapter():
    """V2透传适配器"""

    def convert_create_experiment_request(self, params: Dict) -> Dict:
        """V2不需要转换，直接透传"""
        return params

    def convert_create_experiment_response(self, response: Dict) -> Dict:
        return response

    def convert_get_experiment_details_request(self, params: Dict) -> Dict:
        return params

    def convert_get_experiment_details_response(self, response: Dict) -> Dict:
        return response

    def convert_generate_report_request(self, params: Dict) -> Dict:
        return params

    def convert_generate_report_response(self, response: Dict) -> Dict:
        return response

    def convert_modify_experiment_status_request(self, params: Dict) -> Dict:
        return params

    def convert_modify_experiment_status_response(self, response: Dict) -> Dict:
        return response

    def convert_list_available_metrics_request(self, params: Dict) -> Dict:
        return params

    def convert_list_available_metrics_response(self, response: Dict) -> Dict:
        return response

    def convert_list_mutex_groups_request(self, params: Dict) -> Dict:
        return params

    def convert_list_mutex_groups_response(self, response: Dict) -> Dict:
        return response
'''
Author: ChZheng
Date: 2025-03-05 15:19:27
LastEditTime: 2025-03-13 10:00:54
LastEditors: ChZheng
Description:
FilePath: /ABTest/ABTestProxy/ABTestProxy/app.py
'''
# ---------------------- app.py ----------------------
# app.py
from fastapi import FastAPI, Path, Query, Body, HTTPException, Request
import logging
import re
from typing import Optional, Dict, Any
from service import ABTestService

app = FastAPI(title="ABTest API Service", version="2.0")
logger = logging.getLogger(__name__)

# -------------------- API Endpoints --------------------
@app.post("/openapi/{version}/apps/{app_id}/experiments",
          summary="创建实验",
          tags=["实验管理"])
async def create_experiment(
    request: Request,
    app_id: int = Path(..., description="应用ID"),
    version: str = Path(..., description="API版本控制参数")
):
    """创建新实验（支持V1/V2双版本）"""

    # 解析请求体
    body_data = await request.json()
    # 构建参数
    params = {
        "app_id": app_id,
        "version": version,
        **body_data
    }

    result = ABTestService().create_experiment(params)
    return handle_response(result)



@app.get("/openapi/{version}/apps/{app_id}/experiment/{experiment_id}/details",
         summary="获取实验详情",
         tags=["实验管理"])
async def get_experiment_details(
    app_id: int = Path(..., description="应用ID"),
    experiment_id: int = Path(..., description="实验ID"),
    version: str = Path(..., description="API版本控制参数")
):
    """获取实验配置详情"""

    params = {
        "app_id": app_id,
        "experiment_id": experiment_id,
        "version": version
    }
    result = ABTestService().get_experiment_details(params)
    return handle_response(result)


@app.get("/openapi/{version}/apps/{app_id}/experiment/{experiment_id}/metrics",
         summary="生成实验报告",
         tags=["实验分析"])
async def generate_report(
    app_id: int = Path(..., description="应用ID"),
    experiment_id: int = Path(..., description="实验ID"),
    report_type: str = Query(..., description="报告类型: day/hour/five_minute"),
    start_ts: str = Query(..., description="开始时间戳（10位）"),
    end_ts: str = Query(..., description="结束时间戳（10位）"),
    filters: Optional[str] = Query(None, description="过滤条件"),
    version: str = Path(..., description="API版本控制参数")
):
    """生成实验指标报告"""
    params = {
        "app_id": app_id,
        "experiment_id": experiment_id,
        "report_type": report_type,
        "start_ts": start_ts,
        "end_ts": end_ts,
        "filters": filters,
        "version": version
    }
    result = ABTestService().generate_report(params)
    return handle_response(result)


@app.put("/openapi/{version}/apps/{app_id}/experiments/{experiment_id}/{action}",
         summary="修改实验状态",
         tags=["实验管理"])
async def modify_experiment_status(
    app_id: int = Path(..., description="应用ID"),
    experiment_id: int = Path(..., description="实验ID"),
    action: str = Path(..., description="操作类型: launch/stop"),
    version: str = Path(..., description="API版本控制参数")
):
    """启动/停止实验"""

    params = {
        "app_id": app_id,
        "experiment_id": experiment_id,
        "action": action,
        "version": version
    }
    result = ABTestService().modify_experiment_status(params)
    return handle_response(result)


@app.get("/openapi/{version}/apps/{app_id}/metrics",
         summary="获取指标列表",
         tags=["资源管理"])
async def list_metrics(
    app_id: int = Path(..., description="应用ID"),
    keyword: Optional[str] = Query(None, description="搜索关键字"),
    page: int = Query(1, ge=1, description="当前页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    need_page: int = Query(1, ge=0, le=1, description="是否分页"),
    version: str = Path(..., description="API版本控制参数")
):
    """查询可用指标"""

    params = {
        "app_id": app_id,
        "keyword": keyword,
        "page": page,
        "page_size": page_size,
        "need_page": need_page,
        "version": version
    }
    result = ABTestService().list_available_metrics(params)
    return handle_response(result)


@app.get("/openapi/{version}/apps/{app_id}/layers",
         summary="获取互斥组列表",
         tags=["资源管理"])
async def list_mutex_groups(
    app_id: int = Path(..., description="应用ID"),
    keyword: Optional[str] = Query(None, description="搜索关键字"),
    page: int = Query(1, ge=1, description="当前页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    need_page: int = Query(1, ge=0, le=1, description="是否分页"),
    version: str = Path(..., description="API版本控制参数")
):
    """查询互斥组信息"""

    params = {
        "app_id": app_id,
        "keyword": keyword,
        "page": page,
        "page_size": page_size,
        "need_page": need_page,
        "version": version
    }
    result = ABTestService().list_mutex_groups(params)
    return handle_response(result)


# -------------------- 工具函数 --------------------
def handle_response(result: Dict) -> Dict:
    """统一响应处理"""
    if result.get("code") == 200:
        return {
            "code": 200,
            "message": "success",
            "data": result.get("data", {})
        }
    else:
        raise HTTPException(
            status_code=400,
            detail={
                "code": result.get("code", 500),
                "message": result.get("message", "未知错误")
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)





# auth.py
import hashlib
import hmac
import os
import time
import requests
import logging
from typing import Optional, Dict, Any

from requests import session

from config import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class V1AuthProvider:
    """V1会话认证"""
    def __init__(self):
        self.login_url = config.V1_LOGIN_URL
        self.session_file = config.V1_SESSION_FILE
        self.target_url = config.V1_TARGET_URL
        self.username = config.V1_USERNAME
        self.password = config.V1_PASSWORD

    def get_auth_headers(self) -> Dict[str, str]:
        """实现AuthProvider接口"""
        sessionid = self.get_valid_session()
        return {"Cookie": f"sessionid={sessionid}"} if sessionid else {}

    def get_valid_session(self) -> Optional[str]:
        """获取 session"""
        sessionid = self._load_sessionid()
        if sessionid and self._validate_session(sessionid):
            return sessionid
        return self._login()

    def _load_sessionid(self) -> Optional[str]:
        """加载本地会话ID"""
        if not os.path.exists(self.session_file):
            logger.warning(logger.error(f"会话文件不存在: {self.session_file}")
            return self._login()
        try:
            with open(self.session_file, "r") as f:
                sessionid = f.read().strip()
                logger.info(f"加载会话ID: {sessionid}")
                return sessionid
        except Exception as e:
            logger.error(f"加载会话文件失败: {str(e)}")
            return self._login()

    def _save_sessionid(self, sessionid: str):
        """保存会话ID到文件"""

        with open(self.session_file, "w") as f:
            f.write(sessionid)
        logger.info(f"会话ID已保存至 {self.session_file}")


    def _validate_session(self, sessionid: str) -> bool:
        headers = {"Cookie":f"sessionid={sessionid}"}
        """验证会话有效性"""
        try:
            response = requests.get(
                self.target_url,
                headers=headers
            )
            return bool(self.handle_response(response))
        except requests.RequestException as e:
            logger.error(f"会话验证请求失败: {str(e)}")
            return False

    def handle_response(self, response: requests.Response) -> Optional[Dict]:
        """统一处理响应"""
        try:
            response_data = response.json()
        except requests.JSONDecodeError:
            logger.error(f"响应解析失败: {response.url}")
            return None
        if response.status_code!= 200:
            logger.error(f"请求失败,状态码 {response.status_code}")
            return None
        response_data = response.json()
        if response_data.get("code") == 200:
            logger.info("请求成功")
            return response_data
        else:
            logger.error(f"请求失败，状态码{response_data.get('code')},信息{response_data.get('message')}")
        return None

    def _login(self) -> Optional[str]:
        """执行登录流程"""
        try:
            response = requests.post(
                self.login_url,
                json={"email": self.username, "password": self.password}
            )
            response_data = self.handle_response(response)
            if response_data:
                sessionid = response.cookies.get("sessionid")
                return sessionid
            logger.warning(f"登录成功但是没找到sessionid")
        except Exception as e:
            logger.error(f"登录失败: {str(e)}")
        return None

class V2AuthProvider:
    """V2 AK/SK认证"""
    def __init__(self):
        from config import config
        self.ak = config.V2_ACCESS_KEY
        self.sk = config.V2_SECRET_KEY

    def get_headers(self):
        timestamp = str(int(time.time()))
        signature = hmac.new(
            self.sk.encode(),
            f"{timestamp}\n{self.ak}".encode(),
            hashlib.sha256
        ).hexdigest()
        return {
            "X-Access-Key": self.ak,
            "X-Timestamp": timestamp,
            "X-Signature": signature
        }

'''
Author: ChZheng
Date: 2025-03-05 14:53:48
LastEditTime: 2025-03-10 16:40:35
LastEditors: ChZheng
Description:
FilePath: /ABTest/ABTestProxy/ABTestProxy/clients.py
'''
import json
# ---------------------- clients.py ----------------------
import logging
import uuid
from typing import Dict , Any , Optional
import requests
from config import config
from helpers import post_data , put_data , fetch_data

logger = logging.getLogger(__name__)

class BaseClient:
    """客户端基类"""
    def __init__(self, base_url: str, auth_type: str):
        self.base_url = base_url
        self.auth_type = auth_type



class V1Client(BaseClient):
    """V1客户端完整实现"""
    def __init__(self):
        super().__init__(
            base_url=config.BASE_URLS['V1'],
            auth_type='v1'
        )
    def create_experiment(self, params: Dict) -> Dict:
        """创建实验（参数需适配V1格式）"""
        flight_name=params['name']
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
            "versions": json.dumps([
                {
                    "type": v["type"],
                    "id": v["id"],
                    "name": v["name"],
                    "lable": v["label"],
                    "users":v.get("users", []),
                    "weight": v.get("weight", 50),
                    "config": v["config"],
                }
                for v in versions
            ], ensure_ascii=False),
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
            "versions": json.dumps([
                {
                    "type": v["type"],
                    "id": v["id"],
                    "name": v["name"],
                    "lable": v["label"],
                    "users":v.get("users", []),
                    "weight": v.get("weight", 50),
                    "config": v["config"],
                }
                for v in versions
            ], ensure_ascii=False),
            "filter_rule":"[]",
            "layer_info":json.dumps(layer_info, ensure_ascii=False),
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

        app_id=params['app_id']
        flight_id=params['flight_id']
        report_type=params['report_type']
        start_ts=params['start_ts']
        end_ts=params['end_ts']
        trace_data=params['trace_data']

        url = f"{self.base_url}/datatester/api/v2/app/{app_id}/flight/{flight_id}/rich-metric-report"
        params = {
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

class V2Client(BaseClient):
    """适配config.py的V2客户端实现"""
    def __init__(self):
        super().__init__(
            base_url=config.BASE_URLS['2'],
            auth_type='v2'
        )
    def create_experiment(self, params: Dict) -> Dict:
        return post_data(
            url=self._build_url('create_experiment', app_id=params['app_id']),
            json_data={
                "name": params["name"],
                "mode": params["mode"],
                "endpoint_type": params["endpoint_type"],
                "duration": params["duration"],
                "major_metric": params["major_metric"],
                "metrics": params["metrics"],
                "versions": self._build_versions(params["versions"]),
                "layer_info": params.get("layer_info", {"layer_id": -1})
            },
            auth_type='v2'
        )

    def get_experiment_details(self, params: Dict) -> Dict:
        return fetch_data(
            url=self._build_url('get_details',
                app_id=params['app_id'],
                experiment_id=params['experiment_id']
            ),
            auth_type='v2'
        )

    def generate_report(self, params: Dict) -> Dict:
        return fetch_data(
            url=self._build_url('generate_report',
                app_id=params['app_id'],
                experiment_id=params['experiment_id']
            ),
            params={
                "report_type": params['report_type'],
                "start_ts": params['start_ts'],
                "end_ts": params['end_ts'],
                "filters": params.get("filters", ""),
            },
            auth_type='v2'
        )

    def modify_experiment_status(self, params: Dict) -> Dict:
        valid_actions = ["launch", "stop"]
        if params['action'] not in valid_actions:
            return self._error_response(f"无效操作, 可选值: {valid_actions}")

        return put_data(
            url=self._build_url('modify_status',
                app_id=params['app_id'],
                experiment_id=params['experiment_id'],
                action=params['action']
            ),
            auth_type='v2'
        )

    def list_available_metrics(self, params: Dict) -> Dict:
        return fetch_data(
            url=self._build_url('list_metrics', app_id=params['app_id']),
            params={
                "keyword": params.get('keyword', ''),
                "page": params.get('page', 1),
                "page_size": params.get('page_size', 10)
            },
            auth_type='v2'
        )

    def list_mutex_groups(self, params: Dict) -> Dict:
        return fetch_data(
            url=self._build_url('list_groups', app_id=params['app_id']),
            params={
                "need_page": params.get("need_page", 1),
                "page": params.get('page', 1),
                "page_size": params.get('page_size', 10)
            },
            auth_type='v2'
        )

    def _build_url(self, endpoint_name: str,**path_params) -> str:
        """使用config配置生成完整URL"""
        base_url = config.BASE_URLS['2']
        endpoint_template = config.API_ENDPOINTS[endpoint_name]['V2']
        return f"{base_url}/{endpoint_template.format(**path_params)}"


    def _build_versions(self, versions: list) -> list:
        return [{
            "type": v["type"],
            "name": v["name"],
            "description": v.get("description", ""),  # 补全文档字段
            "weight": v.get("weight", 50),  # 处理weight逻辑
            "config": v.get("config", {}),  # 直接透传
            "users": v.get("users", [])
        } for v in versions]

    def _error_response(self, message: str) -> Dict:
        return {"code": 400, "message": message}

'''
Author: ChZheng
Date: 2025-02-25 19:36:47
LastEditTime: 2025-03-10 16:45:14
LastEditors: ChZheng
Description:
FilePath: /ABTest/ABTestProxy/ABTestProxy/config.py
'''
# ---------------------- config.py ----------------------
import os

class ABTestConfig:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._reload()
        return cls._instance

    @classmethod
    def _reload(cls):
        # 基础配置
        cls.V1_SESSION_FILE = os.getenv('SESSION_FILE', 'session.txt')
        cls.V1_LOGIN_URL = os.getenv('LOGIN_URL', 'https://28.4.136.142/api/login')
        cls.V1_USERNAME = os.getenv("USERNAME")
        cls.V1_PASSWORD = os.getenv("PASSWORD")
        cls.V1_TARGET_URL = os.getenv('TARGET_URL', 'https://28.4.136.142')

        # V2认证配置
        cls.V2_ACCESS_KEY = os.getenv("2_ACCESS_KEY")
        cls.V2_SECRET_KEY = os.getenv("2_SECRET_KEY")


        cls.BASE_URLS = {
            'v1': os.getenv('V1_BASE_URL', 'https://28.4.136.142'),
            'v2': os.getenv('V2_BASE_URL', 'https://default-v2.example.com')
        }
        cls.API_ENDPOINTS = {
            'create_experiment': {
                'v1': 'experiment/create',
                'v2': 'openapi/v2/apps/{app_id}/experiments'
            },
            'get_details': {
                'v1': 'experiment/detail',
                'v2': 'openapi/v2/apps/{app_id}/experiments/{experiment_id}/details'
            },
            'generate_report': {
                'v1': 'report/generate',
                'v2': 'openapi/v2/apps/{app_id}/experiments/{experiment_id}/metrics'
            },
            'modify_status': {
                'v1': 'experiment/status',
                'v2': 'openapi/v2/apps/{app_id}/experiments/{experiment_id}/{action}'
            },
            'list_metrics': {
                'v1': 'metrics',
                'v2': 'openapi/v2/apps/{app_id}/metrics'
            },
            'list_groups': {
                'v1': 'groups',
                'v2': 'openapi/v2/apps/{app_id}/layers'
            }
        }


    def get_endpoint(self, version: str, name: str, **params) -> str:
        """动态获取端点路径"""
        return self.API_ENDPOINTS[name][version].format(**params)

config = ABTestConfig()

'''
Author: ChZheng
Date: 2025-02-13 14:35:07
LastEditTime: 2025-03-10 14:50:28
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
        provider = V1AuthProvider()
        sessionid = provider.get_valid_session()
        return {"Cookie": f"sessionid={sessionid}"}

    if auth_type == 'v2':
        if auth_type == 'v2':
            provider = V2AuthProvider()
            return provider.get_headers()
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

'''
Author: ChZheng
Date: 2025-03-05 15:12:03
LastEditTime: 2025-03-10 16:46:07
LastEditors: ChZheng
Description:
FilePath: /ABTest/ABTestProxy/ABTestProxy/service.py
'''
# ---------------------- service.py ----------------------
from config import config
from clients import V1Client, V2Client
from adapters import V1Adapter, V2Adapter
from typing import Dict
class ABTestService:
    def __init__(self):
        self._version = 'V2'  # 默认版本
        self._clients = {'v1': V1Client(), 'v2': V2Client()}
        self._adapters = {'v1': V1Adapter(), 'v2': V2Adapter()}
    def _setup_components(self, params: Dict):
        """统一初始化组件"""
        version = params.get('version', self._version).upper()
        if version not in ['v1', 'v2']:
            raise ValueError(f"Invalid version: {version}")
        print(f"当前版本: {version}, 适配器类型: {type(self._adapters[version])}")  # 调试输出
        self._client = self._clients[version]
        self._adapter = self._adapters[version]
        return self

    def create_experiment(self, params: Dict) -> Dict:
        self._setup_components(params)
        converted_params = self._adapter.convert_create_experiment_request(params)
        raw_response = self._client.create_experiment(converted_params)
        return self._adapter.convert_create_experiment_response(raw_response)

    def get_experiment_details(self, params: Dict) -> Dict:
        self._setup_components(params)
        converted_params = self._adapter.convert_get_experiment_details_request(params)
        raw_response = self._client.get_experiment_details(converted_params)
        return self._adapter.convert_get_experiment_details_response(raw_response)

    def generate_report(self, params: Dict) -> Dict:
        self._setup_components(params)
        converted_params = self._adapter.convert_generate_report_request(params)
        raw_response = self._client.generate_report(converted_params)
        return self._adapter.convert_generate_report_response(raw_response)

    def modify_experiment_status(self, params: Dict) -> Dict:
        self._setup_components(params)
        converted_params = self._adapter.convert_modify_experiment_status_request(params)
        raw_response = self._client.modify_experiment_status(converted_params)
        return self._adapter.convert_modify_experiment_status_response(raw_response)

    def list_available_metrics(self, params: Dict) -> Dict:
        self._setup_components(params)
        converted_params = self._adapter.convert_list_available_metrics_request(params)
        raw_response = self._client.list_available_metrics(converted_params)
        return self._adapter.convert_list_available_metrics_response(raw_response)

    def list_mutex_groups(self, params: Dict) -> Dict:
        self._setup_components(params)
        converted_params = self._adapter.convert_list_mutex_groups_request(params)
        raw_response = self._client.list_mutex_groups(converted_params)
        return self._adapter.convert_list_mutex_groups_response(raw_response)
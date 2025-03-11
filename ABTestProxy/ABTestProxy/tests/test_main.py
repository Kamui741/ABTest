# test_abtest_api.py
import requests
import json
from typing import Dict
import sys
import os

# 获取当前测试目录的绝对路径
test_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录（即ABTestProxy文件夹）
project_root = os.path.dirname(test_dir)
# 将根目录添加到Python路径
sys.path.insert(0, project_root)

from config import config

# 测试ABTestProxy的API
class ABTestTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_app_id = 1001  # 测试用应用ID
        self.created_experiment_id = None  # 存储新建实验ID
        self.version = "v1"  # API版本
    def print_result(self, case_name: str, success: bool, response: Dict):
        """统一打印测试结果"""
        status = "成功" if success else "失败"
        color = "\033[92m" if success else "\033[91m"
        print(f"{color}{case_name} {status}\033[0m")
        print("响应详情:", json.dumps(response, indent=2, ensure_ascii=False))
        print("-" * 80)

    def test_create_experiment(self) -> bool:
        """测试创建实验"""
        url = f"{self.base_url}/openapi/{self.version}/apps/{self.test_app_id}/experiments"
        params = {
            "name": "端到端测试实验",
            "mode": 1,
            "endpoint_type": 1,
            "duration": 7,
            "major_metric": 29806,
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
                    "config": {"feature_flag": "test"}
                }
            ],
            "layer_info": {
                "layer_id": -1,
                "version_resource": 0.5
            }
        }
        try:
            response = requests.post(url, json=params)
            response.raise_for_status()
            data = response.json()
            if data["code"] == 200 and isinstance(data["data"], int):
                self.created_experiment_id = data["data"]
                self.print_result("1. 创建实验", True, data)
                return True
            self.print_result("1. 创建实验", False, data)
            return False
        except Exception as e:
            print(f"创建实验异常: {str(e)}")
            return False

    def test_get_details(self) -> bool:
        """测试获取实验详情"""
        if not self.created_experiment_id:
            print("未创建实验，跳过详情查询")
            return False

        url = f"{self.base_url}/openapi/{self.version}/apps/{self.test_app_id}/experiment/{self.created_experiment_id}/details"
        params={

            }
        try:
            response = requests.get(url, )
            response.raise_for_status()
            data = response.json()
            success = data["code"] == 200 and data["data"]["id"] == self.created_experiment_id
            self.print_result("2. 获取详情", success, data)
            return success
        except Exception as e:
            print(f"获取详情异常: {str(e)}")
            return False

    def test_generate_report(self) -> bool:
        """测试生成报告"""
        if not self.created_experiment_id:
            print("未创建实验，跳过报告生成")
            return False

        url = f"{self.base_url}/openapi/{self.version}/apps/{self.test_app_id}/experiment/{self.created_experiment_id}/metrics"
        params = {
            "report_type": "day",
            "start_ts": "1625097600",  # 2021-07-01
            "end_ts": "1627689600",     # 2021-07-31
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            success = data["code"] == 200 and "calculation_results" in data["data"]
            self.print_result("3. 生成报告", success, data)
            return success
        except Exception as e:
            print(f"生成报告异常: {str(e)}")
            return False

    def test_modify_status(self) -> bool:
        """测试状态修改"""
        if not self.created_experiment_id:
            print("未创建实验，跳过状态修改")
            return False

        # 先停止实验
        stop_url = f"{self.base_url}/openapi/{self.version}/apps/{self.test_app_id}/experiments/{self.created_experiment_id}/stop"
        try:
            response = requests.put(stop_url)
            response.raise_for_status()
            stop_data = response.json()
            stop_ok = stop_data["code"] == 200

            # 再启动实验
            launch_url = f"{self.base_url}/openapi/{self.version}/apps/{self.test_app_id}/experiments/{self.created_experiment_id}/launch"
            response = requests.put(launch_url)
            response.raise_for_status()
            launch_data = response.json()
            launch_ok = launch_data["code"] == 200

            self.print_result("4. 状态修改", stop_ok and launch_ok, {
                "stop_response": stop_data,
                "launch_response": launch_data
            })
            return stop_ok and launch_ok
        except Exception as e:
            print(f"状态修改异常: {str(e)}")
            return False

    def test_list_metrics(self) -> bool:
        """测试指标列表"""
        url = f"{self.base_url}/openapi/{self.version}/apps/{self.test_app_id}/metrics"
        params = {
            "page": 1,
            "page_size": 5,
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            success = data["code"] == 200 and len(data["data"]["metrics"]) > 0
            self.print_result("5. 指标列表", success, data)
            return success
        except Exception as e:
            print(f"获取指标列表异常: {str(e)}")
            return False

    def test_list_groups(self) -> bool:
        """测试互斥组列表"""
        url = f"{self.base_url}/openapi/{self.version}/apps/{self.test_app_id}/layers"
        params = {
            "page": 1,
            "page_size": 5,
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            success = data["code"] == 200 and isinstance(data["data"], list)
            self.print_result("6. 互斥组列表", success, data)
            return success
        except Exception as e:
            print(f"获取互斥组异常: {str(e)}")
            return False

if __name__ == "__main__":
    print("启动AB测试接口验证...")
    tester = ABTestTester()

    # 按顺序执行测试
    test_results = {
        "create": tester.test_create_experiment(),
        # "details": tester.test_get_details(),
        # "report": tester.test_generate_report(),
        # "status": tester.test_modify_status(),
        # "metrics": tester.test_list_metrics(),
        # "groups": tester.test_list_groups()
    }

    # 打印汇总结果
    print("\n测试结果汇总:")
    for name, result in test_results.items():
        status = "成功" if result else "失败"
        print(f"{name.upper().ljust(8)}: {status}")

    print("\n操作说明:")
    print("1. 启动服务: uvicorn app:app --reload --port 8000")
    print("2. 确保服务运行在 http://localhost:8000")
    print("3. 直接运行本脚本: python test_abtest_api.py")
    print("4. 观察彩色输出结果，绿色为成功，红色为失败")
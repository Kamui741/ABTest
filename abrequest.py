'''
Author: ChZheng
Date: 2024-12-13 17:13:01
LastEditTime: 2024-12-13 17:13:21
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/abrequest.py
'''
import requests
import hmac
import hashlib
import time

# 配置参数
BASE_URL = "http://28.4.136.142"  # 服务器地址
APP_ID = 12345                    # 替换为实际的 app_id
EXPERIMENT_ID = 67890             # 替换为实际的 experiment_id
AK = "your_access_key"            # 替换为你的 Access Key
SK = "your_secret_key"            # 替换为你的 Secret Key

# 签名生成函数
def generate_signature(ak, sk, timestamp, path, params=None):
    """
    生成签名：将 Access Key、时间戳、请求路径等信息组合，进行 HMAC-SHA256 加密
    """
    params_str = "&".join(f"{k}={v}" for k, v in sorted((params or {}).items()))
    sign_data = f"{ak}{timestamp}{path}?{params_str}".encode("utf-8")
    signature = hmac.new(sk.encode("utf-8"), sign_data, hashlib.sha256).hexdigest()
    return signature

# 构建请求函数
def get_experiment_details(app_id, experiment_id):
    """
    获取实验配置的基础信息
    """
    try:
        # 构建请求路径
        path = f"/datataster/openapi/v1/apps/{app_id}/experiment/{experiment_id}/details"
        url = f"{BASE_URL}{path}"

        # 构建签名所需的时间戳
        timestamp = int(time.time())

        # 生成签名
        signature = generate_signature(AK, SK, timestamp, path)

        # 请求头设置
        headers = {
            "Content-Type": "application/json",
            "X-Access-Key": AK,
            "X-Signature": signature,
            "X-Timestamp": str(timestamp)
        }

        # 发送 GET 请求
        print("请求 URL:", url)
        print("请求头:", headers)
        response = requests.get(url, headers=headers)

        # 解析响应
        if response.status_code == 200:
            res_json = response.json()
            if res_json.get("code") == 200:
                print("✅ 请求成功，实验配置信息：")
                print(res_json["data"])
            else:
                print(f"❌ 请求失败，业务错误: {res_json.get('message')}")
        else:
            print(f"❌ 请求失败，HTTP 状态码: {response.status_code}, 响应内容: {response.text}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")

# 执行请求
if __name__ == "__main__":
    get_experiment_details(APP_ID, EXPERIMENT_ID)
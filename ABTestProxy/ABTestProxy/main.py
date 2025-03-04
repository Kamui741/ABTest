from v1_client import V1Client
from v2_client import V2Client
from adapters import V1Adapter, V2Adapter
from auth import V1SessionAuth, V2AKSKAuth
from config import config
from proxy import ABTestProxy
import os

def main_v1():
    """V1版本调用示例"""
    # 设置环境变量（实际使用应从安全渠道获取）
    os.environ.update({
        "USERNAME": "v1_user@example.com",
        "PASSWORD": "v1_password",
        "V1_BASE_URL": "https://28.4.136.142/datatester"
    })

    # 初始化组件
    config.RUNTIME_MODE = 'V1'
    auth = V1SessionAuth()
    client = V1Client()
    adapter = V1Adapter()
    proxy = ABTestProxy(client, adapter)
    app_id = 123
    # 1. 创建实验
    create_params = {
        "name":"测试实验2022041901",
        "mode": 1,
        "endpoint_type": 1,
        "duration": 20,
        "major_metric": 29806,
        "metrics": [29806],
        "versions": [
            {
                "type": 0,
                "name": "实验组2022041901",
                "config": {"shiyu_key": "hello"}
            },
            {
                "type": 1,
                "name": "对照组2022041901",
                "config": {"shiyu_key": "world"}
            }
        ],
        "layer_info": {
            "layer_id": -1,
            "version_resource": 0.7
        }
    }


    create_res = proxy.create_experiment(create_params)
    print(f"[V1] 创建实验结果：{create_res}")
    exp_id = create_res.get('data')

    # 2. 获取实验详情
    if exp_id:
        detail_params = {
            "experiment_id": exp_id,
            "app_id": app_id
            }
        detail_res = proxy.get_experiment_details(detail_params)
        print(f"[V1] 实验详情：{detail_res}")

    # 3. 生成报告
    report_params = {
        "app_id": 123,
        "experiment_id": exp_id,
        "report_type": "daily",
        "start_ts": 1625097600,  # 2021-07-01
        "end_ts": 1627689600,     # 2021-07-31
        "fliters": []
    }
    report = proxy.generate_report(report_params)
    print(f"[V1] 实验报告：{report}")

    # 4. 修改实验状态
    status_params = {
        "experiment_id": exp_id,
        "app_id": app_id,
        "action": "launch"
    }
    status_res = proxy.modify_experiment_status(status_params)
    print(f"[V1] 修改状态结果：{status_res}")

    # 5. 获取指标列表
    metric_params = {
        "app_id": 123,
        "keyword": "关键指标",
        "need_page": 1,
        "page_size": 5,
        "page": 1
    }
    metrics = proxy.list_available_metrics(metric_params)
    print(f"[V1] 指标列表：{metrics}")

    # 6. 获取互斥组列表
    group_params = {
        "app_id": 123,
        "keyword": "互斥组",
        "need_page": 1,
        "page_size": 5,
        "page": 1
    }
    groups = proxy.list_mutex_groups(group_params)
    print(f"[V1] 互斥组列表：{groups}")



def main_v2():
    """V2版本调用示例"""
    # 设置环境变量（实际使用应从安全渠道获取）
    os.environ.update({
        "V2_ACCESS_KEY": "your_ak",
        "V2_SECRET_KEY": "your_sk",
        "V2_BASE_URL": "https://new.abtest.com/api/v2"
    })

    # 初始化组件
    config.RUNTIME_MODE = 'V2'
    auth = V2AKSKAuth()
    client = V2Client(auth)
    adapter = V2Adapter()
    proxy = ABTestProxy(client, adapter)

    # 1. 创建实验
    create_params = {
        "name": "V2优化实验",
        "mode": 1,
        "app_id": 456,
        "duration": 604800,  # 7天
        "major_metric": "metric_123",
        "metrics": ["metric_123", "metric_456"],
        "versions": [
            {
                "type": 0,
                "name": "对照组",
                "config": {"color": "blue"}
            },
            {
                "type": 1,
                "name": "实验组",
                "config": {"color": "red"}
            }
        ]
    }
    create_res = proxy.create_experiment(create_params)
    print(f"[V2] 创建实验结果：{create_res}")
    exp_id = create_res.get('data', {}).get('id')

    # 2. 获取实验详情
    if exp_id:
        detail_params = {
            "experiment_id": exp_id,}
        detail_res = proxy.get_experiment_details(detail_params)
        print(f"[V2] 实验详情：{detail_res}")

    # 3. 修改实验状态
    status_params = {
        "experiment_id": exp_id,
        "action": "launch"
    }
    status_res = proxy.modify_experiment_status(status_params)
    print(f"[V2] 修改状态结果：{status_res}")

    # 4. 获取指标列表
    metric_params = {
        "app_id": 456,
        "keyword": "留存率",
        "page": 1,
        "page_size": 10
    }
    metrics = proxy.list_available_metrics(metric_params)
    print(f"[V2] 指标列表：{metrics}")

    # 5. 获取互斥组列表
    group_params = {
        "app_id": 456,
        "keyword": "核心业务"
    }
    groups = proxy.list_mutex_groups(group_params)
    print(f"[V2] 互斥组列表：{groups}")

    # 6. 生成报告
    report_params = {
        "app_id": 456,
        "experiment_id": exp_id,
        "report_type": "overall",
        "start_ts": 1625097600,
        "end_ts": 1627689600
    }
    report = proxy.generate_report(report_params)
    print(f"[V2] 实验报告：{report}")

if __name__ == "__main__":
    print("========= V1版本调用示例 =========")
    main_v1()

    print("\n========= V2版本调用示例 =========")
    main_v2()
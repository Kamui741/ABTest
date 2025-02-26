# test_integration.py
from config import config
from factories import AuthFactory, ClientFactory

def test_v1_functions():
    """测试V1全部六个功能"""
    print("\n============== V1功能测试 ==============")
    config.RUNTIME_MODE = 'V1'
    client = ClientFactory.create(AuthFactory.create())

    # 测试数据
    test_app_id = 1001
    test_flight_id = 123  # 需要先创建或使用已有ID

    try:
        # 1. 创建实验
        print("\n[1] 创建实验:")
        create_res = client.create_experiment({
            "flight_name": "V1测试实验",
            "duration": 7,
            "hash_strategy": "ssid",
            "app_id": test_app_id
        })
        print("创建结果:", create_res)

        # 2. 获取实验详情
        print("\n[2] 获取实验详情:")
        detail = client.get_experiment_details(test_flight_id)
        print("详情:", detail)

        # 3. 生成报告
        print("\n[3] 生成报告:")
        report = client.generate_report({
            "app_id": test_app_id,
            "flight_id": test_flight_id,
            "report_type": "day",
            "start_ts": 1672502400,
            "end_ts": 1672588800
        })
        print("报告:", report)

        # 4. 修改状态
        print("\n[4] 修改状态:")
        status = client.modify_experiment_status(test_flight_id, "stop")
        print("状态修改:", status)

        # 5. 指标列表
        print("\n[5] 指标列表:")
        metrics = client.list_available_metrics({
            "app_id": test_app_id,
            "keyword": "核心"
        })
        print("指标:", metrics)

        # 6. 互斥组
        print("\n[6] 互斥组列表:")
        groups = client.list_mutex_groups({
            "app_id": test_app_id
        })
        print("互斥组:", groups)

    except Exception as e:
        print(f"V1测试失败: {str(e)}")

def test_v2_functions():
    """测试V2全部六个功能"""
    print("\n============== V2功能测试 ==============")
    config.RUNTIME_MODE = 'V2'
    client = ClientFactory.create(AuthFactory.create())

    # 测试数据
    test_app_id = 2002
    test_exp_id = 456  # 需要先创建或使用已有ID

    try:
        # 1. 创建实验
        print("\n[1] 创建实验:")
        create_res = client.create_experiment({
            "app_id": test_app_id,
            "name": "V2测试实验",
            "mode": 1,
            "endpoint_type": 1,
            "duration": 14,
            "major_metric": 29806,
            "metrics": [29806, 15432],
            "versions": [
                {
                    "type": 0,
                    "name": "V2对照组",
                    "config": {"feature_flag": "control"}
                },
                {
                    "type": 1,
                    "name": "V2实验组",
                    "config": {"feature_flag": "experiment"}
                }
            ]
        })
        print("创建结果:", create_res)

        # 2. 获取实验详情
        print("\n[2] 获取实验详情:")
        detail = client.get_experiment_details({
            "app_id": test_app_id,
            "experiment_id": test_exp_id
        })
        print("详情:", detail)

        # 3. 生成报告
        print("\n[3] 生成报告:")
        report = client.generate_report({
            "app_id": test_app_id,
            "experiment_id": test_exp_id,
            "report_type": "day",
            "start_ts": 1672502400,
            "end_ts": 1672588800
        })
        print("报告:", report)

        # 4. 修改状态
        print("\n[4] 修改状态:")
        status = client.modify_experiment_status({
            "app_id": test_app_id,
            "experiment_id": test_exp_id,
            "action": "stop"
        })
        print("状态修改:", status)

        # 5. 指标列表
        print("\n[5] 指标列表:")
        metrics = client.list_available_metrics({
            "app_id": test_app_id,
            "page": 1,
            "page_size": 10
        })
        print("指标:", metrics)

        # 6. 互斥组
        print("\n[6] 互斥组列表:")
        groups = client.list_mutex_groups({
            "app_id": test_app_id,
            "page": 1,
            "page_size": 10
        })
        print("互斥组:", groups)

    except Exception as e:
        print(f"V2测试失败: {str(e)}")

if __name__ == "__main__":
    # 运行V1测试
    test_v1_functions()

    # 运行V2测试
    test_v2_functions()

    print("\n============== 测试完成 ==============")
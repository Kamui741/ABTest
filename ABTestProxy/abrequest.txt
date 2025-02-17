"""
主函数调用示例（集成二期接口）
"""

from ABTestProxy import SessionManager, V1Client, FieldMapper

def main():
    # 初始化会话管理
    session = SessionManager(
        login_url="https://28.4.136.142/api/login",
        session_file="session.txt"
    )

    # 创建客户端实例
    mapper = FieldMapper(config_path="config/v2_proxy")
    v1_client = V1Client(session)
    proxy = ABTestProxy(v1_client, mapper)

    # 示例应用ID
    demo_app_id = 1001

    try:
        # ================== 1. 创建实验 ==================
        create_params = {
            "name": "新用户引导实验V2",
            "app_id": demo_app_id,
            "mode": 1,
            "endpoint_type": 1,
            "duration": 30,
            "major_metric": 30001,
            "metrics": [30001, 30002],
            "versions": [
                {
                    "type": 0,
                    "name": "对照组_V2",
                    "config": {"feature_flag": "control"}
                },
                {
                    "type": 1,
                    "name": "实验组_V2",
                    "config": {"feature_flag": "experiment"},
                    "weight": 0.6
                }
            ],
            "layer_info": {
                "layer_id": -1,
                "version_resource": 0.7
            }
        }
        creation_res = proxy.create_experiment(create_params)
        if creation_res["code"] != 200:
            raise RuntimeError(f"创建失败: {creation_res['message']}")

        experiment_id = creation_res["data"]
        print(f"成功创建实验，ID: {experiment_id}")

        # ================== 2. 获取实验配置 ==================
        detail_params = {
            "app_id": demo_app_id,
            "experiment_id": experiment_id
        }
        detail_res = proxy.get_experiment_details(detail_params)
        print("实验配置详情:", detail_res["data"])

        # ================== 3. 获取指标报告 ==================
        report_params = {
            "app_id": demo_app_id,
            "experiment_id": experiment_id,
            "report_type": "day",
            "start_ts": 1672502400,  # 2023-01-01
            "end_ts": 1675084800,     # 2023-01-31
            "trace_data": []
        }
        report_res = proxy.generate_report(report_params)
        print("指标报告:", report_res["data"]["calculation_results"])

        # ================== 4. 启动实验 ==================
        launch_params = {
            "app_id": demo_app_id,
            "experiment_id": experiment_id
        }
        launch_res = proxy.modify_experiment_status(launch_params)
        print("启动结果:", "成功" if launch_res["success"] else "失败")

        # ================== 5. 获取指标列表 ==================
        metric_params = {
            "app_id": demo_app_id,
            "keyword": "留存率",
            "page_size": 20,
            "page": 1
        }
        metric_res = proxy.list_available_metrics(metric_params)
        print("指标列表:", metric_res["metrics"][:2])  # 打印前两个结果

        # ================== 6. 获取互斥组 ==================
        layer_params = {
            "app_id": demo_app_id,
            "keyword": "核心功能",
            "page_size": 10,
            "page": 1
        }
        layer_res = proxy.list_mutex_groups(layer_params)
        print("互斥组列表:", layer_res["groups"][:1])  # 打印第一个结果

    except Exception as e:
        print(f"操作失败: {str(e)}")
        # 这里可以添加重试或回滚逻辑

if __name__ == "__main__":
    # 初始化日志等配置
    import logging
    logging.basicConfig(level=logging.INFO)

    main()
# 初始化V2客户端
auth = V2AKSKAuth()
client = V2Client(auth)

# 创建实验
response = client.create_experiment(
    app_id=1001,
    params={
        "name": "新用户引导优化V2",
        "mode": 1,
        "endpoint_type": 1,
        "duration": 30,
        "major_metric": 30001,
        "metrics": [30001, 30002],
        "versions": [
            {
                "type": 0,
                "name": "对照组",
                "config": {"feature_flag": "control"},
                "weight": 0.5
            },
            {
                "type": 1,
                "name": "实验组",
                "config": {"feature_flag": "experiment"},
                "weight": 0.5
            }
        ],
        "layer_info": {
            "layer_id": -1,
            "version_resource": 0.7
        }
    }
)

# 获取实验报告
report = client.generate_report(
    app_id=1001,
    experiment_id=response["data"]["id"],
    report_type="day",
    start_ts=int(datetime(2023, 1, 1).timestamp()),
    end_ts=int(datetime(2023, 1, 31).timestamp())
)
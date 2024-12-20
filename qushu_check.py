import os
import sys
import requests
import pandas as pd
from pyspark.sql import SparkSession
from datetime import datetime, timedelta
import subprocess

# 获取昨天的日期
yesterday_date = (datetime.now() - timedelta(1)).strftime('%Y%m%d')

# 配置环境
dtf_dir = "/nas/data/"
dtf_file = f"{dtf_dir}/dtf_file_{yesterday_date}.dtf"

# 设置今天日期
today_date = datetime.now().strftime('%Y%m%d')

# 初始化 Spark 会话
spark = SparkSession.builder \
    .appName("DataLakeValidation") \
    .enableHiveSupport() \
    .getOrCreate()

# 执行初始化 keytab 脚本
def init_keytab():
    try:
        print("Initializing keytab...")
        result = subprocess.run(["sh", "/root/init_keytab.sh"], check=True, capture_output=True, text=True)
        print("Keytab initialization successful.")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error during keytab initialization: {e.stderr}")
        sys.exit(1)

# 执行 Hive SQL 查询
def get_hive_row_count():
    sql_query = f"SELECT count(*) FROM sdms_re_dw.d_cabs_001_events_all_a WHERE dt = '{today_date}';"
    print(f"Executing SQL query: {sql_query}")
    df = spark.sql(sql_query)
    return df.collect()[0][0]

# 获取 DTF 文件的行数
def get_dtf_row_count():
    print(f"Reading DTF file: {dtf_file}")
    df = pd.read_csv(dtf_file, delimiter='\x03', header=None)
    return len(df)

# 发送警报
def send_alert(message):
    alert_url = "http://26.7.31.220:29494/send_wechat"
    payload = {
        "sender": [""],
        "receivers": "gonghao",
        "body": f"通用技术组 wechat测试--[中信大脑推理平台] {message}"
    }
    response = requests.post(alert_url, json=payload)
    if response.status_code == 200:
        print("Alert sent successfully!")
    else:
        print(f"Failed to send alert: {response.status_code}")

# 主逻辑
def main():
    # 初始化 keytab
    init_keytab()

    # 获取 Hive 行数
    hive_count = get_hive_row_count()
    print(f"Hive row count: {hive_count}")

    # 获取 DTF 文件的行数
    dtf_row_count = get_dtf_row_count()
    print(f"DTF row count: {dtf_row_count}")

    # 对比行数
    if hive_count != dtf_row_count:
        message = f"行数不匹配: Hive 表行数为 {hive_count}，DTF 文件行数为 {dtf_row_count}"
        send_alert(message)
    else:
        print("Row counts match. No alert sent.")

    # 停止 Spark 会话
    spark.stop()

if __name__ == "__main__":
    main()
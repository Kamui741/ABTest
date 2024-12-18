'''
Author: ChZheng
Date: 2024-12-18 19:43:32
LastEditTime: 2024-12-18 19:43:33
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/qushu_check.py
'''
import subprocess
import os
import requests
import pandas as pd
from pyspark.sql import SparkSession
from datetime import datetime, timedelta

# 初始化 keytab
def init_keytab():
    print("Initializing keytab...")
    subprocess.run(["sh", "/root/init_keytab.sh"], check=True)

# Kerberos 认证
kerberos_user = "your_user@YOUR_REALM"
keytab_path = "/path/to/your/keytab"

def kerberos_authenticate():
    cmd = f"kinit -kt {keytab_path} {kerberos_user}"
    subprocess.run(cmd, check=True)

# 获取昨天的日期
yesterday_date = (datetime.now() - timedelta(1)).strftime('%Y%m%d')

# 配置环境
dtf_dir = "/nas/data/"
dtf_file = f"{dtf_dir}/dtf_file_{yesterday_date}.dtf"

# 设置今天日期
today_date = datetime.now().strftime('%Y%m%d')

# 创建 Spark 会话
def create_spark_session():
    spark = SparkSession.builder \
        .appName("DataLakeValidation") \
        .enableHiveSupport() \
        .config("spark.sql.warehouse.dir", "/user/hive/warehouse") \
        .config("spark.hadoop.hive.metastore.uris", "thrift://metastore_host:port") \
        .config("spark.yarn.access.hadoopFileSystems", "hdfs://namenode_host:8020") \
        .config("spark.hadoop.security.authentication", "kerberos") \
        .config("spark.yarn.keytab", keytab_path) \
        .config("spark.yarn.principal", kerberos_user) \
        .getOrCreate()

    return spark

spark = create_spark_session()

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

    # Kerberos 认证
    kerberos_authenticate()

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
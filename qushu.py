'''
Author: ChZheng
Date: 2024-12-13 16:21:49
LastEditTime: 2024-12-13 17:16:03
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/qushu.py
'''

挖掘ds - spark3-lzw - spark3
shell:

source /etc/profile
cd `dirname $0`
base_dir=`pwd`
echo $base_dir

sh /root/init_keytab_cabt.sh
sql_file = abtest-qushu-check/test.sql
sh abtest-qushu-check/sql_execute.sh $sql_file
exit 0

tes.sql:

select count(*) from sdms_re_dw.d_cabs_001_events_all_a where drt = '';


sql_executor.py

import os
import sys
import importlib
import argparse

from pyspark.sql import SparkSession

sys.path.append(".")
base_dir= os.path.split(os.path.realpath(__file__))[0]
sys.path.append(base_dir)

def read_sql(sql_text):
    hsql = ""
    flag = False
    for line in sql_text.split("\n"):
        sql_line = line.strip()
        if not (sql_line.startswith("--") or sql_line == "#" or sql_line == ""):
            if sql_line.startswith("/*"):
                flag = True
            elif sql_line.startswith("*/"):
                flag = False
            if (not flag) and (not sql_line.startswith("*/")):
                hsql = hsql + slq_line + "\n"

    return hsql

if __name__ == "__main__":
    importlib.reload(sys)
    parser = argparse.ArgumentParser()
    parser.add_argument("--hsql",type=str,default="None")
    parser.add_argument("--output",type=str,default="None")
    args = parser.parse_args()

    spark = SparkSession.builder.enableHiveSupport().getOrCreate()
    sc = spark.sparkContext
    hsql = args.hsql
    out_put = args.output

    sql_list = read_sql(hsql)[:-1].split(";")
    sql = list(filter(None, sql_list))
    for i in sql:
        print("hsql is :%s "%i)
        spark.sql(i).show()

    print("sql execute success")

    spark.stop()

    print("sql results have been stored in hdfs address :{} successfully!".format(out_put))


sql_execute.sh

#!/bin/bash
#use timestamp to avoid file name conflict
sql_file=$1
log_file='sql' echo $RANDOM '.log'

hsql = `cat $sql_file`

hdfs_file = "bdsdms_ads/bdcabtApp/yarn_res_liuzhiwei"

local_file = "/data/yarn_res_liuzhiwei"
NUM_EXEC = 1
NUM_CORES = 2
MEM_DRIVER = 2g
MEM_EXECUTOR = 4G

QUEUE = "SDMS_ADS_CABT"

spark-submit \
--master yarn \
--deploy-mode cluster \
--archives hdfs:///bdsdms_ads/bdcabtApp/env/spark3.tar.gz#env \
--num-executors $NUM_EXEC \
--executor-cores $NUM_CORES \
--driver-memory $MEM_DRIVER \
--executor-memory $MEM_EXECUTOR \
--conf spark.yarn.maxAppAttentmpts=1 \
--conf spark.driver.maxResultSize=2g \
--conf spark.sql.shuffle.partitions=200 \
--conf spark.sql.broadcastTimeout=1800 \
--conf spark.driver.memoryOverhead=2g \
--conf spark.executor.memoryOverhead=2g \
--conf spark.yarn.queue=$QUEUE \
--conf spark.executor.extraJavaOptions="-Xss30M"    \
--conf spark.yarn.appMasterEnv.PYSPARK_PYTHON=./env/bin/python \
--name "feature_store_sql_executor.py" \
abtest-qushu-check/sqkl_execute.py \
--output "${hdfs_file}/rst.csv" \
--hsql "${hsql}" 2>&1 | tee ${log_file}

application_id=`cat /tmp/${log_file} | grep -P '(state: Finished)' | awk '{print $8}'`

echo "application_id is :${application_id

rm -rf /tmp/${log_file}

echo "======================get res ==================="

echo "--------------------start querying yarn logs for ${application_id}--------------------------"


dtf check

import pandas as pd

df = pd.read_csv("finename.dtf",'\x03',header=None)

print(df)

行数

信随行  zdjx_cuijunlong  http_test message_end_wechat

curl -X POST -H "Content-Type: application/json" -d  '{"sender":[""],"receivers":"gonghao","body":"通用技术组 wechat测试--[中信大脑推理平台]"}' http://26.7.31.220:29494/send_wechat
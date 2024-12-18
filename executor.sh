###
 # @Author: ChZheng
 # @Date: 2024-12-18 19:46:21
 # @LastEditTime: 2024-12-18 19:46:22
 # @LastEditors: ChZheng
 # @Description:
 # @FilePath: /code/ABTest/executor.sh
###

# sql_execute.sh

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

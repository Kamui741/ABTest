'''
Author: ChZheng
Date: 2024-12-18 19:46:29
LastEditTime: 2024-12-18 19:46:30
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/executor.py
'''
# sql_executor.py

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
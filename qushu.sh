#!/bin/bash
###
 # @Author: ChZheng
 # @Date: 2024-12-17 15:03:17
 # @LastEditTime: 2024-12-17 16:16:42
 # @LastEditors: ChZheng
 # @Description:
 # @FilePath: /code/ABTest/qushu.sh
###
source /etc/profile
cd `dirname $0`
base_dir=`pwd`

# 初始化 keytab（认证）
sh /root/init_keytab_cabt.sh

# 定义 SQL 和本地 DTF 文件目录
dtf_dir="/nas/data/"
today_date=$(date +%Y%m%d)

# 动态生成 SQL 文件内容，使用当前日期作为查询条件
sql_file="abtest-qushu-check/test.sql"

# 创建 SQL 查询内容，替换 dt 为当前日期
sql_query="select count(*) from sdms_re_dw.d_cabs_001_events_all_a where dt = '${today_date}';"

# 将 SQL 内容写入临时文件
echo "$sql_query" > $sql_file

# 执行 SQL 查询并直接捕获结果
echo "Executing SQL query with dt=${today_date}..."
hive_count=$(sh abtest-qushu-check/sql_execute.sh "$sql_file" | grep -oP "\d+" | tail -1)

# 检查是否成功获取 Hive 表行数
if [ -z "$hive_count" ]; then
    echo "ERROR: Failed to retrieve Hive row count."
    exit 1
fi
echo "Hive row count: $hive_count"

# 执行 Python 脚本，进行 DTF 行数统计和对比
alert_url="http://26.7.31.220:29494/send_wechat"  # 警告通知 URL

echo "Comparing Hive row count with DTF file row count..."
python3 abtest-qushu-check/compare_row_counts.py \
    --hive_count "$hive_count" \
    --base_dir "$dtf_dir" \
    --date "$today_date" \
    --alert_url "$alert_url"

# 检查 Python 脚本的执行状态
if [ $? -ne 0 ]; then
    echo "Row count mismatch detected. Alert has been sent."
else
    echo "Row counts match. No action required."
fi

exit 0
'''
Author: ChZheng
Date: 2024-12-17 15:05:29
LastEditTime: 2024-12-17 16:14:12
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/check_dtf.py
'''
import argparse
import os
import pandas as pd
from datetime import datetime
import json

def find_dtf_file(base_dir, date_str):
    """
    在指定目录下，根据日期匹配文件名，返回对应的 dtf 文件路径。
    """
    for filename in os.listdir(base_dir):
        if date_str in filename and filename.endswith(".dtf"):
            return os.path.join(base_dir, filename)
    print(f"ERROR: No DTF file found for date: {date_str}")
    exit(1)

def count_dtf_lines(file_path):
    """
    读取 DTF 文件并计算行数。
    """
    print(f"Reading DTF file: {file_path}")
    try:
        df = pd.read_csv(file_path, sep='\x03', header=None)
        line_count = len(df)
        print(f"Line count in DTF file: {line_count}")
        return line_count
    except Exception as e:
        print(f"ERROR: Failed to read DTF file. Details: {e}")
        exit(1)

def compare_counts(hive_count, dtf_count, tolerance_percentage=0.1):
    """
    对比 Hive 行数和 DTF 行数，考虑误差范围
    tolerance_percentage: 容忍的百分比误差（10%）
    tolerance_absolute: 容忍的绝对行数差异（100行）
    """
    # 计算行数差异的绝对值
    count_difference = abs(hive_count - dtf_count)

    # 容忍范围：相对误差和绝对误差
    if count_difference <= hive_count * tolerance_percentage :
        print(f"Row counts are within the tolerance range (difference: {count_difference}).")
        return True
    else:
        print(f"ERROR: Row counts do not match! Hive count: {hive_count}, DTF count: {dtf_count}")
        return False

def send_alert(alert_url, hive_count, dtf_count):
    """
    发送警报，使用固定格式
    """
    alert_message = {
        "sender": [""],
        "receivers": "gonghao", #逗号分割
        "body": f"通用技术组 wechat测试--[中信大脑推理平台] Hive行数: {hive_count}, DTF行数: {dtf_count} 不匹配！"
    }
    try:
        curl_command = f"""curl -X POST -H "Content-Type: application/json" \
            -d '{json.dumps(alert_message)}' {alert_url}"""
        os.system(curl_command)
        print(f"Alert sent successfully via curl to {alert_url}")
    except Exception as e:
        print(f"ERROR: Failed to send alert. Details: {e}")
        exit(1)

def main():
    parser = argparse.ArgumentParser(description="Compare Hive row count with DTF file row count.")
    parser.add_argument("--hive_count", type=int, required=True, help="Row count from Hive SQL query.")
    parser.add_argument("--base_dir", type=str, required=True, help="Directory containing DTF files.")
    parser.add_argument("--date", type=str, required=True, help="Date string to match DTF file (e.g., '20240613').")
    parser.add_argument("--alert_url", type=str, required=True, help="URL for sending alerts via curl.")
    parser.add_argument("--tolerance_percentage", type=float, default=0.1, help="Percentage tolerance for row count difference (e.g., 0.1 for 10%).")
    parser.add_argument("--tolerance_absolute", type=int, default=100, help="Absolute tolerance for row count difference (e.g., 100 rows).")
    args = parser.parse_args()

    # 查找 DTF 文件并计算行数
    dtf_file = find_dtf_file(args.base_dir, args.date)
    dtf_count = count_dtf_lines(dtf_file)

    # 对比行数
    if compare_counts(args.hive_count, dtf_count, args.tolerance_percentage):
        print("SUCCESS: Row counts match within tolerance.")
        exit(0)
    else:
        # 发送警告
        send_alert(args.alert_url, args.hive_count, dtf_count)
        exit(1)

if __name__ == "__main__":
    main()
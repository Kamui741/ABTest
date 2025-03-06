'''
Author: ChZheng
Date: 2025-03-06 17:06:14
LastEditTime: 2025-03-06 17:12:54
LastEditors: ChZheng
Description:
FilePath: /ABTest/ABTestProxy/test/conftest.py
'''
# tests/conftest.py
import sys
import os

# 获取当前测试目录的绝对路径
test_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录（即ABTestProxy文件夹）
project_root = os.path.dirname(test_dir)
# 将根目录添加到Python路径
sys.path.insert(0, project_root)
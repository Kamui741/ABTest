'''
Author: ChZheng
Date: 2025-02-13 14:35:24
LastEditTime: 2025-02-13 17:11:11
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/api/ABTestProxy/config.py
'''
# # ================== 配置模块 ==================
# [ABTestProxy/config.py]
# |- ABTestConfig
# |- LOGIN_URL
# |- TARGET_URLS
import os
class ABTestConfig:
    SESSION_FILE = os.getenv('SESSION_FILE', 'session.txt')

# 认证信息从环境变量获取
username = os.getenv("USERNAME", "admin")
password = os.getenv("PASSWORD", "admin123")
LOGIN_URL = os.getenv('LOGIN_URL', 'https://28.4.136.142/api/login')
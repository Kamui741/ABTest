'''
Author: ChZheng
Date: 2025-02-13 14:35:24
LastEditTime: 2025-02-14 11:37:29
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
# 会话配置
SESSION_FILE = os.getenv('SESSION_FILE', 'session.txt')
LOGIN_URL = os.getenv('LOGIN_URL', 'https://28.4.136.142/api/login')
TARGET_URLS = "https://28.4.136.142/api/v1/target"
# 认证信息
USERNAME = os.getenv("USERNAME", "admin")
PASSWORD = os.getenv("PASSWORD", "admin123")
'''
Author: ChZheng
Date: 2025-02-12 04:41:20
LastEditTime: 2025-02-12 04:42:23
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/api/qushu/core/config.py
'''
# core/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent.parent
load_dotenv(BASE_DIR / ".env")

class AppConfig:
    """应用配置中心"""

    # 认证配置
    USERNAME = os.getenv("ABTEST_USERNAME", "admin")
    PASSWORD = os.getenv("ABTEST_PASSWORD", "admin123")
    SESSION_FILE = Path(os.getenv("SESSION_FILE", BASE_DIR / ".session"))

    # 服务端点
    V1_BASE_URL = os.getenv("V1_BASE_URL", "http://localhost:8000")
    V2_BASE_URL = os.getenv("V2_BASE_URL", "http://localhost:8001")
    V1_LOGIN_URL = f"{V1_BASE_URL}/api/login"

    # 运行模式
    USE_V2_DIRECT = os.getenv("USE_V2_DIRECT", "false").lower() == "true"
    V1_ADAPTER_MODE = os.getenv("V1_ADAPTER_MODE", "proxy")

    # 路径配置
    MAPPING_DIR = BASE_DIR / "config/mappings"

    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls):
        """验证配置有效性"""
        if not cls.MAPPING_DIR.exists():
            raise ValueError(f"Mapping directory {cls.MAPPING_DIR} not exists")
        if cls.V1_ADAPTER_MODE not in ["proxy", "direct"]:
            raise ValueError("Invalid V1_ADAPTER_MODE")

AppConfig.validate()
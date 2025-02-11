'''
Author: ChZheng
Date: 2025-02-12 04:41:53
LastEditTime: 2025-02-12 04:50:36
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/api/qushu/core/exceptions.py
'''
# project/core/exceptions.py
class ABTestError(Exception):
    """基础异常类"""
    def __init__(self, message: str, code: int = 500):
        super().__init__(message)
        self.code = code

class ConfigurationError(ABTestError):
    """配置错误"""
    def __init__(self, message: str):
        super().__init__(f"Configuration Error: {message}", 500)

class AuthError(ABTestError):
    """认证错误"""
    def __init__(self, message: str):
        super().__init__(f"Authentication Failed: {message}", 401)

class APIClientError(ABTestError):
    """API客户端错误"""
    def __init__(self, message: str):
        super().__init__(f"API Client Error: {message}", 503)

class MappingError(ABTestError):
    """映射错误"""
    def __init__(self, message: str):
        super().__init__(f"Mapping Error: {message}", 422)
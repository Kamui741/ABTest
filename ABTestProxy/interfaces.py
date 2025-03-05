'''
Author: ChZheng
Date: 2025-02-26 08:51:59
LastEditTime: 2025-02-26 14:48:36
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/ABTestProxy/ABTestProxy/interfaces.py
'''
# ---------------------- interfaces.py ----------------------
from abc import ABC, abstractmethod
from typing import Dict, Optional

class IAuthProvider(ABC):
    @abstractmethod
    def get_auth_headers(self) -> Dict[str, str]:
        """获取认证头信息"""
        pass

class IApiClient(ABC):
    @abstractmethod
    def create_experiment(self, params: Dict) -> Dict:
        """创建实验（需实现参数校验）"""
        pass

    @abstractmethod
    def get_experiment_details(self, exp_id: str) -> Dict:
        """获取实验详情（需支持多种ID格式）"""
        pass

    @abstractmethod
    def generate_report(self, params: Dict) -> Dict:
        """生成实验报告（需处理时间范围校验）"""
        pass

    @abstractmethod
    def modify_experiment_status(self, exp_id: str, action: str) -> Dict:
        """修改实验状态（需实现状态机校验）"""
        pass

    @abstractmethod
    def list_available_metrics(self, params: Dict) -> Dict:
        """获取指标列表（需支持分页）"""
        pass

    @abstractmethod
    def list_mutex_groups(self, params: Dict) -> Dict:
        """获取互斥组列表（需支持关键字过滤）"""
        pass

class IAdapter(ABC):
    @staticmethod
    @abstractmethod
    def convert_create_experiment_request(params: Dict) -> Dict:
        """转换创建实验请求参数"""
        pass

    @staticmethod
    @abstractmethod
    def convert_get_experiment_details_response(response: Dict) -> Dict:
        """转换实验详情响应格式"""
        pass

    @staticmethod
    @abstractmethod
    def convert_report_response(response: Dict) -> Dict:
        """转换实验报告响应格式"""
        pass

    @classmethod
    @abstractmethod
    def convert_metric_response(cls, response: Dict) -> Dict:
        """转换指标列表响应格式"""
        pass
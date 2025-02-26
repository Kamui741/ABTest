'''
Author: ChZheng
Date: 2025-02-25 19:36:47
LastEditTime: 2025-02-26 06:55:50
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/ABTestProxy/ABTestProxy/interfaces.py
'''
# ---------------------- interfaces.py ----------------------
from abc import ABC, abstractmethod
from typing import Dict

class IAuthProvider(ABC):
    @abstractmethod
    def get_auth_headers(self) -> Dict[str, str]:
        pass

class IApiClient(ABC):
    @abstractmethod
    def create_experiment(self, params: Dict) -> Dict:
        pass

    @abstractmethod
    def get_experiment_details(self, exp_id: str) -> Dict:
        pass

class IAdapter(ABC):
    @staticmethod
    @abstractmethod
    def convert_request(params: Dict) -> Dict:
        pass

    @staticmethod
    @abstractmethod
    def convert_response(response: Dict) -> Dict:
        pass
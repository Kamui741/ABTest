'''
Author: ChZheng
Date: 2025-02-25 14:32:08
LastEditTime: 2025-02-25 15:52:19
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/ABTestProxy/ABTestProxy/interfaces.py
'''
# ---------------------- interfaces.py ----------------------
from abc import ABC, abstractmethod
from typing import Dict, Any

class IExperimentService(ABC):
    @abstractmethod
    def create_experiment(self, name: str, app_id: int, metrics: list) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_details(self, experiment_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def generate_report(self, experiment_id: str, start: int, end: int) -> Dict[str, Any]:
        pass

class IApiClient(ABC):
    @abstractmethod
    def post(self, endpoint: str, data: dict) -> dict:
        pass

    @abstractmethod
    def get(self, endpoint: str, params: dict) -> dict:
        pass
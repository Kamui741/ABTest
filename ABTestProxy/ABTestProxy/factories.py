'''
Author: ChZheng
Date: 2025-02-26 06:57:42
LastEditTime: 2025-02-26 06:57:43
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/ABTestProxy/ABTestProxy/factories.py
'''
# ---------------------- factories.py ----------------------
from interfaces import IAuthProvider, IApiClient, IAdapter
from auth import V1SessionAuth, V2AKSKAuth
from v1_client import V1Client
from v2_client import V2Client
from adapters import V1Adapter, V2Adapter
from config import config

class AuthFactory:
    @staticmethod
    def create() -> IAuthProvider:
        if config.RUNTIME_MODE == 'V1':
            return V1SessionAuth()
        return V2AKSKAuth()

class ClientFactory:
    @staticmethod
    def create(auth: IAuthProvider) -> IApiClient:
        if config.RUNTIME_MODE == 'V1':
            return V1Client()
        return V2Client(auth)

class AdapterFactory:
    @staticmethod
    def create() -> IAdapter:
        if config.RUNTIME_MODE == 'V1':
            return V1Adapter()
        return V2Adapter()
'''
Author: ChZheng
Date: 2025-02-26 06:57:42
LastEditTime: 2025-03-05 09:06:28
LastEditors: ChZheng
Description:
FilePath: /ABTest/ABTestProxy/ABTestProxy/factories.py
'''
# ---------------------- factories.py ----------------------
from interfaces import IAuthProvider, IApiClient, IAdapter
from auth import V1AuthProvider, V2AuthProvider
from v1_client import V1Client
from v2_client import V2Client
from adapters import V1Adapter, V2Adapter
from config import config

class AuthFactory:
    @staticmethod
    def create(version: str) -> IAuthProvider:
        if version == 'V1':
            return V1AuthProvider()
        return V2AuthProvider()

class ClientFactory:
    @staticmethod
    def create(version: str, auth: IAuthProvider) -> IApiClient:
        if version == 'V1':
            return V1Client()
        return V2Client(auth)

class AdapterFactory:
    @staticmethod
    def create(version: str) -> IAdapter:
        if version == 'V1':
            return V1Adapter()
        return V2Adapter()
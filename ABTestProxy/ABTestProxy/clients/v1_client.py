'''
Author: ChZheng
Date: 2025-02-13 14:34:19
LastEditTime: 2025-02-18 15:56:26
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/ABTestProxy/ABTestProxy/clients/v1_client.py
'''

# [ABTestProxy/clients/v1_client.py]
# |- V1Client
#    |- create_experiment
#    |- get_experiment
#    |- get_report
#    |- update_status
#    |- list_metrics
#    |- list_layers

from typing import Dict
from auth import SessionManager
from api.core import (
    create_experiment,
    get_flight_config,
    get_experiment_report,
    update_flight_status,
    get_metric_list,
    get_mutex_group_list
)

class V1Client:
    def __init__(self, session_manager: SessionManager):
        self.session = session_manager

    def create_experiment(self, **params) -> Dict:
        return create_experiment(
            flight_name=params['flight_name'],
            duration=params['duration'],
            hash_strategy=params.get('hash_strategy', 'ssid'),
            app_id=params['app_id']
        )

    def get_experiment(self, **params) -> Dict:
        return get_flight_config(
            flight_id=params['flight_id'],
            is_duplicate=params.get('is_duplicate', False)
        )

    def get_report(self, **params) -> Dict:
        return get_experiment_report(
            app_id=params['app_id'],
            flight_id=params['flight_id'],
            report_type=params['report_type'],
            start_ts=params['start_ts'],
            end_ts=params['end_ts'],
            trace_data=params.get('trace_data', '')
        )

    def update_status(self, **params) -> Dict:
        return update_flight_status(
            flight_id=params['flight_id'],
            action=params['action']
        )

    def list_metrics(self, **params) -> Dict:
        return get_metric_list(
            app_id=params['app_id'],
            keyword=params.get('keyword', ''),
            status=params.get('status', 1),
            is_required=params.get('is_required', -1),
            need_page=params.get('need_page', 1),
            page_size=params.get('page_size', 10)
        )

    def list_layers(self, **params) -> Dict:
        return get_mutex_group_list(
            app_id=params['app_id'],
            keyword=params.get('keyword', ''),
            status=params.get('status', 1),
            need_page=params.get('need_page', 1),
            page_size=params.get('page_size', 10),
            page=params.get('page', 1),
            need_default=params.get('need_default', False)
        )
# ---------------------- clients/v1_client.py ----------------------
from typing import Dict, Any
from interfaces import IApiClient
from api.core import (
    create_experiment,
    get_flight_config,
    get_experiment_report,
    update_flight_status,
    get_metric_list,
    get_mutex_group_list
)

class V1Client(IApiClient):
    """V1客户端完整实现"""

    def create_experiment(self, params: Dict) -> Dict:
        """创建实验（参数需适配V1格式）"""
        return create_experiment(
            flight_name=params['flight_name'],
            duration=params['duration'],
            hash_strategy=params.get('hash_strategy', 'ssid'),
            app_id=params['app_id']
        )

    def get_experiment_details(self, exp_id: str) -> Dict:
        """获取实验详情"""
        return get_flight_config(
            flight_id=exp_id,
            is_duplicate=False
        )

    def generate_report(self, params: Dict) -> Dict:
        """生成实验报告"""
        return get_experiment_report(
            app_id=params['app_id'],
            flight_id=params['flight_id'],
            report_type=params['report_type'],
            start_ts=params['start_ts'],
            end_ts=params['end_ts'],
            trace_data=params.get('trace_data', '')
        )

    def modify_experiment_status(self, exp_id: str, action: str) -> Dict:
        """修改实验状态"""
        return update_flight_status(
            flight_id=exp_id,
            action=action
        )

    def list_available_metrics(self, params: Dict) -> Dict:
        """获取指标列表"""
        return get_metric_list(
            app_id=params['app_id'],
            keyword=params.get('keyword', ''),
            status=params.get('status', 1),
            is_required=params.get('is_required', -1),
            need_page=params.get('need_page', 1),
            page_size=params.get('page_size', 10)
        )

    def list_mutex_groups(self, params: Dict) -> Dict:
        """获取互斥组列表"""
        return get_mutex_group_list(
            app_id=params['app_id'],
            keyword=params.get('keyword', ''),
            status=params.get('status', 1),
            need_page=params.get('need_page', 1),
            page_size=params.get('page_size', 10),
            page=params.get('page', 1),
            need_default=params.get('need_default', False)
        )

    # 保持与IApiClient接口兼容
    def get_experiment_details(self, exp_id: str) -> Dict:
        """接口兼容实现（参数适配在Adapter处理）"""
        return super().get_experiment_details(exp_id)
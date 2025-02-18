'''
Author: ChZheng
Date: 2025-02-18 20:51:13
LastEditTime: 2025-02-19 05:00:16
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/ABTestProxy/ABTestProxy/mappers.py
'''
"""
简化版字段映射工具，支持：
1. 嵌套字段映射
2. 数组结构映射
3. 默认值处理
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleMapper:
    def __init__(self, config_path: str = None):
        self.config_path = Path(config_path) if config_path else None
        self.default_sep = "||"

    def load_mapping(self, api_name: str, direction: str) -> Dict:
        """加载映射配置"""
        if not self.config_path:
            return {}
        config_file = config_file = self.config_path.joinpath(f"{api_name}_{direction}.json")
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"配置加载失败: {config_file} - {str(e)}")
            return {}

    def transform(self, source_data: Dict, mapping: Dict) -> Dict:
        """执行字段转换"""
        result = {}
        for target_field, source_spec in mapping.items():
            try:
                # 处理嵌套映射
                if isinstance(source_spec, dict):
                    value = self._process_nested(source_data, source_spec)
                # 处理普通字段
                else:
                    value = self._get_value(source_data, source_spec)

                if value is not None:
                    self._set_value(result, target_field, value)
            except Exception as e:
                logger.warning(f"字段映射失败 [{target_field}]: {str(e)}")
        return result

    def _process_nested(self, data: Dict, spec: Dict) -> Any:
        """处理嵌套结构"""
        nested_data = self._get_value(data, spec['path'])
        if nested_data is None:
            return None

        # 处理数组类型
        if isinstance(nested_data, list):
            return [self.transform(item, spec['mapping']) for item in nested_data]

        # 处理对象类型
        return self.transform(nested_data, spec['mapping'])

    def _get_value(self, data: Dict, path: str) -> Any:
        """获取字段值（含默认值处理）"""
        if self.default_sep in path:
            path_part, default_part = path.split(self.default_sep, 1)
            default = json.loads(default_part)
        else:
            path_part = path
            default = None

        keys = path_part.split('.')
        current = data
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key, default)
            elif isinstance(current, list) and key.isdigit():
                index = int(key)
                current = current[index] if index < len(current) else default
            else:
                return default
            if current is None:
                return default
        return current if current is not None else default

    def _set_value(self, data: Dict, path: str, value: Any):
        """设置嵌套字段值"""
        keys = path.split('.')
        current = data
        for key in keys[:-1]:
            current = current.setdefault(key, {})
        current[keys[-1]] = value


# 测试创建实验请求映射
def test_create_experiment_mapping():
    mapper = SimpleMapper("./config/v2_proxy")

    # 模拟外部请求数据
    external_data = {
        "app_id": 123,
        "name": "新用户引导实验",
        "endpoint_type": 1,
        "duration": 20,
        "major_metric": 29806,
        "metrics": [29806, 29807],
        "versions": [
            {
                "type": 0,
                "name": "对照组",
                "config": {"button_color": "blue"}
            },
            {
                "type": 1,
                "name": "实验组",
                "config": {"button_color": "red"}
            }
        ],
        "layer_info": {
            "version_resource": 0.7
        }
    }

    mapping = mapper.load_mapping("create_experiment", "request")
    result1 = mapper.transform(external_data, mapping)
    print("\n测试结果1:")
    print(json.dumps(result1, indent=2, ensure_ascii=False))
    # assert result1 == {
    #     "app_id": 123,
    #     "flight_name": "新用户引导实验",
    #     "mode": 1,  # 使用默认值
    #     "endpoint_type": 1,
    #     "duration": 20,
    #     "major_metric": 29806,
    #     "metrics": [29806, 29807],
    #     "versions": [
    #         {
    #             "version_type": 0,
    #             "version_name": "对照组",
    #             "config": {"button_color": "blue"},
    #             "weight": 0.5
    #         },
    #         {
    #             "version_type": 1,
    #             "version_name": "实验组",
    #             "config": {"button_color": "red"},
    #             "weight": 0.5
    #         }
    #     ],
    #     "layer": {
    #         "layer_id": -1,  # 使用默认值
    #         "version_resource": 0.7
    #     }
    # }

# 测试实验报告响应映射
def test_report_response_mapping():
    mapper = SimpleMapper("./config/v2_proxy")

    # 模拟内部系统数据
    internal_data = {
        "data": {
            "report_id": "rep_123",
            "calculation_results": {
                "hash": "a1b2c3",
                "metrics": [
                    {
                        "id": 10065,
                        "confidence": 0.95
                    }
                ]
            }
        }
    }

    mapping = {
        "report_id": "data.calculation_results.hash",
        "metrics": {
            "path": "data.calculation_results.metrics",
            "mapping": {
                "metric_id": "id",
                "confidence": "confidence"
            }
        }
    }

    result2 = mapper.transform(internal_data, mapping)
    print("\n测试结果2:")
    print(json.dumps(result2, indent=2, ensure_ascii=False))
    # assert result2 == {
    #     "report_id": "a1b2c3",
    #     "metrics": [
    #         {
    #             "metric_id": 10065,
    #             "confidence": 0.95
    #         }
    #     ]
    # }


if __name__ == "__main__":
    test_create_experiment_mapping()
    test_report_response_mapping()
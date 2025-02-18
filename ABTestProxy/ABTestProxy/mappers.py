"""
Author: ChZheng
Date: 2025-02-13 14:33:24
LastEditTime: 2025-02-18 19:30:00
LastEditors: ChZheng
Description: 增强版FieldMapper，支持条件表达式和$parent路径引用
FilePath: /code/ABTest/ABTestProxy/ABTestProxy/mappers.py
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FieldMapper:
    def __init__(self, config_path: str = None):
        self.config_path = Path(config_path) if config_path else None
        self.default_sep = "||"
        self.condition_pattern = re.compile(
            r'^\s*(.*?)\s*\?\s*(.*?)\s*:\s*(.*?)\s*$'
        )

    def load_mapping(self, api_name: str, direction: str) -> Dict:
        """加载映射配置文件"""
        if not self.config_path:
            return {}
        config_file = self.config_path / f"{api_name}_{direction}.json"
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载映射配置失败: {config_file} - {str(e)}")
            return {}

    def transform(self, data: Dict, mapping: Dict, parent_path: List[str] = None) -> Dict:
        """
        执行字段映射转换，支持：
        - 嵌套映射
        - 条件表达式
        - $parent路径引用
        - 默认值
        """
        parent_path = parent_path or []
        result = {}

        for target_field, source_spec in mapping.items():
            try:
                # 处理嵌套映射
                if isinstance(source_spec, dict):
                    nested_value = self._process_nested_mapping(
                        data, source_spec, parent_path, target_field
                    )
                    if nested_value is not None:
                        self._set_nested_value(
                            result, target_field.split('.'), nested_value
                        )
                    continue

                # 处理字符串类型的映射规则
                if isinstance(source_spec, str):
                    value = self._process_string_mapping(
                        data, source_spec, parent_path
                    )
                    if value is not None:
                        self._set_nested_value(
                            result, target_field.split('.'), value
                        )

            except Exception as e:
                logger.warning(
                    f"字段映射失败 [{target_field} <- {source_spec}]: {str(e)}",
                    exc_info=True
                )

        return result

    def _process_nested_mapping(self, data: Dict, source_spec: Dict,
                               parent_path: List[str], target_field: str) -> Any:
        """处理嵌套映射结构"""
        nested_path = source_spec['path'].split('.')
        current_full_path = parent_path + nested_path

        # 获取嵌套数据
        nested_data = self._get_nested_value(data, nested_path)
        if nested_data is None:
            return None

        # 计算新的父级路径（当前路径的父级）
        new_parent_path = current_full_path[:-1]

        # 递归处理嵌套映射
        return self.transform(
            nested_data,
            source_spec['mapping'],
            new_parent_path
        )

    def _process_string_mapping(self, data: Dict, source_spec: str,
                               parent_path: List[str]) -> Any:
        """处理字符串类型的映射规则"""
        # 解析条件表达式
        if '?' in source_spec and ':' in source_spec:
            selected_path = self._handle_condition_expression(data, source_spec)
        else:
            selected_path = source_spec

        # 处理$parent引用
        resolved_path = self._resolve_parent_reference(selected_path, parent_path)

        # 分离路径和默认值
        if self.default_sep in resolved_path:
            path, default_str = resolved_path.split(self.default_sep, 1)
            default = json.loads(default_str)
        else:
            path = resolved_path
            default = None

        # 获取实际值
        return self._get_nested_value(data, path.split('.'), default)

    def _handle_condition_expression(self, data: Dict, expression: str) -> str:
        """处理三元条件表达式"""
        match = self.condition_pattern.match(expression)
        if not match:
            raise ValueError(f"无效的条件表达式格式: {expression}")

        condition, true_path, false_path = match.groups()
        try:
            # 安全评估条件表达式，仅允许访问data中的字段
            condition_met = bool(eval(condition, {}, data))
            return true_path if condition_met else false_path
        except Exception as e:
            logger.warning(f"条件表达式执行失败: {condition} - {str(e)}")
            return false_path

    def _resolve_parent_reference(self, path: str, parent_path: List[str]) -> str:
        """解析路径中的$parent引用"""
        if '$parent' not in path:
            return path

        # 获取有效的父级路径
        parent_str = '.'.join(parent_path[:-1]) if parent_path else ''
        return path.replace('$parent', parent_str)

    def _get_nested_value(self, data: Dict, path: List[str], default: Any = None) -> Any:
        """安全获取嵌套数据结构的值"""
        current = data
        for key in path:
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

    def _set_nested_value(self, data: Dict, path: List[str], value: Any):
        """安全设置嵌套数据结构的值"""
        current = data
        for key in path[:-1]:
            current = current.setdefault(key, {})
        current[path[-1]] = value


# 使用示例
if __name__ == "__main__":
    mapper = FieldMapper("./configs")

    # 测试用例1：条件表达式和嵌套映射
    test_data1 = {
        "endpoint_type": 1,
        "versions": [{"type": "A", "config": {}}],
        "layer_info": {"version_resource": "res123"}
    }

    mapping1 = {
        "hash_strategy": "endpoint_type==1 ? 'user_id' : 'ssid'",
        "versions": {
            "path": "versions",
            "mapping": {
                "type": "type",
                "weight": "weight||0.5"
            }
        },
        "layer_id": "layer_info.layer_id||-1"
    }

    result1 = mapper.transform(test_data1, mapping1)
    print("测试结果1:", json.dumps(result1, indent=2))

    # 测试用例2：$parent引用
    test_data2 = {
        "data": {
            "calculation_results": {
                "hash": "rep123",
                "id": {"confidence": 0.95}
            },
            "metrics": [{"id": "m1"}, {"id": "m2"}]
        }
    }

    mapping2 = {
        "report_id": "data.calculation_results.hash",
        "metrics": {
            "path": "data.metrics",
            "mapping": {
                "metric_id": "id",
                "confidence": "calculation_results.$parent.id.confidence"
            }
        }
    }

    result2 = mapper.transform(test_data2, mapping2)
    print("测试结果2:", json.dumps(result2, indent=2))
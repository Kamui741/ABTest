'''
Author: ChZheng
Date: 2025-02-13 14:33:24
LastEditTime: 2025-02-14 14:49:49
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/ABTestProxy/ABTestProxy/mappers.py
'''

# [ABTestProxy/mappers.py]
# |- FieldMapper
#    |- load_mapping
#    |- transform
#    |- _get_nested_value
#    |- _set_nested_value
import json
import logging
from pathlib import Path
from functools import lru_cache
from typing import Dict, List, Any
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
class FieldMapper:
    def __init__(self, config_path: str = None):
        self.config_path = Path(config_path)
        self.default_sep = "||"


    def load_mapping(self, api_name: str, direction: str) -> Dict:
        """加载简化的映射配置"""
        config_file = self.config_path / f"{api_name}_{direction}.json"
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载映射配置失败: {config_file} - {str(e)}")
            return {}

    def transform(self, data: Dict, mapping: Dict) -> Dict:
        """执行简化版字段映射"""
        result = {}
        for target_field, source_path in mapping.items():
            try:
                # 支持默认值语法：field.path||default_value
                if self.default_sep in source_path:
                    path, default_str = source_path.split(self.default_sep, 1)
                    default = json.loads(default_str)
                else:
                    path = source_path
                    default = None

                # 获取嵌套值
                value = self._get_nested_value(data, path.split('.'), default)

                # 设置到目标字段
                if value is not None:
                    self._set_nested_value(result, target_field.split('.'), value)

            except Exception as e:
                logger.warning(f"字段映射失败 [{target_field} <- {source_path}]: {str(e)}")
        return result

    def _get_nested_value(self, data: Dict, path: List[str], default: Any = None) -> Any:
        """获取嵌套字段值"""
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
        return current

    def _set_nested_value(self, data: Dict, path: List[str], value: Any):
        """设置嵌套字段值"""
        current = data
        for key in path[:-1]:
            current = current.setdefault(key, {})
        current[path[-1]] = value

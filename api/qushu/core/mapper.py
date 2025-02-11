'''
Author: ChZheng
Date: 2025-02-12 04:41:37
LastEditTime: 2025-02-12 04:42:46
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/api/qushu/core/mapper.py
'''
# core/mapper.py
import json
import logging
from functools import lru_cache
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from .config import AppConfig
from .exceptions import MappingError

logger = logging.getLogger(__name__)

class FieldMapper:
    """字段映射处理器"""

    def __init__(self):
        self.mapping_dir = AppConfig.MAPPING_DIR

    @lru_cache(maxsize=32)
    def _load_mapping_file(self, mapping_type: str, direction: str) -> Dict:
        """加载映射配置文件"""
        file_path = self.mapping_dir / f"{mapping_type}_{direction}.json"
        try:
            with file_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            logger.error("Failed to load mapping file: %s", file_path)
            raise MappingError(f"Mapping config error: {str(e)}") from e

    def _convert_value(self, value: Any, transform: Optional[str]) -> Any:
        """值类型转换"""
        if not transform:
            return value

        converters = {
            "timestamp_to_iso": lambda x: datetime.fromtimestamp(x).isoformat(),
            "status_code": self._convert_status_code,
            "version_type": self._convert_version_type
        }

        if converter := converters.get(transform):
            return converter(value)
        raise MappingError(f"Unknown transformer: {transform}")

    @staticmethod
    def _convert_status_code(code: int) -> str:
        """状态码转换"""
        codes = {
            0: "stopped",
            1: "running",
            2: "draft"
        }
        return codes.get(code, "unknown")

    @staticmethod
    def _convert_version_type(v_type: int) -> str:
        """版本类型转换"""
        types = {
            0: "control",
            1: "experiment"
        }
        return types.get(v_type, "unknown")

    def transform(self, data: Dict, mapping_type: str, direction: str) -> Dict:
        """执行字段映射转换"""
        mapping = self._load_mapping_file(mapping_type, direction)
        result = {}

        for target_field, rule in mapping.get("mappings", {}).items():
            try:
                # 处理嵌套映射
                if "mappings" in rule:
                    nested_data = self.transform(
                        data,
                        mapping_type=rule.get("inherit", mapping_type),
                        direction=direction
                    )
                    result[target_field] = nested_data
                    continue

                # 获取源数据
                source_path = rule.get("source")
                default = rule.get("default")
                transform = rule.get("transform")

                value = data
                for key in source_path.split(".") if source_path else []:
                    value = value.get(key, default if default is not None else {})

                # 应用转换
                converted = self._convert_value(value, transform)

                # 设置目标字段
                target_keys = target_field.split(".")
                current = result
                for key in target_keys[:-1]:
                    current = current.setdefault(key, {})
                current[target_keys[-1]] = converted

            except Exception as e:
                logger.warning("Field mapping failed: %s -> %s: %s",
                              source_path, target_field, str(e))
                if rule.get("required", False):
                    raise MappingError(f"Required field {target_field} missing")

        return result
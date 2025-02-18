
    # def _process_nested_mapping(self, data: Dict, source_spec: Dict,
    #                            parent_path: List[str], target_field: str) -> Any:
    #     """处理嵌套映射结构"""
    #     nested_path = source_spec['path'].split('.')
    #     current_full_path = parent_path + nested_path

    #     # 获取嵌套数据
    #     nested_data = self._get_nested_value(data, nested_path)
    #     if nested_data is None:
    #         return None

    #     # 计算新的父级路径（当前路径的父级）
    #     new_parent_path = current_full_path[:-1]

    #     # 递归处理嵌套映射
    #     return self.transform(
    #         nested_data,
    #         source_spec['mapping'],
    #         new_parent_path
    #     )
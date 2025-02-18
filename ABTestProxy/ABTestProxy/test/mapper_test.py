'''
Author: ChZheng
Date: 2025-02-14 14:18:24
LastEditTime: 2025-02-18 16:02:26
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/ABTestProxy/ABTestProxy/test/mapper_test.py
'''
from mappers import FieldMapper



def test_field_mapper():
    mapper = FieldMapper(config_path="ABTest/ABTestProxy/ABTestProxy/config/v2_proxy")


    # 测试数据
    v2_request = {
        "experiment_info": {"name": "新用户引导实验"},
        "project_info": {"app_id": 1001},
        # duration字段缺失
    }

    # 执行转换
    mapping = mapper.load_mapping("test", "request")
    result = mapper.transform(v2_request, mapping)

    # 验证结果
    assert result == {
        "flight_name": "新用户引导实验",
        "duration": 30,  # 应用默认值
        "app_id": 1001
    }
    print("字段映射测试通过！")

# 执行测试
if __name__ == "__main__":
    test_field_mapper()
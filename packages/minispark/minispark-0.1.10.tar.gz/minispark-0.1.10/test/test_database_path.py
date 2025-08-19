"""
测试database_path配置支持的两种类型：
1. 内存数据库 (:memory:)
2. 临时文件数据库 (临时目录中的文件)
"""

import os
import tempfile
from minispark import MiniSpark
import pandas as pd


def test_memory_database():
    """测试内存数据库"""
    print("=== 测试内存数据库 ===")
    
    # 创建使用内存数据库的配置
    config_content = """
[engine]
type = "sqlite"
database_path = ":memory:"

[storage]
format = "parquet"
"""
    
    # 写入配置文件
    with open("memory_config.toml", "w") as f:
        f.write(config_content)
    
    # 初始化MiniSpark
    spark = MiniSpark("memory_config.toml")
    
    # 检查temp_database_path应该为None
    print(f"内存数据库的temp_database_path: {spark.temp_database_path}")
    
    # 创建测试数据
    test_data = pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie']
    })
    
    # 注册表
    spark.engine.register_table("test", test_data)
    
    # 执行查询
    result = spark.execute_query("SELECT * FROM test")
    print("查询结果:")
    print(result)
    
    # 关闭
    spark.close()
    
    # 清理配置文件
    os.remove("memory_config.toml")
    
    print("内存数据库测试完成\n")


def test_temp_file_database():
    """测试临时文件数据库"""
    print("=== 测试临时文件数据库 ===")
    
    # 创建使用临时文件数据库的配置
    config_content = """
[engine]
type = "sqlite"
database_path = "test_minispark.db"

[storage]
format = "parquet"
"""
    
    # 写入配置文件
    with open("temp_file_config.toml", "w") as f:
        f.write(config_content)
    
    # 初始化MiniSpark
    spark = MiniSpark("temp_file_config.toml")
    
    # 检查temp_database_path
    print(f"临时文件数据库的temp_database_path: {spark.temp_database_path}")
    
    # 检查文件是否存在
    if spark.temp_database_path and os.path.exists(spark.temp_database_path):
        print("临时数据库文件已创建")
    else:
        print("临时数据库文件未找到")
    
    # 创建测试数据
    test_data = pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie']
    })
    
    # 注册表
    spark.engine.register_table("test", test_data)
    
    # 执行查询
    result = spark.execute_query("SELECT * FROM test")
    print("查询结果:")
    print(result)
    
    # 获取临时文件路径用于后续检查
    temp_db_path = spark.temp_database_path
    
    # 关闭
    spark.close()
    
    # 检查文件是否被清理
    if temp_db_path and os.path.exists(temp_db_path):
        print("临时数据库文件未被清理")
        # 手动清理
        try:
            os.remove(temp_db_path)
            print("已手动清理临时数据库文件")
        except Exception as e:
            print(f"手动清理失败: {e}")
    elif temp_db_path:
        print("临时数据库文件已成功清理")
    else:
        print("未使用临时数据库文件")
    
    # 清理配置文件
    os.remove("temp_file_config.toml")
    
    print("临时文件数据库测试完成\n")


if __name__ == "__main__":
    test_memory_database()
    test_temp_file_database()
    print("所有测试完成")
"""
测试临时文件数据库功能
"""

import pandas as pd
import os
import tempfile
from minispark import MiniSpark, CSVConnector


def test_temp_database():
    """测试临时文件数据库功能"""
    print("=== 测试临时文件数据库功能 ===")
    
    # 使用测试配置文件初始化MiniSpark
    spark = MiniSpark("test_config.toml")
    
    # 创建测试数据
    test_data = pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'age': [25, 30, 35, 28, 32]
    })
    
    # 注册测试数据到引擎
    spark.engine.register_table("test_table", test_data)
    print("已注册测试表到引擎")
    
    # 执行查询
    result = spark.execute_query("SELECT * FROM test_table WHERE age > 30")
    print("查询结果:")
    print(result)
    
    # 关闭MiniSpark
    spark.close()
    print("测试完成")


if __name__ == "__main__":
    test_temp_database()
    
    # 检查临时文件是否被清理
    import time
    time.sleep(1)  # 等待文件系统操作完成
    
    temp_db_path = os.path.join(tempfile.gettempdir(), "minispark_test.db")
    if os.path.exists(temp_db_path):
        print(f"临时数据库文件仍未被清理: {temp_db_path}")
        # 尝试手动删除
        try:
            os.remove(temp_db_path)
            print("已手动清理临时数据库文件")
        except Exception as e:
            print(f"手动清理失败: {e}")
    else:
        print("临时数据库文件已成功清理")
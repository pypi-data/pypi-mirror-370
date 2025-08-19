"""
测试DuckDB引擎初始化
"""

import os
import sys
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from minispark import MiniSpark


def test_duckdb_engine():
    """测试DuckDB引擎"""
    print("=== 测试DuckDB引擎 ===")
    
    try:
        print("开始初始化MiniSpark并使用DuckDB引擎...")
        # 记录开始时间
        start_time = time.time()
        
        # 初始化MiniSpark（使用DuckDB作为本地处理引擎）
        spark = MiniSpark("duckdb_test_config.toml")
        print("MiniSpark初始化成功")
        
        # 检查是否超时（超过10秒认为失败）
        elapsed_time = time.time() - start_time
        print(f"初始化耗时: {elapsed_time:.2f} 秒")
        
        # 创建测试数据
        import pandas as pd
        test_data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie']
        })
        
        # 注册表到引擎
        print("注册测试表到引擎...")
        spark.engine.register_table("test_table", test_data)
        
        # 执行查询
        print("执行查询...")
        result = spark.execute_query("SELECT * FROM test_table")
        print("查询结果:")
        print(result)
        
        # 关闭连接
        print("关闭连接...")
        spark.close()
        print("MiniSpark关闭成功")
        
    except Exception as e:
        print(f"MiniSpark测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("MiniSpark测试完成\n")


if __name__ == "__main__":
    test_duckdb_engine()
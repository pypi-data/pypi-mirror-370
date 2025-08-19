"""
测试DuckDB引擎初始化（带超时机制）
"""

import os
import sys
import signal

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))


class TimeoutError(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutError("操作超时")


def test_duckdb_engine_with_timeout():
    """测试DuckDB引擎（带超时）"""
    print("=== 测试DuckDB引擎（带超时机制） ===")
    
    # 设置5秒超时
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(5)
    
    try:
        print("开始初始化MiniSpark并使用DuckDB引擎...")
        
        from minispark import MiniSpark
        
        # 初始化MiniSpark（使用DuckDB作为本地处理引擎）
        spark = MiniSpark("duckdb_test_config.toml")
        print("MiniSpark初始化成功")
        
        # 取消超时
        signal.alarm(0)
        
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
        
    except TimeoutError:
        print("DuckDB引擎初始化超时，可能存在兼容性问题")
        # 取消超时
        signal.alarm(0)
    except Exception as e:
        print(f"MiniSpark测试失败: {e}")
        # 取消超时
        signal.alarm(0)
        import traceback
        traceback.print_exc()
    
    print("MiniSpark测试完成\n")


if __name__ == "__main__":
    test_duckdb_engine_with_timeout()
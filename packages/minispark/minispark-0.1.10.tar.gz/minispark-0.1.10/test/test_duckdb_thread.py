"""
测试DuckDB引擎初始化（使用线程超时）
"""

import os
import sys
import threading
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))


def test_duckdb_engine_thread():
    """在单独线程中测试DuckDB引擎"""
    print("=== 测试DuckDB引擎（使用线程） ===")
    
    result = {"success": False, "error": None, "spark": None}
    
    def init_minispark():
        try:
            print("开始初始化MiniSpark并使用DuckDB引擎...")
            from minispark import MiniSpark
            # 初始化MiniSpark（使用DuckDB作为本地处理引擎）
            spark = MiniSpark("duckdb_test_config.toml")
            result["success"] = True
            result["spark"] = spark
            print("MiniSpark初始化成功")
        except Exception as e:
            result["error"] = e
            print(f"MiniSpark初始化失败: {e}")
    
    # 在单独线程中启动
    thread = threading.Thread(target=init_minispark)
    thread.start()
    
    # 等待最多10秒
    thread.join(timeout=10.0)
    
    if thread.is_alive():
        print("DuckDB引擎初始化超时（超过10秒），可能存在兼容性问题")
        # 我们无法强制终止线程，但可以继续执行
        return None
    elif result["success"]:
        print("DuckDB引擎初始化成功")
        # 进行进一步测试
        try:
            # 创建测试数据
            import pandas as pd
            test_data = pd.DataFrame({
                'id': [1, 2, 3],
                'name': ['Alice', 'Bob', 'Charlie']
            })
            
            # 注册表到引擎
            print("注册测试表到引擎...")
            result["spark"].engine.register_table("test_table", test_data)
            
            # 执行查询
            print("执行查询...")
            result = result["spark"].execute_query("SELECT * FROM test_table")
            print("查询结果:")
            print(result)
            
            # 关闭连接
            print("关闭连接...")
            result["spark"].close()
            print("MiniSpark关闭成功")
        except Exception as e:
            print(f"测试过程中出现错误: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"DuckDB引擎初始化失败: {result['error']}")
    
    print("MiniSpark测试完成\n")


if __name__ == "__main__":
    test_duckdb_engine_thread()
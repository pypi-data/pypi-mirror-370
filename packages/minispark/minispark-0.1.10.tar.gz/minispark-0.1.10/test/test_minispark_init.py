"""
测试MiniSpark初始化
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from minispark import MiniSpark


def test_minispark_initialization():
    """测试MiniSpark初始化"""
    print("=== 测试MiniSpark初始化 ===")
    
    try:
        # 初始化MiniSpark（使用SQLite作为本地处理引擎）
        spark = MiniSpark()
        print("MiniSpark初始化成功")
        
        # 执行简单查询
        result = spark.execute_query("SELECT 'test' as result")
        print("简单查询结果:")
        print(result)
        
        # 关闭连接
        spark.close()
        print("MiniSpark关闭成功")
        
    except Exception as e:
        print(f"MiniSpark测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("MiniSpark测试完成\n")


if __name__ == "__main__":
    test_minispark_initialization()
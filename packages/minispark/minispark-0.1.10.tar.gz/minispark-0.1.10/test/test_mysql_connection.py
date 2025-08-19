"""
测试MySQL连接
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from minispark import MiniSpark
from minispark.connectors.mysql_connector import MySQLConnector


def test_mysql_connection():
    """测试MySQL连接"""
    print("=== 测试MySQL连接 ===")
    
    # 初始化MiniSpark
    spark = MiniSpark()
    
    # 添加MySQL连接器
    try:
        mysql_connector = MySQLConnector(
            name='duanfu.vip',
            host='47.108.200.193',
            port=3306,
            user='duanfu',
            password='HTb55A2rFFa4nGft',
            database='duanfu'
        )
        spark.add_connector('mysql', mysql_connector)
        print("成功添加MySQL连接器")
        
        # 测试连接 - 执行一个简单的查询
        print("尝试执行测试查询...")
        result_df = spark.load_data('mysql', 'SELECT 1 as test', 'test_table')
        print("查询结果:")
        print(result_df)
        print("MySQL连接测试成功!")
        
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保已安装必要依赖: pip install pymysql sqlalchemy")
    except Exception as e:
        print(f"MySQL连接测试失败: {e}")
        print("请检查连接参数是否正确")
    
    # 关闭连接
    spark.close()
    print("测试完成")


if __name__ == "__main__":
    test_mysql_connection()
"""
全面测试MySQL连接和查询功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from minispark import MiniSpark
from minispark.connectors.mysql_connector import MySQLConnector


def test_mysql_comprehensive():
    """全面测试MySQL连接和查询功能"""
    print("=== 全面测试MySQL连接和查询功能 ===")
    
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
        
        # 测试1: 简单查询
        print("\n--- 测试1: 简单查询 ---")
        result_df = spark.load_data('mysql', 'SELECT 1 as test_col', 'test_table')
        print("查询结果:")
        print(result_df)
        
        # 测试2: 查询数据库中的表信息
        print("\n--- 测试2: 查询数据库中的表信息 ---")
        tables_df = spark.load_data('mysql', 
                                   "SELECT table_name FROM information_schema.tables WHERE table_schema = 'duanfu'", 
                                   'tables_info')
        print("数据库中的表:")
        print(tables_df)
        print("列名:", tables_df.columns.tolist())
        
        # 测试3: 查看表结构
        print("\n--- 测试3: 查看表结构 ---")
        if len(tables_df) > 0:
            # 注意MySQL返回的列名可能是大写的TABLE_NAME
            table_name_col = 'TABLE_NAME' if 'TABLE_NAME' in tables_df.columns else 'table_name'
            first_table = tables_df.iloc[0][table_name_col]
            print(f"查看表 '{first_table}' 的结构:")
            columns_df = spark.load_data('mysql',
                                        f"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'duanfu' AND table_name = '{first_table}'",
                                        'columns_info')
            print(columns_df)
        else:
            print("数据库中没有找到表")
            
        # 测试4: 查询部分实际数据（如果存在表）
        print("\n--- 测试4: 查询实际数据 ---")
        if len(tables_df) > 0:
            table_name_col = 'TABLE_NAME' if 'TABLE_NAME' in tables_df.columns else 'table_name'
            first_table = tables_df.iloc[0][table_name_col]
            print(f"从表 '{first_table}' 中查询前5行数据:")
            try:
                data_df = spark.load_data('mysql',
                                         f"SELECT * FROM {first_table} LIMIT 5",
                                         'sample_data')
                print(data_df)
            except Exception as e:
                print(f"查询数据时出错: {e}")
        else:
            print("数据库中没有找到表")
            
        print("\nMySQL全面测试完成!")
        
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保已安装必要依赖: pip install pymysql sqlalchemy")
    except Exception as e:
        print(f"MySQL连接测试失败: {e}")
        import traceback
        traceback.print_exc()
        print("请检查连接参数是否正确")
    
    # 关闭连接
    spark.close()
    print("\n测试完成")


if __name__ == "__main__":
    test_mysql_comprehensive()
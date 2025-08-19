"""
MySQL连接器使用示例
"""

import pandas as pd
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from minispark import MiniSpark, MySQLConnector


def create_sample_mysql_data():
    """创建示例MySQL数据说明"""
    print("创建示例MySQL数据...")
    print("注意：需要配置真实的MySQL服务器连接信息")
    
    # 示例数据说明
    print("示例员工数据表结构:")
    print("- id (INT)")
    print("- name (VARCHAR)")
    print("- department (VARCHAR)")
    print("- salary (DECIMAL)")
    print()


def mysql_example():
    """MySQL使用示例"""
    print("=== MySQL连接器使用示例 ===")
    
    # 创建示例数据说明
    create_sample_mysql_data()
    
    # 初始化MiniSpark
    spark = MiniSpark()
    
    # 添加MySQL连接器
    # 注意：需要配置真实的MySQL连接信息
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
        
        # 从MySQL加载数据（示例）
        print("执行测试查询...")
        test_df = spark.load_data('mysql', 'SELECT 1 as connection_test', 'test_result')
        print("连接测试结果:")
        print(test_df)
        print()
        
        # 查询数据库中的表
        tables_df = spark.load_data('mysql', 
                                   "SELECT table_name FROM information_schema.tables WHERE table_schema = 'duanfu'", 
                                   'tables')
        print("数据库中的表:")
        print(tables_df)
        print()
        
        # 如果存在表，则查询第一个表的结构
        if len(tables_df) > 0:
            table_name_col = 'TABLE_NAME' if 'TABLE_NAME' in tables_df.columns else 'table_name'
            first_table = tables_df.iloc[0][table_name_col]
            print(f"表 '{first_table}' 的结构:")
            columns_df = spark.load_data('mysql',
                                        f"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'duanfu' AND table_name = '{first_table}'",
                                        'columns')
            print(columns_df)
            print()
        
    except Exception as e:
        print(f"添加MySQL连接器时出错: {e}")
        print("请确保已安装pymysql并且MySQL服务器配置正确")
        print("运行以下命令安装pymysql: uv pip install pymysql")
        import traceback
        traceback.print_exc()
    
    # 关闭连接
    spark.close()
    print("MySQL示例完成\n")


if __name__ == "__main__":
    # 显示数据生成说明
    from generate_data import mysql_data_info
    mysql_data_info()
    print()
    
    # 运行示例
    mysql_example()
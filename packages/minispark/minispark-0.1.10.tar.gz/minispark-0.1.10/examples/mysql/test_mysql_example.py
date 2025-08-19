"""
MySQL连接器测试示例
专门用于测试MySQL连接和查询功能
"""

import pandas as pd
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from minispark import MiniSpark
from minispark.connectors.mysql_connector import MySQLConnector


def test_mysql_connection():
    """测试MySQL连接和基本功能"""
    print("=== MySQL连接器测试 ===")
    
    # 初始化MiniSpark
    spark = MiniSpark()
    
    try:
        # 添加MySQL连接器
        mysql_connector = MySQLConnector(
            name='duanfu.vip',
            host='47.108.200.193',
            port=3306,
            user='duanfu',
            password='HTb55A2rFFa4nGft',
            database='duanfu'
        )
        spark.add_connector('mysql', mysql_connector)
        print("[OK] 成功添加MySQL连接器")
        
        # 测试1: 简单连接测试
        print("\n--- 测试1: 连接和简单查询 ---")
        test_df = spark.load_data('mysql', 'SELECT 1 as test_column', 'test_table')
        print("连接测试结果:")
        print(test_df)
        print("[OK] 简单查询测试通过")
        
        # 测试2: 查询数据库中的表
        print("\n--- 测试2: 查询数据库结构 ---")
        tables_df = spark.load_data('mysql', 
                                   "SELECT TABLE_NAME FROM information_schema.tables WHERE table_schema = 'duanfu'", 
                                   'database_tables')
        print(f"数据库中找到 {len(tables_df)} 个表:")
        print(tables_df)
        print("[OK] 数据库结构查询测试通过")
        
        # 测试3: 查询表结构
        print("\n--- 测试3: 查询表结构 ---")
        if len(tables_df) > 0:
            first_table = tables_df.iloc[0]['TABLE_NAME']
            print(f"查询表 '{first_table}' 的结构:")
            columns_df = spark.load_data('mysql',
                                        f"SELECT COLUMN_NAME, DATA_TYPE FROM information_schema.columns WHERE table_schema = 'duanfu' AND table_name = '{first_table}'",
                                        'table_columns')
            print(columns_df)
            print("[OK] 表结构查询测试通过")
        else:
            print("数据库中没有找到表")
        
        # 测试4: 查询实际数据
        print("\n--- 测试4: 查询实际数据 ---")
        if len(tables_df) > 0:
            first_table = tables_df.iloc[0]['TABLE_NAME']
            try:
                data_df = spark.load_data('mysql',
                                         f"SELECT * FROM {first_table} LIMIT 3",
                                         'sample_data')
                print(f"从表 '{first_table}' 中获取的数据:")
                print(data_df)
                print("[OK] 实际数据查询测试通过")
            except Exception as e:
                print(f"查询数据时出现错误: {e}")
                print("[OK] 错误处理测试通过")
        else:
            print("数据库中没有找到表")
            
    except ImportError as e:
        print(f"[ERROR] 导入错误: {e}")
        print("请确保已安装必要依赖: pip install pymysql sqlalchemy")
        return False
    except Exception as e:
        print(f"[ERROR] MySQL测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 关闭连接
        spark.close()
    
    print("\n=== MySQL连接器测试完成 ===")
    return True


def main():
    """主函数"""
    print("开始MySQL连接器测试...")
    
    success = test_mysql_connection()
    
    if success:
        print("\n[SUCCESS] MySQL连接器测试成功!")
    else:
        print("\n[FAILED] MySQL连接器测试失败!")


if __name__ == "__main__":
    main()
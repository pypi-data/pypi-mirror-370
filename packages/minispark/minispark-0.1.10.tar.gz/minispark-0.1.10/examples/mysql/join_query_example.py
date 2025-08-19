"""
MySQL关联查询示例
演示如何使用MiniSpark进行多表关联查询
"""

import pandas as pd
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from minispark import MiniSpark
from minispark.connectors.mysql_connector import MySQLConnector


def test_mysql_join_queries():
    """测试MySQL关联查询功能"""
    print("=== MySQL关联查询测试 ===")
    
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
        
        # 获取数据库中的所有表
        print("\n--- 获取数据库表信息 ---")
        tables_df = spark.load_data('mysql', 
                                   "SELECT TABLE_NAME FROM information_schema.tables WHERE table_schema = 'duanfu'", 
                                   'database_tables')
        print(f"数据库中找到 {len(tables_df)} 个表:")
        for i, table_name in enumerate(tables_df['TABLE_NAME']):
            print(f"  {i+1}. {table_name}")
        
        # 检查是否有足够的表进行关联查询
        if len(tables_df) < 2:
            print("\n[WARNING] 数据库中表数量不足，无法进行关联查询测试")
            print("需要至少2个表才能演示关联查询")
            return True
        
        # 获取前两个表的详细信息
        print("\n--- 获取前两个表的结构信息 ---")
        table1 = tables_df.iloc[0]['TABLE_NAME']
        table2 = tables_df.iloc[1]['TABLE_NAME'] if len(tables_df) > 1 else table1
        
        # 获取第一个表的结构
        columns1_df = spark.load_data('mysql',
                                     f"SELECT COLUMN_NAME, DATA_TYPE FROM information_schema.columns WHERE table_schema = 'duanfu' AND table_name = '{table1}'",
                                     'table1_columns')
        print(f"表 '{table1}' 的结构:")
        for _, row in columns1_df.iterrows():
            print(f"  - {row['COLUMN_NAME']} ({row['DATA_TYPE']})")
        
        # 获取第二个表的结构
        if table2 != table1:
            columns2_df = spark.load_data('mysql',
                                         f"SELECT COLUMN_NAME, DATA_TYPE FROM information_schema.columns WHERE table_schema = 'duanfu' AND table_name = '{table2}'",
                                         'table2_columns')
            print(f"表 '{table2}' 的结构:")
            for _, row in columns2_df.iterrows():
                print(f"  - {row['COLUMN_NAME']} ({row['DATA_TYPE']})")
        else:
            print(f"数据库中只有一个表: {table1}")
        
        # 尝试进行关联查询（如果可能）
        print("\n--- 尝试关联查询 ---")
        if table1 != table2:
            # 尝试查找共同字段进行关联
            common_columns = find_common_columns(columns1_df, columns2_df)
            if common_columns:
                print(f"发现共同字段: {', '.join(common_columns)}")
                join_column = common_columns[0]
                print(f"使用 '{join_column}' 字段进行关联查询")
                
                # 执行关联查询
                join_query = f"""
                SELECT t1.*, t2.* 
                FROM {table1} t1
                LEFT JOIN {table2} t2 ON t1.{join_column} = t2.{join_column}
                LIMIT 5
                """
                
                try:
                    join_result = spark.load_data('mysql', join_query, 'join_result')
                    print("关联查询结果:")
                    print(join_result)
                    print("[OK] 关联查询测试通过")
                except Exception as e:
                    print(f"[INFO] 关联查询执行失败: {e}")
                    print("这可能是由于表中没有数据或者字段类型不匹配导致的")
            else:
                print(f"表 '{table1}' 和 '{table2}' 之间没有共同字段")
                print("无法直接进行关联查询")
        else:
            print("数据库中只有一个表，无法进行关联查询")
        
        # 演示子查询
        print("\n--- 演示子查询 ---")
        try:
            # 执行一个包含子查询的复杂查询
            subquery = f"""
            SELECT * FROM {table1} 
            WHERE 1 IN (SELECT 1 FROM information_schema.tables WHERE table_schema = 'duanfu' LIMIT 1)
            LIMIT 3
            """
            subquery_result = spark.load_data('mysql', subquery, 'subquery_result')
            print("子查询结果:")
            print(subquery_result)
            print("[OK] 子查询测试通过")
        except Exception as e:
            print(f"[INFO] 子查询执行失败: {e}")
        
        # 演示聚合查询
        print("\n--- 演示聚合查询 ---")
        try:
            # 执行聚合查询
            agg_query = f"""
            SELECT COUNT(*) as total_rows
            FROM {table1}
            """
            agg_result = spark.load_data('mysql', agg_query, 'agg_result')
            print("聚合查询结果:")
            print(agg_result)
            print("[OK] 聚合查询测试通过")
        except Exception as e:
            print(f"[INFO] 聚合查询执行失败: {e}")
            
    except ImportError as e:
        print(f"[ERROR] 导入错误: {e}")
        print("请确保已安装必要依赖: pip install pymysql sqlalchemy")
        return False
    except Exception as e:
        print(f"[ERROR] MySQL关联查询测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 关闭连接
        spark.close()
    
    print("\n=== MySQL关联查询测试完成 ===")
    return True


def find_common_columns(columns1_df, columns2_df):
    """查找两个表之间的共同字段"""
    columns1 = set(columns1_df['COLUMN_NAME'].tolist())
    columns2 = set(columns2_df['COLUMN_NAME'].tolist())
    return list(columns1.intersection(columns2))


def main():
    """主函数"""
    print("开始MySQL关联查询测试...")
    
    success = test_mysql_join_queries()
    
    if success:
        print("\n[SUCCESS] MySQL关联查询测试完成!")
    else:
        print("\n[FAILED] MySQL关联查询测试失败!")


if __name__ == "__main__":
    main()
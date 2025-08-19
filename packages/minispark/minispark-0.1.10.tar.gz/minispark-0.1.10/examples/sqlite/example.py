"""
SQLite连接器使用示例
"""

import pandas as pd
import sqlite3
import os
import sys
from loguru import logger

# 配置日志
logger.remove()
logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from minispark import MiniSpark, SQLiteConnector


def sqlite_example():
    """SQLite使用示例"""
    logger.info("开始执行SQLite连接器示例")
    print("=== SQLite连接器使用示例 ===")
    
    # 构建数据库文件路径
    db_path = os.path.join(os.path.dirname(__file__), 'company.db')
    
    # 初始化MiniSpark
    spark = MiniSpark()
    
    # 添加SQLite连接器
    sqlite_connector = SQLiteConnector('sqlite', db_path)
    spark.add_connector('sqlite', sqlite_connector)
    print("成功添加SQLite连接器")
    
    # 从SQLite加载数据
    departments_df = spark.load_data('sqlite', 'SELECT * FROM departments', 'departments')
    print("从SQLite加载的部门数据:")
    print(departments_df)
    print()
    
    # 执行查询
    result = spark.execute_query("""
        SELECT department, manager
        FROM departments 
        WHERE budget > 200000
        ORDER BY budget DESC
    """)
    print("预算超过200000的部门:")
    print(result)
    print()
    
    # 关闭连接
    spark.close()
    
    # 清理示例文件
    if os.path.exists(db_path):
        os.remove(db_path)
        print("已清理示例文件: company.db")
    
    logger.info("SQLite连接器示例执行完成")
    print("SQLite示例完成\n")


if __name__ == "__main__":
    # 首先生成示例数据
    from generate_data import create_sample_sqlite_data
    create_sample_sqlite_data()
    
    # 运行示例
    sqlite_example()
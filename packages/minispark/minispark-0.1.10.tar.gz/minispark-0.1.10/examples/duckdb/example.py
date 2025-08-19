"""
DuckDB连接器使用示例
"""

import pandas as pd
import os
import sys

try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from minispark import MiniSpark, DuckDBConnector


def duckdb_example():
    """DuckDB使用示例"""
    print("=== DuckDB连接器使用示例 ===")
    
    if not DUCKDB_AVAILABLE:
        print("跳过DuckDB示例，因为未安装duckdb库")
        print("请运行以下命令安装: uv pip install duckdb")
        return
    
    # 构建数据库文件路径
    db_path = os.path.join(os.path.dirname(__file__), 'projects.db')
    
    # 初始化MiniSpark
    spark = MiniSpark()
    
    # 添加DuckDB连接器
    duckdb_connector = DuckDBConnector('duckdb', db_path)
    spark.add_connector('duckdb', duckdb_connector)
    print("成功添加DuckDB连接器")
    
    # 从DuckDB加载数据
    projects_df = spark.load_data('duckdb', 'SELECT * FROM projects', 'projects')
    print("从DuckDB加载的项目数据:")
    print(projects_df)
    print()
    
    # 执行查询
    result = spark.execute_query("""
        SELECT department, COUNT(*) as project_count, AVG(budget) as avg_budget
        FROM projects 
        GROUP BY department
        ORDER BY avg_budget DESC
    """)
    print("按部门统计的项目数据:")
    print(result)
    print()
    
    # 关闭连接
    spark.close()
    
    # 清理示例文件
    if os.path.exists(db_path):
        os.remove(db_path)
        print("已清理示例文件: projects.db")
    
    print("DuckDB示例完成\n")


if __name__ == "__main__":
    # 首先生成示例数据
    from generate_data import create_sample_duckdb_data
    create_sample_duckdb_data()
    
    # 运行示例
    duckdb_example()
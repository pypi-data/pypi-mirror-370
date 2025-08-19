"""
测试DuckDB连接器功能（不依赖DuckDB作为本地处理引擎）
"""

import pandas as pd
import os
import sys
import tempfile

try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from minispark import MiniSpark, DuckDBConnector


def test_duckdb_connector():
    """测试DuckDB连接器"""
    print("=== 测试DuckDB连接器 ===")
    
    if not DUCKDB_AVAILABLE:
        print("跳过DuckDB连接器测试，因为未安装duckdb库")
        print("请运行以下命令安装: uv pip install duckdb")
        return
    
    # 创建临时DuckDB数据库文件
    temp_dir = tempfile.gettempdir()
    db_path = os.path.join(temp_dir, 'test_projects.db')
    print(f"创建临时DuckDB数据库: {db_path}")
    
    # 创建示例数据并保存到DuckDB数据库
    projects_data = pd.DataFrame({
        'project_id': [1, 2, 3, 4, 5],
        'project_name': ['Project A', 'Project B', 'Project C', 'Project D', 'Project E'],
        'department': ['IT', 'HR', 'Finance', 'IT', 'Finance'],
        'budget': [100000, 50000, 75000, 120000, 80000]
    })
    
    # 保存到DuckDB数据库
    conn = duckdb.connect(db_path)
    conn.execute("CREATE TABLE projects AS SELECT * FROM projects_data")
    conn.close()
    
    print("示例项目数据:")
    print(projects_data)
    print()
    
    # 初始化MiniSpark（使用SQLite作为本地处理引擎）
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
    
    # 清理临时文件
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"已清理临时文件: {db_path}")
    
    print("DuckDB连接器测试完成\n")


if __name__ == "__main__":
    test_duckdb_connector()
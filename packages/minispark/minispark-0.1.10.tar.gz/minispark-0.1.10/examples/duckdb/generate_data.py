"""
生成DuckDB示例数据
"""

import pandas as pd
import os

try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False


def create_sample_duckdb_data():
    """创建示例DuckDB数据"""
    if not DUCKDB_AVAILABLE:
        print("需要安装duckdb库: pip install duckdb")
        return None
    
    print("创建示例DuckDB数据...")
    
    # 创建示例项目数据
    projects_data = pd.DataFrame({
        'project_id': [1, 2, 3, 4, 5],
        'project_name': ['Project A', 'Project B', 'Project C', 'Project D', 'Project E'],
        'department': ['IT', 'HR', 'Finance', 'IT', 'Finance'],
        'budget': [100000, 50000, 75000, 120000, 80000]
    })
    
    # 保存到DuckDB数据库在当前目录下
    db_path = os.path.join(os.path.dirname(__file__), 'projects.db')
    conn = duckdb.connect(db_path)
    conn.execute("CREATE TABLE projects AS SELECT * FROM projects_data")
    conn.close()
    
    print("示例项目数据已保存到projects.db:")
    print(projects_data)
    print()
    
    return projects_data


if __name__ == "__main__":
    create_sample_duckdb_data()
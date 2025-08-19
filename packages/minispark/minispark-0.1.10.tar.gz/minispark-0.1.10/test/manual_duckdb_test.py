"""
手动测试DuckDB连接器核心功能
"""

import pandas as pd
import os
import tempfile
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

try:
    import duckdb
    DUCKDB_AVAILABLE = True
    print("DuckDB库可用")
except ImportError:
    DUCKDB_AVAILABLE = False
    print("DuckDB库不可用")


def test_duckdb_connector_manually():
    """手动测试DuckDB连接器"""
    print("=== 手动测试DuckDB连接器 ===")
    
    if not DUCKDB_AVAILABLE:
        print("跳过测试，因为未安装duckdb库")
        return
    
    # 创建临时数据库文件
    temp_dir = tempfile.gettempdir()
    db_path = os.path.join(temp_dir, 'manual_test.db')
    print(f"创建临时数据库: {db_path}")
    
    try:
        # 创建示例数据
        data = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Project A', 'Project B', 'Project C', 'Project D', 'Project E'],
            'department': ['IT', 'HR', 'Finance', 'IT', 'Finance'],
            'budget': [100000, 50000, 75000, 120000, 80000]
        })
        
        print("示例数据:")
        print(data)
        
        # 保存到DuckDB数据库
        print("连接DuckDB数据库...")
        conn = duckdb.connect(db_path)
        print("创建表...")
        conn.execute("CREATE TABLE projects AS SELECT * FROM data")
        print("查询数据...")
        result = conn.execute("SELECT * FROM projects").fetchdf()
        print("从DuckDB查询的结果:")
        print(result)
        
        # 测试SQL查询
        print("执行统计查询...")
        stats_result = conn.execute("""
            SELECT department, COUNT(*) as project_count, AVG(budget) as avg_budget
            FROM projects 
            GROUP BY department
            ORDER BY avg_budget DESC
        """).fetchdf()
        print("统计查询结果:")
        print(stats_result)
        
        conn.close()
        
        # 清理临时文件
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"已清理临时文件: {db_path}")
            
        print("手动DuckDB连接器测试完成")
        
    except Exception as e:
        print(f"手动DuckDB连接器测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_duckdb_connector_manually()
import duckdb
import pandas as pd

print("测试DuckDB连接...")

# 测试内存数据库连接
try:
    conn = duckdb.connect(':memory:')
    print("内存数据库连接成功")
    
    # 测试简单查询
    result = conn.execute('SELECT 1 as test').fetchdf()
    print("简单查询结果:", result)
    
    # 测试创建表和插入数据
    conn.execute("CREATE TABLE test_table (id INTEGER, name VARCHAR)")
    conn.execute("INSERT INTO test_table VALUES (1, 'test')")
    result = conn.execute("SELECT * FROM test_table").fetchdf()
    print("表查询结果:", result)
    
    conn.close()
    print("DuckDB测试完成")
except Exception as e:
    print(f"DuckDB测试失败: {e}")
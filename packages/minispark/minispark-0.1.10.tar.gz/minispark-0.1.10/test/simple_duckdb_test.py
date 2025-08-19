import duckdb
import pandas as pd
import os
import tempfile

print("开始测试DuckDB...")

# 创建临时数据库文件
temp_dir = tempfile.gettempdir()
db_path = os.path.join(temp_dir, 'simple_test.db')
print(f"数据库路径: {db_path}")

try:
    # 创建示例数据
    data = pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['A', 'B', 'C']
    })
    
    print("创建的示例数据:")
    print(data)
    
    # 连接DuckDB并保存数据
    print("连接DuckDB数据库...")
    conn = duckdb.connect(db_path)
    print("创建表...")
    conn.execute("CREATE TABLE test_table AS SELECT * FROM data")
    print("查询数据...")
    result = conn.execute("SELECT * FROM test_table").fetchdf()
    print("查询结果:")
    print(result)
    conn.close()
    
    # 验证文件是否存在
    if os.path.exists(db_path):
        print(f"数据库文件已创建: {db_path}")
        # 清理文件
        os.remove(db_path)
        print("已清理数据库文件")
    else:
        print("数据库文件未创建")
        
    print("DuckDB测试完成")
    
except Exception as e:
    print(f"DuckDB测试失败: {e}")
    import traceback
    traceback.print_exc()
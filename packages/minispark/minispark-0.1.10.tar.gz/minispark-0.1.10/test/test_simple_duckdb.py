import duckdb

print("创建连接")
conn = duckdb.connect(":memory:")
print("连接成功")

print("执行查询")
result = conn.execute("SELECT 'Hello World' as msg").fetchone()
print("查询结果:", result)

conn.close()
print("完成")
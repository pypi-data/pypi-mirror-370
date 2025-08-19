import duckdb

conn = duckdb.connect(':memory:')
print('连接成功')

result = conn.execute('SELECT 1').fetchdf()
print('查询结果:', result)
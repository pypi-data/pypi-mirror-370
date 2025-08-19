import duckdb
import os

# 删除可能存在的测试数据库文件
if os.path.exists("test.db"):
    os.remove("test.db")

print("创建文件数据库连接")
conn = duckdb.connect("test.db")
print("连接成功")

print("执行查询")
result = conn.execute("SELECT 'Hello World' as msg").fetchone()
print("查询结果:", result)

conn.close()
print("完成")

# 清理测试文件
if os.path.exists("test.db"):
    os.remove("test.db")
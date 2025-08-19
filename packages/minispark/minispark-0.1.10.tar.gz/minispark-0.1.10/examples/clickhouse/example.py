"""
ClickHouse 连接器使用示例
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from minispark import MiniSpark, ClickHouseConnector


def main():
    """主函数"""
    print("ClickHouse 连接器使用示例")
    
    try:
        # 初始化 MiniSpark
        spark = MiniSpark()
        print("✅ MiniSpark 初始化成功")
        
        # 添加 ClickHouse 连接器
        # 注意：请根据你的 ClickHouse 配置修改以下参数
        clickhouse_connector = ClickHouseConnector(
            name='clickhouse_example',
            host='localhost',      # ClickHouse 主机
            port=9000,             # ClickHouse 端口 (TCP接口)
            user='default',        # 用户名
            password='',           # 密码
            database='default'     # 数据库名
        )
        spark.add_connector('clickhouse', clickhouse_connector)
        print("✅ ClickHouse 连接器添加成功")
        
        # 创建示例表 (如果表不存在)
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id UInt32,
            name String,
            age UInt8,
            city String
        ) ENGINE = MergeTree()
        ORDER BY id
        """
        
        # 执行创建表的查询
        spark.load_data('clickhouse', create_table_query, 'create_result', register=False)
        print("✅ 示例表创建成功")
        
        # 插入一些示例数据
        insert_query = """
        INSERT INTO users (id, name, age, city) VALUES
        (1, 'Alice', 25, 'New York'),
        (2, 'Bob', 30, 'London'),
        (3, 'Charlie', 35, 'Tokyo'),
        (4, 'David', 28, 'Paris'),
        (5, 'Eve', 32, 'Berlin')
        """
        
        spark.load_data('clickhouse', insert_query, 'insert_result', register=False)
        print("✅ 示例数据插入成功")
        
        # 查询数据
        select_query = "SELECT * FROM users WHERE age > 30"
        df = spark.load_data('clickhouse', select_query, 'users_over_30')
        print("✅ 数据查询成功")
        print("查询结果:")
        print(df)
        print()
        
        # 使用 execute_query 方法执行查询
        result = spark.execute_query("""
            SELECT city, avg(age) as avg_age
            FROM users
            GROUP BY city
            ORDER BY avg_age DESC
        """)
        print("✅ 聚合查询执行成功")
        print("聚合查询结果:")
        print(result)
        
        # 清理资源
        spark.close()
        print("✅ 示例运行完成")
        
    except Exception as e:
        print(f"❌ 示例运行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
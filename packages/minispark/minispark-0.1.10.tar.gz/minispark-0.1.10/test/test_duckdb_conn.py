import duckdb
import pandas as pd
from datetime import datetime

def duckdb_demo():
    # 1. 连接数据库（使用内存数据库进行演示）
    print("=== 连接数据库 ===")
    con = duckdb.connect(database=':memory:')
    print("成功连接到内存数据库")

    # 2. 创建表并插入数据
    print("\n=== 创建表并插入数据 ===")
    con.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name VARCHAR,
            email VARCHAR UNIQUE,
            join_date DATE,
            tier VARCHAR
        )
    """)
    
    con.execute("""
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            order_date DATE,
            amount DECIMAL(10,2),
            status VARCHAR,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)
    
    # 插入客户数据
    con.execute("""
        INSERT INTO customers VALUES
        (1, 'Alice Smith', 'alice@example.com', '2023-01-15', 'premium'),
        (2, 'Bob Johnson', 'bob@example.com', '2023-02-20', 'standard'),
        (3, 'Charlie Brown', 'charlie@example.com', '2023-03-10', 'standard'),
        (4, 'Diana Prince', 'diana@example.com', '2023-04-05', 'premium')
    """)
    
    # 插入订单数据
    con.execute("""
        INSERT INTO orders VALUES
        (101, 1, '2023-05-01', 99.99, 'completed'),
        (102, 1, '2023-06-15', 149.50, 'completed'),
        (103, 2, '2023-05-20', 49.99, 'completed'),
        (104, 3, '2023-06-01', 79.99, 'pending'),
        (105, 4, '2023-06-10', 199.99, 'completed'),
        (106, 2, '2023-06-18', 29.99, 'refunded')
    """)
    
    print("创建了 customers 和 orders 表并插入了示例数据")

    # 3. 基本查询操作
    print("\n=== 基本查询示例 ===")
    # 查询所有高级会员
    premium_customers = con.execute("""
        SELECT id, name, email FROM customers WHERE tier = 'premium'
    """).fetchall()
    print("高级会员列表：")
    for customer in premium_customers:
        print(f"ID: {customer[0]}, 姓名: {customer[1]}, 邮箱: {customer[2]}")
    
    # 以DataFrame形式查询订单
    orders_df = con.execute("""
        SELECT order_id, customer_id, amount, status 
        FROM orders 
        WHERE status = 'completed'
        ORDER BY amount DESC
    """).df()
    print("\n已完成的订单（按金额降序）：")
    print(orders_df)

    # 4. 复杂查询和聚合分析
    print("\n=== 复杂查询和聚合分析 ===")
    # 每个客户的总消费金额
    customer_spending = con.execute("""
        SELECT c.id, c.name, SUM(o.amount) as total_spent, COUNT(o.order_id) as order_count
        FROM customers c
        LEFT JOIN orders o ON c.id = o.customer_id
        GROUP BY c.id, c.name
        ORDER BY total_spent DESC
    """).df()
    print("客户消费统计：")
    print(customer_spending)

    # 5. 与Pandas集成
    print("\n=== 与Pandas集成 ===")
    # 创建一个Pandas DataFrame
    products_df = pd.DataFrame({
        'product_id': [1, 2, 3, 4],
        'name': ['Laptop', 'Phone', 'Tablet', 'Headphones'],
        'category': ['Electronics', 'Electronics', 'Electronics', 'Audio'],
        'price': [999.99, 699.99, 299.99, 199.99],
        'stock': [15, 30, 25, 50]
    })
    
    # 将DataFrame注册为DuckDB临时表
    con.register('products', products_df)
    
    # 使用SQL查询DataFrame
    expensive_products = con.execute("""
        SELECT name, price, category 
        FROM products 
        WHERE price > 500
        ORDER BY price DESC
    """).df()
    print("价格超过500的产品：")
    print(expensive_products)

    # 6. 处理外部文件（这里使用模拟数据演示）
    print("\n=== 处理外部文件 ===")
    # 先创建一个示例CSV文件
    demo_data = pd.DataFrame({
        'date': pd.date_range(start='2023-01-01', periods=10),
        'sales': [1200, 1500, 1300, 1700, 1900, 1600, 1800, 2100, 1400, 1600],
        'region': ['North', 'South', 'East', 'West', 'North', 'South', 'East', 'West', 'North', 'South']
    })
    demo_data.to_csv('sales_demo.csv', index=False)
    print("已创建示例CSV文件: sales_demo.csv")
    
    # 直接查询CSV文件
    csv_query = con.execute("""
        SELECT region, AVG(sales) as avg_sales, SUM(sales) as total_sales
        FROM read_csv('sales_demo.csv', header=True, parse_dates=['date'])
        GROUP BY region
        ORDER BY total_sales DESC
    """).df()
    print("按地区的销售统计：")
    print(csv_query)

    # 7. 事务处理示例
    print("\n=== 事务处理示例 ===")
    try:
        con.begin()
        print("开始事务...")
        
        # 插入新客户
        con.execute("""
            INSERT INTO customers VALUES
            (5, 'Eve Adams', 'eve@example.com', '2023-07-01', 'standard')
        """)
        
        # 为新客户创建订单
        con.execute("""
            INSERT INTO orders VALUES
            (107, 5, '2023-07-02', 89.99, 'completed')
        """)
        
        con.commit()
        print("事务提交成功")
        
        # 验证新数据
        new_customer = con.execute("SELECT * FROM customers WHERE id = 5").df()
        print("新插入的客户：")
        print(new_customer)
        
    except Exception as e:
        con.rollback()
        print(f"事务失败，已回滚: {str(e)}")

    # 8. 关闭连接
    print("\n=== 关闭连接 ===")
    con.close()
    print("数据库连接已关闭")

if __name__ == "__main__":
    duckdb_demo()

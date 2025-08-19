"""
测试修改后的execute_query方法，验证table_name和register参数功能
"""

import pandas as pd
import os
import sys
import tempfile

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from minispark import MiniSpark, CSVConnector


def create_test_csv_data():
    """创建测试CSV数据"""
    # 创建销售数据
    sales_data = pd.DataFrame({
        'sale_id': [1, 2, 3, 4, 5, 6],
        'product_id': [101, 102, 103, 101, 104, 102],
        'quantity': [2, 1, 5, 3, 2, 4],
        'sale_date': ['2023-01-15', '2023-01-16', '2023-01-17', '2023-01-18', '2023-01-19', '2023-01-20']
    })
    
    # 创建产品数据
    products_data = pd.DataFrame({
        'product_id': [101, 102, 103, 104],
        'product_name': ['Laptop', 'Mouse', 'Keyboard', 'Monitor'],
        'price': [1200.00, 25.00, 75.00, 300.00]
    })
    
    # 保存为CSV文件
    temp_dir = tempfile.gettempdir()
    sales_csv = os.path.join(temp_dir, 'sales_test.csv')
    products_csv = os.path.join(temp_dir, 'products_test.csv')
    
    sales_data.to_csv(sales_csv, index=False)
    products_data.to_csv(products_csv, index=False)
    
    print("创建测试CSV数据:")
    print("销售数据:")
    print(sales_data)
    print("\n产品数据:")
    print(products_data)
    print()
    
    return sales_csv, products_csv


def test_execute_query_with_registration():
    """测试execute_query方法的表注册功能"""
    print("=== 测试execute_query方法的表注册功能 ===")
    
    # 创建测试数据
    sales_csv, products_csv = create_test_csv_data()
    
    try:
        # 初始化MiniSpark
        spark = MiniSpark()
        
        # 添加CSV连接器
        sales_connector = CSVConnector('sales')
        products_connector = CSVConnector('products')
        spark.add_connector('sales', sales_connector)
        spark.add_connector('products', products_connector)
        
        # 加载数据
        sales_df = spark.load_data('sales', sales_csv, 'sales')
        products_df = spark.load_data('products', products_csv, 'products')
        
        print("从CSV加载的数据:")
        print("销售数据:")
        print(sales_df)
        print("\n产品数据:")
        print(products_df)
        print()
        
        # 测试新的execute_query功能 - 将查询结果注册为新表
        print("执行查询并将结果注册为新表...")
        
        # 执行一个聚合查询并注册结果
        spark.execute_query("""
            SELECT product_id, SUM(quantity) as total_quantity
            FROM sales
            GROUP BY product_id
        """, table_name="product_summary")
        
        print("产品汇总表已注册")
        
        # 查看注册的表
        summary_result = spark.execute_query("SELECT * FROM product_summary")
        print("产品汇总数据:")
        print(summary_result)
        print()
        
        # 执行复杂查询并将结果注册为表
        spark.execute_query("""
            SELECT 
                p.product_name,
                p.price,
                s.total_quantity,
                (p.price * s.total_quantity) as total_value
            FROM products p
            JOIN product_summary s ON p.product_id = s.product_id
            ORDER BY total_value DESC
        """, table_name="sales_analysis")
        
        print("销售分析表已注册")
        
        # 查询注册的分析表
        analysis_result = spark.execute_query("SELECT * FROM sales_analysis")
        print("销售分析数据:")
        print(analysis_result)
        print()
        
        # 测试不注册的情况
        print("执行查询但不注册结果...")
        temp_result = spark.execute_query("""
            SELECT COUNT(*) as total_sales
            FROM sales
        """, table_name="temp_count", register=False)
        
        print("临时查询结果:")
        print(temp_result)
        
        # 验证表未被注册
        try:
            spark.execute_query("SELECT * FROM temp_count")
            print("错误：临时表不应该被注册")
        except Exception as e:
            print("确认：临时表未被注册")
        
        # 关闭MiniSpark
        spark.close()
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    # 清理测试文件
    for file_path in [sales_csv, products_csv]:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"已清理测试文件: {file_path}")
    
    print("execute_query方法测试完成\n")


if __name__ == "__main__":
    test_execute_query_with_registration()
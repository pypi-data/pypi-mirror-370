"""
Excel连接器使用示例
"""

import pandas as pd
import os
import sys

try:
    import openpyxl
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from minispark import MiniSpark, ExcelConnector


def excel_example():
    """Excel使用示例"""
    print("=== Excel连接器使用示例 ===")
    
    if not EXCEL_AVAILABLE:
        print("跳过Excel示例，因为未安装openpyxl库")
        print("请运行以下命令安装: uv pip install openpyxl")
        return
    
    # 构建Excel文件路径
    excel_path = os.path.join(os.path.dirname(__file__), 'sales_data.xlsx')
    
    # 初始化MiniSpark
    spark = MiniSpark()
    
    # 添加Excel连接器
    excel_connector = ExcelConnector('excel', 'Products')  # 默认读取Products工作表
    spark.add_connector('excel', excel_connector)
    print("成功添加Excel连接器")
    
    # 从Excel加载Products表数据
    products_df = spark.load_data('excel', excel_path, 'products')
    print("从Excel加载的产品数据:")
    print(products_df)
    print()
    
    # 添加另一个连接器读取Orders表
    orders_connector = ExcelConnector('excel_orders', 'Orders')
    spark.add_connector('excel_orders', orders_connector)
    orders_df = spark.load_data('excel_orders', excel_path, 'orders')
    print("从Excel加载的订单数据:")
    print(orders_df)
    print()
    
    # 执行查询
    result = spark.execute_query("""
        SELECT p.product_name, p.category, p.price, o.quantity, 
               (p.price * o.quantity) as total_value
        FROM products p
        JOIN orders o ON p.product_id = o.product_id
        ORDER BY total_value DESC
    """)
    print("产品销售详情（按总价值排序）:")
    print(result)
    print()
    
    # 关闭连接
    spark.close()
    
    # 清理示例文件
    if os.path.exists(excel_path):
        os.remove(excel_path)
        print("已清理示例文件: sales_data.xlsx")
    
    print("Excel示例完成\n")


if __name__ == "__main__":
    # 首先生成示例数据
    from generate_data import create_sample_excel_data
    create_sample_excel_data()
    
    # 运行示例
    excel_example()
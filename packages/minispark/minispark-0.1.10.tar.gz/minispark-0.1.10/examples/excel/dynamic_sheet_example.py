"""
Excel连接器动态工作表使用示例
演示如何使用改进后的Excel连接器在加载数据时动态指定工作表
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


def create_sample_excel_data():
    """创建包含多个工作表的示例Excel数据"""
    if not EXCEL_AVAILABLE:
        print("需要安装openpyxl库: pip install openpyxl")
        return None, None, None
    
    print("创建包含多个工作表的示例Excel数据...")
    
    # 创建示例产品数据
    products_data = pd.DataFrame({
        'product_id': [1, 2, 3, 4],
        'product_name': ['笔记本电脑', '手机', '平板', '耳机'],
        'category': ['电子产品', '电子产品', '电子产品', '配件'],
        'price': [5000, 3000, 2000, 500]
    })
    
    # 创建示例订单数据
    orders_data = pd.DataFrame({
        'order_id': [101, 102, 103, 104],
        'product_id': [1, 3, 2, 1],
        'quantity': [2, 1, 3, 1],
        'order_date': ['2023-01-15', '2023-01-16', '2023-01-17', '2023-01-18']
    })
    
    # 创建示例客户数据
    customers_data = pd.DataFrame({
        'customer_id': [1001, 1002, 1003],
        'customer_name': ['张三', '李四', '王五'],
        'city': ['北京', '上海', '广州']
    })
    
    # 保存为Excel文件（不同工作表）
    with pd.ExcelWriter('multi_sheet_data.xlsx') as writer:
        products_data.to_excel(writer, sheet_name='Products', index=False)
        orders_data.to_excel(writer, sheet_name='Orders', index=False)
        customers_data.to_excel(writer, sheet_name='Customers', index=False)
    
    print("示例数据已保存到multi_sheet_data.xlsx:")
    print("Products表:")
    print(products_data)
    print("\nOrders表:")
    print(orders_data)
    print("\nCustomers表:")
    print(customers_data)
    print()
    
    return products_data, orders_data, customers_data


def dynamic_sheet_example():
    """动态工作表使用示例"""
    print("=== Excel连接器动态工作表使用示例 ===")
    
    if not EXCEL_AVAILABLE:
        print("跳过Excel示例，因为未安装openpyxl库")
        print("请运行以下命令安装: pip install openpyxl")
        return
    
    # 创建示例数据
    products_data, orders_data, customers_data = create_sample_excel_data()
    
    # 初始化MiniSpark
    spark = MiniSpark()
    
    # 添加一个通用的Excel连接器（不指定默认工作表）
    excel_connector = ExcelConnector('excel_connector')
    spark.add_connector('excel', excel_connector)
    print("成功添加通用Excel连接器")
    
    # 使用同一个连接器从不同工作表加载数据
    print("--- 使用同一个连接器读取不同工作表 ---")
    
    # 从Products工作表加载数据
    products_df = spark.load_data('excel', 'multi_sheet_data.xlsx', 'products', sheet_name='Products')
    print("从Products工作表加载的数据:")
    print(products_df)
    print()
    
    # 从Orders工作表加载数据
    orders_df = spark.load_data('excel', 'multi_sheet_data.xlsx', 'orders', sheet_name='Orders')
    print("从Orders工作表加载的数据:")
    print(orders_df)
    print()
    
    # 从Customers工作表加载数据
    customers_df = spark.load_data('excel', 'multi_sheet_data.xlsx', 'customers', sheet_name='Customers')
    print("从Customers工作表加载的数据:")
    print(customers_df)
    print()
    
    # 显示表结构
    print("--- 表结构信息 ---")
    print("Products表列名:", list(products_df.columns))
    print("Orders表列名:", list(orders_df.columns))
    print("Customers表列名:", list(customers_df.columns))
    print()
    
    # 关闭连接
    spark.close()
    
    # 清理示例文件
    if os.path.exists('multi_sheet_data.xlsx'):
        os.remove('multi_sheet_data.xlsx')
        print("已清理示例文件: multi_sheet_data.xlsx")
    
    print("Excel动态工作表示例完成\n")


def default_sheet_example():
    """默认工作表示例"""
    print("=== Excel连接器默认工作表示例 ===")
    
    if not EXCEL_AVAILABLE:
        print("跳过Excel示例，因为未安装openpyxl库")
        return
    
    # 创建示例数据
    products_data, orders_data, customers_data = create_sample_excel_data()
    
    # 初始化MiniSpark
    spark = MiniSpark()
    
    # 添加一个指定默认工作表的Excel连接器
    excel_connector = ExcelConnector('excel_connector', sheet_name='Products')  # 默认读取Products工作表
    spark.add_connector('excel', excel_connector)
    print("成功添加默认工作表Excel连接器")
    
    # 使用默认工作表加载数据（不指定sheet_name参数）
    products_df = spark.load_data('excel', 'multi_sheet_data.xlsx', 'products_table')
    print("使用默认工作表加载的数据:")
    print(products_df)
    print()
    
    # 也可以覆盖默认工作表
    orders_df = spark.load_data('excel', 'multi_sheet_data.xlsx', 'orders_table', sheet_name='Orders')
    print("覆盖默认工作表加载的数据:")
    print(orders_df)
    print()
    
    # 关闭连接
    spark.close()
    
    # 清理示例文件
    if os.path.exists('multi_sheet_data.xlsx'):
        os.remove('multi_sheet_data.xlsx')
        print("已清理示例文件: multi_sheet_data.xlsx")
    
    print("Excel默认工作表示例完成\n")


if __name__ == "__main__":
    # 运行动态工作表示例
    dynamic_sheet_example()
    
    # 运行默认工作表示例
    default_sheet_example()
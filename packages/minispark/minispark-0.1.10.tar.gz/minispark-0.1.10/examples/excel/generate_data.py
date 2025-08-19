"""
生成Excel示例数据
"""

import pandas as pd
import os

try:
    import openpyxl
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False


def create_sample_excel_data():
    """创建示例Excel数据"""
    if not EXCEL_AVAILABLE:
        print("需要安装openpyxl库: pip install openpyxl")
        return None, None
    
    print("创建示例Excel数据...")
    
    # 创建示例销售数据
    sales_data = pd.DataFrame({
        'product_id': [1, 2, 3, 4, 5, 6, 7, 8],
        'product_name': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones', 'Webcam', 'Printer', 'Scanner'],
        'category': ['Electronics', 'Accessories', 'Accessories', 'Electronics', 'Accessories', 'Electronics', 'Electronics', 'Electronics'],
        'price': [1200.00, 25.00, 75.00, 300.00, 150.00, 80.00, 150.00, 100.00],
        'stock': [50, 200, 150, 30, 75, 40, 25, 20]
    })
    
    # 创建示例订单数据
    orders_data = pd.DataFrame({
        'order_id': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
        'product_id': [1, 3, 2, 5, 4, 1, 6, 3, 2, 7],
        'quantity': [2, 5, 3, 2, 1, 1, 2, 4, 1, 1],
        'order_date': ['2023-01-15', '2023-01-16', '2023-01-16', '2023-01-17', '2023-01-18', 
                      '2023-01-19', '2023-01-20', '2023-01-21', '2023-01-22', '2023-01-23']
    })
    
    # 保存为Excel文件在当前目录下
    excel_path = os.path.join(os.path.dirname(__file__), 'sales_data.xlsx')
    with pd.ExcelWriter(excel_path) as writer:
        sales_data.to_excel(writer, sheet_name='Products', index=False)
        orders_data.to_excel(writer, sheet_name='Orders', index=False)
    
    print("示例销售数据已保存到sales_data.xlsx:")
    print("Products表:")
    print(sales_data)
    print("\nOrders表:")
    print(orders_data)
    print()
    
    return sales_data, orders_data


if __name__ == "__main__":
    create_sample_excel_data()
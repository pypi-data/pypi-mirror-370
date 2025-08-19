"""
Excel连接器与explode功能结合使用示例
演示如何将Excel中的数据加载后使用explode_column功能拆分字段
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


def create_sample_excel_data_with_explode():
    """创建包含需要拆分字段的示例Excel数据"""
    if not EXCEL_AVAILABLE:
        print("需要安装openpyxl库: pip install openpyxl")
        return None
    
    print("创建包含需要拆分字段的示例Excel数据...")
    
    # 创建示例产品数据，其中tags列包含用逗号分隔的标签，description列包含用多种分隔符分隔的内容
    products_data = pd.DataFrame({
        'product_id': [1, 2, 3, 4],
        'product_name': ['笔记本电脑', '手机', '平板', '耳机'],
        'category': ['电子产品', '电子产品', '电子产品', '配件'],
        'tags': ['tech,computer,work', 'tech,mobile,communication', 'tech,computer,entertainment', 'audio,accessory,music'],
        'description': ['fast;light|portable', 'smart|modern;communication', 'light|entertainment;portable', 'sound|music;accessory'],
        'features': ['wifi;bluetooth|usb', 'touch-screen|camera;gps', 'battery|screen;touch', 'wireless|bluetooth;comfort'],
        'price': [5000, 3000, 2000, 500]
    })
    
    # 保存为Excel文件
    with pd.ExcelWriter('products_with_tags.xlsx') as writer:
        products_data.to_excel(writer, sheet_name='Products', index=False)
    
    print("示例数据已保存到products_with_tags.xlsx:")
    print(products_data)
    print()
    
    return products_data


def excel_explode_example():
    """Excel数据与explode功能结合使用示例"""
    print("=== Excel连接器与explode功能结合使用示例 ===")
    
    if not EXCEL_AVAILABLE:
        print("跳过Excel示例，因为未安装openpyxl库")
        print("请运行以下命令安装: pip install openpyxl")
        return
    
    # 创建示例数据
    products_data = create_sample_excel_data_with_explode()
    
    # 初始化MiniSpark
    spark = MiniSpark()
    
    try:
        # 添加Excel连接器
        excel_connector = ExcelConnector('excel_connector')
        spark.add_connector('excel', excel_connector)
        print("成功添加Excel连接器")
        
        # 从Excel加载数据
        products_df = spark.load_data('excel', 'products_with_tags.xlsx', 'products', sheet_name='Products')
        print("从Excel加载的产品数据:")
        print(products_df)
        print()
        
        # 使用数据处理器的explode功能将tags列按逗号拆分成多行
        processor = spark.processor
        exploded_df = processor.explode_column(products_df, 'tags', ',', 'tags')
        
        print("将tags列按逗号拆分后的数据:")
        print(exploded_df)
        print()
        
        # 演示使用多个分隔符拆分description列
        print("将description列按多个分隔符(';|')拆分后的数据:")
        multi_separator_exploded_df = processor.explode_column(exploded_df, 'description', [';', '|'], 'description')
        print(multi_separator_exploded_df)
        print()
        
        # 演示链式操作，再次使用多个分隔符拆分features列
        print("将features列按多个分隔符(';|')拆分后的数据:")
        fully_exploded_df = processor.explode_column(multi_separator_exploded_df, 'features', [';', '|'], 'features')
        print(fully_exploded_df)
        print()
        
        # 注册拆分后的数据到引擎
        spark.engine.register_table('exploded_products', fully_exploded_df)
        
        # 执行SQL查询，查找包含特定标签的产品
        result = spark.execute_query("""
            SELECT product_name, category, tags, description, features, price
            FROM exploded_products 
            WHERE tags IN ('tech', 'computer', 'audio')
            ORDER BY product_name, tags
        """)
        
        print("查询包含'tech', 'computer', 'audio'标签的产品:")
        print(result)
        print()
        
        # 统计各标签的数量
        tag_stats = spark.execute_query("""
            SELECT tags, COUNT(*) as count
            FROM exploded_products
            GROUP BY tags
            ORDER BY count DESC
        """)
        
        print("各标签的数量统计:")
        print(tag_stats)
        print()
        
        # 统计各描述词的数量
        desc_stats = spark.execute_query("""
            SELECT description, COUNT(*) as count
            FROM exploded_products
            GROUP BY description
            ORDER BY count DESC
        """)
        
        print("各描述词的数量统计:")
        print(desc_stats)
        print()
        
        # 统计各功能的数量
        feature_stats = spark.execute_query("""
            SELECT features, COUNT(*) as count
            FROM exploded_products
            GROUP BY features
            ORDER BY count DESC
        """)
        
        print("各功能的数量统计:")
        print(feature_stats)
        print()
        
        # 展示行数变化
        print(f"原始数据行数: {len(products_df)}")
        print(f"tags列拆分后数据行数: {len(exploded_df)}")
        print(f"tags+description列拆分后数据行数: {len(multi_separator_exploded_df)}")
        print(f"全部三列拆分后数据行数: {len(fully_exploded_df)}")
        print()
        
        # 演示复杂的SQL查询
        complex_query_result = spark.execute_query("""
            SELECT 
                product_name,
                category,
                COUNT(DISTINCT tags) as tag_count,
                COUNT(DISTINCT description) as desc_count,
                COUNT(DISTINCT features) as feature_count
            FROM exploded_products
            GROUP BY product_name, category
            ORDER BY tag_count DESC
        """)
        
        print("每个产品的标签、描述和功能计数:")
        print(complex_query_result)
        print()
        
    except Exception as e:
        print(f"使用Excel连接器时出错: {e}")
        import traceback
        traceback.print_exc()
    
    # 关闭连接
    spark.close()
    
    # 清理示例文件
    if os.path.exists('products_with_tags.xlsx'):
        os.remove('products_with_tags.xlsx')
        print("已清理示例文件: products_with_tags.xlsx")
    
    print("Excel与explode功能结合使用示例完成\n")


if __name__ == "__main__":
    excel_explode_example()
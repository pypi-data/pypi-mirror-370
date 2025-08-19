"""
MiniSpark CLI 入口点
"""

import argparse
import sys
from .minispark import MiniSpark


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="MiniSpark CLI工具")
    parser.add_argument(
        "--version", action="version", version="%(prog)s {version}".format(version="0.1.10")
    )
    
    # 添加子命令
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 示例命令
    example_parser = subparsers.add_parser("example", help="运行示例")
    
    args = parser.parse_args()
    
    if args.command == "example":
        run_example()
    else:
        parser.print_help()


def run_example():
    """运行简单示例"""
    print("运行MiniSpark示例...")
    
    try:
        # 初始化MiniSpark
        spark = MiniSpark()
        print("✅ MiniSpark初始化成功")
        
        # 创建示例数据
        import pandas as pd
        data = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
            'age': [25, 30, 35, 28, 32]
        })
        data.to_csv('example_data.csv', index=False)
        print("✅ 示例数据创建成功")
        
        # 添加CSV连接器
        from .connectors.csv_connector import CSVConnector
        csv_connector = CSVConnector('example_csv')
        spark.add_connector('csv', csv_connector)
        print("✅ CSV连接器添加成功")
        
        # 加载数据
        df = spark.load_data('csv', 'example_data.csv', 'people')
        print("✅ 数据加载成功")
        print("数据预览:")
        print(df)
        
        # 执行查询
        result = spark.execute_query("""
            SELECT name, age 
            FROM people 
            WHERE age > 30
            ORDER BY age DESC
        """)
        print("\n✅ 查询执行成功")
        print("查询结果:")
        print(result)
        
        # 清理
        import os
        if os.path.exists('example_data.csv'):
            os.remove('example_data.csv')
            
        spark.close()
        print("✅ 示例运行完成")
        
    except Exception as e:
        print(f"❌ 示例运行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
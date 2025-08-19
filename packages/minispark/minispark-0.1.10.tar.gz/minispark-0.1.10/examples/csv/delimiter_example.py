"""
CSV连接器分隔符使用示例
演示如何使用不同的分隔符加载CSV文件
"""

import pandas as pd
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from minispark import MiniSpark, CSVConnector


def create_sample_data_with_delimiters():
    """创建使用不同分隔符的示例CSV数据"""
    print("创建使用不同分隔符的示例CSV数据...")
    
    # 创建示例数据
    data = pd.DataFrame({
        'id': [1, 2, 3, 4],
        'name': ['张三', '李四', '王五', '赵六'],
        'department': ['技术部', '销售部', '人事部', '财务部'],
        'salary': [8000, 7500, 6500, 7000]
    })
    
    # 保存为不同分隔符的CSV文件
    # 1. 默认逗号分隔
    data.to_csv('employees_comma.csv', index=False)
    print("已创建逗号分隔的CSV文件: employees_comma.csv")
    
    # 2. 分号分隔
    data.to_csv('employees_semicolon.csv', sep=';', index=False)
    print("已创建分号分隔的CSV文件: employees_semicolon.csv")
    
    # 3. 制表符分隔
    data.to_csv('employees_tab.csv', sep='\t', index=False)
    print("已创建制表符分隔的CSV文件: employees_tab.csv")
    
    # 4. 管道符分隔
    data.to_csv('employees_pipe.csv', sep='|', index=False)
    print("已创建管道符分隔的CSV文件: employees_pipe.csv")
    
    print()


def csv_delimiter_example():
    """CSV分隔符使用示例"""
    print("=== CSV连接器分隔符使用示例 ===")
    
    # 创建示例数据
    create_sample_data_with_delimiters()
    
    # 初始化MiniSpark
    spark = MiniSpark()
    
    try:
        # 1. 使用默认逗号分隔符
        print("--- 使用默认逗号分隔符 ---")
        comma_connector = CSVConnector('comma_csv')
        spark.add_connector('comma', comma_connector)
        
        comma_df = spark.load_data('comma', 'employees_comma.csv', 'comma_employees')
        print("逗号分隔的员工数据:")
        print(comma_df)
        print()
        
        # 2. 使用分号分隔符
        print("--- 使用分号分隔符 ---")
        semicolon_connector = CSVConnector('semicolon_csv', delimiter=';')
        spark.add_connector('semicolon', semicolon_connector)
        
        semicolon_df = spark.load_data('semicolon', 'employees_semicolon.csv', 'semicolon_employees')
        print("分号分隔的员工数据:")
        print(semicolon_df)
        print()
        
        # 3. 使用制表符分隔符
        print("--- 使用制表符分隔符 ---")
        tab_connector = CSVConnector('tab_csv', delimiter='\t')
        spark.add_connector('tab', tab_connector)
        
        tab_df = spark.load_data('tab', 'employees_tab.csv', 'tab_employees')
        print("制表符分隔的员工数据:")
        print(tab_df)
        print()
        
        # 4. 使用管道符分隔符
        print("--- 使用管道符分隔符 ---")
        pipe_connector = CSVConnector('pipe_csv', delimiter='|')
        spark.add_connector('pipe', pipe_connector)
        
        pipe_df = spark.load_data('pipe', 'employees_pipe.csv', 'pipe_employees')
        print("管道符分隔的员工数据:")
        print(pipe_df)
        print()
        
        # 5. 演示使用不同的编码
        print("--- 使用不同编码 ---")
        # 创建一个包含中文的UTF-8编码文件
        utf8_connector = CSVConnector('utf8_csv', delimiter=',', encoding='utf-8')
        spark.add_connector('utf8', utf8_connector)
        
        utf8_df = spark.load_data('utf8', 'employees_comma.csv', 'utf8_employees')
        print("UTF-8编码的员工数据:")
        print(utf8_df)
        print()
        
        # 执行查询示例
        print("--- 执行查询示例 ---")
        high_salary_employees = spark.execute_query("""
            SELECT name, department, salary 
            FROM comma_employees 
            WHERE salary > 7000
            ORDER BY salary DESC
        """, 'high_salary_employees')
        
        print("高薪员工:")
        print(high_salary_employees)
        print()
        
    except Exception as e:
        print(f"使用CSV连接器时出错: {e}")
        import traceback
        traceback.print_exc()
    
    # 关闭连接
    spark.close()
    
    # 清理示例文件
    try:
        os.remove('employees_comma.csv')
        os.remove('employees_semicolon.csv')
        os.remove('employees_tab.csv')
        os.remove('employees_pipe.csv')
        print("已清理示例文件")
    except:
        pass
    
    print("CSV分隔符示例完成\n")


if __name__ == "__main__":
    csv_delimiter_example()
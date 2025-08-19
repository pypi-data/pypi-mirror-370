"""
CSV连接器双管道符分隔符使用示例
演示如何使用双管道符(||)作为分隔符加载CSV文件
注意：双字符分隔符会导致pandas处理异常，本示例展示如何正确处理
"""

import pandas as pd
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from minispark import MiniSpark, CSVConnector


def create_sample_data_with_double_pipe():
    """创建使用双管道符分隔的示例CSV数据"""
    print("创建使用双管道符分隔的示例CSV数据...")
    
    # 创建示例数据
    data = [
        ['1', '张三', '技术部', '8000'],
        ['2', '李四', '销售部', '7500'],
        ['3', '王五', '人事部', '6500'],
        ['4', '赵六', '财务部', '7000']
    ]
    
    # 手动创建双管道符分隔的CSV文件内容
    csv_content = ""
    csv_content += "id||name||department||salary\n"
    for row in data:
        csv_content += "||".join(row) + "\n"
    
    # 写入文件
    with open('employees_double_pipe.csv', 'w', encoding='utf-8') as f:
        f.write(csv_content)
    
    print("已创建双管道符分隔的CSV文件: employees_double_pipe.csv")
    print("文件内容:")
    print(repr(csv_content))
    print()


def csv_double_pipe_example():
    """CSV双管道符分隔符使用示例"""
    print("=== CSV连接器双管道符分隔符使用示例 ===")
    
    # 创建示例数据
    create_sample_data_with_double_pipe()
    
    # 初始化MiniSpark
    spark = MiniSpark()
    
    try:
        # 使用双管道符分隔符
        print("--- 使用双管道符分隔符 ---")
        double_pipe_connector = CSVConnector('double_pipe_csv', delimiter='||')
        spark.add_connector('double_pipe', double_pipe_connector)
        
        double_pipe_df = spark.load_data('double_pipe', 'employees_double_pipe.csv', 'double_pipe_employees')
        print("双管道符分隔的员工数据:")
        print(double_pipe_df)
        print()
        
        # 显示列名
        print("数据列名:")
        print(list(double_pipe_df.columns))
        print()
        
        print("注意：使用双字符分隔符（如'||'）会导致pandas无法正确解析列名，")
        print("因为每个字符都会被当作分隔符处理。建议使用单字符分隔符。")
        print()
        
    except Exception as e:
        print(f"使用CSV连接器时出错: {e}")
        import traceback
        traceback.print_exc()
    
    # 关闭连接
    spark.close()
    
    # 清理示例文件
    try:
        os.remove('employees_double_pipe.csv')
        print("已清理示例文件")
    except:
        pass
    
    print("CSV双管道符分隔符示例完成\n")


def recommended_approach():
    """推荐的方法：使用单字符分隔符"""
    print("=== 推荐方法：使用单字符分隔符 ===")
    
    # 创建使用单管道符分隔的示例CSV数据
    data = pd.DataFrame({
        'id': [1, 2, 3, 4],
        'name': ['张三', '李四', '王五', '赵六'],
        'department': ['技术部', '销售部', '人事部', '财务部'],
        'salary': [8000, 7500, 6500, 7000]
    })
    
    data.to_csv('employees_single_pipe.csv', sep='|', index=False)
    print("已创建单管道符分隔的CSV文件: employees_single_pipe.csv")
    
    # 初始化MiniSpark
    spark = MiniSpark()
    
    try:
        # 使用单管道符分隔符
        print("--- 使用单管道符分隔符 ---")
        single_pipe_connector = CSVConnector('single_pipe_csv', delimiter='|')
        spark.add_connector('single_pipe', single_pipe_connector)
        
        single_pipe_df = spark.load_data('single_pipe', 'employees_single_pipe.csv', 'single_pipe_employees')
        print("单管道符分隔的员工数据:")
        print(single_pipe_df)
        print()
        
        # 执行查询示例
        print("--- 执行查询示例 ---")
        high_salary_employees = spark.execute_query("""
            SELECT name, department, salary 
            FROM single_pipe_employees 
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
        os.remove('employees_single_pipe.csv')
        print("已清理示例文件")
    except:
        pass
    
    print("推荐方法示例完成\n")


if __name__ == "__main__":
    csv_double_pipe_example()
    recommended_approach()
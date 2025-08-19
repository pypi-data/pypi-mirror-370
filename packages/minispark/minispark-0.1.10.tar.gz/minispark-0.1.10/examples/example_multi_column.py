"""
MiniSpark简化API功能示例
演示如何在DataProcessor中使用简化后的API直接传入整行数据给自定义函数
"""

import pandas as pd
import tempfile
import os
from minispark import MiniSpark
from minispark.connectors.csv_connector import CSVConnector


def create_sample_data():
    """创建示例数据"""
    # 创建示例数据
    data = pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'department': ['IT', 'HR', 'Finance', 'IT', 'Marketing'],
        'salary': [75000, 65000, 70000, 80000, 60000],
        'bonus': [7500, 6500, 7000, 8000, 6000],
        'experience': [5, 3, 4, 6, 2]
    })
    
    # 保存为CSV文件
    temp_dir = tempfile.gettempdir()
    csv_file = os.path.join(temp_dir, 'employees_simple_api.csv')
    data.to_csv(csv_file, index=False, encoding='utf-8')
    
    print("原始数据:")
    print(data)
    print()
    
    return csv_file


def simple_api_example():
    """演示简化后的API"""
    print("=== MiniSpark简化API功能示例 ===\n")
    
    # 创建示例数据
    csv_file = create_sample_data()
    
    try:
        # 初始化MiniSpark
        spark = MiniSpark()
        
        # 添加CSV连接器
        csv_connector = CSVConnector('csv')
        spark.add_connector('csv', csv_connector)
        
        # 从CSV加载数据
        df = spark.load_data('csv', csv_file, 'employees')
        print("从CSV加载的数据:")
        print(df)
        print()
        
        # 使用数据处理器
        processor = spark.processor
        
        # 示例1: 使用自定义函数处理整行数据（计算总薪酬）
        print("--- 示例1: 计算总薪酬（薪资+奖金） ---")
        df_with_total = processor.apply_custom_function(
            df, 
            'total_compensation',  # 新列名
            lambda row: row['salary'] + row['bonus']  # 函数
        )
        print("计算总薪酬后的数据:")
        print(df_with_total[['name', 'salary', 'bonus', 'total_compensation']])
        print()
        
        # 示例2: 使用更复杂的整行处理函数（计算绩效得分）
        print("--- 示例2: 计算绩效得分 ---")
        def calculate_performance_score(row):
            # 基于薪资、经验和部门计算绩效得分
            base_score = row['salary'] / 10000
            experience_bonus = row['experience'] * 2
            department_multiplier = 1.2 if row['department'] == 'IT' else 1.0
            return (base_score + experience_bonus) * department_multiplier
        
        df_with_score = processor.apply_custom_function(
            df, 
            'performance_score',  # 新列名
            calculate_performance_score  # 函数
        )
        print("计算绩效得分后的数据:")
        print(df_with_score[['name', 'department', 'salary', 'experience', 'performance_score']])
        print()
        
        # 示例3: 注册并应用处理整行数据的函数
        print("--- 示例3: 注册并应用处理整行数据的函数 ---")
        def calculate_annual_cost(row):
            # 计算年度总成本（薪资+奖金*12）
            return row['salary'] + row['bonus'] * 12
        
        # 注册函数
        processor.register_function('annual_cost', calculate_annual_cost)
        
        # 应用已注册的函数
        df_with_cost = processor.apply_function(
            df, 
            'annual_cost',  # 新列名
            'annual_cost'  # 已注册的函数名
        )
        print("计算年度成本后的数据:")
        print(df_with_cost[['name', 'salary', 'bonus', 'annual_cost']])
        print()
        
        # 示例4: 将处理后的数据注册到引擎并执行SQL查询
        print("--- 示例4: 使用SQL查询处理后的数据 ---")
        spark.engine.register_table('enhanced_employees', df_with_score)
        
        # 执行SQL查询，找出绩效得分最高的员工
        result = spark.execute_query("""
            SELECT name, department, performance_score
            FROM enhanced_employees
            ORDER BY performance_score DESC
            LIMIT 3
        """)
        print("绩效得分最高的3名员工:")
        print(result)
        print()
        
        # 示例5: 按部门统计平均绩效得分
        department_stats = spark.execute_query("""
            SELECT department, 
                   COUNT(*) as employee_count,
                   AVG(performance_score) as avg_performance_score
            FROM enhanced_employees
            GROUP BY department
            ORDER BY avg_performance_score DESC
        """)
        print("各部门平均绩效得分:")
        print(department_stats)
        print()
        
    except Exception as e:
        print(f"执行示例时出错: {e}")
        import traceback
        traceback.print_exc()
    
    # 清理
    spark.close()
    if os.path.exists(csv_file):
        os.remove(csv_file)
        print(f"已清理临时文件: {csv_file}")


if __name__ == "__main__":
    simple_api_example()
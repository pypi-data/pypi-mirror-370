"""
MiniSpark DataProcessor自动注册功能示例
演示如何使用DataProcessor处理数据后自动注册到本地引擎
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
        'id': [1, 2, 3, 4, 5],
        'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'department': ['IT', 'HR', 'Finance', 'IT', 'Marketing'],
        'salary': [75000, 65000, 70000, 80000, 60000],
        'bonus': [7500, 6500, 7000, 8000, 6000],
        'experience': [5, 3, 4, 6, 2],
        'tags': ['python,sql', 'excel,communication', 'finance,analysis', 'java,python', 'marketing,design']
    })
    
    # 保存为CSV文件
    temp_dir = tempfile.gettempdir()
    csv_file = os.path.join(temp_dir, 'employees_auto_register.csv')
    data.to_csv(csv_file, index=False, encoding='utf-8')
    
    print("原始数据:")
    print(data)
    print()
    
    return csv_file


def auto_register_example():
    """演示DataProcessor的自动注册功能"""
    print("=== MiniSpark DataProcessor自动注册功能示例 ===\n")
    
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
        
        # 示例1: 使用apply_custom_function处理数据并自动注册结果
        print("--- 示例1: 使用apply_custom_function处理数据并自动注册 ---")
        def calculate_total_compensation(row):
            """计算总薪酬（薪资+奖金）"""
            return row['salary'] + row['bonus']
        
        # 应用函数并自动注册结果为新表
        df_with_compensation = processor.apply_custom_function(
            df, 
            'total_compensation',  # 新列名
            calculate_total_compensation,  # 函数
            table_name='employees_with_compensation'  # 自动注册为新表
        )
        print("计算总薪酬后的数据:")
        print(df_with_compensation[['name', 'salary', 'bonus', 'total_compensation']])
        print()
        
        # 验证表已自动注册
        print("验证自动注册的表:")
        table_info = spark.list_tables()
        print()
        
        # 查询自动注册的表
        compensation_data = spark.execute_query("SELECT name, total_compensation FROM employees_with_compensation ORDER BY total_compensation DESC")
        print("从自动注册表中查询的数据:")
        print(compensation_data)
        print()
        
        # 示例2: 使用apply_function处理数据并自动注册结果
        print("--- 示例2: 使用apply_function处理数据并自动注册 ---")
        def categorize_salary(row):
            """根据薪资分类"""
            salary = row['salary']
            if salary >= 75000:
                return 'High'
            elif salary >= 65000:
                return 'Medium'
            else:
                return 'Low'
        
        # 注册函数
        processor.register_function('salary_category', categorize_salary)
        
        # 应用已注册的函数并自动注册结果
        df_with_category = processor.apply_function(
            df_with_compensation, 
            'salary_category',  # 新列名
            'salary_category',  # 已注册的函数名
            table_name='employees_with_categories'  # 自动注册为新表
        )
        print("薪资分类后的数据:")
        print(df_with_category[['name', 'salary', 'salary_category']])
        print()
        
        # 验证新表已自动注册
        print("验证新自动注册的表:")
        table_info = spark.list_tables()
        print()
        
        # 示例3: 使用explode_column处理数据并自动注册结果
        print("--- 示例3: 使用explode_column处理数据并自动注册 ---")
        # 拆分tags列并自动注册结果
        df_exploded = processor.explode_column(
            df_with_category,
            'tags',  # 要拆分的列
            ',',     # 分隔符
            table_name='employees_exploded_tags'  # 自动注册为新表
        )
        print("拆分tags列后的数据 (前10行):")
        print(df_exploded[['name', 'tags']].head(10))
        print()
        
        # 验证新表已自动注册
        print("验证新自动注册的表:")
        table_info = spark.list_tables()
        print()
        
        # 示例4: 禁用自动注册功能
        print("--- 示例4: 禁用自动注册功能 ---")
        def calculate_experience_bonus(row):
            """根据工龄计算奖金"""
            return row['experience'] * 1000
        
        # 应用函数但禁用自动注册
        df_with_bonus = processor.apply_custom_function(
            df_exploded, 
            'experience_bonus',  # 新列名
            calculate_experience_bonus,  # 函数
            table_name='employees_with_bonus',  # 表名
            register=False  # 禁用自动注册
        )
        print("计算工龄奖金后的数据:")
        print(df_with_bonus[['name', 'experience', 'experience_bonus']])
        print()
        
        # 验证表未被自动注册
        print("验证表未被自动注册:")
        if 'employees_with_bonus' not in spark.tables:
            print("✓ 表'employees_with_bonus'未被自动注册")
        else:
            print("✗ 表'employees_with_bonus'被错误地自动注册了")
        print()
        
        # 示例5: 复杂的数据处理流程
        print("--- 示例5: 复杂的数据处理流程 ---")
        # 计算综合评分
        def calculate_overall_score(row):
            """计算综合评分"""
            # 薪资权重0.4，工龄权重0.3，奖金权重0.3
            salary_score = row['salary'] / 1000 * 0.4
            experience_score = row['experience'] * 0.3
            bonus_score = row['bonus'] / 1000 * 0.3
            return round(salary_score + experience_score + bonus_score, 2)
        
        # 应用函数并自动注册
        df_with_score = processor.apply_custom_function(
            df, 
            'overall_score',  # 新列名
            calculate_overall_score,  # 函数
            table_name='employees_with_scores'  # 自动注册为新表
        )
        print("计算综合评分后的数据:")
        print(df_with_score[['name', 'salary', 'experience', 'bonus', 'overall_score']].sort_values('overall_score', ascending=False))
        print()
        
        # 使用SQL查询分析数据
        print("使用SQL查询分析员工数据:")
        analysis_result = spark.execute_query("""
            SELECT 
                department,
                COUNT(*) as employee_count,
                AVG(overall_score) as avg_score,
                MAX(overall_score) as max_score
            FROM employees_with_scores
            GROUP BY department
            ORDER BY avg_score DESC
        """)
        print(analysis_result)
        print()
        
        # 展示所有已注册的表
        print("--- 所有已注册的表 ---")
        table_info = spark.list_tables()
        
    except Exception as e:
        print(f"执行示例时出错: {e}")
        import traceback
        traceback.print_exc()
    
    # 清理
    spark.close()
    if os.path.exists(csv_file):
        os.remove(csv_file)
        print(f"\n已清理临时文件: {csv_file}")


if __name__ == "__main__":
    auto_register_example()
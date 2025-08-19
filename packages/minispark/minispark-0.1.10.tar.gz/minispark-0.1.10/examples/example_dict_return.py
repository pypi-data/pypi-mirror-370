"""
MiniSpark DataProcessor 返回字典功能示例
演示当new_column_name为None时，如何处理函数返回字典或字典列表的情况
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
        'name': ['Alice', 'Bob', 'Charlie'],
        'department': ['IT', 'HR', 'Finance'],
        'salary': [75000, 65000, 70000]
    })
    
    # 保存为CSV文件
    temp_dir = tempfile.gettempdir()
    csv_file = os.path.join(temp_dir, 'employees_dict_example.csv')
    data.to_csv(csv_file, index=False, encoding='utf-8')
    
    print("原始数据:")
    print(data)
    print()
    
    return csv_file


def dict_return_example():
    """演示返回字典的功能"""
    print("=== MiniSpark DataProcessor 返回字典功能示例 ===\n")
    
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
        
        # 示例1: 函数返回字典，自动创建新列
        print("--- 示例1: 函数返回字典，自动创建新列 ---")
        def calculate_benefits_dict(row):
            """计算福利信息并以字典形式返回"""
            # 根据薪资和部门计算奖金和股票期权
            bonus = row['salary'] * 0.1 if row['department'] == 'IT' else row['salary'] * 0.05
            stock_options = row['salary'] * 0.2 if row['department'] == 'IT' else 0
            # 返回字典，键将成为新列名
            return {
                'bonus': round(bonus, 2),
                'stock_options': round(stock_options, 2),
                'total_compensation': row['salary'] + bonus + stock_options
            }
        
        # 应用函数，new_column_name设为None
        df_with_benefits = processor.apply_custom_function(
            df, 
            new_column_name=None,  # 关键：设置为None以处理返回的字典
            func=calculate_benefits_dict
        )
        print("添加福利信息后的数据:")
        print(df_with_benefits)
        print()
        
        # 示例2: 函数返回字典列表，自动展开为多行
        print("--- 示例2: 函数返回字典列表，自动展开为多行 ---")
        def generate_skill_list(row):
            """为每个员工生成技能列表，以字典列表形式返回"""
            base_skills = ['Communication', 'Teamwork']
            
            if row['department'] == 'IT':
                extra_skills = ['Python', 'SQL', 'Problem Solving']
            elif row['department'] == 'HR':
                extra_skills = ['Recruitment', 'Employee Relations']
            else:  # Finance
                extra_skills = ['Financial Analysis', 'Excel', 'Reporting']
            
            # 返回字典列表，每个字典将变成一行
            skills_list = []
            for skill in (base_skills + extra_skills):
                skills_list.append({
                    'name': row['name'],
                    'department': row['department'],
                    'skill': skill
                })
            return skills_list
        
        # 应用函数，new_column_name设为None
        df_with_skills = processor.apply_custom_function(
            df_with_benefits.head(2),  # 只处理前2行以避免输出过长
            new_column_name=None,  # 关键：设置为None以处理返回的字典列表
            func=generate_skill_list
        )
        print("展开技能信息后的数据:")
        print(df_with_skills)
        print(f"行数从2行扩展到了{len(df_with_skills)}行")
        print()
        
        # 示例3: 将处理后的数据注册到引擎并执行SQL查询
        print("--- 示例3: 使用SQL查询处理后的数据 ---")
        spark.engine.register_table('enhanced_employees', df_with_benefits)
        
        # 执行SQL查询，找出总薪酬最高的员工
        result = spark.execute_query("""
            SELECT name, department, salary, bonus, stock_options, total_compensation
            FROM enhanced_employees
            ORDER BY total_compensation DESC
        """)
        print("总薪酬最高的员工:")
        print(result)
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
    dict_return_example()
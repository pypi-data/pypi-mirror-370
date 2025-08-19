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
        'experience': [5, 3, 4, 6, 2],
        'performance_score': [4.5, 3.8, 4.2, 4.8, 3.5]
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
        
        # 示例1: 使用自定义函数处理整行数据（计算综合福利）
        print("--- 示例1: 计算员工综合福利 ---")
        def calculate_benefits(row):
            """
            根据多个因素计算员工福利
            - 基础福利：薪资的10%
            - 部门福利：IT部门额外5000元
            - 绩效福利：绩效分高于4.0的额外2000元
            - 工龄福利：每满一年增加100元
            """
            # print("正在处理员工:", row.get('name55',88))
            
            base_benefits = row['salary'] * 0.1
            dept_bonus = 5000 if row['department'] == 'IT' else 0
            performance_bonus = 2000 if row['performance_score'] > 4.0 else 0
            experience_bonus = row['experience'] * 100
            return base_benefits + dept_bonus + performance_bonus + experience_bonus
        
        df_with_benefits = processor.apply_custom_function(
            df, 
            'total_benefits',  # 新列名
            calculate_benefits  # 函数
        )
        print("计算综合福利后的数据:")
        print(df_with_benefits[['name', 'department', 'salary', 'performance_score', 'experience', 'total_benefits']])
        print()
        
        # 示例2: 使用更复杂的整行处理函数（员工评级）
        print("--- 示例2: 员工综合评级 ---")
        def employee_rating(row):
            """
            综合评级考虑以下因素：
            - 薪资评级：薪资/10000
            - 绩效评级：绩效分
            - 部门评级：IT部门1.2倍，Finance部门1.1倍
            - 工龄评级：工龄*0.5
            """
            salary_rating = row['salary'] / 10000
            performance_rating = row['performance_score']
            
            dept_multiplier = 1.0
            if row['department'] == 'IT':
                dept_multiplier = 1.2
            elif row['department'] == 'Finance':
                dept_multiplier = 1.1
                
            experience_rating = row['experience'] * 0.5
            
            total_rating = (salary_rating + performance_rating + experience_rating) * dept_multiplier
            return round(total_rating, 2)
        
        df_with_rating = processor.apply_custom_function(
            df, 
            'employee_rating',  # 新列名
            employee_rating  # 函数
        )
        print("员工综合评级:")
        print(df_with_rating[['name', 'department', 'salary', 'performance_score', 'experience', 'employee_rating']])
        print()
        
        # 示例3: 注册并应用处理整行数据的函数
        print("--- 示例3: 注册并应用整行处理函数 ---")
        def calculate_tax_and_deductions(row):
            """
            计算税费和扣除项
            - 个人所得税：薪资超过50000部分的20%
            - 社保：薪资的10%
            - 公积金：薪资的12%
            """
            taxable_income = max(0, row['salary'] - 50000)
            income_tax = taxable_income * 0.2
            social_security = row['salary'] * 0.1
            housing_fund = row['salary'] * 0.12
            return income_tax + social_security + housing_fund
        
        # 注册函数
        processor.register_function('tax_calculator', calculate_tax_and_deductions)
        
        # 应用已注册的函数
        df_with_tax = processor.apply_function(
            df, 
            'total_deductions',  # 新列名
            'tax_calculator'  # 已注册的函数名
        )
        print("计算税费和扣除项后的数据:")
        print(df_with_tax[['name', 'salary', 'total_deductions']])
        print()
        
        # 示例4: 将处理后的数据注册到引擎并执行SQL查询
        print("--- 示例4: 使用SQL查询处理后的数据 ---")
        spark.engine.register_table('enhanced_employees', df_with_rating)
        
        # 执行SQL查询，找出评级最高的员工
        result = spark.execute_query("""
            SELECT name, department, employee_rating
            FROM enhanced_employees
            ORDER BY employee_rating DESC
            LIMIT 3
        """)
        print("员工评级最高的3名员工:")
        print(result)
        print()
        
        # 示例5: 按部门统计平均评级
        department_stats = spark.execute_query("""
            SELECT department, 
                   COUNT(*) as employee_count,
                   AVG(employee_rating) as avg_rating
            FROM enhanced_employees
            GROUP BY department
            ORDER BY avg_rating DESC
        """)
        print("各部门平均评级:")
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
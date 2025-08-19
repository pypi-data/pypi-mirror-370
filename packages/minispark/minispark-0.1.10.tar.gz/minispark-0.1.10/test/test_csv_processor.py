"""
测试CSV数据处理器功能，特别是将Python函数应用于数据表的列
"""

import pandas as pd
import os
import sys
import tempfile

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from minispark import MiniSpark, CSVConnector
from minispark.processors.data_processor import DataProcessor


def create_test_csv_data():
    """创建测试CSV数据"""
    # 创建员工数据
    employees_data = pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['Alice Smith', 'Bob Johnson', 'Charlie Brown', 'Diana Miller', 'Edward Wilson'],
        'department': ['IT', 'HR', 'Finance', 'IT', 'Marketing'],
        'salary': [75000, 65000, 70000, 80000, 60000],
        'email': ['alice@example.com', 'bob@example.com', 'charlie@example.com', 'diana@example.com', 'edward@example.com']
    })
    
    # 创建技能数据
    skills_data = pd.DataFrame({
        'employee_id': [1, 1, 2, 3, 3, 4, 5],
        'skill': ['Python', 'SQL', 'Recruiting', 'Financial Analysis', 'Excel', 'Java', 'SEO'],
        'level': [5, 4, 3, 5, 4, 4, 3]  # 技能等级 1-5
    })
    
    # 保存为CSV文件
    temp_dir = tempfile.gettempdir()
    employees_csv = os.path.join(temp_dir, 'employees_test.csv')
    skills_csv = os.path.join(temp_dir, 'skills_test.csv')
    
    employees_data.to_csv(employees_csv, index=False)
    skills_data.to_csv(skills_csv, index=False)
    
    print("创建测试CSV数据:")
    print("员工数据:")
    print(employees_data)
    print("\n技能数据:")
    print(skills_data)
    print()
    
    return employees_csv, skills_csv


def custom_email_function(email):
    """自定义函数：提取邮箱域名"""
    if '@' in email:
        return email.split('@')[1]
    return 'unknown'


def custom_salary_category(salary):
    """自定义函数：根据薪资分类"""
    if salary >= 75000:
        return 'High'
    elif salary >= 65000:
        return 'Medium'
    else:
        return 'Low'


def test_csv_data_processor():
    """测试CSV数据处理器"""
    print("=== 测试CSV数据处理器 ===")
    
    # 创建测试数据
    employees_csv, skills_csv = create_test_csv_data()
    
    try:
        # 初始化MiniSpark
        spark = MiniSpark()
        
        # 添加CSV连接器
        employees_connector = CSVConnector('employees')
        skills_connector = CSVConnector('skills')
        spark.add_connector('employees', employees_connector)
        spark.add_connector('skills', skills_connector)
        
        # 加载数据
        employees_df = spark.load_data('employees', employees_csv, 'employees')
        skills_df = spark.load_data('skills', skills_csv, 'skills')
        
        print("从CSV加载的数据:")
        print("员工数据:")
        print(employees_df)
        print("\n技能数据:")
        print(skills_df)
        print()
        
        # 测试数据处理器
        processor = spark.processor
        
        # 注册函数
        processor.register_function('salary_category', custom_salary_category)
        processor.register_function('extract_domain', custom_email_function)
        
        # 应用已注册的函数
        print("应用已注册的函数...")
        # 为薪资添加分类
        employees_df = processor.apply_function(
            employees_df, 'salary', 'salary_category', 'salary_category'
        )
        
        # 提取邮箱域名
        employees_df = processor.apply_function(
            employees_df, 'email', 'extract_domain', 'email_domain'
        )
        
        print("应用已注册函数后的员工数据:")
        print(employees_df)
        print()
        
        # 应用自定义函数（不预先注册）
        print("应用自定义函数...")
        
        # 添加姓名长度列
        employees_df = processor.apply_custom_function(
            employees_df, 'name', lambda x: len(x), 'name_length'
        )
        
        # 将部门名称转为小写
        employees_df = processor.apply_custom_function(
            employees_df, 'department', lambda x: x.lower(), 'department_lower'
        )
        
        print("应用自定义函数后的员工数据:")
        print(employees_df)
        print()
        
        # 注册处理后的数据到引擎
        spark.engine.register_table('processed_employees', employees_df)
        spark.engine.register_table('skills', skills_df)
        
        # 执行复杂查询
        result = spark.execute_query("""
            SELECT p.department, p.salary_category, COUNT(*) as employee_count,
                   AVG(s.level) as avg_skill_level
            FROM processed_employees p
            JOIN skills s ON p.id = s.employee_id
            GROUP BY p.department, p.salary_category
            ORDER BY p.department, p.salary_category
        """)
        
        print("处理后的数据分析结果:")
        print(result)
        print()
        
        # 关闭MiniSpark
        spark.close()
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    # 清理测试文件
    for file_path in [employees_csv, skills_csv]:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"已清理测试文件: {file_path}")
    
    print("CSV数据处理器测试完成\n")


if __name__ == "__main__":
    test_csv_data_processor()
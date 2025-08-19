"""
生成CSV示例数据
"""

import pandas as pd
import os


def create_sample_csv_data():
    """创建示例CSV数据"""
    print("创建示例CSV数据...")
    
    # 创建示例员工数据
    employees_data = pd.DataFrame({
        'emp_id': [1, 2, 3, 4, 5, 6],
        'name': ['Alice Johnson', 'Bob Smith', 'Charlie Brown', 'Diana Miller', 'Edward Davis', 'Fiona Wilson'],
        'department': ['HR', 'IT', 'Finance', 'IT', 'HR', 'Finance'],
        'salary': [50000, 60000, 70000, 55000, 52000, 68000],
        'hire_date': ['2020-01-15', '2019-03-22', '2018-07-10', '2021-02-01', '2020-11-05', '2019-05-17']
    })
    
    # 保存为CSV文件在当前目录下
    employees_data.to_csv(os.path.join(os.path.dirname(__file__), 'employees.csv'), index=False)
    
    print("示例员工数据已保存到employees.csv:")
    print(employees_data)
    print()
    
    # 创建示例技能数据
    skills_data = pd.DataFrame({
        'emp_id': [1, 2, 3, 4, 5, 6],
        'skill': ['Recruitment', 'Python', 'Financial Modeling', 'Java', 'Training', 'Excel'],
        'experience_years': [5, 2, 7, 3, 4, 6]
    })
    
    skills_data.to_csv(os.path.join(os.path.dirname(__file__), 'skills.csv'), index=False)
    
    print("示例技能数据已保存到skills.csv:")
    print(skills_data)
    print()
    
    return employees_data, skills_data


if __name__ == "__main__":
    create_sample_csv_data()
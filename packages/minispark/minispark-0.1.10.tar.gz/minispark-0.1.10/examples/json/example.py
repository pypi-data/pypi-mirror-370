"""
JSON连接器使用示例
"""

import pandas as pd
import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from minispark import MiniSpark, JSONConnector


def create_sample_json_data():
    """创建示例JSON数据"""
    print("创建示例JSON数据...")
    
    # 示例数据1: 对象数组
    employees_data = [
        {"id": 1, "name": "张三", "department": "技术部", "salary": 8000, "skills": ["Python", "SQL"]},
        {"id": 2, "name": "李四", "department": "销售部", "salary": 7500, "skills": ["Excel", "沟通"]},
        {"id": 3, "name": "王五", "department": "技术部", "salary": 9000, "skills": ["Java", "Docker"]},
        {"id": 4, "name": "赵六", "department": "人事部", "salary": 6500, "skills": ["招聘", "培训"]},
    ]
    
    # 保存为JSON文件
    with open('employees.json', 'w', encoding='utf-8') as f:
        json.dump(employees_data, f, ensure_ascii=False, indent=2)
    
    # 示例数据2: 嵌套对象
    company_data = {
        "name": "示例公司",
        "founded": 2020,
        "departments": [
            {"name": "技术部", "employees": 10},
            {"name": "销售部", "employees": 8},
            {"name": "人事部", "employees": 5}
        ],
        "address": {
            "city": "北京",
            "district": "朝阳区"
        }
    }
    
    # 保存为JSON文件
    with open('company.json', 'w', encoding='utf-8') as f:
        json.dump(company_data, f, ensure_ascii=False, indent=2)
    
    print("示例JSON数据创建完成")
    print()


def json_example():
    """JSON使用示例"""
    print("=== JSON连接器使用示例 ===")
    
    # 创建示例数据
    create_sample_json_data()
    
    # 初始化MiniSpark
    spark = MiniSpark()
    
    # 添加JSON连接器
    try:
        json_connector = JSONConnector('json')
        spark.add_connector('json', json_connector)
        print("成功添加JSON连接器")
        
        # 从JSON加载数据（对象数组）
        print("--- 从employees.json加载数据 ---")
        employees_df = spark.load_data('json', 'employees.json', 'employees')
        print("员工数据:")
        print(employees_df)
        print(f"数据形状: {employees_df.shape}")
        print()
        
        # 从JSON加载数据（嵌套对象）
        print("--- 从company.json加载数据 ---")
        company_df = spark.load_data('json', 'company.json', 'company')
        print("公司数据:")
        print(company_df)
        print(f"数据形状: {company_df.shape}")
        print()
        
        # 使用本地引擎执行查询
        print("--- 使用本地引擎查询员工数据 ---")
        high_salary_employees = spark.execute_query("""
            SELECT name, department, salary 
            FROM employees 
            WHERE salary > 7000
            ORDER BY salary DESC
        """, 'high_salary_employees')
        
        print("高薪员工:")
        print(high_salary_employees)
        print()
        
        # 处理JSON数组字段
        print("--- 处理技能数组字段 ---")
        print("员工技能信息:")
        for idx, row in employees_df.iterrows():
            # 将字符串转换回JSON对象进行显示
            skills = json.loads(row['skills'])
            print(f"{row['name']}: {', '.join(skills)}")
        print()
        
        # 演示JSON数据处理功能
        print("--- JSON数据处理功能 ---")
        # 添加一个处理函数来计算技能数量
        def count_skills(skills_str):
            skills = json.loads(skills_str)
            return len(skills)
        
        # 应用函数计算每个员工的技能数量
        employees_df['skill_count'] = employees_df['skills'].apply(count_skills)
        print("员工技能数量:")
        for idx, row in employees_df.iterrows():
            print(f"{row['name']}: {row['skill_count']} 项技能")
        print()
        
    except Exception as e:
        print(f"使用JSON连接器时出错: {e}")
        import traceback
        traceback.print_exc()
    
    # 关闭连接
    spark.close()
    
    # 清理示例文件
    try:
        os.remove('employees.json')
        os.remove('company.json')
        print("已清理示例文件")
    except:
        pass
    
    print("JSON示例完成\n")


if __name__ == "__main__":
    json_example()
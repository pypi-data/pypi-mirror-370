"""
CSV连接器使用示例
"""

import pandas as pd
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from minispark import MiniSpark, CSVConnector


def csv_example():
    """CSV使用示例"""
    print("=== CSV连接器使用示例 ===")
    
    # 构建CSV文件路径
    employees_csv = os.path.join(os.path.dirname(__file__), 'employees.csv')
    skills_csv = os.path.join(os.path.dirname(__file__), 'skills.csv')
    
    # 初始化MiniSpark
    spark = MiniSpark()
    
    # 添加CSV连接器
    employees_connector = CSVConnector('employees')
    skills_connector = CSVConnector('skills')
    spark.add_connector('employees', employees_connector)
    spark.add_connector('skills', skills_connector)
    print("成功添加CSV连接器")
    
    # 从CSV加载数据
    employees_df = spark.load_data('employees', employees_csv, 'employees')
    print("从CSV加载的员工数据:")
    print(employees_df)
    print()
    
    skills_df = spark.load_data('skills', skills_csv, 'skills')
    print("从CSV加载的技能数据:")
    print(skills_df)
    print()
    
    # 执行查询 - 使用新的table_name参数直接将结果注册为表
    print("执行查询并将结果注册为新表...")
    spark.execute_query("""
        SELECT 
            s.emp_id,
            e.name,
            e.department,
            s.skill,
            s.experience_years as level
        FROM employees e
        JOIN skills s ON e.emp_id = s.emp_id
        WHERE s.experience_years >= 4
        ORDER BY s.experience_years DESC, e.name
    """, table_name="high_level_skills")
    
    print("高技能员工数据已注册为表: high_level_skills")
    
    # 查询已注册的表
    high_skills = spark.execute_query("SELECT * FROM high_level_skills")
    print("高技能员工数据:")
    print(high_skills)
    print()
    
    # 执行聚合查询并注册结果
    spark.execute_query("""
        SELECT 
            department,
            COUNT(*) as employee_count,
            AVG(level) as avg_skill_level
        FROM high_level_skills
        GROUP BY department
        ORDER BY avg_skill_level DESC
    """, table_name="department_skill_analysis")
    
    print("部门技能分析数据已注册为表: department_skill_analysis")
    
    # 查看分析结果
    analysis = spark.execute_query("SELECT * FROM department_skill_analysis")
    print("部门技能分析结果:")
    print(analysis)
    print()
    
    # 执行查询但不注册结果（演示register=False参数）
    summary = spark.execute_query("""
        SELECT 
            COUNT(DISTINCT department) as departments,
            COUNT(*) as total_high_skills
        FROM high_level_skills
    """, table_name="summary_stats", register=False)
    
    print("统计摘要（未注册为表）:")
    print(summary)
    print()
    
    # 关闭连接
    spark.close()
    
    # 清理示例文件
    for file_path in [employees_csv, skills_csv]:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"已清理示例文件: {file_path}")
    
    print("CSV示例完成\n")


if __name__ == "__main__":
    # 首先生成示例数据
    from generate_data import create_sample_csv_data
    create_sample_csv_data()
    
    # 运行示例
    csv_example()
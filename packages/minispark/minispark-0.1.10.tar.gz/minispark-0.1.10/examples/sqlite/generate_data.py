"""
生成SQLite示例数据
"""

import pandas as pd
import sqlite3
import os


def create_sample_sqlite_data():
    """创建示例SQLite数据"""
    print("创建示例SQLite数据...")
    
    # 创建示例部门数据
    departments_data = pd.DataFrame({
        'dept_id': [1, 2, 3, 4],
        'department': ['Human Resources', 'Information Technology', 'Finance', 'Marketing'],
        'manager': ['Alice Johnson', 'Bob Smith', 'Charlie Brown', 'Diana Miller'],
        'budget': [200000, 500000, 300000, 150000]
    })
    
    # 保存到SQLite数据库在当前目录下
    db_path = os.path.join(os.path.dirname(__file__), 'company.db')
    conn = sqlite3.connect(db_path)
    departments_data.to_sql('departments', conn, if_exists='replace', index=False)
    conn.close()
    
    print("示例部门数据已保存到company.db:")
    print(departments_data)
    print()
    
    return departments_data


if __name__ == "__main__":
    create_sample_sqlite_data()
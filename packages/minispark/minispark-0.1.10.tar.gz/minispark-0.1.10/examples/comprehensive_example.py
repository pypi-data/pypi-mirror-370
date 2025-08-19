"""
MiniSpark综合示例
展示所有支持的数据源类型使用方法
"""

import pandas as pd
import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from minispark import MiniSpark
from minispark import (
    CSVConnector,
    ExcelConnector,
    JSONConnector,
    SQLiteConnector,
    MySQLConnector,
    DuckDBConnector
)


def create_sample_data():
    """创建所有示例数据文件"""
    print("创建示例数据文件...")
    
    # 1. 创建CSV数据
    csv_data = pd.DataFrame({
        'id': [1, 2, 3, 4],
        'name': ['张三', '李四', '王五', '赵六'],
        'department': ['技术部', '销售部', '人事部', '财务部'],
        'salary': [8000, 7500, 6500, 7000]
    })
    csv_data.to_csv('employees.csv', index=False)
    print("✓ 已创建 employees.csv")
    
    # 2. 创建Excel数据
    excel_data = pd.DataFrame({
        'product_id': [101, 102, 103, 104],
        'product_name': ['笔记本电脑', '手机', '平板', '耳机'],
        'price': [5000, 3000, 2000, 500],
        'stock': [50, 100, 80, 200]
    })
    excel_data.to_excel('products.xlsx', index=False)
    print("✓ 已创建 products.xlsx")
    
    # 3. 创建JSON数据
    json_data = [
        {"id": 1, "name": "张三", "skills": ["Python", "SQL"]},
        {"id": 2, "name": "李四", "skills": ["Excel", "沟通"]},
        {"id": 3, "name": "王五", "skills": ["Java", "Docker"]},
        {"id": 4, "name": "赵六", "skills": ["招聘", "培训"]}
    ]
    with open('skills.json', 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print("✓ 已创建 skills.json")
    
    # 4. 创建SQLite数据库和表
    import sqlite3
    conn = sqlite3.connect('company.db')
    cursor = conn.cursor()
    
    # 创建部门表
    cursor.execute('''
        CREATE TABLE departments (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            location TEXT
        )
    ''')
    
    # 插入部门数据
    departments_data = [
        (1, '技术部', '北京'),
        (2, '销售部', '上海'),
        (3, '人事部', '广州'),
        (4, '财务部', '深圳')
    ]
    cursor.executemany('INSERT INTO departments VALUES (?, ?, ?)', departments_data)
    
    conn.commit()
    conn.close()
    print("✓ 已创建 company.db SQLite数据库")
    
    print("所有示例数据文件创建完成\n")


def csv_example(spark):
    """CSV连接器使用示例"""
    print("=== CSV连接器使用示例 ===")
    
    # 创建CSV连接器
    csv_connector = CSVConnector('csv_connector')
    spark.add_connector('csv', csv_connector)
    
    # 从CSV文件加载数据
    employees_df = spark.load_data('csv', 'employees.csv', 'employees')
    print("员工数据:")
    print(employees_df)
    print()
    
    # 使用不同分隔符的CSV连接器
    semicolon_csv = pd.DataFrame({
        'id': [1, 2],
        'name': ['测试1', '测试2']
    })
    semicolon_csv.to_csv('test_semicolon.csv', sep=';', index=False)
    
    semicolon_connector = CSVConnector('semicolon_csv', delimiter=';')
    spark.add_connector('semicolon_csv', semicolon_connector)
    
    semicolon_df = spark.load_data('semicolon_csv', 'test_semicolon.csv', 'semicolon_data')
    print("分号分隔符数据:")
    print(semicolon_df)
    print()
    
    # 清理临时文件
    try:
        os.remove('test_semicolon.csv')
    except:
        pass


def excel_example(spark):
    """Excel连接器使用示例"""
    print("=== Excel连接器使用示例 ===")
    
    # 创建Excel连接器
    excel_connector = ExcelConnector('excel_connector')
    spark.add_connector('excel', excel_connector)
    
    # 从Excel文件加载数据
    products_df = spark.load_data('excel', 'products.xlsx', 'products')
    print("产品数据:")
    print(products_df)
    print()


def json_example(spark):
    """JSON连接器使用示例"""
    print("=== JSON连接器使用示例 ===")
    
    # 创建JSON连接器
    json_connector = JSONConnector('json_connector')
    spark.add_connector('json', json_connector)
    
    # 从JSON文件加载数据
    skills_df = spark.load_data('json', 'skills.json', 'skills')
    print("技能数据:")
    print(skills_df)
    print()
    
    # 处理JSON数组字段
    print("员工技能详情:")
    for idx, row in skills_df.iterrows():
        skills = json.loads(row['skills'])
        print(f"{row['name']}: {', '.join(skills)}")
    print()


def sqlite_example(spark):
    """SQLite连接器使用示例"""
    print("=== SQLite连接器使用示例 ===")
    
    # 创建SQLite连接器
    sqlite_connector = SQLiteConnector('sqlite_connector', 'company.db')
    spark.add_connector('sqlite', sqlite_connector)
    
    # 从SQLite数据库查询数据
    departments_df = spark.load_data('sqlite', 'SELECT * FROM departments', 'departments')
    print("部门数据:")
    print(departments_df)
    print()


def mysql_example(spark):
    """MySQL连接器使用示例"""
    print("=== MySQL连接器使用示例 ===")
    
    try:
        # 创建MySQL连接器
        mysql_connector = MySQLConnector(
            name='mysql_connector',
            host='47.108.200.193',
            port=3306,
            user='duanfu',
            password='HTb55A2rFFa4nGft',
            database='duanfu'
        )
        spark.add_connector('mysql', mysql_connector)
        
        # 执行简单查询
        result_df = spark.load_data('mysql', 'SELECT 1 as test_column', 'mysql_test')
        print("MySQL连接测试结果:")
        print(result_df)
        print()
        
    except Exception as e:
        print(f"⚠️  MySQL连接示例跳过: {e}")
        print("请确保MySQL服务器可访问且凭据正确\n")


def duckdb_example(spark):
    """DuckDB连接器使用示例"""
    print("=== DuckDB连接器使用示例 ===")
    
    try:
        # 创建DuckDB连接器
        duckdb_connector = DuckDBConnector('duckdb_connector')
        spark.add_connector('duckdb', duckdb_connector)
        
        # 执行简单查询
        result_df = spark.load_data('duckdb', 'SELECT 1 as test_column', 'duckdb_test')
        print("DuckDB连接测试结果:")
        print(result_df)
        print()
        
    except Exception as e:
        print(f"⚠️  DuckDB连接示例跳过: {e}")
        print("请确保已安装duckdb库: pip install duckdb\n")


def cross_source_query_example(spark):
    """跨数据源查询示例"""
    print("=== 跨数据源查询示例 ===")
    
    # 将不同数据源的数据注册到本地引擎后进行关联查询
    try:
        # 从CSV加载员工数据
        csv_connector = CSVConnector('cross_csv')
        spark.add_connector('cross_csv', csv_connector)
        employees_df = spark.load_data('cross_csv', 'employees.csv', 'cross_employees')
        
        # 从JSON加载技能数据
        json_connector = JSONConnector('cross_json')
        spark.add_connector('cross_json', json_connector)
        skills_df = spark.load_data('cross_json', 'skills.json', 'cross_skills')
        
        # 在本地引擎中执行关联查询
        result = spark.execute_query("""
            SELECT e.name, e.department, e.salary
            FROM cross_employees e
            WHERE e.salary > 7000
            ORDER BY e.salary DESC
        """, 'high_salary_employees')
        
        print("高薪员工数据:")
        print(result)
        print()
        
    except Exception as e:
        print(f"跨数据源查询示例执行失败: {e}\n")


def main():
    """主函数"""
    print("MiniSpark综合使用示例")
    print("=" * 50)
    
    # 创建示例数据
    create_sample_data()
    
    # 初始化MiniSpark
    spark = MiniSpark()
    
    try:
        # 依次演示各种连接器的使用
        csv_example(spark)
        excel_example(spark)
        json_example(spark)
        sqlite_example(spark)
        mysql_example(spark)
        duckdb_example(spark)
        cross_source_query_example(spark)
        
        print("✅ 所有示例执行完成!")
        
    except Exception as e:
        print(f"❌ 示例执行过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 关闭连接
        spark.close()
        
        # 清理示例文件
        try:
            os.remove('employees.csv')
            os.remove('products.xlsx')
            os.remove('skills.json')
            os.remove('company.db')
            print("\n已清理示例文件")
        except:
            pass


if __name__ == "__main__":
    main()
"""
在MySQL中创建关联数据用于测试
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from minispark import MiniSpark
from minispark.connectors.mysql_connector import MySQLConnector
from sqlalchemy import text
import pandas as pd
from sqlalchemy import create_engine
import pymysql


def execute_non_query_sql(host, port, user, password, database, sql):
    """执行非查询SQL语句"""
    connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    engine = create_engine(connection_string)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            conn.commit()
            return True
    except Exception as e:
        print(f"[ERROR] 执行SQL语句时出错: {e}")
        return False
    finally:
        engine.dispose()


def create_test_data():
    """在MySQL中创建测试数据"""
    print("=== 创建MySQL关联测试数据 ===")
    
    # 数据库连接信息
    host = '47.108.200.193'
    port = 3306
    user = 'duanfu'
    password = 'HTb55A2rFFa4nGft'
    database = 'duanfu'
    
    try:
        # 检查是否已存在测试表
        print("\n--- 检查是否存在测试表 ---")
        # 使用MiniSpark查询
        spark = MiniSpark()
        mysql_connector = MySQLConnector(
            name='duanfu.vip',
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        spark.add_connector('mysql', mysql_connector)
        
        # 修复转义字符问题，使用双百分号
        tables_query = "SELECT TABLE_NAME FROM information_schema.tables WHERE table_schema = 'duanfu' AND TABLE_NAME LIKE 'test_%%'"
        tables_df = spark.load_data('mysql', tables_query, 'test_tables')
        
        existing_test_tables = tables_df['TABLE_NAME'].tolist() if len(tables_df) > 0 else []
        print(f"已存在的测试表: {existing_test_tables}")
        
        # 删除已存在的测试表
        for table in existing_test_tables:
            try:
                drop_query = f"DROP TABLE {table}"
                if execute_non_query_sql(host, port, user, password, database, drop_query):
                    print(f"[OK] 已删除表: {table}")
                else:
                    print(f"[ERROR] 删除表 {table} 失败")
            except Exception as e:
                print(f"[INFO] 删除表 {table} 时出错: {e}")
        
        # 关闭连接
        spark.close()
        
        # 创建员工表
        print("\n--- 创建员工表 ---")
        create_employee_table = """
        CREATE TABLE test_employees (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(50) NOT NULL,
            department_id INT,
            salary DECIMAL(10,2),
            hire_date DATE
        )
        """
        if execute_non_query_sql(host, port, user, password, database, create_employee_table):
            print("[OK] 成功创建员工表: test_employees")
        else:
            print("[ERROR] 创建员工表失败")
            return False
        
        # 创建部门表
        print("\n--- 创建部门表 ---")
        create_department_table = """
        CREATE TABLE test_departments (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(50) NOT NULL,
            location VARCHAR(50)
        )
        """
        if execute_non_query_sql(host, port, user, password, database, create_department_table):
            print("[OK] 成功创建部门表: test_departments")
        else:
            print("[ERROR] 创建部门表失败")
            return False
        
        # 插入部门数据
        print("\n--- 插入部门数据 ---")
        insert_departments = """
        INSERT INTO test_departments (name, location) VALUES
        ('技术部', '北京'),
        ('销售部', '上海'),
        ('人事部', '广州'),
        ('财务部', '深圳')
        """
        if execute_non_query_sql(host, port, user, password, database, insert_departments):
            print("[OK] 成功插入部门数据")
        else:
            print("[ERROR] 插入部门数据失败")
            return False
        
        # 插入员工数据
        print("\n--- 插入员工数据 ---")
        insert_employees = """
        INSERT INTO test_employees (name, department_id, salary, hire_date) VALUES
        ('张三', 1, 8000.00, '2022-01-15'),
        ('李四', 2, 7500.00, '2022-02-20'),
        ('王五', 1, 9000.00, '2021-11-10'),
        ('赵六', 3, 6500.00, '2023-03-05'),
        ('钱七', 2, 7800.00, '2022-07-12'),
        ('孙八', 1, 9500.00, '2020-09-18'),
        ('周九', 4, 7000.00, '2022-12-30'),
        ('吴十', NULL, 6000.00, '2023-01-25')
        """
        if execute_non_query_sql(host, port, user, password, database, insert_employees):
            print("[OK] 成功插入员工数据")
        else:
            print("[ERROR] 插入员工数据失败")
            return False
        
        # 验证数据
        print("\n--- 验证数据 ---")
        # 重新建立连接以验证数据
        spark = MiniSpark()
        mysql_connector = MySQLConnector(
            name='duanfu.vip',
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        spark.add_connector('mysql', mysql_connector)
        
        # 查询部门数据
        departments_df = spark.load_data('mysql', 'SELECT * FROM test_departments', 'departments')
        print("部门表数据:")
        print(departments_df)
        
        # 查询员工数据
        employees_df = spark.load_data('mysql', 'SELECT * FROM test_employees', 'employees')
        print("\n员工表数据:")
        print(employees_df)
        
        # 关闭连接
        spark.close()
        
        print("\n[SUCCESS] 测试数据创建完成!")
        return True
        
    except Exception as e:
        print(f"[ERROR] 创建测试数据时出错: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("开始创建MySQL关联测试数据...")
    
    success = create_test_data()
    
    if success:
        print("\n[SUCCESS] MySQL关联测试数据创建成功!")
    else:
        print("\n[FAILED] MySQL关联测试数据创建失败!")


if __name__ == "__main__":
    main()
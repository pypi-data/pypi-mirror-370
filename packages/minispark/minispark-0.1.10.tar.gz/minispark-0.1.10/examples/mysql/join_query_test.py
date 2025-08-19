"""
MySQL关联查询测试示例
演示如何使用MiniSpark进行多表关联查询
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from minispark import MiniSpark
from minispark.connectors.mysql_connector import MySQLConnector


def test_join_queries():
    """测试MySQL关联查询功能"""
    print("=== MySQL关联查询测试 ===")
    
    # 初始化MiniSpark
    spark = MiniSpark()
    
    try:
        # 添加MySQL连接器
        mysql_connector = MySQLConnector(
            name='duanfu.vip',
            host='47.108.200.193',
            port=3306,
            user='duanfu',
            password='HTb55A2rFFa4nGft',
            database='duanfu'
        )
        spark.add_connector('mysql', mysql_connector)
        print("[OK] 成功添加MySQL连接器")
        
        # 测试1: 内连接查询
        print("\n--- 测试1: 内连接查询 ---")
        inner_join_query = """
        SELECT e.name AS employee_name, e.salary, d.name AS department_name, d.location
        FROM test_employees e
        INNER JOIN test_departments d ON e.department_id = d.id
        ORDER BY e.salary DESC
        """
        try:
            inner_join_result = spark.load_data('mysql', inner_join_query, 'inner_join_result')
            print("内连接查询结果:")
            print(inner_join_result)
            print("[OK] 内连接查询测试通过")
        except Exception as e:
            print(f"[ERROR] 内连接查询失败: {e}")
        
        # 测试2: 左连接查询
        print("\n--- 测试2: 左连接查询 ---")
        left_join_query = """
        SELECT e.name AS employee_name, e.salary, d.name AS department_name, d.location
        FROM test_employees e
        LEFT JOIN test_departments d ON e.department_id = d.id
        ORDER BY e.id
        """
        try:
            left_join_result = spark.load_data('mysql', left_join_query, 'left_join_result')
            print("左连接查询结果:")
            print(left_join_result)
            print("[OK] 左连接查询测试通过")
        except Exception as e:
            print(f"[ERROR] 左连接查询失败: {e}")
        
        # 测试3: 聚合查询（按部门统计）
        print("\n--- 测试3: 聚合查询（按部门统计） ---")
        agg_query = """
        SELECT d.name AS department_name, 
               COUNT(e.id) AS employee_count, 
               AVG(e.salary) AS avg_salary,
               MAX(e.salary) AS max_salary,
               MIN(e.salary) AS min_salary
        FROM test_departments d
        LEFT JOIN test_employees e ON d.id = e.department_id
        GROUP BY d.id, d.name
        ORDER BY avg_salary DESC
        """
        try:
            agg_result = spark.load_data('mysql', agg_query, 'agg_result')
            print("聚合查询结果:")
            print(agg_result)
            print("[OK] 聚合查询测试通过")
        except Exception as e:
            print(f"[ERROR] 聚合查询失败: {e}")
        
        # 测试4: 子查询
        print("\n--- 测试4: 子查询 ---")
        subquery = """
        SELECT name, salary
        FROM test_employees
        WHERE salary > (SELECT AVG(salary) FROM test_employees)
        ORDER BY salary DESC
        """
        try:
            subquery_result = spark.load_data('mysql', subquery, 'subquery_result')
            print("子查询结果（高于平均薪资的员工）:")
            print(subquery_result)
            print("[OK] 子查询测试通过")
        except Exception as e:
            print(f"[ERROR] 子查询失败: {e}")
        
        # 测试5: 复杂关联查询
        print("\n--- 测试5: 复杂关联查询 ---")
        complex_query = """
        SELECT d.name AS department_name,
               d.location,
               e.name AS employee_name,
               e.salary,
               CASE 
                   WHEN e.salary >= 9000 THEN '高'
                   WHEN e.salary >= 7000 THEN '中'
                   ELSE '低'
               END AS salary_level
        FROM test_departments d
        INNER JOIN test_employees e ON d.id = e.department_id
        WHERE e.salary >= 7000
        ORDER BY d.name, e.salary DESC
        """
        try:
            complex_result = spark.load_data('mysql', complex_query, 'complex_result')
            print("复杂关联查询结果:")
            print(complex_result)
            print("[OK] 复杂关联查询测试通过")
        except Exception as e:
            print(f"[ERROR] 复杂关联查询失败: {e}")
            
    except Exception as e:
        print(f"[ERROR] MySQL关联查询测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 关闭连接
        spark.close()
    
    print("\n=== MySQL关联查询测试完成 ===")
    return True


def main():
    """主函数"""
    print("开始MySQL关联查询测试...")
    
    success = test_join_queries()
    
    if success:
        print("\n[SUCCESS] MySQL关联查询测试成功!")
    else:
        print("\n[FAILED] MySQL关联查询测试失败!")


if __name__ == "__main__":
    main()
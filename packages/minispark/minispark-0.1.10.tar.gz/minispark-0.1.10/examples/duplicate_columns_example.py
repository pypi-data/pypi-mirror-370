"""
处理重复列名的示例
演示MiniSpark如何处理包含重复列名的数据表
"""

import pandas as pd
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from minispark import MiniSpark


def create_sample_data():
    """创建示例数据"""
    print("创建示例数据...")
    
    # 创建第一个表 - 员工基本信息
    employees_data = pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['张三', '李四', '王五', '赵六', '钱七'],
        'department': ['技术部', '销售部', '人事部', '技术部', '财务部'],
        'salary': [8000, 7500, 6500, 9000, 7000]
    })
    
    # 创建第二个表 - 员工绩效信息
    performance_data = pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['张三', '李四', '王五', '赵六', '钱七'],
        'performance_score': [95, 87, 92, 98, 88],
        'bonus': [8000, 5000, 6500, 10000, 5500]
    })
    
    # 创建第三个表 - 员工项目信息
    project_data = pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['张三', '李四', '王五', '赵六', '钱七'],
        'project_count': [5, 3, 2, 7, 4],
        'avg_hours': [45, 40, 35, 50, 42]
    })
    
    print("员工基本信息:")
    print(employees_data)
    print("\n员工绩效信息:")
    print(performance_data)
    print("\n员工项目信息:")
    print(project_data)
    print()
    
    return employees_data, performance_data, project_data


def duplicate_columns_rename_example():
    """演示重命名重复列名的示例"""
    print("=== 重命名重复列名示例 ===\n")
    
    # 创建示例数据
    employees_data, performance_data, project_data = create_sample_data()
    
    # 初始化MiniSpark，使用重命名方式处理重复列
    spark = MiniSpark()
    
    try:
        # 注册数据表到MiniSpark
        spark.engine.register_table("employees", employees_data)
        spark.engine.register_table("performance", performance_data)
        spark.engine.register_table("projects", project_data)
        
        print("已注册三个表到MiniSpark引擎")
        print("注意：这些表中都有重复的列名 'id' 和 'name'")
        print()
        
        # 执行一个会产生重复列名的查询
        print("执行包含重复列名的查询:")
        query = """
        SELECT 
            e.*,
            p.performance_score,
            p.bonus,
            pr.project_count,
            pr.avg_hours
        FROM employees e
        LEFT JOIN performance p ON e.id = p.id
        LEFT JOIN projects pr ON e.id = pr.id
        ORDER BY e.id
        """
        
        print(query)
        print()
        
        # 执行查询
        result = spark.execute_query(query)
        
        print("查询结果:")
        print(result)
        print(f"\n结果形状: {result.shape}")
        print(f"列名: {list(result.columns)}")
        print()
        
        # 将结果注册为新表（这在修复前会失败）
        print("将查询结果注册为新表 'employee_summary'...")
        spark.engine.register_table("employee_summary", result)
        
        print("表注册成功！重复列名已自动重命名。")
        print(f"注册后的列名: {list(result.columns)}")
        print()
        
    except Exception as e:
        print(f"执行示例时出错: {e}")
        import traceback
        traceback.print_exc()
    
    # 关闭连接
    spark.close()
    print("示例完成\n")


def duplicate_columns_error_example():
    """演示错误处理方式的示例"""
    print("=== 错误处理方式示例 ===\n")
    
    # 创建示例数据
    employees_data, performance_data, project_data = create_sample_data()
    
    # 初始化MiniSpark，使用错误处理方式处理重复列
    spark = MiniSpark()
    spark.handle_duplicate_columns = "error"
    
    try:
        # 注册数据表到MiniSpark
        spark.engine.register_table("employees", employees_data)
        spark.engine.register_table("performance", performance_data)
        spark.engine.register_table("projects", project_data)
        
        print("已注册三个表到MiniSpark引擎")
        print("注意：这些表中都有重复的列名 'id' 和 'name'")
        print()
        
        # 执行一个会产生重复列名的查询
        print("执行包含重复列名的查询:")
        query = """
        SELECT 
            e.*,
            p.performance_score,
            p.bonus,
            pr.project_count,
            pr.avg_hours
        FROM employees e
        LEFT JOIN performance p ON e.id = p.id
        LEFT JOIN projects pr ON e.id = pr.id
        ORDER BY e.id
        """
        
        print(query)
        print()
        
        # 执行查询
        result = spark.execute_query(query)
        
        print("查询结果:")
        print(result)
        print(f"\n结果形状: {result.shape}")
        print(f"列名: {list(result.columns)}")
        print()
        
        # 尝试将结果注册为新表，这会抛出异常
        print("尝试将查询结果注册为新表 'employee_summary'...")
        spark.engine.register_table("employee_summary", result)
        
    except Exception as e:
        print(f"表注册失败，正如预期: {e}")
        print()
        
    # 关闭连接
    spark.close()
    print("示例完成\n")


def duplicate_columns_keep_first_example():
    """演示只保留第一个重复列的示例"""
    print("=== 只保留第一个重复列示例 ===\n")
    
    # 创建示例数据
    employees_data, performance_data, project_data = create_sample_data()
    
    # 初始化MiniSpark，使用保留第一个重复列的方式处理重复列
    spark = MiniSpark()
    spark.handle_duplicate_columns = "keep_first"
    
    try:
        # 注册数据表到MiniSpark
        spark.engine.register_table("employees", employees_data)
        spark.engine.register_table("performance", performance_data)
        spark.engine.register_table("projects", project_data)
        
        print("已注册三个表到MiniSpark引擎")
        print("注意：这些表中都有重复的列名 'id' 和 'name'")
        print()
        
        # 执行一个会产生重复列名的查询
        print("执行包含重复列名的查询:")
        query = """
        SELECT 
            e.*,
            p.performance_score,
            p.bonus,
            pr.project_count,
            pr.avg_hours
        FROM employees e
        LEFT JOIN performance p ON e.id = p.id
        LEFT JOIN projects pr ON e.id = pr.id
        ORDER BY e.id
        """
        
        print(query)
        print()
        
        # 执行查询
        result = spark.execute_query(query)
        
        print("查询结果:")
        print(result)
        print(f"\n结果形状: {result.shape}")
        print(f"列名: {list(result.columns)}")
        print()
        
        # 将结果注册为新表
        print("将查询结果注册为新表 'employee_summary'...")
        original_columns = list(result.columns)
        spark.engine.register_table("employee_summary", result)
        
        print("表注册成功！重复列名中只保留了第一个。")
        print(f"注册前的列名: {original_columns}")
        print(f"注册后的列名: {list(result.columns)}")
        print()
        
    except Exception as e:
        print(f"执行示例时出错: {e}")
        import traceback
        traceback.print_exc()
    
    # 关闭连接
    spark.close()
    print("示例完成\n")


def config_dict_example():
    """演示使用配置字典而不是配置文件"""
    print("=== 使用配置字典示例 ===\n")
    
    # 创建示例数据
    employees_data, performance_data, project_data = create_sample_data()
    
    # 直接使用配置字典初始化MiniSpark
    config = {
        "engine": {
            "type": "sqlite",
            "database_path": ":memory:"
        },
        "storage": {
            "format": "parquet"
        },
        "handle_duplicate_columns": "rename"
    }
    
    spark = MiniSpark(config=config)
    
    try:
        # 注册数据表到MiniSpark
        spark.engine.register_table("employees", employees_data)
        spark.engine.register_table("performance", performance_data)
        spark.engine.register_table("projects", project_data)
        
        print("已使用配置字典初始化MiniSpark并注册三个表")
        print()
        
        # 执行查询
        result = spark.execute_query("SELECT * FROM employees WHERE id <= 3")
        
        print("查询结果:")
        print(result)
        print(f"\n结果形状: {result.shape}")
        
    except Exception as e:
        print(f"执行示例时出错: {e}")
        import traceback
        traceback.print_exc()
    
    # 关闭连接
    spark.close()
    print("示例完成\n")


def setter_methods_example():
    """演示使用setter方法配置MiniSpark"""
    print("=== 使用setter方法示例 ===\n")
    
    # 创建示例数据
    employees_data, performance_data, project_data = create_sample_data()
    
    # 使用默认配置初始化MiniSpark
    spark = MiniSpark()
    
    # 使用setter方法更改处理重复列名的方式
    spark.handle_duplicate_columns = "keep_first"
    print("已将处理重复列名的方式设置为 'keep_first'")
    
    try:
        # 注册数据表到MiniSpark
        spark.engine.register_table("employees", employees_data)
        spark.engine.register_table("performance", performance_data)
        spark.engine.register_table("projects", project_data)
        
        print("已注册三个表到MiniSpark引擎")
        print()
        
        # 执行查询
        result = spark.execute_query("SELECT * FROM employees WHERE id <= 3")
        
        print("查询结果:")
        print(result)
        print(f"\n结果形状: {result.shape}")
        print(f"列名: {list(result.columns)}")
        
    except Exception as e:
        print(f"执行示例时出错: {e}")
        import traceback
        traceback.print_exc()
    
    # 关闭连接
    spark.close()
    print("示例完成\n")


def dot_object_config_example():
    """演示使用点对象方式配置MiniSpark"""
    print("=== 使用点对象方式配置示例 ===\n")
    
    # 创建示例数据
    employees_data, performance_data, project_data = create_sample_data()
    
    # 使用默认配置初始化MiniSpark
    spark = MiniSpark()
    
    # 使用点对象方式设置配置
    spark.config.engine.type = "sqlite"
    spark.config.engine.database_path = ":memory:"
    spark.config.storage.format = "parquet"
    spark.config.handle_duplicate_columns = "rename"
    
    print(f"引擎类型: {spark.config.engine.type}")
    print(f"数据库路径: {spark.config.engine.database_path}")
    print(f"存储格式: {spark.config.storage.format}")
    print(f"处理重复列名方式: {spark.config.handle_duplicate_columns}")
    print()
    
    try:
        # 注册数据表到MiniSpark
        spark.engine.register_table("employees", employees_data)
        spark.engine.register_table("performance", performance_data)
        spark.engine.register_table("projects", project_data)
        
        print("已注册三个表到MiniSpark引擎")
        print()
        
        # 执行查询
        result = spark.execute_query("SELECT * FROM employees WHERE id <= 3")
        
        print("查询结果:")
        print(result)
        print(f"\n结果形状: {result.shape}")
        print(f"列名: {list(result.columns)}")
        
    except Exception as e:
        print(f"执行示例时出错: {e}")
        import traceback
        traceback.print_exc()
    
    # 关闭连接
    spark.close()
    print("示例完成\n")


def best_practice_example():
    """演示最佳实践 - 使用明确的列名和别名"""
    print("=== 最佳实践示例 ===\n")
    
    # 创建示例数据
    employees_data, performance_data, project_data = create_sample_data()
    
    # 初始化MiniSpark
    spark = MiniSpark()
    
    try:
        # 注册数据表到MiniSpark
        spark.engine.register_table("employees", employees_data)
        spark.engine.register_table("performance", performance_data)
        spark.engine.register_table("projects", project_data)
        
        # 执行一个明确指定列名和别名的查询
        print("执行使用明确列名和别名的查询:")
        query = """
        SELECT 
            e.id AS employee_id,
            e.name AS employee_name,
            e.department,
            e.salary,
            p.performance_score,
            p.bonus,
            pr.project_count,
            pr.avg_hours
        FROM employees e
        LEFT JOIN performance p ON e.id = p.id
        LEFT JOIN projects pr ON e.id = pr.id
        ORDER BY e.id
        """
        
        print(query)
        print()
        
        # 执行查询
        result = spark.execute_query(query)
        
        print("查询结果:")
        print(result)
        print(f"\n结果形状: {result.shape}")
        print(f"列名: {list(result.columns)}")
        print()
        
        print("注意：这次没有重复的列名，因为我们都使用了明确的别名。")
        print("这是处理多表连接的最佳实践。")
        
    except Exception as e:
        print(f"执行示例时出错: {e}")
        import traceback
        traceback.print_exc()
    
    # 关闭连接
    spark.close()
    print("示例完成\n")


if __name__ == "__main__":
    # 运行示例
    duplicate_columns_rename_example()     # 重命名重复列（默认方式）
    duplicate_columns_error_example()     # 抛出异常
    duplicate_columns_keep_first_example() # 只保留第一个重复列
    config_dict_example()                 # 使用配置字典
    setter_methods_example()              # 使用setter方法
    dot_object_config_example()           # 使用点对象方式配置
    best_practice_example()               # 最佳实践
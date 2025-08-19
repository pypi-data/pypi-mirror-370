"""
生成JSON示例数据说明
"""

def json_data_info():
    """JSON示例数据说明"""
    print("JSON示例数据说明")
    print("==================")
    print("JSON连接器支持多种JSON数据格式:")
    print("1. 对象数组格式")
    print("2. 单个对象格式")
    print("3. 嵌套对象格式")
    print()
    print("示例数据结构:")
    print("- employees.json (对象数组):")
    print("  - id (整数)")
    print("  - name (字符串)")
    print("  - department (字符串)")
    print("  - salary (数字)")
    print("  - skills (数组)")
    print()
    print("- company.json (嵌套对象):")
    print("  - name (字符串)")
    print("  - founded (数字)")
    print("  - departments (对象数组)")
    print("  - address (嵌套对象)")
    print()


if __name__ == "__main__":
    json_data_info()
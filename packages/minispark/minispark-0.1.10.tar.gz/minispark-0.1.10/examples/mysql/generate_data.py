"""
生成MySQL示例数据说明
"""

def mysql_data_info():
    """MySQL示例数据说明"""
    print("MySQL示例数据说明")
    print("==================")
    print("MySQL示例需要真实的MySQL服务器环境，无法自动生成示例数据文件。")
    print()
    print("要运行MySQL示例，您需要：")
    print("1. 一个运行中的MySQL服务器")
    print("2. 安装pymysql库: pip install pymysql")
    print("3. 在MySQL中创建示例数据库和表")
    print()
    print("示例表结构:")
    print("- employees表:")
    print("  - id (INT)")
    print("  - name (VARCHAR)")
    print("  - department (VARCHAR)")
    print("  - salary (DECIMAL)")
    print()
    print("请根据您的实际MySQL环境修改连接参数。")


if __name__ == "__main__":
    mysql_data_info()
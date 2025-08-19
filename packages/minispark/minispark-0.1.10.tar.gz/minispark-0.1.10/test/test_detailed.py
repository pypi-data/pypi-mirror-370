print("开始测试")

try:
    print("1. 导入基础模块")
    import pandas as pd
    import toml
    print("基础模块导入成功")
    
    print("2. 导入自定义模块")
    from minispark.connectors.base import BaseConnector
    from minispark.engines.base import BaseEngine
    from minispark.processors.data_processor import DataProcessor
    print("自定义模块导入成功")
    
    print("3. 尝试加载配置")
    try:
        with open("config.toml", 'r', encoding='utf-8') as f:
            config = toml.load(f)
        print("配置加载成功:", config)
    except FileNotFoundError:
        config = {
            "engine": {
                "type": "duckdb",
                "database_path": ":memory:"
            },
            "storage": {
                "format": "parquet"
            }
        }
        print("使用默认配置:", config)
    
    print("4. 尝试初始化引擎")
    engine_type = config.get("engine", {}).get("type", "duckdb")
    database_path = config.get("engine", {}).get("database_path", ":memory:")
    print(f"引擎类型: {engine_type}, 数据库路径: {database_path}")
    
    if engine_type == "duckdb":
        print("导入DuckDB引擎")
        from minispark.engines.duckdb_engine import DuckDBEngine
        print("DuckDB引擎导入成功")
        print("创建DuckDB引擎实例")
        engine = DuckDBEngine(database_path)
        print("DuckDB引擎实例创建成功")
    elif engine_type == "sqlite":
        print("导入SQLite引擎")
        from minispark.engines.sqlite_engine import SQLiteEngine
        print("SQLite引擎导入成功")
    
    print("测试完成")
    
except Exception as e:
    print(f"出现错误: {e}")
    import traceback
    traceback.print_exc()
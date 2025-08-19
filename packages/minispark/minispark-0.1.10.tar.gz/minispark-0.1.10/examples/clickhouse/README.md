# ClickHouse 连接器使用说明

ClickHouse 连接器允许 MiniSpark 连接到 ClickHouse 数据库并执行查询。

## 安装依赖

在使用 ClickHouse 连接器之前，需要安装必要的依赖包：

```bash
pip install clickhouse-driver
```

## 使用示例

### 创建连接器

```python
from minispark import MiniSpark, ClickHouseConnector

# 初始化 MiniSpark
spark = MiniSpark()

# 创建 ClickHouse 连接器
clickhouse_connector = ClickHouseConnector(
    name='clickhouse_example',
    host='localhost',      # ClickHouse 主机
    port=9000,             # ClickHouse 端口 (TCP接口)
    user='default',        # 用户名
    password='',           # 密码
    database='default'     # 数据库名
)

# 添加连接器到 MiniSpark
spark.add_connector('clickhouse', clickhouse_connector)
```

### 执行查询

```python
# 执行查询并将结果注册为表
df = spark.load_data('clickhouse', 'SELECT * FROM your_table', 'table_name')

# 执行 DDL 或 DML 语句 (不注册结果)
spark.load_data('clickhouse', 'CREATE TABLE ...', 'result', register=False)
spark.load_data('clickhouse', 'INSERT INTO ...', 'result', register=False)
```

## 参数说明

ClickHouseConnector 构造函数参数：

- `name`: 连接器名称
- `host`: ClickHouse 主机地址，默认为 "localhost"
- `port`: ClickHouse TCP 端口，默认为 9000
- `user`: 用户名，默认为 "default"
- `password`: 密码，默认为空字符串
- `database`: 数据库名，默认为 "default"

## 注意事项

1. ClickHouse 连接器使用 `clickhouse-driver` 库进行连接，该库使用 ClickHouse 的原生 TCP 接口
2. 端口 9000 是 ClickHouse 的 TCP 接口端口，而不是 HTTP 接口端口 (通常为 8123)
3. 查询结果会被转换为 pandas DataFrame 格式
4. 支持所有标准 SQL 操作，包括 SELECT、INSERT、CREATE 等
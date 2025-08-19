# MiniSpark

MiniSpark是一个轻量级的Python库，用于从多种数据源读取数据并在本地进行高效处理，类似于Apache Spark的功能。

作者: 段福 (duanfu456@163.cm)

## 功能特性

- 多数据源支持：MySQL、DuckDB、SQLite、CSV、Excel和JSON
- 本地数据处理引擎（DuckDB/SQLite）
- 统一API接口
- 查询结果表注册与复用
- 支持自定义函数处理数据（简化API，直接传入整行数据）
- 支持将字段值按分隔符拆分成多行（支持单个或多个分隔符）
- 支持自定义函数返回多个列
- 支持查看已注册的表信息
- DataProcessor处理后的数据可自动注册到本地引擎
- 灵活的配置管理，支持多种配置方式
- 可配置的重复列名处理策略

## 安装

```bash
pip install minispark
```

对于特定数据库支持，可以安装额外的依赖：

```bash
# MySQL支持
pip install minispqrk[mysql]

# DuckDB支持
pip install minispqrk[duckdb]

# Excel支持
pip install minispqrk[excel]
```

## CLI工具

安装后可以使用命令行工具：

```bash
# 查看帮助
minispark --help

# 运行示例
minispark example
```

### ClickHouse 连接器使用示例

```python
from minispark import MiniSpark, ClickHouseConnector

# 初始化
spark = MiniSpark()

# 添加 ClickHouse 连接器
clickhouse = ClickHouseConnector(
    name='ch',
    host='localhost',
    port=9000,
    user='default',
    password='',
    database='default'
)
spark.add_connector('clickhouse', clickhouse)

# 查询数据
df = spark.load_data('clickhouse', 'SELECT * FROM table', 'my_table')
```

## 支持的数据源

1. **关系型数据库**：
   - MySQL
   - DuckDB
   - SQLite
   - ClickHouse

2. **文件格式**：
   - CSV
   - Excel (xlsx/xls)
   - JSON

## 各数据源使用示例

### CSV连接器

```python
from minispark import MiniSpark, CSVConnector
import pandas as pd

// 创建示例数据
data = pd.DataFrame({
    'id': [1, 2, 3],
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35]
})
data.to_csv('sample.csv', index=False)

// 初始化MiniSpark
spark = MiniSpark()

// 创建CSV连接器
csv_connector = CSVConnector('csv_connector')
spark.add_connector('csv', csv_connector)

// 从CSV文件加载数据
df = spark.load_data('csv', 'sample.csv', 'sample_table')
print(df)
```

**指定不同分隔符**：

```python
// 使用分号分隔符
semicolon_connector = CSVConnector('semicolon_csv', delimiter=';')

// 使用制表符分隔符
tab_connector = CSVConnector('tab_csv', delimiter='\t')

// 使用管道符分隔符
pipe_connector = CSVConnector('pipe_csv', delimiter='|')
```

### Excel连接器

```python
from minispark import MiniSpark, ExcelConnector
import pandas as pd

// 创建示例数据（包含多个工作表）
products_data = pd.DataFrame({
    'id': [1, 2, 3],
    'product': ['Laptop', 'Phone', 'Tablet'],
    'price': [1000, 500, 300]
})

orders_data = pd.DataFrame({
    'order_id': [101, 102],
    'product_id': [1, 2],
    'quantity': [2, 1]
})

// 保存为包含多个工作表的Excel文件
with pd.ExcelWriter('data.xlsx') as writer:
    products_data.to_excel(writer, sheet_name='Products', index=False)
    orders_data.to_excel(writer, sheet_name='Orders', index=False)

// 初始化MiniSpark
spark = MiniSpark()

// 方法1：创建通用Excel连接器（推荐）
excel_connector = ExcelConnector('excel_connector')
spark.add_connector('excel', excel_connector)

// 使用同一个连接器读取不同工作表
products_df = spark.load_data('excel', 'data.xlsx', 'products_table', sheet_name='Products')
orders_df = spark.load_data('excel', 'data.xlsx', 'orders_table', sheet_name='Orders')

// 方法2：创建指定默认工作表的Excel连接器
default_excel_connector = ExcelConnector('default_excel', sheet_name='Products')
spark.add_connector('default_excel', default_excel_connector)

// 使用默认工作表加载数据
products_df = spark.load_data('default_excel', 'data.xlsx', 'products_table')

// 覆盖默认工作表
orders_df = spark.load_data('default_excel', 'data.xlsx', 'orders_table', sheet_name='Orders')
```

### JSON连接器

```python
from minispark import MiniSpark, JSONConnector
import json

// 创建示例数据
data = [
    {"id": 1, "name": "Alice", "skills": ["Python", "SQL"]},
    {"id": 2, "name": "Bob", "skills": ["Java", "Docker"]},
    {"id": 3, "name": "Charlie", "skills": ["Excel", "Communication"]}
]

with open('employees.json', 'w') as f:
    json.dump(data, f)

// 初始化MiniSpark
spark = MiniSpark()

// 创建JSON连接器
json_connector = JSONConnector('json_connector')
spark.add_connector('json', json_connector)

// 从JSON文件加载数据
df = spark.load_data('json', 'employees.json', 'employees_table')
print(df)
```

### SQLite连接器

```python
from minispark import MiniSpark, SQLiteConnector
import sqlite3

// 创建示例数据库和数据
conn = sqlite3.connect('sample.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT
    )
''')
cursor.execute("INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com')")
cursor.execute("INSERT INTO users (name, email) VALUES ('Bob', 'bob@example.com')")
conn.commit()
conn.close()

// 初始化MiniSpark
spark = MiniSpark()

// 创建SQLite连接器
sqlite_connector = SQLiteConnector('sqlite_connector', 'sample.db')
spark.add_connector('sqlite', sqlite_connector)

// 从SQLite数据库查询数据
df = spark.load_data('sqlite', 'SELECT * FROM users', 'users_table')
print(df)
```

### MySQL连接器

```python
from minispark import MiniSpark, MySQLConnector

// 初始化MiniSpark
spark = MiniSpark()

// 创建MySQL连接器
mysql_connector = MySQLConnector(
    name='mysql_connector',
    host='localhost',
    port=3306,
    user='username',
    password='password',
    database='database_name'
)
spark.add_connector('mysql', mysql_connector)

// 从MySQL数据库查询数据
df = spark.load_data('mysql', 'SELECT * FROM table_name LIMIT 10', 'mysql_table')
print(df)
```

### DuckDB连接器

```python
from minispark import MiniSpark, DuckDBConnector

// 初始化MiniSpark
spark = MiniSpark()

// 创建DuckDB连接器（内存数据库）
duckdb_connector = DuckDBConnector('duckdb_connector')
spark.add_connector('duckdb', duckdb_connector)

// 执行查询
df = spark.load_data('duckdb', 'SELECT 1 as number', 'test_table')
print(df)
```

### 跨数据源查询示例

```python
from minispark import MiniSpark, CSVConnector, JSONConnector

// 初始化MiniSpark
spark = MiniSpark()

// 添加多个数据源
csv_connector = CSVConnector('csv_connector')
json_connector = JSONConnector('json_connector')
spark.add_connector('csv', csv_connector)
spark.add_connector('json', json_connector)

// 从不同数据源加载数据
employees_df = spark.load_data('csv', 'employees.csv', 'employees')
skills_df = spark.load_data('json', 'skills.json', 'skills')

// 在本地引擎中执行跨数据源查询
result = spark.execute_query("""
    SELECT e.name, e.department, e.salary
    FROM employees e
    WHERE e.salary > 7000
    ORDER BY e.salary DESC
""", 'high_salary_employees')

print(result)
```

### 2. 本地处理引擎
- SQLite引擎：轻量级本地数据库引擎
- DuckDB引擎：高性能分析型数据库引擎

### 3. 数据处理功能
- 注册自定义函数并在数据处理中应用
- 直接应用匿名函数进行数据转换
- 使用swifter加速Pandas操作

### 4. 查询结果表注册
`execute_query`方法支持将查询结果直接注册为表，方便后续关联查询：

```python
// 将查询结果注册为新表
spark.execute_query("""
    SELECT department, AVG(salary) as avg_salary
    FROM employees
    GROUP BY department
""", table_name="department_avg")

// 后续可以直接查询已注册的表
result = spark.execute_query("SELECT * FROM department_avg WHERE avg_salary > 50000")
```

通过提供`table_name`参数，查询结果将自动注册为可重用的表。如果需要执行查询但不希望注册结果，可以设置`register=False`。

## JSON支持

MiniSpark现在支持JSON数据源，可以处理多种JSON格式：

1. 对象数组格式
2. 单个对象格式
3. 嵌套对象格式

### JSON使用示例

```python
from minispark import MiniSpark, JSONConnector

// 初始化MiniSpark
spark = MiniSpark()

// 添加JSON连接器
json_connector = JSONConnector('json')
spark.add_connector('json', json_connector)

// 从JSON文件加载数据
df = spark.load_data('json', 'data.json', 'my_table')

// 处理复杂数据类型（如数组、嵌套对象）
// 这些数据在加载时会被自动转换为字符串格式以兼容SQL引擎
```

## 运行测试

项目包含一系列测试用例，确保功能正常工作。要运行所有测试：

```bash
// 从项目根目录运行
python -m unittest discover test

// 或者使用测试运行脚本
python test/run_tests.py
```

## 示例程序

项目提供了一些完整的示例程序，展示了MiniSpark的各种功能。这些示例位于[examples](file://./examples)目录中：


要运行示例程序：

```bash
cd examples
python example_row_function.py
python example_multi_column.py
python comprehensive_example.py
```

## 配置

MiniSpark支持多种配置方式，提供了灵活的配置管理机制：

### 1. 配置文件方式（默认）

使用`config.toml`文件进行配置：

```toml
// 本地处理引擎配置
[engine]
// 引擎类型，支持 duckdb 或 sqlite
type = "duckdb"
// 数据库路径，:memory: 表示内存模式
database_path = ":memory:"

// 临时数据存储配置
[storage]
// 存储格式，支持 parquet 或 avro
format = "parquet"

// 重复列名处理方式，支持 rename/error/keep_first
handle_duplicate_columns = "rename"
```

### 2. 配置字典方式

可以直接传递配置字典：

```python
from minispark import MiniSpark

config = {
    "engine": {
        "type": "sqlite",
        "database_path": ":memory:"
    },
    "storage": {
        "format": "parquet"
    }
}

spark = MiniSpark(config=config)
```

### 3. 指定配置文件路径

可以指定配置文件的路径：

```python
from minispark import MiniSpark

spark = MiniSpark(config_path="/path/to/your/config.toml")
```

### 4. 点对象方式访问和修改配置

可以通过点对象方式访问和修改配置：

```python
from minispark import MiniSpark

spark = MiniSpark()

// 访问配置
print(spark.config.engine.type)
print(spark.config.engine.database_path)
print(spark.config.storage.format)

// 修改配置
spark.config.engine.type = "sqlite"
spark.config.engine.database_path = ":memory:"
spark.config.storage.format = "parquet"
```

### 5. 属性方式访问和修改配置

可以通过属性方式访问和修改配置：

```python
from minispark import MiniSpark

spark = MiniSpark()

// 访问配置
print(spark.config.engine.type)
print(spark.config.engine.database_path)
print(spark.config.storage.format)
print(spark.config.handle_duplicate_columns)

// 修改配置
spark.config.engine.type = "sqlite"
spark.config.engine.database_path = ":memory:"
spark.config.storage.format = "parquet"
spark.config.handle_duplicate_columns = "error"
```

### 6. Setter方法方式

可以使用setter方法修改配置：

```python
from minispark import MiniSpark

spark = MiniSpark()

// 设置新的配置字典
spark.set_config({
    "engine": {"type": "sqlite"},
    "storage": {"format": "parquet"},
    "handle_duplicate_columns": "error"
})

// 通过配置文件路径设置配置
spark.set_config_path("/path/to/your/config.toml")
```

## 依赖

- Python 3.9+
- pandas>=1.3.0
- sqlalchemy>=1.4.0
- toml>=0.10.2
- swifter>=1.0.0

可选依赖：
- pymysql>=1.0.0 (MySQL支持)
- duckdb>=0.3.0 (DuckDB支持)
- openpyxl>=3.0.0, xlrd>=2.0.0 (Excel支持)

## 数据处理功能

MiniSpark提供了一个强大的数据处理器，可用于对数据进行各种操作，处理后的结果数据表可以自动注册到本地引擎中，方便后续查询和分析。

## 重复列名处理策略

MiniSpark支持三种处理重复列名的策略：

1. **rename**（默认）：自动重命名重复列，在重复列名后添加后缀（如`_2`, `_3`等）
2. **error**：当发现重复列名时抛出异常
3. **keep_first**：只保留第一个重复列，删除其他重复列

### 1. 自定义函数应用

可以将Python函数应用于数据表的行，函数接收整行数据作为参数：

```python
from minispark import MiniSpark

// 初始化MiniSpark
spark = MiniSpark()

// 获取数据处理器
processor = spark.processor

// 定义处理整行数据的函数
def calculate_employee_benefits(row):
    // 根据多个字段综合计算员工福利
    base_benefits = row['salary'] * 0.1
    // IT部门有额外福利
    it_bonus = 5000 if row['department'] == 'IT' else 0
    // 工龄超过5年有额外福利
    experience_bonus = 2000 if row['years_of_service'] > 5 else 0
    return base_benefits + it_bonus + experience_bonus

// 应用处理整行数据的函数
df_with_benefits = processor.apply_custom_function(
    df,
    'benefits',  // 新列名
    calculate_employee_benefits,  // 函数
    table_name='employees_with_benefits'  // 自动注册为新表
)


// 注册并使用处理整行数据的函数
def calculate_performance_score(row):
    // 基于多个因素计算绩效得分
    base_score = row['salary'] / 1000
    bonus_factor = row['bonus'] / 100
    return base_score + bonus_factor

processor.register_function('performance_score', calculate_performance_score)

df_with_score = processor.apply_function(
    df,
    'performance_score',  // 新列名
    'performance_score'    // 已注册的函数名
)

// 支持返回多个列的函数
def calculate_min_max_salary(row):
    // 返回最小和最大薪资的元组
    return (row['salary'] * 0.8, row['salary'] * 1.2)

// 创建两个新列来接收返回值
df_with_ranges = processor.apply_custom_function(
    df,
    ['min_salary', 'max_salary'],  // 多个新列名
    calculate_min_max_salary,       // 返回多个值的函数
    table_name='employees_with_ranges'  // 自动注册为新表
)

// 支持函数返回字典动态创建列 (new_column_name=None)
def calculate_benefits_dict(row):
    // 根据员工信息计算福利，以字典形式返回
    bonus = row['salary'] * 0.1 if row['department'] == 'IT' else row['salary'] * 0.05
    stock_options = row['salary'] * 0.2 if row['department'] == 'IT' else 0
    return {
        'bonus': round(bonus, 2),
        'stock_options': round(stock_options, 2),
        'total_compensation': row['salary'] + bonus + stock_options
    }

// 当new_column_name为None时，函数返回的字典键会自动成为新列名
df_with_benefits = processor.apply_custom_function(
    df,
    None,  // new_column_name为None，表示根据函数返回的字典动态创建列
    calculate_benefits_dict
)

// 支持函数返回字典列表动态展开行 (new_column_name=None)
def generate_skill_list(row):
    // 为每个员工生成技能列表，以字典列表形式返回
    base_skills = ['Communication', 'Teamwork']
    
    if row['department'] == 'IT':
        extra_skills = ['Python', 'SQL', 'Problem Solving']
    elif row['department'] == 'HR':
        extra_skills = ['Recruitment', 'Employee Relations']
    else:  // Finance
        extra_skills = ['Financial Analysis', 'Excel', 'Reporting']
    
    // 返回字典列表，每个字典将变成一行
    skills_list = []
    for skill in (base_skills + extra_skills):
        skills_list.append({
            'name': row['name'],
            'department': row['department'],
            'skill': skill
        })
    return skills_list

// 当new_column_name为None时，函数返回的字典列表会自动展开为多行
df_with_skills = processor.apply_custom_function(
    df,
    None,  // new_column_name为None，表示根据函数返回的字典列表动态展开行
    generate_skill_list
)
```

### 2. 查看已注册的表

可以使用`list_tables`方法查看所有已注册的表及其信息：

```python
from minispark import MiniSpark
import pandas as pd

// 初始化MiniSpark
spark = MiniSpark()

// 创建一些示例数据
users_data = pd.DataFrame({
    'id': [1, 2, 3],
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35]
})

orders_data = pd.DataFrame({
    'order_id': [101, 102, 103],
    'user_id': [1, 2, 1],
    'amount': [100.0, 200.0, 150.0]
})

// 注册表到引擎
spark.engine.register_table('users', users_data)
spark.engine.register_table('orders', orders_data)

// 查看所有已注册的表
table_info = spark.list_tables()
print(table_info)
```

### 3. 字段拆分功能（支持单个或多个分隔符）

支持将包含分隔符的字段拆分成多行：

```python
from minispark import MiniSpark

// 初始化MiniSpark
spark = MiniSpark()

// 获取数据处理器
processor = spark.processor

// 假设有一个DataFrame，其中"tags"列包含用逗号分隔的标签
// 例如: "python,spark,data" => 拆分成3行，每行一个标签
df = spark.load_data('csv', 'data.csv', 'original_data')

// 使用单个分隔符
df_exploded = processor.explode_column(
    df, 
    'tags', 
    ',', 
    table_name='exploded_data'  // 自动注册为新表
)

// 使用多个分隔符（分号、竖线和连字符）
df_multi_exploded = processor.explode_column(
    df, 
    'description', 
    [';', '|', '-'], 
    table_name='multi_exploded_data'  // 自动注册为新表
)


// 现在可以将拆分后的数据注册到引擎中进行SQL查询
spark.engine.register_table('exploded_data', df_exploded)
result = spark.execute_query("SELECT * FROM exploded_data WHERE tags = 'python'")

// 链式操作示例：连续拆分多个列
df_step1 = processor.explode_column(df, 'tags', ',')
df_step2 = processor.explode_column(df_step1, 'description', [';', '|'])
df_step3 = processor.explode_column(df_step2, 'features', ['-', '#'])
```
# 文档目录
```
examples/
├── example_row_function.py          # 简化API处理整行数据示例
├── example_multi_column.py          # 多列处理示例
├── example_auto_register.py         # DataProcessor自动注册功能示例
├── example_dict_return.py           # 返回字典功能示例
├── comprehensive_example.py         # 综合示例
├── run_all_examples.py              # 运行所有示例的脚本
├── csv/                             # CSV相关示例
│   ├── example.py
│   ├── delimiter_example.py
│   ├── double_pipe_example.py
│   ├── generate_data.py
│   ├── employees.csv
│   └── README.md
├── excel/                           # Excel相关示例
│   ├── example.py
│   ├── dynamic_sheet_example.py
│   ├── explode_example.py
│   ├── generate_data.py
│   ├── products.xlsx
│   ├── salaries.xlsx
│   └── README.md
├── json/                            # JSON相关示例
│   ├── example.py
│   ├── generate_data.py
│   ├── skills.json
│   └── README.md
├── mysql/                           # MySQL相关示例
│   ├── example.py
│   ├── generate_data.py
│   ├── create_join_data.py
│   ├── join_query_example.py
│   ├── join_query_test.py
│   └── test_mysql_example.py
├── sqlite/                          # SQLite相关示例
│   ├── example.py
│   ├── generate_data.py
│   └── company.db
└── duckdb/                          # DuckDB相关示例
    ├── example.py
    └── generate_data.py
```

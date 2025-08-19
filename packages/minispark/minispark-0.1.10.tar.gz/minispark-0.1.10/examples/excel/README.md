# Excel 示例

这个目录包含了使用MiniSpark处理Excel数据的示例。

## 文件说明

- [example.py](file:///d:/python/softwarwe/minispqrk/examples/excel/example.py) - 基本Excel使用示例
- [generate_data.py](file:///d:/python/softwarwe/minispqrk/examples/excel/generate_data.py) - 生成示例数据
- [dynamic_sheet_example.py](file:///d:/python/softwarwe/minispqrk/examples/excel/dynamic_sheet_example.py) - 动态工作表使用示例
- [explode_example.py](file:///d:/python/softwarwe/minispqrk/minispark_examples/excel/explode_example.py) - 结合explode功能使用示例

## 如何指定Excel工作表

在MiniSpark中，有两种方式指定要读取的Excel工作表：

### 1. 在连接器中指定默认工作表

```python
# 指定默认工作表为"Products"
excel_connector = ExcelConnector('excel_connector', sheet_name='Products')
spark.add_connector('excel', excel_connector)

# 使用默认工作表加载数据
df = spark.load_data('excel', 'data.xlsx', 'table_name')
```

### 2. 在加载数据时动态指定工作表（推荐）

```python
# 创建不指定默认工作表的连接器
excel_connector = ExcelConnector('excel_connector')
spark.add_connector('excel', excel_connector)

# 在加载数据时动态指定工作表
products_df = spark.load_data('excel', 'data.xlsx', 'products_table', sheet_name='Products')
orders_df = spark.load_data('excel', 'data.xlsx', 'orders_table', sheet_name='Orders')
```

第二种方式更加灵活，允许使用同一个连接器读取同一个Excel文件中的不同工作表。

## 数据处理功能

### 使用explode功能处理Excel数据

MiniSpark的数据处理器提供了[explode_column](file:///d:/python/softwarwe/minispqrk/build/lib/minispark/processors/data_processor.py#L74-L111)方法，可以将包含分隔符的字段拆分成多行。例如，如果Excel中有一列包含用逗号分隔的标签：

```python
# 加载Excel数据
df = spark.load_data('excel', 'products.xlsx', 'products')

# 使用explode功能将tags列按逗号拆分成多行
processor = spark.processor
exploded_df = processor.explode_column(df, 'tags', ',')

# 注册处理后的数据到引擎
spark.engine.register_table('exploded_products', exploded_df)

# 现在可以执行SQL查询
result = spark.execute_query("""
    SELECT product_name, tags
    FROM exploded_products 
    WHERE tags = 'electronics'
""")
```

### 使用多个分隔符处理Excel数据

现在[explode_column](file:///d:/python/softwarwe/minispqrk/build/lib/minispark/processors/data_processor.py#L74-L111)方法支持同时使用多个分隔符进行拆分，这在处理复杂数据时非常有用：

```python
# 加载Excel数据
df = spark.load_data('excel', 'products.xlsx', 'products')

# 使用多个分隔符将features列拆分成多行
# 数据示例: "wifi;bluetooth|usb" 将被拆分为三行: "wifi", "bluetooth", "usb"
processor = spark.processor
exploded_df = processor.explode_column(df, 'features', [';', '|'])

# 注册处理后的数据到引擎
spark.engine.register_table('exploded_products', exploded_df)

# 现在可以执行SQL查询
result = spark.execute_query("""
    SELECT product_name, features
    FROM exploded_products 
    WHERE features = 'bluetooth'
""")
```

## 支持的Excel文件格式

MiniSpark支持常见的Excel文件格式：
- `.xlsx` - Excel 2007及以后版本
- `.xls` - Excel 97-2003版本

## 依赖库

使用Excel功能需要安装相应的依赖库：

```bash
# 对于.xlsx文件
pip install openpyxl

# 对于.xls文件
pip install xlrd
```

## 运行示例

```bash
# 运行基本示例
python example.py

# 运行动态工作表示例
python dynamic_sheet_example.py

# 运行explode功能示例（支持单一分隔符）
python explode_example.py

# 运行explode功能示例（支持多分隔符）
python explode_example.py
```
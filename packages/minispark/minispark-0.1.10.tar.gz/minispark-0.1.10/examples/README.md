# MiniSpark 使用示例

这个目录包含了针对每种支持的数据类型的具体使用示例。每个数据类型都有独立的子目录，包含生成示例数据的脚本和使用示例。

## 目录结构

```
examples/
├── csv/           # CSV文件示例
│   ├── generate_data.py  # 生成示例CSV数据
│   └── example.py        # CSV使用示例
├── sqlite/        # SQLite数据库示例
│   ├── generate_data.py  # 生成示例SQLite数据
│   └── example.py        # SQLite使用示例
├── duckdb/        # DuckDB数据库示例
│   ├── generate_data.py  # 生成示例DuckDB数据
│   └── example.py        # DuckDB使用示例
├── mysql/         # MySQL数据库示例
│   ├── generate_data.py  # MySQL数据说明
│   └── example.py        # MySQL使用示例
├── excel/         # Excel文件示例
│   ├── generate_data.py  # 生成示例Excel数据
│   └── example.py        # Excel使用示例
├── example_row_function.py     # 简化API处理整行数据示例
├── example_multi_column.py     # 多列返回功能示例
├── example_auto_register.py    # DataProcessor自动注册功能示例
├── example_dict_return.py      # 返回字典功能示例
├── comprehensive_example.py    # 综合示例
└── run_all_examples.py         # 运行所有示例的脚本
```

## 运行示例

### 运行单个示例

```bash
# 在项目根目录下运行
uv run python examples/csv/example.py
uv run python examples/sqlite/example.py
uv run python examples/duckdb/example.py
uv run python examples/mysql/example.py
uv run python examples/excel/example.py
uv run python examples/excel/explode_example.py
uv run python examples/example_row_function.py
uv run python examples/example_multi_column.py
uv run python examples/example_auto_register.py
uv run python examples/example_dict_return.py
uv run python examples/comprehensive_example.py
```

### 运行所有示例

```bash
# 在项目根目录下运行
uv run python examples/run_all_examples.py
```

## 依赖说明

不同示例需要安装不同的可选依赖：

- CSV示例: 无需额外依赖（pandas已包含）
- SQLite示例: 无需额外依赖（python内置sqlite3）
- DuckDB示例: 需要安装duckdb `uv pip install duckdb`
- MySQL示例: 需要安装pymysql `uv pip install pymysql`
- Excel示例: 需要安装openpyxl `uv pip install openpyxl`

## 安装所有依赖

```bash
uv pip install pymysql duckdb openpyxl
```

注意: 基本依赖(pandas, sqlalchemy, toml, swifter)在安装minispark时已自动安装。

## 示例说明

### example_row_function.py
演示如何使用简化后的DataProcessor API直接传入整行数据给自定义函数。

### example_multi_column.py
演示如何使用DataProcessor的多列返回功能，让自定义函数可以同时创建多个列。

### example_auto_register.py
演示如何使用DataProcessor处理数据后自动将结果注册到本地引擎，便于后续查询和分析。

### example_dict_return.py
演示当[new_column_name](file:///d:/python/softwarwe/minispqrk/minispark/processors/data_processor.py#L71-L71)为None时，如何处理函数返回字典或字典列表的情况，自动创建新列或展开多行。

### comprehensive_example.py
综合示例，展示所有支持的数据源类型使用方法。
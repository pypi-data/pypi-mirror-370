# 更新日志

## [0.1.10] - 2025-08-18

### 新增功能

- 添加ClickHouse数据库连接器支持：
  - 新增ClickHouseConnector类，支持连接和查询ClickHouse数据库
  - 使用clickhouse-driver库实现高效的数据传输
  - 支持通过extras_require安装clickhouse依赖：pip install minispark[clickhouse]
  - 提供完整的使用示例和文档说明
  - 保持与其他连接器一致的API接口设计

## [0.1.9] - 2025-08-16

### 新增功能

- 增强DataProcessor的apply_custom_function方法，支持new_column_name默认为None：
  - new_column_name参数现在默认为None
  - 当new_column_name为None时，函数可以返回字典或字典列表来动态创建列或展开行
  - 函数返回字典时，字典的键会成为新列名，值会成为对应的数据
  - 函数返回字典列表时，每个字典会扩展成一行数据
  - 保持向后兼容，原有使用方式不变

## [0.1.8] - 2025-08-13

### 新增功能

- 将handle_duplicate_columns参数移至配置中管理：
  - 作为配置项，可以通过config.toml或配置字典进行设置
  - 支持通过点对象方式访问和修改（spark.config.handle_duplicate_columns）
  - 支持通过属性访问和修改（spark.handle_duplicate_columns）
  - 保持向后兼容，默认值仍为"rename"

## [0.1.7] - 2025-08-12

### 新增功能

- 增强MiniSpark配置管理，支持多种配置方式：
  - 支持通过点对象方式访问和修改配置（如spark.config.engine.type）
  - 支持使用SimpleNamespace实现嵌套配置访问
  - 保持向后兼容，原有的配置字典和配置文件方式仍然可用
  - 移除了属性风格配置访问（如spark.engine_type），统一使用点对象方式

## [0.1.6] - 2025-08-12

### 新增功能

- 增强DataProcessor的apply_custom_function方法，支持返回多个列
  - new_column_name参数现在支持字符串列表，可以同时创建多个列
  - 函数可以返回列表、元组或字典，自动展开到对应的多个列
  - 保持向后兼容，原有单列使用方式不变
  - 添加了完整的测试用例，确保功能稳定可靠

- 增强MiniSpark类，添加list_tables方法用于查看已注册的表信息
  - 提供便捷的方法查看所有已注册表的名称、形状、列名和内存占用
  - 添加了完整的测试用例，确保功能稳定可靠

- 增强DataProcessor类，支持处理后的数据自动注册到本地引擎
  - apply_function、apply_custom_function和explode_column方法现在支持table_name和register参数
  - 处理后的数据可以自动注册为新表，便于后续查询
  - 支持通过register=False禁用自动注册功能

## [0.1.5] - 2025-08-18

### 新增功能

- 添加ClickHouse数据库连接器支持：
  - 新增ClickHouseConnector类，支持连接和查询ClickHouse数据库
  - 使用clickhouse-driver库实现高效的数据传输
  - 支持通过extras_require安装clickhouse依赖：pip install minispark[clickhouse]
  - 提供完整的使用示例和文档说明
  - 保持与其他连接器一致的API接口设计
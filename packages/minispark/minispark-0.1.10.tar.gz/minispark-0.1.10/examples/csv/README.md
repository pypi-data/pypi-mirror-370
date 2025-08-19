# CSV 示例

这个目录包含了使用MiniSpark处理CSV数据的示例。

## 文件说明

- [example.py](file:///d:/python/softwarwe/minispqrk/examples/csv/example.py) - 基本CSV使用示例
- [generate_data.py](file:///d:/python/softwarwe/minispqrk/examples/csv/generate_data.py) - 生成示例数据
- [delimiter_example.py](file:///d:/python/softwarwe/minispqrk/examples/csv/delimiter_example.py) - 演示如何使用不同分隔符的示例
- [double_pipe_example.py](file:///d:/python/softwarwe/minispqrk/examples/csv/double_pipe_example.py) - 演示双字符分隔符问题及推荐解决方案

## 如何指定CSV分隔符

在MiniSpark中，可以通过CSVConnector的构造函数指定分隔符：

```python
# 使用默认逗号分隔符
connector = CSVConnector('name')

# 使用分号分隔符
connector = CSVConnector('name', delimiter=';')

# 使用制表符分隔符
connector = CSVConnector('name', delimiter='\t')

# 使用管道符分隔符
connector = CSVConnector('name', delimiter='|')
```

## 分隔符使用注意事项

1. **推荐使用单字符分隔符**：如逗号(,)、分号(;)、制表符(\t)、管道符(|)等
2. **避免使用双字符分隔符**：如双管道符(||)会导致pandas无法正确解析列名，因为每个字符都会被当作分隔符处理
3. **特殊情况处理**：如果必须使用双字符分隔符，需要先对文件进行预处理

## 如何指定编码

也可以通过CSVConnector的构造函数指定文件编码：

```python
# 使用UTF-8编码（默认）
connector = CSVConnector('name', delimiter=',', encoding='utf-8')

# 使用其他编码
connector = CSVConnector('name', delimiter=',', encoding='gbk')
```

## 运行示例

```bash
# 运行基本示例
python example.py

# 运行分隔符示例
python delimiter_example.py

# 运行双管道符示例
python double_pipe_example.py
```
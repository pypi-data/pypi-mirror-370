import pandas as pd
import swifter
import re
from typing import Callable, Any, Union, List, Optional
from loguru import logger


class DataProcessor:
    """数据处理器，支持将Python函数应用于数据表的行"""
    
    def __init__(self):
        self.functions = {}
        self.minispark = None  # 添加对MiniSpark实例的引用
        logger.info("初始化数据处理器")
    
    def set_minispark(self, minispark):
        """设置MiniSpark实例引用"""
        self.minispark = minispark
    
    def register_function(self, name: str, func: Callable):
        """
        注册函数以便在数据处理中使用
        
        Args:
            name: 函数名称
            func: 函数对象
        """
        logger.info(f"注册函数: {name}")
        self.functions[name] = func
    
    def apply_function(self, dataframe: pd.DataFrame, new_column_name: str,
                      function_name: str, table_name: Optional[str] = None, 
                      register: bool = True) -> pd.DataFrame:
        """
        将已注册的函数应用于数据表的行
        
        Args:
            dataframe: 输入的DataFrame
            new_column_name: 新列的名称
            function_name: 已注册的函数名称
            table_name: 表名称，如果提供则将结果注册到本地引擎
            register: 是否注册到本地引擎（仅在table_name提供时有效）
        """
        logger.info(f"应用已注册函数: {function_name} 创建新列: {new_column_name}")
        
        if function_name not in self.functions:
            logger.error(f"函数 {function_name} 未注册")
            raise ValueError(f"函数 {function_name} 未注册")
        
        func = self.functions[function_name]
        
        try:
            # 使用swifter加速pandas操作，将整行数据传入函数
            dataframe[new_column_name] = dataframe.swifter.apply(func, axis=1)
            
            # 如果提供了表名且需要注册，则注册到本地引擎
            if table_name is not None and register and self.minispark is not None:
                logger.info(f"将处理后的数据注册为表: {table_name}")
                self.minispark.engine.register_table(table_name, dataframe)
                # 同时保存到本地表缓存
                self.minispark.tables[table_name] = dataframe
            
            logger.info(f"函数 {function_name} 应用成功")
            return dataframe
        except Exception as e:
            logger.error(f"函数 {function_name} 应用失败: {e}")
            raise
    
    def apply_custom_function(self, dataframe: pd.DataFrame, func: Callable, new_column_name: Union[str, List[str]] = None,
                             setswifter=True, table_name: Optional[str] = None, 
                             register: bool = True) -> pd.DataFrame:
        """
        将自定义函数应用于数据表的行
        
        Args:
            dataframe: 输入的DataFrame
            new_column_name: 新列的名称，可以是字符串或字符串列表，如果为None则根据函数返回的字典动态创建列
            func: 自定义函数
            table_name: 表名称，如果提供则将结果注册到本地引擎
            register: 是否注册到本地引擎（仅在table_name提供时有效）
        """
        logger.info(f"应用自定义函数创建新列: {new_column_name}")
        
        try:
            if setswifter:
                result = dataframe.swifter.apply(func, axis=1)
            else:
                result = dataframe.apply(func, axis=1)
            
            # 处理返回的结果
            if new_column_name is None:
                # 当new_column_name为None时，处理函数返回字典或字典列表的情况
                if len(result) > 0:
                    first_result = result.iloc[0]
                    
                    # 判断是否是字典列表的情况（需要展开成多行）
                    if isinstance(first_result, list) and len(first_result) > 0 and isinstance(first_result[0], dict):
                        # 处理函数返回List[dict]的情况
                        expanded_rows = []
                        
                        for idx, row in dataframe.iterrows():
                            result_item = result.iloc[idx]
                            if isinstance(result_item, list) and all(isinstance(item, dict) for item in result_item):
                                # 对于每个字典创建一行新数据
                                for dict_item in result_item:
                                    new_row = row.to_dict()
                                    new_row.update(dict_item)
                                    expanded_rows.append(new_row)
                            else:
                                # 如果不是列表或不是字典列表，则直接添加原行
                                expanded_rows.append(row.to_dict())
                        
                        dataframe = pd.DataFrame(expanded_rows)
                    elif isinstance(first_result, dict):
                        # 处理函数返回dict的情况
                        result_df = pd.DataFrame(result.tolist())
                        dataframe = pd.concat([dataframe.reset_index(drop=True), result_df.reset_index(drop=True)], axis=1)
                    else:
                        raise ValueError("当new_column_name为None时，函数必须返回dict或List[dict]")
            elif isinstance(new_column_name, str):
                # 单列情况
                dataframe[new_column_name] = result
            elif isinstance(new_column_name, list):
                # 多列情况
                if len(new_column_name) == 0:
                    raise ValueError("new_column_name列表不能为空")
                
                # 检查结果是否可以展开为多列
                if hasattr(result.iloc[0], '__iter__') and not isinstance(result.iloc[0], (str, bytes)):
                    # 如果结果是可迭代的（列表、元组、字典等），展开到多列
                    result_df = pd.DataFrame(result.tolist(), index=dataframe.index)
                    if len(new_column_name) != len(result_df.columns):
                        raise ValueError(f"返回的值数量({len(result_df.columns)})与指定的列数({len(new_column_name)})不匹配")
                    
                    # 将结果分配到指定的列
                    for i, col_name in enumerate(new_column_name):
                        dataframe[col_name] = result_df.iloc[:, i]
                else:
                    # 如果只有一个值但指定了多列，复制该值到所有列
                    for col_name in new_column_name:
                        dataframe[col_name] = result
            else:
                raise ValueError("new_column_name必须是None、字符串或字符串列表")
            
            # 如果提供了表名且需要注册，则注册到本地引擎
            if table_name is not None and register and self.minispark is not None:
                logger.info(f"将处理后的数据注册为表: {table_name}")
                self.minispark.engine.register_table(table_name, dataframe)
                # 同时保存到本地表缓存
                self.minispark.tables[table_name] = dataframe
            
            logger.info("自定义函数应用成功")
            return dataframe
        except Exception as e:
            logger.error(f"自定义函数应用失败: {e}")
            raise
    
    def explode_column(self, dataframe: pd.DataFrame, column: str, separator: Union[str, List[str]] = "-",
                      new_column_name: str = None, table_name: Optional[str] = None, 
                      register: bool = True) -> pd.DataFrame:
        """
        将指定列的值按分隔符拆分成多行
        
        Args:
            dataframe: 输入的DataFrame
            column: 要拆分的列名
            separator: 分隔符，可以是字符串或字符串列表，默认为"-"
            new_column_name: 新列的名称，如果为None则使用原列名
            table_name: 表名称，如果提供则将结果注册到本地引擎
            register: 是否注册到本地引擎（仅在table_name提供时有效）
            
        Returns:
            拆分后的DataFrame
        """
        logger.info(f"拆分列 {column}，分隔符: {separator}")
        
        try:
            # 如果指定了新列名，则重命名列
            if new_column_name and new_column_name != column:
                dataframe = dataframe.rename(columns={column: new_column_name})
                column = new_column_name
            
            # 创建一个新的列表来存储结果行
            result_rows = []
            
            # 遍历每一行
            for _, row in dataframe.iterrows():
                # 获取要拆分的值
                cell_value = str(row[column])
                
                # 根据分隔符类型处理
                if isinstance(separator, list):
                    # 如果是分隔符列表，使用正则表达式分割
                    pattern = '|'.join(map(re.escape, separator))
                    values = re.split(pattern, cell_value)
                else:
                    # 单个分隔符的情况
                    values = cell_value.split(separator)
                
                # 处理拆分后的值
                processed_values = []
                for value in values:
                    stripped_value = value.strip()
                    # 保留非空值和原始空字符串（如果输入本身就是空字符串）
                    if stripped_value or (len(values) == 1 and cell_value == ''):
                        processed_values.append(stripped_value)
                
                # 为每个拆分的值创建一行新数据
                for value in processed_values:
                    # 创建新行
                    new_row = row.copy()
                    new_row[column] = value
                    result_rows.append(new_row)
            
            # 创建新的DataFrame
            result_df = pd.DataFrame(result_rows)
            
            # 如果提供了表名且需要注册，则注册到本地引擎
            if table_name is not None and register and self.minispark is not None:
                logger.info(f"将处理后的数据注册为表: {table_name}")
                self.minispark.engine.register_table(table_name, result_df)
                # 同时保存到本地表缓存
                self.minispark.tables[table_name] = result_df
            
            logger.info(f"列 {column} 拆分成功，行数从 {len(dataframe)} 增加到 {len(result_df)}")
            return result_df
        except Exception as e:
            logger.error(f"列 {column} 拆分失败: {e}")
            raise
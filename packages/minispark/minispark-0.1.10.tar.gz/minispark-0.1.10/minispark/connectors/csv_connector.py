import pandas as pd
from loguru import logger
from .base import BaseConnector


class CSVConnector(BaseConnector):
    """CSV文件连接器"""
    
    def __init__(self, name: str, delimiter: str = ",", encoding: str = "utf-8"):
        super().__init__(name)
        self.delimiter = delimiter
        self.encoding = encoding
        logger.info(f"初始化CSV连接器: {name}, 分隔符: {delimiter}, 编码: {encoding}")
    
    def sql(self, query: str, table_name: str, register: bool = True):
        """
        执行SQL查询（基于CSV文件）
        注意：对于CSV文件，query参数应该是文件路径
        
        Args:
            query: CSV文件路径
            table_name: 表名称
            register: 是否注册到本地数据处理引擎
        """
        logger.info(f"CSV连接器执行查询, 文件: {query}, 表名: {table_name}")
        
        try:
            # 检查分隔符长度，如果大于1个字符则使用python引擎
            if len(self.delimiter) > 1:
                df = pd.read_csv(query, delimiter=self.delimiter, encoding=self.encoding, engine='python')
            else:
                df = pd.read_csv(query, delimiter=self.delimiter, encoding=self.encoding)
            df.table_name = table_name
            df.register = register
            logger.info(f"CSV文件读取成功, 形状: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"读取CSV文件失败: {e}")
            raise
    
    def close(self):
        """关闭连接（CSV不需要关闭连接）"""
        logger.info(f"关闭CSV连接器: {self.name}")
        pass
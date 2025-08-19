import pandas as pd
from loguru import logger
from .base import BaseConnector


class ExcelConnector(BaseConnector):
    """Excel文件连接器"""
    
    def __init__(self, name: str, sheet_name=None):
        """
        初始化Excel连接器
        
        Args:
            name: 连接器名称
            sheet_name: 默认工作表名称或索引，可为None
        """
        super().__init__(name)
        self.sheet_name = sheet_name
        logger.info(f"初始化Excel连接器: {name}, 默认工作表: {sheet_name}")
    
    def sql(self, query: str, table_name: str, register: bool = True, **kwargs):
        """
        执行SQL查询（基于Excel文件）
        注意：对于Excel文件，query参数应该是文件路径
        
        Args:
            query: Excel文件路径
            table_name: 表名称
            register: 是否注册到本地数据处理引擎
            **kwargs: 额外参数，支持sheet_name参数
        """
        # 如果kwargs中指定了sheet_name，则使用它，否则使用默认值
        sheet_name = kwargs.get('sheet_name', self.sheet_name)
        if sheet_name is None:
            sheet_name = 0  # 默认读取第一个工作表
            
        logger.info(f"Excel连接器执行查询, 文件: {query}, 工作表: {sheet_name}, 表名: {table_name}")
        
        try:
            df = pd.read_excel(query, sheet_name=sheet_name)
            df.table_name = table_name
            df.register = register
            logger.info(f"Excel文件读取成功, 形状: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"读取Excel文件失败: {e}")
            raise
    
    def close(self):
        """关闭连接（Excel不需要关闭连接）"""
        logger.info(f"关闭Excel连接器: {self.name}")
        pass
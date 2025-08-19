from abc import ABC, abstractmethod
from typing import Dict
import pandas as pd


class BaseEngine(ABC):
    """本地处理引擎基类"""
    
    def __init__(self):
        self.tables: Dict[str, pd.DataFrame] = {}
    
    @abstractmethod
    def register_table(self, table_name: str, dataframe: pd.DataFrame):
        """
        注册表到本地引擎
        
        Args:
            table_name: 表名称
            dataframe: DataFrame数据
        """
        pass
    
    @abstractmethod
    def execute_query(self, query: str):
        """
        执行SQL查询
        
        Args:
            query: SQL查询语句
        """
        pass
    
    @abstractmethod
    def close(self):
        """关闭引擎"""
        pass
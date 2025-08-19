from abc import ABC, abstractmethod
from typing import Optional


class BaseConnector(ABC):
    """数据库连接器基类"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def sql(self, query: str, table_name: str, register: bool = True):
        """
        执行SQL查询
        
        Args:
            query: SQL查询语句
            table_name: 表名称
            register: 是否注册到本地数据处理引擎
        """
        pass
    
    @abstractmethod
    def close(self):
        """关闭连接"""
        pass
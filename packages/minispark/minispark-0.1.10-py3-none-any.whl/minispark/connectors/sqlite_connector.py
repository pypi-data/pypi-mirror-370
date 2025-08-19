import pandas as pd
from loguru import logger
from .base import BaseConnector
from sqlalchemy import create_engine


class SQLiteConnector(BaseConnector):
    """SQLite数据库连接器"""
    
    def __init__(self, name: str, database_path: str = ":memory:"):
        super().__init__(name)
        self.database_path = database_path
        self.connection = None
        logger.info(f"初始化SQLite连接器: {name}, 数据库路径: {database_path}")
    
    def _get_connection(self):
        """获取数据库连接"""
        if self.connection is None:
            logger.info("创建新的SQLite连接")
            self.connection = create_engine(f"sqlite:///{self.database_path}")
        return self.connection
    
    def sql(self, query: str, table_name: str, register: bool = True):
        """
        执行SQL查询
        
        Args:
            query: SQL查询语句
            table_name: 表名称
            register: 是否注册到本地数据处理引擎
        """
        logger.info(f"SQLite连接器执行查询, 表名: {table_name}")
        
        try:
            conn = self._get_connection()
            df = pd.read_sql(query, conn)
            df.table_name = table_name
            df.register = register
            logger.info(f"SQLite查询执行成功, 形状: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"SQLite查询执行失败: {e}")
            raise
    
    def close(self):
        """关闭连接"""
        logger.info(f"关闭SQLite连接器: {self.name}")
        if self.connection:
            self.connection.dispose()
            self.connection = None
            logger.info("SQLite连接已关闭")
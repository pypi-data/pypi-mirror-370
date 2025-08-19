import pandas as pd
from loguru import logger
from .base import BaseConnector


class DuckDBConnector(BaseConnector):
    """DuckDB数据库连接器"""
    
    def __init__(self, name: str, database_path: str = ":memory:"):
        super().__init__(name)
        self.database_path = database_path
        self.connection = None
        logger.info(f"初始化DuckDB连接器: {name}, 数据库路径: {database_path}")
    
    def _get_connection(self):
        """获取数据库连接"""
        try:
            import duckdb
            
            if self.connection is None:
                logger.info("创建新的DuckDB连接")
                self.connection = duckdb.connect(self.database_path)
            return self.connection
        except ImportError:
            logger.error("使用DuckDB连接器需要安装duckdb库")
            raise ImportError("使用DuckDB连接器需要安装duckdb库")
        except Exception as e:
            logger.error(f"创建DuckDB连接失败: {e}")
            raise
    
    def sql(self, query: str, table_name: str, register: bool = True):
        """
        执行SQL查询
        
        Args:
            query: SQL查询语句
            table_name: 表名称
            register: 是否注册到本地数据处理引擎
        """
        logger.info(f"DuckDB连接器执行查询, 表名: {table_name}")
        
        try:
            conn = self._get_connection()
            df = conn.execute(query).fetchdf()
            df.table_name = table_name
            df.register = register
            logger.info(f"DuckDB查询执行成功, 形状: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"DuckDB查询执行失败: {e}")
            raise
    
    def close(self):
        """关闭连接"""
        logger.info(f"关闭DuckDB连接器: {self.name}")
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("DuckDB连接已关闭")
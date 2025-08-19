from typing import Optional
import pandas as pd
from loguru import logger
from .base import BaseConnector


class MySQLConnector(BaseConnector):
    """MySQL数据库连接器"""
    
    def __init__(self, name: str, host: str, port: int, user: str, password: str, database: str):
        super().__init__(name)
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        # 连接将在实际查询时创建
        self.connection = None
        logger.info(f"初始化MySQL连接器: {name}, 主机: {host}, 端口: {port}, 数据库: {database}")
    
    def _get_connection(self):
        """获取数据库连接"""
        try:
            import pymysql
            from sqlalchemy import create_engine
            
            if self.connection is None:
                logger.info("创建新的MySQL连接")
                connection_string = f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
                self.connection = create_engine(connection_string)
            return self.connection
        except ImportError:
            logger.error("使用MySQL连接器需要安装pymysql和sqlalchemy库")
            raise ImportError("使用MySQL连接器需要安装pymysql和sqlalchemy库")
        except Exception as e:
            logger.error(f"创建MySQL连接失败: {e}")
            raise
    
    def sql(self, query: str, table_name: str, register: bool = True):
        """
        执行SQL查询
        
        Args:
            query: SQL查询语句
            table_name: 表名称
            register: 是否注册到本地数据处理引擎
        """
        logger.info(f"MySQL连接器执行查询, 表名: {table_name}")
        
        try:
            conn = self._get_connection()
            df = pd.read_sql(query, conn)
            df.table_name = table_name
            df.register = register
            logger.info(f"MySQL查询执行成功, 形状: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"MySQL查询执行失败: {e}")
            raise
    
    def close(self):
        """关闭连接"""
        logger.info(f"关闭MySQL连接器: {self.name}")
        if self.connection:
            self.connection.dispose()
            self.connection = None
            logger.info("MySQL连接已关闭")
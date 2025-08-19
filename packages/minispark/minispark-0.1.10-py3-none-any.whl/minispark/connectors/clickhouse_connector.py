import pandas as pd
from loguru import logger
from .base import BaseConnector


class ClickHouseConnector(BaseConnector):
    """ClickHouse数据库连接器"""
    
    def __init__(self, name: str, host: str = "localhost", port: int = 8123, 
                 user: str = "default", password: str = "", database: str = "default"):
        super().__init__(name)
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        # 连接将在实际查询时创建
        self.connection = None
        logger.info(f"初始化ClickHouse连接器: {name}, 主机: {host}, 端口: {port}, 数据库: {database}")
    
    def _get_connection(self):
        """获取数据库连接"""
        try:
            from clickhouse_driver import Client
            
            if self.connection is None:
                logger.info("创建新的ClickHouse连接")
                self.connection = Client(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
            return self.connection
        except ImportError:
            logger.error("使用ClickHouse连接器需要安装clickhouse-driver库")
            raise ImportError("使用ClickHouse连接器需要安装clickhouse-driver库")
        except Exception as e:
            logger.error(f"创建ClickHouse连接失败: {e}")
            raise
    
    def sql(self, query: str, table_name: str, register: bool = True):
        """
        执行SQL查询
        
        Args:
            query: SQL查询语句
            table_name: 表名称
            register: 是否注册到本地数据处理引擎
        """
        logger.info(f"ClickHouse连接器执行查询, 表名: {table_name}")
        
        try:
            conn = self._get_connection()
            # 使用clickhouse_driver执行查询并获取结果
            result = conn.execute(query, with_column_types=True)
            
            # 将结果转换为DataFrame
            if result[0]:  # 如果有数据
                columns = [col[0] for col in result[1]]  # 获取列名
                df = pd.DataFrame(result[0], columns=columns)
            else:
                # 如果没有数据，创建一个空的DataFrame
                df = pd.DataFrame()
            
            df.table_name = table_name
            df.register = register
            logger.info(f"ClickHouse查询执行成功, 形状: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"ClickHouse查询执行失败: {e}")
            raise
    
    def close(self):
        """关闭连接"""
        logger.info(f"关闭ClickHouse连接器: {self.name}")
        if self.connection:
            # clickhouse_driver的Client不需要显式关闭连接
            self.connection = None
            logger.info("ClickHouse连接已关闭")
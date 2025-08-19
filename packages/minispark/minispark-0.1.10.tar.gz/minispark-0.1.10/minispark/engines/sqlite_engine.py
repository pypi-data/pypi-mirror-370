import pandas as pd
import os
from typing import Dict
from loguru import logger
from .base import BaseEngine
from sqlalchemy import create_engine


class SQLiteEngine(BaseEngine):
    """SQLite本地处理引擎"""
    
    def __init__(self, database_path: str = ":memory:"):
        super().__init__()
        self.database_path = database_path
        self.handle_duplicate_columns = "rename"  # 默认处理方式：重命名重复列
        self.connection = None
        logger.info(f"初始化SQLite引擎, 数据库路径: {database_path}")
        
        # 如果是文件数据库，确保目录存在
        if database_path != ":memory:":
            db_dir = os.path.dirname(database_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
        
        self._get_connection()
    
    def _get_connection(self):
        """获取数据库连接"""
        if self.connection is None:
            logger.info("创建新的SQLite引擎连接")
            if self.database_path == ":memory:":
                self.connection = create_engine(f"sqlite:///{self.database_path}")
            else:
                # 对于文件数据库，使用绝对路径
                self.connection = create_engine(f"sqlite:///{os.path.abspath(self.database_path)}")
        return self.connection
    
    def register_table(self, table_name: str, dataframe: pd.DataFrame):
        """
        注册表到本地引擎
        
        Args:
            table_name: 表名称
            dataframe: DataFrame数据
        """
        logger.info(f"注册表到SQLite引擎: {table_name}, 形状: {dataframe.shape}")
        
        try:
            # 处理重复列名问题
            cols = pd.Series(dataframe.columns)
            cols_counts = cols.value_counts()
            duplicated_cols = cols_counts[cols_counts > 1].index
            
            # 根据配置处理重复列名
            if len(duplicated_cols) > 0:
                if self.handle_duplicate_columns == "error":
                    # 抛出异常
                    raise ValueError(f"表 {table_name} 包含重复列名: {list(duplicated_cols)}")
                elif self.handle_duplicate_columns == "rename":
                    # 为重复的列名添加后缀以区分
                    logger.warning(f"发现重复列名: {list(duplicated_cols)}, 正在处理...")
                    new_cols = []
                    col_counters = {col: 0 for col in duplicated_cols}
                    
                    for col in dataframe.columns:
                        if col in duplicated_cols:
                            col_counters[col] += 1
                            if col_counters[col] > 1:
                                new_col_name = f"{col}_{col_counters[col]}"
                                new_cols.append(new_col_name)
                            else:
                                new_cols.append(col)
                        else:
                            new_cols.append(col)
                    
                    dataframe.columns = new_cols
                    logger.info(f"重复列名处理完成，新列名: {[col for col, count in col_counters.items() if count > 1]}")
                elif self.handle_duplicate_columns == "keep_first":
                    # 只保留第一个重复列，删除其他重复列
                    logger.warning(f"发现重复列名: {list(duplicated_cols)}, 只保留第一个...")
                    
                    # 记录要删除的列名
                    cols_to_drop = []
                    seen_cols = set()
                    dropped_col_names = []
                    
                    # 从左到右遍历列名，标记需要删除的列（保留第一个）
                    for i in range(len(dataframe.columns)):
                        col = dataframe.columns[i]
                        if col in duplicated_cols:
                            if col in seen_cols:
                                cols_to_drop.append(col)
                                dropped_col_names.append(col)
                            else:
                                seen_cols.add(col)
                    
                    # 删除重复的列
                    if cols_to_drop:
                        dataframe.drop(columns=cols_to_drop, inplace=True)
                    
                    logger.info(f"重复列名处理完成，已删除重复列: {dropped_col_names}")
                else:
                    # 未知处理方式，使用默认的重命名方式
                    logger.warning(f"未知的重复列名处理方式: {self.handle_duplicate_columns}，使用默认的重命名方式")
                    logger.warning(f"发现重复列名: {list(duplicated_cols)}, 正在处理...")
                    new_cols = []
                    col_counters = {col: 0 for col in duplicated_cols}
                    
                    for col in dataframe.columns:
                        if col in duplicated_cols:
                            col_counters[col] += 1
                            if col_counters[col] > 1:
                                new_col_name = f"{col}_{col_counters[col]}"
                                new_cols.append(new_col_name)
                            else:
                                new_cols.append(col)
                        else:
                            new_cols.append(col)
                    
                    dataframe.columns = new_cols
                    logger.info(f"重复列名处理完成，新列名: {[col for col, count in col_counters.items() if count > 1]}")
            
            conn = self._get_connection()
            dataframe.to_sql(table_name, conn, if_exists='replace', index=False)
            self.tables[table_name] = dataframe
            logger.info(f"表 {table_name} 注册成功")
        except Exception as e:
            logger.error(f"表 {table_name} 注册失败: {e}")
            raise
    
    def execute_query(self, query: str):
        """
        执行SQL查询
        
        Args:
            query: SQL查询语句
        """
        logger.info(f"SQLite引擎执行查询: {query}")
        
        try:
            conn = self._get_connection()
            result = pd.read_sql(query, conn)
            logger.info(f"查询执行成功, 结果形状: {result.shape}")
            return result
        except Exception as e:
            logger.error(f"SQLite查询执行失败: {e}")
            raise
    
    def close(self):
        """关闭引擎"""
        logger.info("关闭SQLite引擎")
        try:
            if self.connection:
                self.connection.dispose()
                self.connection = None
                logger.info("SQLite引擎已关闭")
        except Exception as e:
            logger.error(f"关闭SQLite引擎时发生错误: {e}")
            raise
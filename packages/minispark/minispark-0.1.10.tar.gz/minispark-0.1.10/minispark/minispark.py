import pandas as pd
import toml
import os
import tempfile
from typing import Dict, Any, List, Optional
from loguru import logger
from .connectors.base import BaseConnector
from .engines.base import BaseEngine
from .processors.data_processor import DataProcessor
import time
import atexit
import shutil
from types import SimpleNamespace


def dict_to_namespace(d):
    """递归将嵌套字典转换为 SimpleNamespace 对象"""
    if isinstance(d, dict):
        # 对字典中的每个值递归处理
        return SimpleNamespace(**{k: dict_to_namespace(v) for k, v in d.items()})
    elif isinstance(d, list):
        # 如果遇到列表，对列表中的每个元素递归处理
        return [dict_to_namespace(item) for item in d]
    else:
        # 非字典/列表类型直接返回
        return d


class MiniSpark:
    """MiniSpark主类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, config_path: Optional[str] = None):
        """
        初始化MiniSpark
        
        Args:
            config: 配置字典，直接提供配置信息
            config_path: 配置文件路径
        """
        # 配置日志
        logger.info("初始化MiniSpark")
        
        # 优先使用传入的config字典，否则加载配置文件，最后使用默认配置
        if config is not None:
            self.config = dict_to_namespace(config)
            logger.info("使用传入的配置字典")
        else:
            config_file = config_path or "config.toml"
            config_dict = self._load_config(config_file)
            self.config = dict_to_namespace(config_dict)
        self.connectors: Dict[str, BaseConnector] = {}
        # 用于跟踪临时数据库文件，以便在程序结束时清理
        self.temp_database_path = None
        self.engine: BaseEngine = self._init_engine()
        self.processor = DataProcessor()
        # 设置DataProcessor对MiniSpark的引用
        self.processor.set_minispark(self)
        
        # 初始化处理重复列名的设置
        if hasattr(self.config, 'handle_duplicate_columns'):
            self.engine.handle_duplicate_columns = self.config.handle_duplicate_columns
        self.tables: Dict[str, pd.DataFrame] = {}
        
        # 注册退出处理函数
        atexit.register(self._cleanup_temp_database)
        
        logger.info("MiniSpark初始化完成")
        
    @property
    def handle_duplicate_columns(self):
        """获取处理重复列名的方式"""
        return self.config.handle_duplicate_columns if hasattr(self.config, 'handle_duplicate_columns') else 'rename'
    
    @handle_duplicate_columns.setter
    def handle_duplicate_columns(self, value):
        """设置处理重复列名的方式"""
        logger.info(f"设置处理重复列名的方式: {value}")
        self.config.handle_duplicate_columns = value
        # 更新引擎中的设置
        if self.engine:
            self.engine.handle_duplicate_columns = value
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        logger.info(f"加载配置文件: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = toml.load(f)
            logger.info("配置文件加载成功")
            
            # 确保配置中包含handle_duplicate_columns
            if 'handle_duplicate_columns' not in config:
                config['handle_duplicate_columns'] = 'rename'
                
            return config
        except FileNotFoundError:
            logger.warning(f"配置文件 {config_path} 不存在，使用默认配置")
            # 如果配置文件不存在，返回默认配置
            return {
                "engine": {
                    "type": "sqlite",
                    "database_path": ":memory:"
                },
                "storage": {
                    "format": "parquet"
                },
                "handle_duplicate_columns": "rename"
            }
    
    def _init_engine(self) -> BaseEngine:
        """初始化本地处理引擎"""
        engine_type = self.config.engine.type if hasattr(self.config, 'engine') and hasattr(self.config.engine, 'type') else 'sqlite'
        database_path = self.config.engine.database_path if hasattr(self.config, 'engine') and hasattr(self.config.engine, 'database_path') else ':memory:'
        
        # 处理临时文件数据库路径
        final_database_path = database_path
        if database_path != ":memory:" and not os.path.isabs(database_path):
            # 如果不是内存数据库且不是绝对路径，则在临时目录中创建
            temp_dir = tempfile.gettempdir()
            final_database_path = os.path.join(temp_dir, database_path)
            self.temp_database_path = final_database_path
            # 确保临时文件所在的目录存在
            os.makedirs(os.path.dirname(final_database_path) if os.path.dirname(final_database_path) else temp_dir, exist_ok=True)
            logger.info(f"使用临时数据库文件: {final_database_path}")
        elif database_path != ":memory:" and os.path.isabs(database_path):
            # 如果是绝对路径，也记录下来以便清理
            self.temp_database_path = database_path
        
        logger.info(f"初始化本地处理引擎: {engine_type}, 数据库路径: {final_database_path}")
        
        if engine_type == "duckdb":
            try:
                from .engines.duckdb_engine import DuckDBEngine
                # 添加超时机制测试DuckDB引擎
                engine = None
                start_time = time.time()
                timeout = 10  # 10秒超时
                
                logger.info("尝试初始化DuckDB引擎")
                engine = DuckDBEngine(final_database_path)
                
                # 简单测试引擎是否工作正常
                test_result = engine.execute_query("SELECT 'test' as result")
                logger.info("DuckDB引擎测试查询成功")
                
                logger.info("DuckDB引擎初始化成功")
                engine.handle_duplicate_columns = self.handle_duplicate_columns
                return engine
            except Exception as e:
                logger.warning(f"DuckDB引擎初始化失败: {e}，回退到SQLite引擎")
                from .engines.sqlite_engine import SQLiteEngine
                engine = SQLiteEngine(final_database_path)
                engine.handle_duplicate_columns = self.handle_duplicate_columns
                return engine
        elif engine_type == "sqlite":
            from .engines.sqlite_engine import SQLiteEngine
            engine = SQLiteEngine(final_database_path)
            engine.handle_duplicate_columns = self.handle_duplicate_columns
            return engine
        else:
            logger.error(f"不支持的引擎类型: {engine_type}")
            raise ValueError(f"不支持的引擎类型: {engine_type}")
    
    def _cleanup_temp_database(self):
        """清理临时数据库文件"""
        if self.temp_database_path and os.path.exists(self.temp_database_path):
            try:
                # 先关闭引擎以释放文件锁
                if hasattr(self, 'engine') and self.engine:
                    self.engine.close()
                
                # 删除临时数据库文件
                os.remove(self.temp_database_path)
                logger.info(f"已清理临时数据库文件: {self.temp_database_path}")
            except Exception as e:
                logger.warning(f"清理临时数据库文件失败: {e}")
    
    def set_config(self, config: Dict[str, Any]):
        """
        设置配置字典
        
        Args:
            config: 配置字典
        """
        logger.info("设置新的配置")
        self.config = dict_to_namespace(config)
        # 重新初始化引擎以应用新配置
        self.engine = self._init_engine()
    
    def set_config_path(self, config_path: str):
        """
        通过配置文件路径设置配置
        
        Args:
            config_path: 配置文件路径
        """
        logger.info(f"通过路径设置配置: {config_path}")
        config_dict = self._load_config(config_path)
        self.config = dict_to_namespace(config_dict)
        # 重新初始化引擎以应用新配置
        self.engine = self._init_engine()
    
    def set_handle_duplicate_columns(self, handle_duplicate_columns: str):
        """
        设置处理重复列名的方式
        
        Args:
            handle_duplicate_columns: 处理重复列名的方式:
                "rename" - 自动重命名重复列
                "error" - 抛出异常
                "keep_first" - 只保留第一个重复列，删除其他重复列
        """
        logger.info(f"设置处理重复列名的方式: {handle_duplicate_columns}")
        self.handle_duplicate_columns = handle_duplicate_columns
        # 更新引擎中的设置
        if self.engine:
            self.engine.handle_duplicate_columns = self.handle_duplicate_columns
    
    
    def add_connector(self, name: str, connector: BaseConnector):
        """
        添加数据库连接器
        
        Args:
            name: 连接器名称
            connector: 连接器实例
        """
        logger.info(f"添加连接器: {name}, 类型: {type(connector).__name__}")
        self.connectors[name] = connector
    
    def load_data(self, connector_name: str, query: str, table_name: str, register: bool = True, **kwargs):
        """
        从指定连接器加载数据
        
        Args:
            connector_name: 连接器名称
            query: SQL查询语句或文件路径
            table_name: 表名称
            register: 是否注册到本地引擎
            **kwargs: 传递给连接器的额外参数
        """
        logger.info(f"从连接器 {connector_name} 加载数据, 表名: {table_name}")
        
        if connector_name not in self.connectors:
            logger.error(f"连接器 {connector_name} 不存在")
            raise ValueError(f"连接器 {connector_name} 不存在")
        
        connector = self.connectors[connector_name]
        # 检查连接器的sql方法是否支持额外参数
        import inspect
        sig = inspect.signature(connector.sql)
        if 'kwargs' in sig.parameters or any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()):
            df = connector.sql(query, table_name, register, **kwargs)
        else:
            df = connector.sql(query, table_name, register)
        
        # 保存到本地表缓存
        self.tables[table_name] = df
        
        # 如果需要注册到本地引擎
        if register:
            logger.info(f"注册表 {table_name} 到本地引擎")
            self.engine.register_table(table_name, df)
        
        logger.info(f"数据加载完成，表名: {table_name}")
        return df
    
    def execute_query(self, query: str, table_name: str = None, register: bool = True):
        """
        在本地引擎中执行SQL查询
        
        Args:
            query: SQL查询语句
            table_name: 表名称，如果提供则将结果注册为表
            register: 是否注册到本地引擎（仅在table_name提供时有效）
        """
        logger.info(f"执行SQL查询: {query}")
        result = self.engine.execute_query(query)
        logger.info("查询执行完成")
        
        # 如果提供了表名，则将结果注册到本地引擎
        if table_name is not None and register:
            logger.info(f"将查询结果注册为表: {table_name}")
            self.engine.register_table(table_name, result)
            # 同时保存到本地表缓存
            self.tables[table_name] = result
        
        return result
    
    def list_tables(self):
        """
        列出所有已注册的表及其基本信息
        
        Returns:
            dict: 包含表信息的字典
        """
        if not self.tables:
            print("没有已注册的表")
            return {}
        
        print("已注册的表:")
        print("=" * 60)
        table_info = {}
        for table_name, df in self.tables.items():
            info = {
                'shape': df.shape,
                'columns': list(df.columns),
                'memory_usage': df.memory_usage(deep=True).sum()
            }
            table_info[table_name] = info
            
            print(f"表名: {table_name}")
            print(f"  形状: {df.shape}")
            print(f"  列名: {list(df.columns)}")
            print(f"  内存占用: {info['memory_usage']} bytes")
            print()
            
        return table_info
    
    def close(self):
        """关闭所有连接和引擎"""
        logger.info("关闭所有连接和引擎")
        
        # 关闭所有连接器
        for name, connector in self.connectors.items():
            logger.info(f"关闭连接器: {name}")
            connector.close()
        
        # 关闭本地引擎
        logger.info("关闭本地引擎")
        self.engine.close()
        
        # 清理临时数据库文件
        self._cleanup_temp_database()
        
        logger.info("所有连接和引擎已关闭")
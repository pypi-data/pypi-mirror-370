import pandas as pd
from loguru import logger
from .base import BaseConnector
import json


class JSONConnector(BaseConnector):
    """JSON文件连接器"""
    
    def __init__(self, name: str, encoding: str = "utf-8"):
        super().__init__(name)
        self.encoding = encoding
        logger.info(f"初始化JSON连接器: {name}, 编码: {encoding}")
    
    def sql(self, query: str, table_name: str, register: bool = True):
        """
        执行SQL查询（基于JSON文件）
        注意：对于JSON文件，query参数应该是文件路径
        
        Args:
            query: JSON文件路径
            table_name: 表名称
            register: 是否注册到本地数据处理引擎
        """
        logger.info(f"JSON连接器执行查询, 文件: {query}, 表名: {table_name}")
        
        try:
            # 读取JSON文件
            with open(query, 'r', encoding=self.encoding) as f:
                data = json.load(f)
            
            # 将JSON数据转换为DataFrame
            # 如果数据是字典列表，直接转换
            if isinstance(data, list):
                df = pd.DataFrame(data)
            # 如果数据是字典，需要特殊处理
            elif isinstance(data, dict):
                # 如果字典的值是列表，且长度相同，可以转换为DataFrame
                if all(isinstance(v, list) for v in data.values()):
                    df = pd.DataFrame(data)
                else:
                    # 否则将字典作为一行数据
                    df = pd.DataFrame([data])
            else:
                # 其他情况，创建单列DataFrame
                df = pd.DataFrame({'value': [data]})
            
            # 处理复杂数据类型（如列表、字典），将其转换为字符串
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].apply(lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, (list, dict)) else x)
            
            df.table_name = table_name
            df.register = register
            logger.info(f"JSON文件读取成功, 形状: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"读取JSON文件失败: {e}")
            raise
    
    def close(self):
        """关闭连接（JSON不需要关闭连接）"""
        logger.info(f"关闭JSON连接器: {self.name}")
        pass
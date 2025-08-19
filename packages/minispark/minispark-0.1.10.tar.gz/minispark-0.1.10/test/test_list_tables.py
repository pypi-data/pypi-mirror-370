"""
测试MiniSpark的list_tables方法
"""

import pandas as pd
import sys
import os
import unittest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from minispark import MiniSpark


class TestListTables(unittest.TestCase):
    """测试MiniSpark的list_tables方法"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.spark = MiniSpark()
    
    def test_list_tables_with_data(self):
        """测试有数据时的list_tables方法"""
        # 创建测试数据
        users_data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [25, 30, 35]
        })
        
        orders_data = pd.DataFrame({
            'order_id': [101, 102, 103],
            'user_id': [1, 2, 1],
            'amount': [100.0, 200.0, 150.0]
        })
        
        # 注册表到引擎
        self.spark.engine.register_table('users', users_data)
        self.spark.engine.register_table('orders', orders_data)
        
        # 保存到本地表缓存
        self.spark.tables['users'] = users_data
        self.spark.tables['orders'] = orders_data
        
        # 测试list_tables方法
        table_info = self.spark.list_tables()
        
        # 验证返回结果
        self.assertIsInstance(table_info, dict)
        self.assertIn('users', table_info)
        self.assertIn('orders', table_info)
        self.assertEqual(len(table_info), 2)
        
        # 验证表信息
        self.assertEqual(table_info['users']['shape'], (3, 3))
        self.assertEqual(table_info['orders']['shape'], (3, 3))
        self.assertIn('id', table_info['users']['columns'])
        self.assertIn('order_id', table_info['orders']['columns'])
    
    def test_list_tables_empty(self):
        """测试没有表时的list_tables方法"""
        # 确保没有表
        self.spark.tables = {}
        
        # 测试list_tables方法
        table_info = self.spark.list_tables()
        
        # 验证返回结果
        self.assertIsInstance(table_info, dict)
        self.assertEqual(len(table_info), 0)
    
    def tearDown(self):
        """测试结束后的清理工作"""
        self.spark.close()


def run_tests():
    """运行所有测试"""
    print("开始测试MiniSpark的list_tables方法...")
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestListTables)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回测试结果
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    if success:
        print("\n✅ 所有测试通过!")
    else:
        print("\n❌ 部分测试失败!")
        sys.exit(1)
"""
测试DataProcessor的自动注册功能
"""

import pandas as pd
import sys
import os
import unittest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from minispark import MiniSpark


class TestProcessorAutoRegister(unittest.TestCase):
    """测试DataProcessor的自动注册功能"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.spark = MiniSpark()
    
    def test_apply_function_with_auto_register(self):
        """测试apply_function方法的自动注册功能"""
        # 创建测试数据
        data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'salary': [50000, 60000, 70000]
        })
        
        # 注册表到引擎
        self.spark.engine.register_table('employees', data)
        self.spark.tables['employees'] = data
        
        # 定义处理函数
        def categorize_salary(row):
            salary = row['salary']
            if salary >= 65000:
                return 'High'
            elif salary >= 55000:
                return 'Medium'
            else:
                return 'Low'
        
        # 注册函数
        self.spark.processor.register_function('salary_category', categorize_salary)
        
        # 应用函数并自动注册结果
        result = self.spark.processor.apply_function(
            data, 
            'salary_category', 
            'salary_category',
            table_name='employees_with_category'
        )
        
        # 验证结果
        self.assertIn('salary_category', result.columns)
        self.assertIn('employees_with_category', self.spark.tables)
        self.assertIn('employees_with_category', self.spark.engine.tables)
        
        # 验证注册的表与返回的结果一致
        registered_table = self.spark.tables['employees_with_category']
        pd.testing.assert_frame_equal(result, registered_table)
    
    def test_apply_custom_function_with_auto_register(self):
        """测试apply_custom_function方法的自动注册功能"""
        # 创建测试数据
        data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'salary': [50000, 60000, 70000],
            'bonus': [5000, 6000, 7000]
        })
        
        # 注册表到引擎
        self.spark.engine.register_table('employees', data)
        self.spark.tables['employees'] = data
        
        # 应用自定义函数并自动注册结果
        result = self.spark.processor.apply_custom_function(
            data,
            lambda row: row['salary'] + row['bonus'],
            'total_compensation',
            table_name='employees_with_compensation'
        )
        
        # 验证结果
        self.assertIn('total_compensation', result.columns)
        self.assertIn('employees_with_compensation', self.spark.tables)
        self.assertIn('employees_with_compensation', self.spark.engine.tables)
        
        # 验证计算结果
        expected_compensation = [55000, 66000, 77000]
        actual_compensation = result['total_compensation'].tolist()
        self.assertEqual(expected_compensation, actual_compensation)
        
        # 验证注册的表与返回的结果一致
        registered_table = self.spark.tables['employees_with_compensation']
        pd.testing.assert_frame_equal(result, registered_table)
    
    def test_explode_column_with_auto_register(self):
        """测试explode_column方法的自动注册功能"""
        # 创建测试数据
        data = pd.DataFrame({
            'id': [1, 2],
            'tags': ['python,java,c++', 'javascript,html,css'],
            'value': [100, 200]
        })
        
        # 注册表到引擎
        self.spark.engine.register_table('data_with_tags', data)
        self.spark.tables['data_with_tags'] = data
        
        # 应用拆分并自动注册结果
        result = self.spark.processor.explode_column(
            data,
            'tags',
            ',',
            table_name='exploded_tags'
        )
        
        # 验证结果
        self.assertEqual(len(result), 6)  # 原来2行，每行3个标签，共6行
        self.assertIn('exploded_tags', self.spark.tables)
        self.assertIn('exploded_tags', self.spark.engine.tables)
        
        expected_tags = ['python', 'java', 'c++', 'javascript', 'html', 'css']
        actual_tags = result['tags'].tolist()
        self.assertEqual(expected_tags, actual_tags)
        
        # 验证注册的表与返回的结果一致
        registered_table = self.spark.tables['exploded_tags']
        pd.testing.assert_frame_equal(result, registered_table)
    
    def test_disable_auto_register(self):
        """测试禁用自动注册功能"""
        # 创建测试数据
        data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'salary': [50000, 60000, 70000]
        })
        
        # 注册表到引擎
        self.spark.engine.register_table('employees', data)
        self.spark.tables['employees'] = data
        
        # 定义处理函数
        def categorize_salary(row):
            salary = row['salary']
            if salary >= 65000:
                return 'High'
            elif salary >= 55000:
                return 'Medium'
            else:
                return 'Low'
        
        # 注册函数
        self.spark.processor.register_function('salary_category', categorize_salary)
        
        # 应用函数但禁用自动注册
        result = self.spark.processor.apply_function(
            data, 
            'salary_category', 
            'salary_category',
            table_name='employees_with_category',
            register=False  # 禁用注册
        )
        
        # 验证结果未被注册
        self.assertNotIn('employees_with_category', self.spark.tables)
        self.assertNotIn('employees_with_category', self.spark.engine.tables)
    
    def tearDown(self):
        """测试结束后的清理工作"""
        self.spark.close()


def run_tests():
    """运行所有测试"""
    print("开始测试DataProcessor的自动注册功能...")
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestProcessorAutoRegister)
    
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
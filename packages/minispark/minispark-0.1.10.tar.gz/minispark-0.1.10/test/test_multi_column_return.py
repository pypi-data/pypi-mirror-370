"""
测试DataProcessor的apply_custom_function方法支持返回多个列的功能
"""

import pandas as pd
import sys
import os
import unittest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from minispark.processors.data_processor import DataProcessor


class TestMultiColumnReturn(unittest.TestCase):
    """测试apply_custom_function支持返回多个列的功能"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.processor = DataProcessor()
    
    def test_single_column_return(self):
        """测试单列返回（向后兼容性）"""
        # 创建测试数据
        data = pd.DataFrame({
            'a': [1, 2, 3],
            'b': [4, 5, 6]
        })
        
        # 应用返回单个值的函数
        result = self.processor.apply_custom_function(
            data, 
            lambda row: row['a'] + row['b'],
            ['sum']
        )
        
        # 验证结果
        self.assertIn('sum', result.columns)
        expected_values = [5, 7, 9]
        actual_values = result['sum'].tolist()
        self.assertEqual(expected_values, actual_values)
    
    def test_multiple_columns_return_list(self):
        """测试多列返回（列表形式）"""
        # 创建测试数据
        data = pd.DataFrame({
            'a': [1, 2, 3],
            'b': [4, 5, 6],
            'c': [7, 8, 9]
        })
        
        # 应用返回列表的函数
        result = self.processor.apply_custom_function(
            data, 
            lambda row: [min(row['a'], row['b'], row['c']), max(row['a'], row['b'], row['c'])],
            ['min_val', 'max_val']
        )
        
        # 验证结果
        self.assertIn('min_val', result.columns)
        self.assertIn('max_val', result.columns)
        
        expected_min_values = [1, 2, 3]
        expected_max_values = [7, 8, 9]
        
        actual_min_values = result['min_val'].tolist()
        actual_max_values = result['max_val'].tolist()
        
        self.assertEqual(expected_min_values, actual_min_values)
        self.assertEqual(expected_max_values, actual_max_values)
    
    def test_multiple_columns_return_tuple(self):
        """测试多列返回（元组形式）"""
        # 创建测试数据
        data = pd.DataFrame({
            'price': [100, 200, 150],
            'quantity': [2, 3, 1],
            'discount': [0.1, 0.2, 0.05]
        })
        
        # 应用返回元组的函数
        result = self.processor.apply_custom_function(
            data,
            lambda row: (
                row['price'] * row['quantity'] * (1 - row['discount']),  # 总价
                row['price'] * row['quantity'] * row['discount']         # 折扣金额
            ),
            ['total', 'discount_amount']
        )
        
        # 验证结果
        self.assertIn('total', result.columns)
        self.assertIn('discount_amount', result.columns)
        
        # 验证总价计算
        expected_total = [180.0, 480.0, 142.5]  # (100*2*0.9, 200*3*0.8, 150*1*0.95)
        actual_total = result['total'].tolist()
        for expected, actual in zip(expected_total, actual_total):
            self.assertAlmostEqual(expected, actual, places=2)
        
        # 验证折扣金额计算
        expected_discount = [20.0, 120.0, 7.5]  # (100*2*0.1, 200*3*0.2, 150*1*0.05)
        actual_discount = result['discount_amount'].tolist()
        for expected, actual in zip(expected_discount, actual_discount):
            self.assertAlmostEqual(expected, actual, places=2)
    
    def test_multiple_columns_return_dict(self):
        """测试多列返回（字典形式）"""
        # 创建测试数据
        data = pd.DataFrame({
            'score1': [80, 90, 70],
            'score2': [85, 88, 75],
            'score3': [90, 85, 80]
        })
        
        # 应用返回字典的函数
        result = self.processor.apply_custom_function(
            data,
            lambda row: {
                'average': (row['score1'] + row['score2'] + row['score3']) / 3,
                'highest': max(row['score1'], row['score2'], row['score3'])
            },
            ['average', 'highest']
        )
        
        # 验证结果
        self.assertIn('average', result.columns)
        self.assertIn('highest', result.columns)
        
        # 验证平均分计算
        expected_avg = [85.0, 87.67, 75.0]  # [(80+85+90)/3, (90+88+85)/3, (70+75+80)/3]
        actual_avg = result['average'].tolist()
        for expected, actual in zip(expected_avg, actual_avg):
            self.assertAlmostEqual(expected, actual, places=2)
        
        # 验证最高分
        expected_max = [90, 90, 80]
        actual_max = result['highest'].tolist()
        self.assertEqual(expected_max, actual_max)
    
    def test_error_handling_mismatched_columns(self):
        """测试列数不匹配时的错误处理"""
        # 创建测试数据
        data = pd.DataFrame({
            'a': [1, 2, 3],
            'b': [4, 5, 6]
        })
        
        # 应用返回值数量与列数不匹配的函数
        with self.assertRaises(ValueError) as context:
            self.processor.apply_custom_function(
                data,
                lambda row: [row['a'], row['b']],  # 但只返回2个值
                ['col1', 'col2', 'col3']  # 要求3列
            )
        
        self.assertIn("返回的值数量", str(context.exception))
        self.assertIn("与指定的列数", str(context.exception))
    
    def test_error_handling_empty_column_list(self):
        """测试空列名列表的错误处理"""
        # 创建测试数据
        data = pd.DataFrame({
            'a': [1, 2, 3],
            'b': [4, 5, 6]
        })
        
        # 使用空列表作为列名
        with self.assertRaises(ValueError) as context:
            self.processor.apply_custom_function(
                data,
                lambda row: row['a'] + row['b'],
                []
            )
        
        self.assertIn("new_column_name列表不能为空", str(context.exception))
    
    def test_single_value_multiple_columns(self):
        """测试单个值复制到多个列"""
        # 创建测试数据
        data = pd.DataFrame({
            'a': [1, 2, 3]
        })
        
        # 应用返回单个值的函数，但指定多个列
        result = self.processor.apply_custom_function(
            data,
            lambda row: row['a'] * 2,
            ['copy1', 'copy2', 'copy3']
        )
        
        # 验证结果
        self.assertIn('copy1', result.columns)
        self.assertIn('copy2', result.columns)
        self.assertIn('copy3', result.columns)
        
        expected_values = [2, 4, 6]
        self.assertEqual(result['copy1'].tolist(), expected_values)
        self.assertEqual(result['copy2'].tolist(), expected_values)
        self.assertEqual(result['copy3'].tolist(), expected_values)


def run_tests():
    """运行所有测试"""
    print("开始测试apply_custom_function支持返回多个列的功能...")
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMultiColumnReturn)
    
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
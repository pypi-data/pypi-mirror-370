"""
测试简化后的DataProcessor API
"""

import pandas as pd
import sys
import os
import unittest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from minispark.processors.data_processor import DataProcessor


class TestSimplifiedAPI(unittest.TestCase):
    """测试简化后的DataProcessor API"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.processor = DataProcessor()
    
    def test_single_column_custom_function(self):
        """测试单列自定义函数（通过访问整行数据实现）"""
        # 创建测试数据
        data = pd.DataFrame({
            'id': [1, 2, 3],
            'salary': [50000, 60000, 70000],
            'bonus': [5000, 6000, 7000]
        })
        
        # 应用自定义函数（通过访问整行数据实现单列处理）
        result = self.processor.apply_custom_function(
            data, 
            lambda row: row['salary'] * 1.1,
            'salary_with_tax'
        )
        
        # 验证结果
        self.assertIn('salary_with_tax', result.columns)
        expected_values = [55000.0, 66000.0, 77000.0]
        actual_values = result['salary_with_tax'].tolist()
        for expected, actual in zip(expected_values, actual_values):
            self.assertAlmostEqual(expected, actual, places=2)
    
    def test_multi_column_custom_function(self):
        """测试多列自定义函数（通过访问整行数据实现）"""
        # 创建测试数据
        data = pd.DataFrame({
            'id': [1, 2, 3],
            'salary': [50000, 60000, 70000],
            'bonus': [5000, 6000, 7000],
            'department': ['IT', 'HR', 'Finance']
        })
        
        # 应用自定义函数（通过访问整行数据实现多列处理）
        result = self.processor.apply_custom_function(
            data, 
            lambda row: row['salary'] + row['bonus'],
            'total_compensation'
        )
        
        # 验证结果
        self.assertIn('total_compensation', result.columns)
        expected_values = [55000, 66000, 77000]
        actual_values = result['total_compensation'].tolist()
        self.assertEqual(expected_values, actual_values)
    
    def test_multi_column_custom_function_complex(self):
        """测试复杂的多列自定义函数（通过访问整行数据实现）"""
        # 创建测试数据
        data = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'salary': [50000, 60000, 70000],
            'bonus': [5000, 6000, 7000],
            'department': ['IT', 'HR', 'Finance']
        })
        
        # 定义复杂函数：根据部门和薪资计算等级
        def calculate_level(row):
            base_score = row['salary'] / 10000
            if row['department'] == 'IT':
                base_score += 2
            elif row['department'] == 'Finance':
                base_score += 1.5
            # 奖金也会影响等级
            bonus_score = row['bonus'] / 1000
            return base_score + bonus_score
        
        # 应用自定义函数（通过访问整行数据实现多列处理）
        result = self.processor.apply_custom_function(
            data, 
            calculate_level,
            'employee_level'
        )
        
        # 验证结果
        self.assertIn('employee_level', result.columns)
        # 验证Alice的等级: 50000/10000 + 2 + 5000/1000 = 5 + 2 + 5 = 12
        self.assertAlmostEqual(result.iloc[0]['employee_level'], 12.0, places=2)
        # 验证Bob的等级: 60000/10000 + 0 + 6000/1000 = 6 + 0 + 6 = 12
        self.assertAlmostEqual(result.iloc[1]['employee_level'], 12.0, places=2)
        # 验证Charlie的等级: 70000/10000 + 1.5 + 7000/1000 = 7 + 1.5 + 7 = 15.5
        self.assertAlmostEqual(result.iloc[2]['employee_level'], 15.5, places=2)
    
    def test_register_and_apply_multi_column_function(self):
        """测试注册并应用多列函数（通过访问整行数据实现）"""
        # 创建测试数据
        data = pd.DataFrame({
            'product': ['A', 'B', 'C'],
            'price': [100, 200, 150],
            'quantity': [10, 5, 8],
            'discount': [0.1, 0.2, 0.05]
        })
        
        # 注册函数
        def calculate_revenue(row):
            return row['price'] * row['quantity'] * (1 - row['discount'])
        
        self.processor.register_function('revenue_calculator', calculate_revenue)
        
        # 应用已注册的函数（通过访问整行数据实现多列处理）
        result = self.processor.apply_function(
            data, 
            'revenue',
            'revenue_calculator'
        )
        
        # 验证结果
        self.assertIn('revenue', result.columns)
        # 验证产品A的收入: 100 * 10 * (1 - 0.1) = 900
        self.assertAlmostEqual(result.iloc[0]['revenue'], 900.0, places=2)
        # 验证产品B的收入: 200 * 5 * (1 - 0.2) = 800
        self.assertAlmostEqual(result.iloc[1]['revenue'], 800.0, places=2)
        # 验证产品C的收入: 150 * 8 * (1 - 0.05) = 1140
        self.assertAlmostEqual(result.iloc[2]['revenue'], 1140.0, places=2)


def run_tests():
    """运行所有测试"""
    print("开始测试简化后的DataProcessor API...")
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSimplifiedAPI)
    
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
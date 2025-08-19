"""
测试DataProcessor默认传入整行数据的功能
"""

import pandas as pd
import sys
import os
import unittest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from minispark.processors.data_processor import DataProcessor


class TestRowFunction(unittest.TestCase):
    """测试简化后的DataProcessor API"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.processor = DataProcessor()
    
    def test_apply_custom_function_with_row(self):
        """测试自定义函数接收整行数据"""
        # 创建测试数据
        data = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [25, 30, 35],
            'salary': [50000, 60000, 70000],
            'department': ['IT', 'HR', 'Finance']
        })
        
        # 定义处理整行数据的函数
        def process_row(row):
            # 根据年龄和部门计算奖金
            bonus_rate = 0.1 if row['age'] > 30 else 0.05
            dept_bonus = 5000 if row['department'] == 'IT' else 0
            return row['salary'] * bonus_rate + dept_bonus
        
        # 应用函数，不指定具体列
        result = self.processor.apply_custom_function(
            data, 
            process_row,
            'bonus'
        )
        
        # 验证结果
        self.assertIn('bonus', result.columns)
        # Alice: 50000 * 0.05 + 5000 = 7500 (IT部门有额外奖金)
        self.assertEqual(result.iloc[0]['bonus'], 7500.0)
        # Bob: 60000 * 0.05 + 0 = 3000
        self.assertEqual(result.iloc[1]['bonus'], 3000.0)
        # Charlie: 70000 * 0.1 + 0 = 7000
        self.assertEqual(result.iloc[2]['bonus'], 7000.0)
    
    def test_register_and_apply_function_with_row(self):
        """测试注册并应用接收整行数据的函数"""
        # 创建测试数据
        data = pd.DataFrame({
            'product': ['A', 'B', 'C'],
            'price': [100, 200, 150],
            'quantity': [10, 5, 8],
            'category': ['Electronics', 'Books', 'Clothing']
        })
        
        # 定义处理整行数据的函数
        def calculate_revenue(row):
            # 根据类别应用不同的税率
            tax_rate = 0.1 if row['category'] == 'Electronics' else 0.05
            base_revenue = row['price'] * row['quantity']
            return base_revenue * (1 - tax_rate)
        
        # 注册函数
        self.processor.register_function('revenue_calculator', calculate_revenue)
        
        # 应用已注册的函数
        result = self.processor.apply_function(
            data, 
            'revenue',
            'revenue_calculator'
        )
        
        # 验证结果
        self.assertIn('revenue', result.columns)
        # 产品A: 100 * 10 * (1 - 0.1) = 900
        self.assertAlmostEqual(result.iloc[0]['revenue'], 900.0, places=2)
        # 产品B: 200 * 5 * (1 - 0.05) = 950
        self.assertAlmostEqual(result.iloc[1]['revenue'], 950.0, places=2)
        # 产品C: 150 * 8 * (1 - 0.05) = 1140
        self.assertAlmostEqual(result.iloc[2]['revenue'], 1140.0, places=2)
    
    def test_apply_custom_function_with_row_complex(self):
        """测试复杂的整行数据处理函数"""
        # 创建测试数据
        data = pd.DataFrame({
            'student': ['Alice', 'Bob', 'Charlie', 'David'],
            'math': [90, 85, 95, 80],
            'english': [85, 90, 80, 85],
            'science': [88, 92, 90, 87],
            'grade': [10, 10, 11, 11]
        })
        
        # 定义复杂的处理函数
        def calculate_gpa(row):
            # 计算平均分并根据年级调整
            avg_score = (row['math'] + row['english'] + row['science']) / 3
            grade_bonus = 1.0 if row['grade'] == 11 else 0.0
            # 转换为4.0 GPA制
            gpa = (avg_score / 100) * 4.0 + grade_bonus
            return round(gpa, 2)
        
        # 应用函数
        result = self.processor.apply_custom_function(
            data, 
            calculate_gpa,
            'gpa'
        )
        
        # 验证结果
        self.assertIn('gpa', result.columns)
        # Alice: ((90+85+88)/3 / 100) * 4.0 + 0 = 3.51
        self.assertAlmostEqual(result.iloc[0]['gpa'], 3.51, places=2)
        # Bob: ((85+90+92)/3 / 100) * 4.0 + 0 = 3.56
        self.assertAlmostEqual(result.iloc[1]['gpa'], 3.56, places=2)
        # Charlie: ((95+80+90)/3 / 100) * 4.0 + 1.0 = 4.53
        self.assertAlmostEqual(result.iloc[2]['gpa'], 4.53, places=2)
        # David: ((80+85+87)/3 / 100) * 4.0 + 1.0 = 4.36
        self.assertAlmostEqual(result.iloc[3]['gpa'], 4.36, places=2)
    


def run_tests():
    """运行所有测试"""
    print("开始测试简化后的DataProcessor API...")
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRowFunction)
    
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
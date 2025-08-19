"""
测试DataProcessor的explode_column方法支持多个分隔符的功能
"""

import pandas as pd
import sys
import os
import unittest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from minispark.processors.data_processor import DataProcessor


class TestExplodeMultipleSeparators(unittest.TestCase):
    """测试explode_column方法支持多个分隔符的功能"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.processor = DataProcessor()
    
    def test_single_separator(self):
        """测试单个分隔符的功能"""
        # 创建测试数据
        data = pd.DataFrame({
            'id': [1, 2],
            'tags': ['python,java,c++', 'javascript,html,css'],
            'value': [100, 200]
        })
        
        # 使用单个分隔符进行拆分
        result = self.processor.explode_column(data, 'tags', ',')
        
        # 验证结果
        self.assertEqual(len(result), 6)  # 原来2行，每行3个标签，共6行
        self.assertEqual(list(result['tags']), ['python', 'java', 'c++', 'javascript', 'html', 'css'])
        self.assertEqual(list(result['value']), [100, 100, 100, 200, 200, 200])
        
        # 验证列名保持不变
        expected_columns = ['id', 'tags', 'value']
        self.assertEqual(list(result.columns), expected_columns)
    
    def test_multiple_separators_list(self):
        """测试多个分隔符列表的功能"""
        # 创建测试数据
        data = pd.DataFrame({
            'id': [1, 2],
            'tags': ['python;java|c++', 'javascript-html-css'],
            'value': [100, 200]
        })
        
        # 使用多个分隔符进行拆分
        result = self.processor.explode_column(data, 'tags', [';', '|', '-'])
        
        # 验证结果
        self.assertEqual(len(result), 6)  # 原来2行，每行3个标签，共6行
        self.assertEqual(list(result['tags']), ['python', 'java', 'c++', 'javascript', 'html', 'css'])
        self.assertEqual(list(result['value']), [100, 100, 100, 200, 200, 200])
    
    def test_multiple_separators_with_empty_values(self):
        """测试多个分隔符处理包含空值的情况"""
        # 创建测试数据，包含空值
        data = pd.DataFrame({
            'id': [1, 2],
            'tags': ['python;;java|c++|', '|javascript--html-css'],
            'value': [100, 200]
        })
        
        # 使用多个分隔符进行拆分
        result = self.processor.explode_column(data, 'tags', [';', '|', '-'])
        
        # 验证结果，空值应该被过滤掉
        self.assertEqual(len(result), 6)  # 不包含空值
        expected_tags = ['python', 'java', 'c++', 'javascript', 'html', 'css']
        self.assertEqual(list(result['tags']), expected_tags)
    
    def test_mixed_separators_in_same_column(self):
        """测试同一列中混合使用不同分隔符的情况"""
        # 创建测试数据，同一列中混合使用不同分隔符
        data = pd.DataFrame({
            'id': [1],
            'tags': ['python;java|c++-javascript,html|css'],
            'value': [100]
        })
        
        # 使用多个分隔符进行拆分
        result = self.processor.explode_column(data, 'tags', [';', '|', '-', ','])
        
        # 验证结果
        self.assertEqual(len(result), 6)
        expected_tags = ['python', 'java', 'c++', 'javascript', 'html', 'css']
        self.assertEqual(list(result['tags']), expected_tags)
        self.assertEqual(list(result['value']), [100, 100, 100, 100, 100, 100])
    
    def test_no_separators_found(self):
        """测试未找到分隔符的情况"""
        # 创建测试数据，不包含任何分隔符
        data = pd.DataFrame({
            'id': [1, 2],
            'tags': ['python', 'java'],
            'value': [100, 200]
        })
        
        # 使用多个分隔符进行拆分
        result = self.processor.explode_column(data, 'tags', [';', '|'])
        
        # 验证结果保持不变
        self.assertEqual(len(result), 2)
        self.assertEqual(list(result['tags']), ['python', 'java'])
        self.assertEqual(list(result['value']), [100, 200])
    
    def test_empty_string_handling(self):
        """测试空字符串的处理"""
        # 创建测试数据，包含空字符串
        data = pd.DataFrame({
            'id': [1],
            'tags': [''],
            'value': [100]
        })
        
        # 使用多个分隔符进行拆分
        result = self.processor.explode_column(data, 'tags', [';', '|'])
        
        # 验证结果，空字符串应该被保留
        self.assertEqual(len(result), 1)
        self.assertEqual(list(result['tags']), [''])
        self.assertEqual(list(result['value']), [100])
    
    def test_special_characters_in_separators(self):
        """测试分隔符中的特殊字符"""
        # 创建测试数据，使用包含特殊字符的分隔符
        data = pd.DataFrame({
            'id': [1],
            'tags': ['python$java#c++'],
            'value': [100]
        })
        
        # 使用特殊字符作为分隔符
        result = self.processor.explode_column(data, 'tags', ['$', '#'])
        
        # 验证结果
        self.assertEqual(len(result), 3)
        self.assertEqual(list(result['tags']), ['python', 'java', 'c++'])
        self.assertEqual(list(result['value']), [100, 100, 100])
    
    def test_chaining_explode_operations(self):
        """测试链式调用explode操作"""
        # 创建测试数据
        data = pd.DataFrame({
            'id': [1],
            'tags': ['python,java;c++|javascript'],
            'value': [100]
        })
        
        # 链式调用explode操作
        result1 = self.processor.explode_column(data, 'tags', ',')
        result2 = self.processor.explode_column(result1, 'tags', [';', '|'])
        
        # 验证结果
        self.assertEqual(len(result2), 4)
        expected_tags = ['python', 'java', 'c++', 'javascript']
        self.assertEqual(list(result2['tags']), expected_tags)
        self.assertEqual(list(result2['value']), [100, 100, 100, 100])


def run_tests():
    """运行所有测试"""
    print("开始测试explode_column方法支持多个分隔符的功能...")
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestExplodeMultipleSeparators)
    
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
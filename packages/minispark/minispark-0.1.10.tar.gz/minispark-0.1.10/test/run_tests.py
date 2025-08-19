"""
运行所有测试的脚本
"""

import os
import sys
import unittest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_all_tests():
    """运行所有测试并生成覆盖率报告"""
    # 发现并运行所有测试
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # 使用 coverage 运行测试
    import coverage
    cov = coverage.Coverage()
    cov.start()

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    cov.stop()
    cov.save()
    cov.report()

    return result.wasSuccessful()

if __name__ == '__main__':
    print("开始运行所有测试...")
    success = run_all_tests()
    if success:
        print("\n✅ 所有测试通过!")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败!")
        sys.exit(1)
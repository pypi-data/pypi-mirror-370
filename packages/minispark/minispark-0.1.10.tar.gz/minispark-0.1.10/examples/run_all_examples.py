#!/usr/bin/env python3
"""
运行所有示例的脚本
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"INFO: 已将项目根目录添加到Python路径: {project_root}")

def run_example(example_name, example_func):
    """运行单个示例"""
    print(f"\n{'='*60}")
    print(f"运行示例: {example_name}")
    print('='*60)
    
    try:
        example_func()
        print(f"\n✅ {example_name} 运行成功")
        return True
    except Exception as e:
        print(f"\n❌ {example_name} 运行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数，运行所有示例"""
    print("开始运行所有MiniSpark示例...")
    
    # 导入所有示例
    try:
        from examples.duplicate_columns_example import (
            duplicate_columns_rename_example,
            duplicate_columns_error_example,
            duplicate_columns_keep_first_example,
            config_dict_example,
            setter_methods_example,
            dot_object_config_example,
            best_practice_example
        )
        print("INFO: 成功加载模块: duplicate_columns_example")
    except ImportError as e:
        print(f"ERROR: 无法加载模块 duplicate_columns_example: {e}")
        sys.exit(1)
    
    # 定义要运行的示例列表
    examples = [
        ("重命名重复列示例", duplicate_columns_rename_example),
        ("错误处理方式示例", duplicate_columns_error_example),
        ("只保留第一个重复列示例", duplicate_columns_keep_first_example),
        ("配置字典示例", config_dict_example),
        ("Setter方法示例", setter_methods_example),
        ("点对象配置示例", dot_object_config_example),
        ("最佳实践示例", best_practice_example)
    ]
    
    # 运行所有示例
    passed = 0
    failed = 0
    
    for example_name, example_func in examples:
        if run_example(example_name, example_func):
            passed += 1
        else:
            failed += 1
    
    # 输出总结
    print(f"\n{'='*60}")
    print("所有示例运行完成!")
    print(f"成功: {passed}")
    print(f"失败: {failed}")
    print(f"总计: {passed + failed}")
    print('='*60)
    
    # 如果有任何示例失败，返回非零退出码
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()

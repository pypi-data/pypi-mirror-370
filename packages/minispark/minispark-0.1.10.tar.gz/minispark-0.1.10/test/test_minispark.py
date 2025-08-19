print("开始测试")

try:
    print("尝试导入MiniSpark")
    from minispark import MiniSpark
    print("MiniSpark导入成功")
    
    print("尝试创建MiniSpark实例")
    spark = MiniSpark()
    print("MiniSpark实例创建成功")
    
    print("测试完成")
except Exception as e:
    print(f"出现错误: {e}")
    import traceback
    traceback.print_exc()
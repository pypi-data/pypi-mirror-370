#!/usr/bin/env python3
"""
运行所有测试用例
"""

import asyncio
import unittest
import sys
import os

# 导入测试模块
from test_create_document_alert_params import TestCreateDocumentAlert
from test_folder_team_params import TestFolderTeamParams
from test_payload_construction import TestPayloadConstruction

def run_all_tests():
    """运行所有测试用例"""
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_suite.addTest(unittest.makeSuite(TestCreateDocumentAlert))
    test_suite.addTest(unittest.makeSuite(TestFolderTeamParams))
    test_suite.addTest(unittest.makeSuite(TestPayloadConstruction))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 返回测试结果
    return result.wasSuccessful()

async def run_async_tests():
    """运行异步测试用例"""
    # 创建测试加载器
    loader = unittest.TestLoader()
    
    # 加载测试用例
    test_suite = unittest.TestSuite()
    test_suite.addTest(loader.loadTestsFromTestCase(TestCreateDocumentAlert))
    test_suite.addTest(loader.loadTestsFromTestCase(TestFolderTeamParams))
    test_suite.addTest(loader.loadTestsFromTestCase(TestPayloadConstruction))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 返回测试结果
    return result.wasSuccessful()

if __name__ == "__main__":
    try:
        # 检查命令行参数
        if len(sys.argv) > 1 and sys.argv[1] == "--async":
            # 使用 asyncio 运行异步测试
            print("🚀 运行异步测试...")
            success = asyncio.run(run_async_tests())
        else:
            # 运行同步测试
            print("🚀 运行同步测试...")
            success = run_all_tests()
        
        # 输出测试结果
        if success:
            print("✅ 所有测试通过！")
        else:
            print("❌ 测试失败！")
        
        # 根据测试结果设置退出码
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试运行出错: {str(e)}")
        sys.exit(1)
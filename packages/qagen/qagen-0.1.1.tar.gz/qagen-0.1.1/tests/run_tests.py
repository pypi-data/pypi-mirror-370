#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试运行脚本
"""

import sys
import os
import subprocess
from pathlib import Path

def run_tests():
    """运行所有测试"""
    print("🧪 开始运行QA Generation CN单元测试...")
    print("=" * 50)
    
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # 运行测试命令
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--color=yes"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 运行测试时出错: {e}")
        return False

def run_specific_test(test_file):
    """运行特定测试文件"""
    print(f"🧪 运行特定测试: {test_file}")
    print("=" * 50)
    
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    cmd = [
        sys.executable, "-m", "pytest",
        f"tests/{test_file}",
        "-v",
        "--tb=short",
        "--color=yes"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 运行测试时出错: {e}")
        return False

def run_coverage():
    """运行覆盖率测试"""
    print("📊 运行覆盖率测试...")
    print("=" * 50)
    
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--cov=qa_gen_cn",
        "--cov-report=html",
        "--cov-report=term-missing",
        "-v"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 运行覆盖率测试时出错: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "coverage":
            success = run_coverage()
        else:
            success = run_specific_test(sys.argv[1])
    else:
        success = run_tests()
    
    if success:
        print("\n✅ 所有测试通过！")
        sys.exit(0)
    else:
        print("\n❌ 测试失败！")
        sys.exit(1)

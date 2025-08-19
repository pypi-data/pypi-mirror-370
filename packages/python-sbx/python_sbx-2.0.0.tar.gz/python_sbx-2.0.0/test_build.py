#!/usr/bin/env python3
"""
测试构建脚本 - 验证包配置是否正确
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

def test_import():
    """测试模块是否能正确导入"""
    print("测试模块导入...")
    try:
        import app
        print("✓ 模块导入成功")
        return True
    except ImportError as e:
        print(f"✗ 模块导入失败: {e}")
        return False

def test_setup():
    """测试setup.py配置"""
    print("测试setup.py配置...")
    try:
        # 在临时目录中测试
        with tempfile.TemporaryDirectory() as temp_dir:
            # 复制必要文件到临时目录
            files_to_copy = ['setup.py', 'app.py', 'requirements.txt']
            for file in files_to_copy:
                if os.path.exists(file):
                    shutil.copy2(file, temp_dir)
            
            # 切换到临时目录
            original_dir = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # 测试setup.py语法
                result = subprocess.run(
                    [sys.executable, 'setup.py', 'check'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print("✓ setup.py配置正确")
                    return True
                else:
                    print(f"✗ setup.py配置错误: {result.stderr}")
                    return False
                    
            finally:
                os.chdir(original_dir)
                
    except Exception as e:
        print(f"✗ 测试setup.py时出错: {e}")
        return False

def test_pyproject():
    """测试pyproject.toml配置"""
    print("测试pyproject.toml配置...")
    try:
        import tomllib
        with open('pyproject.toml', 'rb') as f:
            config = tomllib.load(f)
        
        required_keys = ['build-system', 'project']
        for key in required_keys:
            if key not in config:
                print(f"✗ 缺少必要的配置项: {key}")
                return False
        
        print("✓ pyproject.toml配置正确")
        return True
        
    except ImportError:
        print("⚠ tomllib不可用（Python < 3.11），跳过pyproject.toml测试")
        return True
    except Exception as e:
        print(f"✗ 测试pyproject.toml时出错: {e}")
        return False

def test_requirements():
    """测试requirements.txt"""
    print("测试requirements.txt...")
    try:
        if not os.path.exists('requirements.txt'):
            print("✗ requirements.txt文件不存在")
            return False
        
        with open('requirements.txt', 'r') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        if not requirements:
            print("⚠ requirements.txt为空")
        else:
            print(f"✓ 找到 {len(requirements)} 个依赖")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试requirements.txt时出错: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试包配置...\n")
    
    tests = [
        test_import,
        test_setup,
        test_pyproject,
        test_requirements,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ 测试 {test.__name__} 时出错: {e}")
        print()
    
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！包配置正确。")
        print("\n下一步:")
        print("1. 修改配置文件中的个人信息（作者名、邮箱、项目URL等）")
        print("2. 运行 'python publish.py' 开始发布流程")
    else:
        print("❌ 部分测试失败，请检查配置。")
        sys.exit(1)

if __name__ == "__main__":
    main()
